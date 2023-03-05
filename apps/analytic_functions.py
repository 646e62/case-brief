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
    print("Retrieving citations: ", end="")
    nlp = spacy.load("./models/span_citations_min_v1/model-best/")
    doc = nlp(text)

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
                    span.text 
                    for span in doc.spans["sc"] 
                    if span.label_ in ["LEGISLATION"]
                ]
            citation["sections"] = [
                    span.text 
                    for span in doc.spans["sc"] 
                    if span.label_ in ["SECTION"]
                ]
    print("Done")

    return citations


def compile_citations(text: str) -> list[dict]:
    """
    Breaks a long string into paragraphs, and adds those paragraphs to a list.
    The function then retrieves the citations, if any, from each paragraph and
    returns a list of dictionaries for each paragraph with a citation and a set 
    containing each citation item located.

    The dictionaries may be useful for further analysis on the legislation/
    statute spans (which label both short forms and full citations as 
    "LEGISLATION") and their corresponding sections. The case citations may be
    used to match a case citation to a legal test.
    """

    nlp = spacy.load("en_core_web_md")
    


def get_legal_test(citations: list[str], legal_tests: dict) -> list[dict]:
    """
    This function takes a citation and returns the legal test for that
    citation. After other
    """

    test_list = []
    citation = citation.lower().replace(".", "")

    for dictionary in legal_tests:
        if dictionary["origins"]["citation"].lower() == citation:
            test_list.append(dictionary)

    return test_list

