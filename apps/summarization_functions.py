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
    text: str, percentage: float, abbreviations: list[str] | None = None
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

    # Create a regex pattern to match the abbreviations with periods at the end
    # then loops through each word and remove the period if it matches an
    # abbreviation. This ostensibly resolves Issue #7.
    # Future versions should also target paragraph numbers and citations.
    pattern = "|".join(
        [re.escape(abreviation) + r"\." for abreviation in abbreviations]
    )

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

    # Tokenize the formatted text

    nlp = spacy.load("en_core_web_md")
    doc = nlp(text)
    stopwords = list(STOP_WORDS)

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
    sentence_tokens = [sentence for sentence in doc.sents]
    sentence_scores = Counter(
        {
            sentence: sum(
                word_frequency_counter.get(word.text.lower(), 0) for word in sentence
            )
            for sentence in sentence_tokens
        }
    )

    len_tokens = int(len(sentence_tokens) * percentage)

    # Returns the top sentences based on the percentage of the original text.
    summary = [sentence for sentence, score in sentence_scores.most_common(len_tokens)]
    final_summary = [word.text for word in summary]
    summary = " ".join(final_summary)

    return summary


# Abbreviations
abbreviations = ["para.", "paras.", "p.", "pp.", "Cst", "Csts."]

