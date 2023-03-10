#!/usr/bin/env python3

"""
Runs the case brief program from the command line.
"""

import argparse
import os.path
import sys


# from typing import List, Tuple

from apps.analytic_functions import retrieve_citations, get_legal_test
from apps.classification_functions import classify_firac
from apps.html_to_txt import canlii_html_to_txt
from apps.summarization_functions import text_summarizer


# Argument functions

def text_argument(file: str) -> str:
    text = extract_text(file)
    return text


def local_argument(file: str, verbose: False) -> tuple:
    text = extract_text(file)
    firac = classify_firac(text)
    citations = extract_citations(text)
    summary = summarize_text_local(text)
    analysis = analyze_text(text)

    if verbose == True:
        return text, firac, summary, analysis, citations
    else:
        return summary, analysis, citations


def citation_argument():
    text = extract_text(file)
    return extract_citations(text)


def default(file):
    return local_argument(file)


# Supportive functions

def extract_text(file: str):
    
    print("Verifying file path: ", end = "")
    if not os.path.exists(args.file_path):
        print("File not found.")
        sys.exit()
    else:
        print("Done.\n")
   
    # Write a local copy of the text file
    file_name = os.path.basename(args.file_path)
    file_name = os.path.splitext(file_name)[0]
    file_name += ".txt"
    file_path = f"./data/training_data/{file_name}"

    # Convert the HTML file to text
    text = canlii_html_to_txt(args.file_path)

    # Check to see if a file copy exists. If not, create one.
    if not os.path.exists(file_path):
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(text)
        print(f"Wrote {file_path}")
    else:
        print("File already exists.")


def summarize_text_local(file: str, percentage: float = 0.2) -> tuple:
    
    for key in firac:
        section_text = " ".join(firac[key])
        section_text = text_summarizer(section_text, percentage)
      
    return key, section_text


def extract_citations(text: str):
    """
    Extracts citations from a legal text, if any, and exports the results as a
    dictionary.
    """
    print("Retrieving citations: ", end="")
    citations = retrieve_citations(text)
    print("Done")

    decisions = []
    legislation = []
    sections = []
 
    # Isolate the citations into a set
    # If the underlying list is empty, a "None" string is added to the set
    decisions = set(
        [
            decision
            for citation in citations
            if citation["type"] == "decisions"
            for decision in citation["citations"]
        ]
    )

    legislation = set(
        [
            statute
            for citation in citations
            if citation["type"] == "legislation"
            for statute in citation["citations"]
        ]
    )

    sections = set(
        [
            section
            for citation in citations
            if citation["type"] == "legislation"
            for section in citation["sections"]
        ]
    )
    
    return decision_list

def analyze_text_local(text: str):
    # Check to see if any of the citations are in the legal tests
    if get_legal_test(decision_list):

        print("\nLegal test(s) found:")
        for test in get_legal_test(decision_list):
            print("* " + test["short_form"].title())
    else:
        print("\nNo legal tests found.")


# Arguments
parser = argparse.ArgumentParser()
parser.add_argument(
    "file_path",
    nargs="?",
    help="The path to the HTML file to be processed.",
    type=str,
)
parser.add_argument(
    "--text",
    nargs="?",
    help="Converts the HTML file to text and exits."
)
parser.add_argument(
    "--local",
    nargs="?",
    help="Analyzes a file without calling the GPT-3.5 API."
)
parser.add_argument("--citation", 
    nargs="?", 
    help="Extracts citations and exits."
)
args = parser.parse_args()

