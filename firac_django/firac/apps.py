"""
Apps to run the FIRAC Django app.
"""
import os
import sys
import json
import re

from collections import Counter
from string import punctuation
from heapq import nlargest

import spacy
import openai

from bs4 import BeautifulSoup
from spacy.lang.en.stop_words import STOP_WORDS
from transformers import AutoTokenizer

from django.core.files.uploadedfile import InMemoryUploadedFile
from django.apps import AppConfig

# Django app config
class FiracConfig(AppConfig):
    """
    Default app config for FIRAC.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'firac'


# File imports
# Abbreviations
BASE_DIR_ABBREVIATIONS = os.path.dirname(os.path.abspath(__file__))
ABBREVIATIONS = os.path.join(BASE_DIR_ABBREVIATIONS, "data", "abbreviations.json")

with open(ABBREVIATIONS, "r", encoding="utf-8") as file:
    abbreviations = json.load(file)

# Legal tests
BASE_DIR_TESTS = os.path.dirname(os.path.abspath(__file__))
LEGAL_TESTS = os.path.join(BASE_DIR_TESTS, "data", "legal-tests.json")

with open(LEGAL_TESTS, "r", encoding="utf-8") as file:
    legal_tests = json.load(file)

# Citation model
BASE_DIR_CITATION_MODEL = os.path.dirname(os.path.abspath(__file__))
CITAION_MODEL = os.path.join(BASE_DIR_CITATION_MODEL, "models", "ner_sections_v1", "model-last")

# Categorization model
BASE_DIR_CATEGORIZATION = os.path.dirname(os.path.abspath(__file__))
CATEGORY_MODEL = os.path.join(BASE_DIR_CATEGORIZATION, "models", "textcat_firac_v3", "model-last")

# Analytic functions

#def local_text_analysis(citations: list):
#    """
#    Analyzes a text locally using the local analysis function. This function
#    returns a dictionary of the legal tests used in the text. If the function
#    finds a citation matching one linked to a legal test, it will return the
#    legal test.
#    """
#    legal_tests_identified = get_legal_test(citations)
#    text_string = ""

#    if legal_tests_identified:
#        text_string += "\nTests found:\n"
#        for test in legal_tests_identified:
#            text_string += f" \u2022 {test['short_form']}\n"
#    else:
#        text_string += "\nTests found: None\n"

#    return text_string


def retrieve_citations(text: str) -> dict:
    """
    Calls a bare-bones NLP model to retrieve citations from text.
    """

    citations = [
        {"type": "decisions", "citations": []},
        {"type": "legislation", "citations": [], "sections": []},
    ]

    # Statutes that are likely to form part of a legal test
    statutes = [
        "Charter",
        "Charter of Rights and Freedoms",
        "Canadian Charter of Rights and Freedoms",
        "Canadian Charter of Rights and Freedoms, Part I of the Constitution \
            Act, 1982, being Schedule B to the Canada Act 1982 (UK), 1982, c \
            11",
        "Canadian Charter of Rights and Freedoms, Part I of the Constitution Act, 1982",
        "CDSA",
        "Controlled Drugs and Substances Act",
        "Controlled Drugs and Substances Act, SC 1996, c 19",
        "Cr. C.",
        "Cr C",
        "Criminal Code",
        "Criminal Code of Canada",
        "Criminal Code, RSC 1985, c C-46",
    ]

    # Extracting neutral and CanLII citations using regex was more economical
    # (and probably accurate) than using the lightly-trained NLP model I used
    # previously.
    case_citation_pattern = r"\b\d{4}\s(?:[A-Z]{2,}\s\d+|CanLII\s\d+)\b"
    citation_list = re.findall(case_citation_pattern, text)
    citations[0]["citations"] = citation_list

    # Finds statutes from the list in the text and adds them to the statute
    # list.
    for statute in statutes:
        if statute in text:
            citations[1]["citations"].append(statute)

    # Add the statutes to the list of citations
    citations[1]["citations"] = [statute for statute in statutes if statute in text]

    # Although regex may be useful for extracting statute names, this will
    # require a fairly comprehensive dictionary of all statutes in Canada that
    # are likely to appear in a legal test. Furthermore, regex turns out to be
    # a poor way to extract statute sections, given how variably they can be
    # written, while a relatively simple NLP model can do a good job of getting
    # enough of them to make this function useful.
    nlp = spacy.load(CITAION_MODEL)
    doc = nlp(text)

    for ent in doc.ents:
        if ent.label_ == "SECTION":
            citations[1]["sections"].append(ent.text)

    for citation in citations:
        citation["citations"] = set(
            citation["citations"] if citation["citations"] else []
        )
        citation["sections"] = set(
            citation["sections"] if "sections" in citation else []
        )
    return citations


#def get_legal_test(citations: dict) -> list[dict]:
#    """
#    This function takes a list of citations and checks them against a list of
#    legal tests. If a citation matches a legal test, the function returns the
#    legal test.
#    """
#    case_citations = citations[0]["citations"]

#    for test in legal_tests:
#        if test["origins"]["citation"] in case_citations:
#            return [test]


#def detect_legal_tests(citations: dict):
#    """
#    Scans a list of citations to determine if any of them correspond to a legal
#    test.
#    """
#    print("\n[underline #FFA500]Analysis[/underline #FFA500]")
#    print("Analyzing text: ", end="")
#    legal_tests_detected = get_legal_test(citations)
#    print("[green]Done.[/green]")
#    test_list = []
#
#    if legal_tests_detected:
#        print("\nTests found:")
#        for test in legal_tests_detected:
#            print(f" \u2022 {test['short_form']}")
#            test_list.append(test["short_form"])
#    else:
#        print("\nTests found: [red]None[/red]")

#    return test_list


# Classification functions


def classify_firac(text: str) -> dict:
    """
    This function splits the document into sentences and then classifies each
    sentence with the closest corresponding FIRAC element. The function returns
    a dictionary with the FIRAC elements as keys and the sentences in a list as
    values.
    """
    print("\n[bold underline #FFA500]Clasifying FIRAC using textcat_firac_v3[/bold underline #FFA500]")
    print("Classifying FIRAC elements: ", end="")
    nlp = spacy.load(CATEGORY_MODEL)
    nlp.add_pipe("sentencizer")
    doc = nlp(text)
    firac = {}

    for sentence in doc.sents:
        categories = nlp(sentence.text).cats
        max_value = max(categories.values())

        for category, score in categories.items():
            # If the category's score is 80% or more of the maximum value,
            # append the sentence to the corresponding FIRAC key.
            if score >= max_value * 0.8:
                category = category.lower()
                firac.setdefault(category, []).append(sentence.text)
        
    print("[green bold]Done.[/green bold]\n")
    print(firac)
    return firac


# Extraction functions
def extract_text(file_path: str):
    """
    Extracts text from an HTML file.
    """
    if file_path.endswith(".html"):
        # Convert HTML to text and return the text
        text = canlii_html_to_txt(file_path)
#       write_text(text, file_path)
        return text

    elif file_path.endswith(".txt"):
        # Return txt files as a string
        with open(file_path, "r", encoding="utf-8") as file:
            text = file.read()
        return text

    else:
        print("[bold red]File type not supported.[/bold red]")
        sys.exit()


def extract_citations(text: str):
    """
    Extracts citations from a legal text, if any, and exports the results as a
    string.

    This function doesn't look like it'll work. It's not currently being used
    in the Django app.
    """
    citations = retrieve_citations(text)

    # Add citations to a list if they contain "SCC"
    scc_citations = [
        citation for citation in citations[0]["citations"] if "SCC" in citation
    ]
    # Add citations to another list if they contain "CA"
    ca_citations = [
        citation for citation in citations[0]["citations"] if "CA" in citation
    ]
    unknown_citations = [
        citation for citation in citations[0]["citations"] if "CanLII" in citation
    ]
    other_citations = [
        citation
        for citation in citations[0]["citations"]
        if "SCC" not in citation and "CA" not in citation and "CanLII" not in citation
    ]

    citation_string_list = [
        f"\u2022 Total case citations found: {len(citations[0]['citations'])}\n",
        f"\u2022 Supreme Court of Canada citations: {len(scc_citations)}\n",
        f"\u2022 Court of Appeal citations: {len(ca_citations)}\n",
        f"\u2022 Other citations: {len(other_citations)}\n",
        f"\u2022 Unknown citations: {len(unknown_citations)}\n"
        ]

    citation_string = "".join(citation_string_list)

    return citations, citation_string

# GPT-3.5/4 functions

# Tests on smaller cases using manual input and hybrid models are yielding
# comparable results to GPT-4 alone at 1/5th the cost. Trying a new test with
# dynamically adjusted messaging.

# Progressively removing information and labelling previous responses turned
# out well. I was able to reduce costs from $0.22 to $0.05 per report.


def gpt_token_counter(text: str) -> int:
    """
    Counts the number of tokens in a string. This is used to calculate the
    number of tokens that will be charged to the user's account.
    """
    tokenizer = AutoTokenizer.from_pretrained("gpt2")

    # Count the number of tokens in a sentence
    encoding = tokenizer.encode(text)
    num_tokens = len(encoding)

    return num_tokens

def gpt_chat_completion(parameters: dict) -> dict:
    """
    This function uses a GPT chat completion model to complete a prompt. This
    is the standard API call used in the MVP.
    """
    response = openai.ChatCompletion.create(
        model=parameters["model"],
        messages=parameters["messages"],
        temperature=parameters["temperature"],
        max_tokens=parameters["max_tokens"],
        top_p=parameters["top_p"],
        frequency_penalty=parameters["frequency_penalty"],
        presence_penalty=parameters["presence_penalty"],
    )

    return response


def gpt_hybrid_analysis_manual(sorted_text: dict, api_key: str, auto: bool = False) -> dict:
    """
    Although GPT-4 is far more capable than GPT-3.5 at handling larger strings,
    it currently can be prohibitively expensive. This function uses GPT-3.5 to
    analyze the text and GPT-4 to summarize the text.

    Future implementations should track the number of tokens used so that the
    model can be more finely tuned in the future. For example, inexpensive API
    calls dealing with important info should be sent to GPT-4 rather than 3.5.
    """
    openai.api_key = api_key

    print("\n[underline #FFA500]GPT-3.5/4 hybrid[/underline \
          #FFA500].\n")
    # Default parameters for GPT-3.5
    parameters = {
        "model": "gpt-3.5-turbo",
        "messages": [],
        "temperature": 0.4,
        "max_tokens": 750,
        "top_p": 1,
        "frequency_penalty": 0.0,
        "presence_penalty": 0.0,
    }

    # Change this logic to account for none opinion types
    if sorted_text["opinion_type"] == "court's":
        case_type = "first instance"
    elif sorted_text["opinion_type"] == "None detected":
        case_type = "unknown"
    else:
        case_type = "appeal"

    opinion_type = sorted_text["opinion_type"]
    facts = sorted_text["facts"]
    issues = sorted_text["issues"]
    rules = sorted_text["rules"]
    analysis = sorted_text["analysis"]
    conclusion = sorted_text["conclusion"]
    system_prompt = "You are an assistant helping summarize Canadian criminal \
        legal cases into a FIRAC case brief. FIRAC stands for facts, issues, \
        rules, analysis, and conclusion.\nFacts include everything before the \
        court heard the case it was reporting. For appeal cases, this will \
        usually include procedural history. Facts should be one or a few more \
        paragraphs.\nIssues are the questions that the parties are asking the \
        court to answer. Issues should be listed as brief questions to be \
        answered in an ordered list.\nRules are the legal rules and procedures\
         the court must apply to answer the questions.\nAnalysis refers to the\
         court's reasons for how it answers the questions raised in the issues\
         section. Analysis can include justification for the rules used and \
        how they should be applied to the facts in the case. Analysis should \
        address each distinct issue in one or more paragraphs\nThe conclusion \
        is a brief summary of what happened. In trials, it will be whether the\
         defendant was acquitted or convicted. In appeals, it will be whether \
        the appeal was allowed or dismissed.\nSome cases may have multiple \
        opnions. One common example is an appeal, which may have majority, \
        dissenting, and concurring opinions. Where there are multiple \
        opinions, the FIRAC analysis should be done for each of them.\nThe \
        entire brief should be between 500 - 1500 words per opinion but may be\
         somewhat more or less for larger and smaller cases."
    # Adjust the system prompt based on whether the text was sorted through NLP
    # or manually.
    if auto:
        system_prompt += "\nThis text was sorted by a spaCy model that is \
            still being developed. You should assume that the text is \
            generally sorted correctly, but not always. Some sections may be \
            incomplete or inaccurate."
    else:
        system_prompt += "\nThe following text was sorted by a human and you \
            should assume it's complete and accurate."

    # Hybrid prompts
    fact_prompt = f"These are the facts in the case: {facts}\nPlease summarize\
          the facts in this case."
    if case_type == "appeal":
        fact_prompt += (
            "Because this is an appeal, please also summarize the procedural \
                history."
        )
    if case_type == "unknown":
        fact_prompt += (
            "Because the type of case is unknown, please also investigate \
                whether this is an appeal or a first instance case. If it is \
                an appeal, please also summarize the procedural history."
        )
    issue_prompt = f"These are the issues the {opinion_type} found in the \
        case:\n{issues}\nList the issues the {opinion_type} found in this \
        case in an ordered list. Phrase the issues as questions to be \
        answered."
    analysis_prompt = f"This is the analysis the {opinion_type} conducted in \
        the case:\n{analysis}\nHow did the {opinion_type} answer the issues in\
         the case? Please use the issues as headings and provide one or more \
        brief paragraphs as answers."
    rules_prompt = f"These are legal rules the {opinion_type} applied in this\
         case:\n{rules}\nOther rules may be contained in the above analysis. \
        What legal rules did the  {opinion_type} apply in this case? Please \
        list the rules as brief sentences in an ordered list."
    conclusion_prompt = f"This is the conclusion the {opinion_type} reached in\
         this case:\n{conclusion}\nOther conclusive statements may be in the\
         analysis, or inferred from the issues. What was the conclusion of the\
         {opinion_type} in this case? Answer in one brief sentence."

    # Hybrid analysis workflow

    # 1. {system_prompt} is sent to GPT-3.5
    # 2. {fact_prompt} is sent to GPT-3.5
    # 3. GPT-3.5 responds with a summary of the facts {fact_summary}

    print("Setting system prompt and summarizing facts: ", end="")
    parameters["messages"] = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": fact_prompt},
    ]

    response = gpt_chat_completion(parameters)
    fact_summary = response["choices"][0]["message"]["content"]
    print("[bold green]Done[/bold green].")

    # 4. The {fact_summary} and {issue_prompt} are sent to GPT-3.5
    # 5. GPT-3.5 responds with a summary of the issues {issue_summary}
    #    * Consider using GPT-4 for the issues, given how important they are

    print("Summarizing issues: ", end="")
    parameters["messages"] = [
        {"role": "assistant", "content": fact_summary},
        {"role": "user", "content": issue_prompt},
    ]
    response = gpt_chat_completion(parameters)
    issue_summary = response["choices"][0]["message"]["content"]
    print("[bold green]Done[/bold green].")

    # 6. {fact_summary}, {issue_summary}, and analysis_prompt are sent to
    #        GPT-3.5
    # 7. GPT-3.5 responds with a summary of the analysis {analysis_summary}
    print("Summarizing analysis: ", end="")
    parameters["messages"] = [
        {"role": "assistant", "content": fact_summary},
        {"role": "assistant", "content": issue_summary},
        {"role": "user", "content": analysis_prompt},
    ]

    response = gpt_chat_completion(parameters)
    analysis_summary = response["choices"][0]["message"]["content"]
    print("[bold green]Done[/bold green].")

    # 8. {issue_summary}, {analysis_summary}, and {rules_prompt} are sent to
    #        GPT-4
    # 9. GPT-4 responds with a summary of the rules {rules_summary}
    print("Inferring rules: ", end="")
    parameters["messages"] = [
        {"role": "assistant", "content": issue_summary},
        {"role": "assistant", "content": analysis_summary},
        {"role": "user", "content": rules_prompt},
    ]

    parameters["model"] = "gpt-4"
    response = gpt_chat_completion(parameters)
    rules_summary = response["choices"][0]["message"]["content"]
    print("[bold green]Done[/bold green].")

    print("Concluding: ", end="")
    # 10. {issue_summary}, {analysis_summary}, {rules_summary}, and
    #         {conclusion_prompt} are sent to GPT-3.5
    # 11. GPT-3.5 responds with a summary of the conclusion
    #         {conclusion_summary}
    parameters["messages"] = [
        {"role": "assistant", "content": issue_summary},
        {"role": "assistant", "content": analysis_summary},
        {"role": "assistant", "content": rules_summary},
        {"role": "user", "content": conclusion_prompt},
    ]
    parameters["model"] = "gpt-3.5-turbo"
    response = gpt_chat_completion(parameters)
    conclusion_summary = response["choices"][0]["message"]["content"]
    print("[bold green]Done[/bold green].")

    final_summary = {
        "facts": fact_summary,
        "issues": issue_summary,
        "rules": rules_summary,
        "analysis": analysis_summary,
        "conclusion": conclusion_summary,
    }

    for key, value in final_summary.items():
        print(f"\n<h1>{key.title()}</h1>\n{value}")

    return final_summary

# InMemoryUploadedFile to JSON
def process_json_file(file: InMemoryUploadedFile) -> dict:
    """
    Reads a JSON file and returns its content as a dictionary.
    """
    content = file.read().decode('utf-8')
    data = json.loads(content)

    return data

# HTML to TXT functions
def resolve_abbreviations(text: str) -> str:
    """
    Create a regex pattern to match the abbreviations with periods at the end
    then loops through each word and remove the period if it matches an 
    abbreviation. This ostensibly resolves Issue #7.
    Future versions should also target paragraph numbers and citations.
    """
    pattern = "|".join([re.escape(abreviation) + r"\." for abreviation in abbreviations])

    text = text.split()
    processed_text = []

    for word in text:
        match = re.match(pattern, word)

        if match:
            new_word = match.group(0)[:-1]
            processed_text.append(new_word)
        else:
            processed_text.append(word)

    text = " ".join(processed_text)

    return text


# Reads an HTML file and returns the text as a string
def canlii_html_to_txt(file: InMemoryUploadedFile) -> tuple[str, list]:
    """
    Reads a CanLII HTML file and saves a text file. Although CanLII HTML isn't
    uniform, this function should work for most cases.
    """

    content = file.read().decode('utf-8')
    soup = BeautifulSoup(content, 'html.parser')
    text = soup.get_text()
    text = resolve_abbreviations(text)

    return text

def write_text(text: str, file_path: str):
    """
    Writes the files that the FIRAC classifying function reads. This function
    infers a file path from the file's name and saves it into the archive folder.
    """
    # Change the file extension if necessary
    if file_path.endswith(".html"):
        file_name = os.path.basename(file_path)
        file_name = os.path.splitext(file_name)[0]
        file_name += ".txt"
    else:
        file_name = os.path.basename(file_path)

    # Create the file path
    year = file_name[:4]
    court = ''.join(filter(str.isalpha, file_name[4:-3]))

    # Construct the archive directory path based on the year and court/jurisdiction
    archive_dir = os.path.join(os.getcwd(), 'archive', year, court)
    if not os.path.exists(archive_dir):
        os.makedirs(archive_dir)

    # Construct the new file path and move the file to the archive directory
    new_file_path = os.path.join(archive_dir, file_name)
    os.rename(file_path, new_file_path)
    print(file_path, new_file_path)
    # Return the new file path for future use

    with open(new_file_path, "w", encoding="utf-8") as file:
        file.write(text)
    print(f"Wrote {new_file_path}")


# Summarization functions
def preprocess_text_for_gpt(text: str) -> str:
    """
    Removes line breaks and other extraneous characters. Other character combos
    like bracketed paragraph numbers turn out to be very expensive for GPT-3.5
    without providing much value, and are therefore removed.
    """
    # Resolve abbreviations
    text = resolve_abbreviations(text)

    # Remove bracketed paragraph numbers and other bracketed numbers, like SCR
    # page citations
    text = re.sub(r"\[\d{1,4}\]", "", text)

    # Remove SCR citations
    text = re.sub(r"\d\s*(?:S\.C\.R\.|SCR)\s*\d{1,4}", "", text)

    # Removes extraneous line breaks
    text = re.sub(r"\n+", " ", text)

    # Find spaces larger than a single space and replace them with a single
    # space
    text = re.sub(r"\s{2,}", " ", text)
    text = text.replace('\xa0', ' ')

    # Replaces stylized quotation marks with standard single quotation marks
    # This includes double quotes, which are converted to single quotes
    # GPT-2 counts stylized quotes as two separate tokens but doesn't count
    # standard quotes as separate tokens at all. Replacing the stylized quotes
    # with standard quotes reduces the number of tokens without any impact on
    # the text's semantics.
    text = text.replace("‘", "'")
    text = text.replace("’", "'")
    text = text.replace("“", "'")
    text = text.replace("”", "'")

    text = text.replace("R. v.", "R v")
    text = text.replace("J.A.", "JA")
    text = text.replace("J.", "J")
    text = text.replace(" ,", "")
    text = text.replace(" .", ".")

    return text


def extraction_text_summarizer(
        text: str,
        percentage: float = 0.2,
        min_length: int = 500,
        max_length: int = 1500,
) -> str:
    """
    Summarizes text using extractive summarization methods. First, the function
    tokenizes the text and then calculates the frequency of each word. Then, it
    calculates the weighted frequency of each word. Finally, it calculates the
    weighted frequency of each sentence and returns the top sentences based on
    the percentage of the original text.

    This function is designed to minimize the amount of text that needs to be
    sent to the GPT-3 functions for further summarization and analysis. It is
    not designed to be a perfect summarization of the text.
    """
    # Load the abbreviations file
    with open(ABBREVIATIONS, "r", encoding="utf-8") as file:
        abbreviations = json.load(file)

    # Preprocess the text
    text = preprocess_text_for_gpt(text)

    # Tokenize the formatted text using gpt-2 to determine the call's expense
    tokenizer = AutoTokenizer.from_pretrained("gpt2")
    gpt2_tokens = tokenizer.encode(text)
    total_gpt2_tokens = len(gpt2_tokens)

    # Tokenize the formatted text using spaCy
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)
    stopwords = list(STOP_WORDS)

    # Calculates the frequency of each substantive word and generates the
    # frequency table.
    word_frequency = Counter(
        [
            token.text
            for token in doc
            if token.text.lower() not in stopwords
            and token.text not in punctuation
            and token.text not in abbreviations
        ]
    )

    # Calculates a word's weighted frequency
    word_frequency_counter = Counter(word_frequency)
    max_frequency = max(word_frequency.values())
    for word in word_frequency.keys():
        word_frequency[word] = word_frequency[word] / max_frequency

    # Removes the stop words and punctuation from the sentences
    sentence_tokens = list(doc.sents)
    sentence_scores = Counter(
        {
            sentence: sum(
                word_frequency_counter.get(word.text.lower(), 0) for word in sentence
            )
            for sentence in sentence_tokens
        }
    )

    # Calculate the number of total tokens across all sentences
    total_spacy_tokens = sum(len(sentence) for sentence in sentence_tokens)

    # The percentage should aim to get as close to the min_length as possible while
    # not exceeding the max_length. The percentage is calculated based on the
    # total number of tokens in the text.
    if total_spacy_tokens < min_length:
        percentage = 1
    elif total_spacy_tokens > max_length:
        percentage = max_length / total_spacy_tokens
    else:
        percentage = min_length / total_spacy_tokens

    # Adds the sentences to a weighted frequency list in descending order
    # If the total length of the sentences is less than the minimum length,
    # the function will return the entire text.

    weighted_sentences = nlargest(
        int(len(sentence_tokens) * percentage), sentence_scores, key=sentence_scores.get
    )

    # Creates the summary based on the weighted frequency list
    # The summary is limited to a minimum and maximum length
    summary = [word.text for word in weighted_sentences]
    return summary, total_spacy_tokens, percentage, total_gpt2_tokens

def local_text_summary(firac: dict) -> dict:
    """
    Summarizes a text locally using the local summarization function. This
    function ranks sentences based on a simple word frequency algorithm. Future
    verions will allow more sophisticated summarization methods.
    """
    summary = {}

    def process_key(key: str):
        """
        Processes the key and returns the summary.
        """
        # Remove extraneous spaces and characters
        firac[key] = preprocess_text_for_gpt(firac[key])

        # Summarize the text
        firac[key] = extraction_text_summarizer(firac[key])

        # Add the summary to the summary dictionary
        summary[key] = firac[key]

    # Each FIRAC key contains a list of sentences. Go through each list and
    # remove \n characters. Then, join the sentences into a single string.
    # If the key is not in the FIRAC dictionary, add it with a string value of
    # "None detected"

    keys = ["opinion_type", "facts", "issues", "rules", "analysis", "conclusion"]

    for key in keys:
        if key in firac:
            process_key(key)
        else:
            firac[key] = "None detected"
            process_key(key)

    return summary
