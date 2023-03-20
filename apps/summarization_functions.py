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

import spacy
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

    # Tokenize the formatted text
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
    total_tokens = sum(len(sentence) for sentence in sentence_tokens)

    # The percentage should aim to get as close to the min_length as possible while
    # not exceeding the max_length. The percentage is calculated based on the
    # total number of tokens in the text.
    if total_tokens < min_length:
        percentage = 1
    elif total_tokens > max_length:
        percentage = max_length / total_tokens
    else:
        percentage = min_length / total_tokens

    # Adds the sentences to a weighted frequency list in descending order
    # If the total length of the sentences is less than the minimum length,
    # the function will return the entire text.

    weighted_sentences = nlargest(
        int(len(sentence_tokens) * percentage), sentence_scores, key=sentence_scores.get
    )

    # Creates the summary based on the weighted frequency list
    # The summary is limited to a minimum and maximum length
    summary = [word.text for word in weighted_sentences]
    return summary, percentage, total_tokens
