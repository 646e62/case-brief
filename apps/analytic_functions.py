"""
Tools to analyze case data through NL rules
"""

import json
import os
import re
import spacy

LEGAL_TESTS = "./data/legal-tests.json"
with open(LEGAL_TESTS, "r") as file:
    legal_tests = json.load(file)


def retrieve_citations(text: str) -> dict:
    """
    Calls a bare-bones NLP model to retrieve citations from text.
    """
    nlp = spacy.load("./models/span_citations_min_v1/model-best/")
    doc = nlp(text)

    # Remove \xa0 from the tokens

    citations = [
        {"type": "decisions", "citations": []},
        {"type": "legislation", "citations": [], "sections": []},
    ]

    # Sorts the citations by their labels and returns a corresponding dict
    for citation in citations:
        if citation["type"] == "decisions":
            citation["citations"] = [
                span.text
                for span in doc.spans["sc"]
                if span.label_ in ["CANLII_CITATION", "NEUTRAL_CITATION"]
            ]
        elif citation["type"] == "legislation":
            citation["citations"] = [
                span.text for span in doc.spans["sc"] if span.label_ in ["LEGISLATION"]
            ]
            citation["sections"] = [
                span.text for span in doc.spans["sc"] if span.label_ in ["SECTION"]
            ]

    return citations


def get_legal_test(citations: list[str]) -> list[dict]:
    """
    This function takes a citation and returns the legal test for that
    citation. After other
    """
    test_list = [
        dictionary
        for dictionary in legal_tests
        for citation in citations
        if citation in dictionary["origins"]["citation"]
    ]

    return test_list
