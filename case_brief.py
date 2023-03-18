#!/usr/bin/env python3

"""
Runs the case brief program from the command line.
"""

import os.path
import sys
import typer

# from typing import List, Tuple

from apps.analytic_functions import retrieve_citations, get_legal_test
from apps.classification_functions import classify_firac
from apps.html_to_txt import canlii_html_to_txt
from apps.summarization_functions import text_summarizer


# Argument functions


def text_argument(file: str) -> str:
    """
    Extracts text from an HTML file, saves a local copy (unless one already
    exists), and exits.
    """
    text = extract_text(file)
    return text


def local_argument(file: str, verbose: False) -> tuple:
    """
    Runs local-only functions and returns the results.
    """
    text = extract_text(file)
    firac = classify_firac(text)
    print("\nCitation extraction")
    print("===================")
    citations = extract_citations(text)
    print("\nSummarization")
    print("=============")
    summary = summarize_text_local(firac)
    print("\nAnalysis")
    print("========")
    analyze_text_local(text, citations)

    if verbose is True:
        return text, firac, summary, citations
    return summary, citations


def citation_argument(file):
    """
    Returns a list of citations from a text file.
    """
    text = extract_text(file)
    return extract_citations(text)


def default(file: str):
    """
    Runs the default case brief program.
    """
    return local_argument(file, verbose=False)


# Supportive functions


def extract_text(file_path: str):
    """
    Extracts text from an HTML file.
    """
    print("\nText extraction")
    print("===============")
    print("Verifying file path: ", end="")
    if not os.path.exists(file_path):
        print("File not found.")
        sys.exit()
    else:
        print("Done.")

    # Write a local copy of the text file
    file_name = os.path.basename(file_path)
    file_name = os.path.splitext(file_name)[0]
    file_name += ".txt"
    new_file_path = f"./data/training_data/{file_name}"

    # Convert the HTML file to text
    text = canlii_html_to_txt(file_path)

    # Check to see if a file copy exists. If not, create one.
    if not os.path.exists(new_file_path):
        with open(new_file_path, "w", encoding="utf-8") as file:
            file.write(text)
        print(f"Wrote {file_path}")
    else:
        print("File already exists.")

    return text


def summarize_text_local(
        firac: dict
) -> dict:
    """
    Summarizes a text locally using the local summarization function. This
    function ranks sentences based on a simple word frequency algorithm. Future
    verions will allow more sophisticated summarization methods.
    """
    print("Summarizing text: ", end="")
    print("Done")
    summary = {}

    # Each FIRAC key contains a list of sentences. Go through each list and
    # remove \n characters. Then, join the sentences into a single string.
    for key in firac:
        firac[key] = " ".join([sentence.replace("\n", " ") for sentence in firac[key]])
        # Summarize the text
        firac[key] = text_summarizer(firac[key])
        # Add the summary to the summary dictionary
        summary[key] = firac[key]

    return summary

def extract_citations(text: str):
    """
    Extracts citations from a legal text, if any, and exports the results as a
    dictionary.
    """
    print("Retrieving citations: ", end="")
    citations = retrieve_citations(text)
    print("Done")

    # Add citations to a list if they contain "SCC"
    scc_citations = [citation for citation in citations[0]["citations"] if "SCC" in citation]
    # Add citations to another list if they contain "CA"
    ca_citations = [citation for citation in citations[0]["citations"] if "CA" in citation]
    unknown_citations = [citation for citation in citations[0]["citations"] if "CanLII" in citation]
    other_citations = [citation for citation in citations[0]["citations"] if "SCC" not in citation and "CA" not in citation and "CanLII" not in citation]

    print(f"Case citations found: {len(citations[0]['citations'])}")
    print(f"SCC citations:\n{scc_citations}")
    print(f"CA citations:\n{ca_citations}")
    print(f"Unknown citations:\n{unknown_citations}")
    print(f"Other citations:\n{other_citations}")

    return citations


def analyze_text_local(text: str, citations: dict):
    """
    Analyzes a text locally using the local analysis function. This function
    returns a dictionary of the legal tests used in the text. If the function
    finds a citation matching one linked to a legal test, it will return the
    legal test.
    """
    print("Analyzing text: ", end="")
    legal_tests = get_legal_test(citations)
    print("Done")

    if legal_tests:
        print("Tests found:\n")
        for test in legal_tests:
            print(test)
    else:
        print("No tests found.")


if __name__ == "__main__":
    typer.run(default)

