"""
Tools to analyze case data through NL rules
"""

import json
import os
import re
import spacy

LEGAL_TESTS = "../data/legal-tests.json"


def retrieve_citations(text: str) -> list:
    """
    Calls a bare-bones NLP model to retrieve citations from text.
    """
    nlp = spacy.load("../models/span_citations_min_v1/model-best/")
    doc = nlp(text)

    citations = [
        {"type": "decisions", "citations": []},
        {"type": "legislation", "citations": [], "sections": []},
    ]

    

    for citation in citations:
        if citation["type"] == "decisions":
            citation["citations"].append(
                [
                    span.text
                    for span in doc.spans["sc"]
                    if span.label_ in ["CANLII_CITATION", "NEUTRAL_CITATION"]
                ]
            )
        elif citation["type"] == "legislation":
            citation["citations"].append(
                [
                    span.text 
                    for span in doc.spans["sc"] 
                    if span.label_ in ["LEGISLATION"]
                ]
            )
            citation["sections"].append(
                [
                    span.text 
                    for span in doc.spans["sc"] 
                    if span.label_ in ["SECTION"]
                ]
            )

    return citations


def get_legal_test(citations: list[str]) -> list[dict]:
    """
    This function takes a citation and returns the legal test for that
    citation. After other
    """
    test_list = []
    citation = citation.lower().replace(".", "")

    # Load the legal test data from JSON file
    with open(LEGAL_TESTS, "r") as file:
        legal_tests = json.load(file)

    for dictionary in legal_tests:
        if dictionary["origins"]["citation"].lower() == citation:
            test_list.append(dictionary)

    return test_list
