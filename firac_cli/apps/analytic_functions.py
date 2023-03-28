"""
Tools to analyze case data through NL rules
"""

import json
import re
import spacy

from rich import print

LEGAL_TESTS = "./data/legal-tests.json"
with open(LEGAL_TESTS, "r", encoding="utf-8") as file:
    legal_tests = json.load(file)

def local_text_analysis(citations: list):
    """
    Analyzes a text locally using the local analysis function. This function
    returns a dictionary of the legal tests used in the text. If the function
    finds a citation matching one linked to a legal test, it will return the
    legal test.
    """
    print("\n[underline #FFA500]Analysis[/underline #FFA500]")
    print("Analyzing text: ", end="")
    legal_tests_identified = get_legal_test(citations)
    print("[green]Done.[/green]")

    text_string = ""

    if legal_tests_identified:
        print("\nTests found:")
        text_string += "\nTests found:\n"

        for test in legal_tests_identified:
            print(f" \u2022 {test['short_form']}")
            text_string += f" \u2022 {test['short_form']}\n"
    else:
        print("\nTests found: [red]None[/red]")
        text_string += "\nTests found: None\n"

    return text_string

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
    nlp = spacy.load("./models/ner_sections_v1/model-last/")
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


def get_legal_test(citations: dict) -> list[dict]:
    """
    This function takes a list of citations and checks them against a list of
    legal tests. If a citation matches a legal test, the function returns the
    legal test.
    """
    case_citations = citations[0]["citations"]

    for test in legal_tests:
        if test["origins"]["citation"] in case_citations:
            return [test]


def detect_legal_tests(citations: dict):
    """
    Scans a list of citations to determine if any of them correspond to a legal
    test.
    """
    print("\n[underline #FFA500]Analysis[/underline #FFA500]")
    print("Analyzing text: ", end="")
    legal_tests_detected = get_legal_test(citations)
    print("[green]Done.[/green]")
    test_list = []

    if legal_tests_detected:
        print("\nTests found:")
        for test in legal_tests_detected:
            print(f" \u2022 {test['short_form']}")
            test_list.append(test["short_form"])
    else:
        print("\nTests found: [red]None[/red]")

    return test_list
