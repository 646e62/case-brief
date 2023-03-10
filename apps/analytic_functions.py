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

    citations = [
        {"type": "decisions", "citations": []},
        {"type": "legislation", "citations": [], "sections": []},
    ]

    # Statutes that are likely to form part of a legal test
    statutes = [
        "Charter",
        "Charter of Rights and Freedoms",
        "Canadian Charter of Rights and Freedoms",
        "Canadian Charter of Rights and Freedoms, Part I of the Constitution Act, 1982, being Schedule B to the Canada Act 1982 (UK), 1982, c 11",
        "Canadian Charter of Rights and Freedoms, Part I of the Constitution Act, 1982",
        "CDSA",
        "Controlled Drugs and Substances Act",
        "Controlled Drugs and Substances Act, SC 1996, c 19",
        "Cr. C.",
        "Cr C",
        "Criminal Code",
        "Criminal Code of Canada",
        "Criminal Code, RSC 1985, c C-46",]

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
    nlp = spacy.load("./models/ner_sections_v1/model-last/")
    doc = nlp(text)

    for ent in doc.ents:
        # if ent.label_ == "STATUTE":
        #   citations[1]["citations"].append(ent.text)
        if ent.label_ == "SECTION":
            citations[1]["sections"].append(ent.text)
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
