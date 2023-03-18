"""
The decision class contains the functions that parse the decision sentences 
into lists. The lists are then used to generate the decision summary.



The summarization functions are designed to minimize the amount of text that
needs to be sent to the GPT-3 functions for further summarization and analysis.
"""

import json
import spacy
import re
from collections import Counter
from spacy.lang.en.stop_words import STOP_WORDS
from spacy.lang.en import English
from string import punctuation
from heapq import nlargest


# Create a decision class that will include the extracted textual portions.


class Decision:
    def __init__(self, pfirac: dict):
        """
        This class creates a decision object that contains the extracted
        textual portions of a decision.

        The "meta" parameter should contain the following items:

            * Case citation
            * Judge or judges signing onto the decision
            * The position the decision takes with respect to the case as a whole (majority, dissent, etc.)

        Taken together, these items can be used to create a unique class identifier.

        Each of the remaining parameters should be lists of sentences. They
        should be combined into a single string before being passed to the
        summarization function.
        """

        self.meta = pfirac.get("meta", {})
        self.id = f"{self.meta.get('citation', '')} — {self.meta.get('judges', '')} — {self.meta.get('decision_type', '')}"
        self.facts = pfirac.get("facts", {})
        self.history = pfirac.get("history", {})
        self.issues = pfirac.get("issues", {})
        self.rules = pfirac.get("rules", {})
        self.analysis = pfirac.get("analysis", {})
        self.conclusion = pfirac.get("conclusion", {})

    def __str__(self):
        return self.id


def text_summarizer(
        text: str,
        percentage: float = 0.2,
        min_length: int = 500,
        max_length: int = 1500,
        abbreviations: list[str] | None = None
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


    # Tokenize the formatted text

    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)
    stopwords = list(STOP_WORDS)
    abbreviations = ["para.", "paras", "p", "pp", "Cst", "Csts", "s", "ss"]
    # Calculates the frequency of each substantive word and generates the
    # frequency table. Future versions should also exclude citations and
    # paragraph numbers.
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

    print(f"Percentage: {percentage}")
    print(f"Total tokens: {total_tokens}")

    # Adds the sentences to a weighted frequency list in descending order
    # If the total length of the sentences is less than the minimum length,
    # the function will return the entire text.

    weighted_sentences = nlargest(
        int(len(sentence_tokens) * percentage), sentence_scores, key=sentence_scores.get
    )

    # Creates the summary based on the weighted frequency list
    # The summary is limited to a minimum and maximum length
    summary = [word.text for word in weighted_sentences]

    print(summary)
    return summary

