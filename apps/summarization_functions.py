"""
The decision class contains the functions that parse the decision sentences 
into lists. The lists are then used to generate the decision summary.



The summarization functions are designed to minimize the amount of text that
needs to be sent to the GPT-3 functions for further summarization and analysis.
"""

import json
import re

from collections import Counter
from string import punctuation
from heapq import nlargest
from transformers import AutoTokenizer
from rich import print

import spacy
import typer

from prettytable import PrettyTable
from spacy.lang.en.stop_words import STOP_WORDS
from apps.html_to_txt import resolve_abbreviations

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
    with open("./data/abbreviations.json", "r", encoding="utf-8") as file:
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
    print("\n[bold underline #FFA500]Summarization[/bold underline #FFA500]")
    print("Summarizing text: \n", end="")
    summary = {}
    table = PrettyTable()
    table.field_names = ["", "Total spaCy Tokens", "Percentage Included"]

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
        table.add_row(
            [f"{key.title()}", firac[key][1], round(firac[key][2] * 100, 2)]
        )

    # Each FIRAC key contains a list of sentences. Go through each list and
    # remove \n characters. Then, join the sentences into a single string.

    keys = ["opinion_type", "facts", "issues", "rules", "analysis", "conclusion"]

    for key in keys:
        process_key(key)

    print("[bold green]Done.[/bold green]\n")
    typer.echo(table)

    return summary
