"""
Classify reported court cases using spaCy and a custom model trained to detect
FIRAC elements. V2 and onward are trained on the text from the cases the 
Supreme Court of Canada cases decided in 2022. Model development is ongoing.
"""

import spacy
from rich import print

def majority_minority(text: str) -> list:
    """
    Identifies the number of different opinions in a case, the type of opinion,
    the judge(s) who wrote the opinion, and the text attributable to the 
    faction. Returns a list of dictionaries with the citation, the name of the 
    judge(s) who wrote the decision, and the type of decision, as well as the
    decision text.

    The four types of decisions are:
    - Curium: The whole court agrees on the outcome of the case.
    - Majority: The majority of the court agrees with the decision.
    - Dissent: The minority of the court disagrees with the decision.
    - Concurring: The concurrance agrees with the decision but for different
      reasons.

    Depending on how well I'm able to clean the data, I may be able to use 
    rule-based matching to identify the judge names. If not, I'll have to 
    incorporate a named entity recognition model.
    """

    pass


def classify_firac(text: str) -> dict:
    """
    This function splits the document into sentences and then classifies each
    sentence with the closest corresponding FIRAC element. The function returns
    a dictionary with the FIRAC elements as keys and the sentences in a list as
    values.
    """
    nlp = spacy.load("./models/textcat_firac_v3/model-last/")
    nlp.add_pipe("sentencizer")
    doc = nlp(text)
    firac = {}

    for sentence in doc.sents:
        categories = nlp(sentence.text).cats
        max_key = max(categories, key=lambda k: categories[k])
        max_key = max_key.lower()

        # Append the sentence to the FIRAC element that achieved the highest
        # score, and the value of the score to the sentence_values list. Append
        # a blank list to the FIRAC element if it doesn't exist.
        firac.setdefault(max_key, []).append(sentence.text)
        

    return firac
