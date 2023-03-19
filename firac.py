#!/usr/bin/env python3

"""
FIRAC is a command-line tool that analyzes legal texts and returns a summary of
the text, a list of citations, and a classification of the text based on the
FIRAC model. FIRAC is a work in progress and is not yet ready for production.
"""

import os.path
import sys

# import json

# from typing import List, Tuple

from typing import Optional
from rich import print
from prettytable import PrettyTable

import typer

from apps.analytic_functions import retrieve_citations, get_legal_test
from apps.classification_functions import classify_firac
from apps.html_to_txt import canlii_html_to_txt
from apps.summarization_functions import text_summarizer
from apps.gpt_functions import gpt_analysis


# Commands
app = typer.Typer()


@app.command()
def extract_text_only(file: str) -> str:
    """
    Extracts text from an HTML file, saves a local copy (unless one already
    exists), and exits.
    """
    text = extract_text(file)
    return text


@app.command()
def local(file: Optional[str] = None) -> tuple:
    """
    Runs local-only functions and returns the results.
    """
    os.system("clear")
    print("[bold #FFA500]FIRAC[/bold #FFA500]\n")

    if file:
        text = extract_text(file)
    else:
        text = extract_text(input("File path: "))

    firac = classify_firac(text)
    citations = extract_citations(text)
    summary = summarize_text_local(firac)
    analysis = analyze_text_local(text, citations)

    return text, firac, citations, summary, analysis


@app.command()
def extract_citations_only(file):
    """
    Returns a list of citations from a text file.
    """
    text = extract_text(file)
    return extract_citations(text)


@app.command()
def gpt_3():
    """
    Analyzes text using GPT-3/.5. This function is not yet implemented.
    """
    pass


@app.command()
def gpt_4():
    """
    Analyzes text using GPT-4. This function is not yet implemented.
    """
    pass


# Supportive functions
# 1. Text extraction functions
def extract_text(file_path: str):
    """
    Extracts text from an HTML file.
    """
    print("[underline #FFA500]Text extraction[/underline #FFA500]")
    print("Verifying file path: ", end="")
    if not os.path.exists(file_path):
        print("File not found.")
        sys.exit()
    else:
        print("[green]Done.[/green]")

    if file_path.endswith(".html"):
        # Convert the HTML file to text
        text = canlii_html_to_txt(file_path)

        # Write to file
        write_text(text, file_path)
        return text

    elif file_path.endswith(".txt"):
        with open(file_path, "r", encoding="utf-8") as file:
            text = file.read()
        return text

    else:
        print("[bold red]File type not supported.[/bold red]")
        sys.exit()


def write_text(text: str, file_path: str):
    """
    Writes the files that the FIRAC classifying function reads. This function
    infers a file path from the file's name and saves it into the archive folder.
    """
    # Change the file extension if necessary
    if file_path.endswith(".html"):
        file_name = os.path.basename(file_path)
        file_name = os.path.splitext(file_name)[0]
        file_name += ".txt"

    # Create the file path
    print(file_name)

    # Check to see if a file copy exists. If not, create one.
    if not os.path.exists(file_path):
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(text)
        print(f"Wrote {file_path}")
    else:
        print("[bold red]File already exists.[/bold red] Skipping file writing.")


# 2. Local summarization functions
# 2.1. Extractive summarization
def summarize_text_local(firac: dict) -> dict:
    """
    Summarizes a text locally using the local summarization function. This
    function ranks sentences based on a simple word frequency algorithm. Future
    verions will allow more sophisticated summarization methods.
    """
    print("\n[bold underline #FFA500]Summarization[/bold underline #FFA500]")
    print("Summarizing text: ", end="")
    summary = {}
    table = PrettyTable()
    table.field_names = ["", "Percentage Included", "Total Tokens"]

    # Each FIRAC key contains a list of sentences. Go through each list and
    # remove \n characters. Then, join the sentences into a single string.
    for key in firac:
        if key != "heading":
            firac[key] = " ".join(
                [sentence.replace("\n", " ") for sentence in firac[key]]
            )
            # Summarize the text
            firac[key] = text_summarizer(firac[key])
            # Add the summary to the summary dictionary
            summary[key] = firac[key]
            table.add_row(
                [f"{key.title()}", round(firac[key][1] * 100, 2), firac[key][2]]
            )
        else:
            pass
    print("[green]Done.[/green]\n")

    typer.echo(table)
    return summary


# 2.2. Citation extraction
def extract_citations(text: str):
    """
    Extracts citations from a legal text, if any, and exports the results as a
    dictionary.
    """
    print("\n[underline #FFA500]Citation extraction[/underline #FFA500]")
    print("Retrieving citations: ", end="")
    citations = retrieve_citations(text)
    print("[green]Done.[/green]\n")

    # Add citations to a list if they contain "SCC"
    scc_citations = [
        citation for citation in citations[0]["citations"] if "SCC" in citation
    ]
    # Add citations to another list if they contain "CA"
    ca_citations = [
        citation for citation in citations[0]["citations"] if "CA" in citation
    ]
    unknown_citations = [
        citation for citation in citations[0]["citations"] if "CanLII" in citation
    ]
    other_citations = [
        citation
        for citation in citations[0]["citations"]
        if "SCC" not in citation and "CA" not in citation and "CanLII" not in citation
    ]

    print(f"\u2022 Total case citations found: {len(citations[0]['citations'])}")
    print(f"\u2022 Supreme Court of Canada citations: {len(scc_citations)}")
    print(f"\u2022 Court of Appeal citations: {len(ca_citations)}")
    print(f"\u2022 Provincial and superior court decisions: {len(other_citations)}")
    print(f"\u2022 Unknown citations: {len(unknown_citations)}")

    return citations


# 2.3. Legal test analysis
def analyze_text_local(text: str, citations: dict):
    """
    Analyzes a text locally using the local analysis function. This function
    returns a dictionary of the legal tests used in the text. If the function
    finds a citation matching one linked to a legal test, it will return the
    legal test.
    """
    print("\n[underline #FFA500]Analysis[/underline #FFA500]")
    print("Analyzing text: ", end="")
    legal_tests = get_legal_test(citations)
    print("[green]Done.[/green]")

    if legal_tests:
        print("\nTests found:")
        for test in legal_tests:
            print(f" \u2022 {test['short_form']}")
    else:
        print("\nTests found: [red]None[/red]")

    return legal_tests


# 3. Remote summarization functions
# 3.1. GPT



if __name__ == "__main__":
    app()
