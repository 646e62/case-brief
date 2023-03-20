#!/usr/bin/env python3

"""
FIRAC is a command-line tool that analyzes legal texts and returns a summary of
the text, a list of citations, and a classification of the text based on the
FIRAC model. FIRAC is a work in progress and is not yet ready for production.
"""

import os.path
import sys
import json

# from typing import List, Tuple

from typing import Optional
from rich import print
from prettytable import PrettyTable

import typer

from apps.analytic_functions import retrieve_citations, get_legal_test
from apps.classification_functions import classify_firac
from apps.html_to_txt import canlii_html_to_txt, write_text
from apps.summarization_functions import extraction_text_summarizer, preprocess_text_for_gpt
from apps.gpt_functions import gpt_hybrid_analysis_manual


# Commands
app = typer.Typer()

@app.command()
def text_extractor(file: str) -> str:
    """
    Extracts text from an HTML file, saves a local copy (unless one already
    exists), and exits.
    """
    os.system("clear")
    print("\n[underline #FFA500]Text extractor[/underline #FFA500]\n")
    text = extract_text(file)
    return text


@app.command()
def citation_extractor(file: str) -> dict:
    """
    Returns a list of citations from a text file.
    """
    os.system("clear")
    print("\n[underline #FFA500]Citation extractor[/underline #FFA500]\n")
    text = extract_text(file)
    return extract_citations(text)


@app.command()
def legal_test_detector(file: str) -> str:
    """
    Returns a list of legal tests from a text file.
    """
    os.system("clear")
    print("\n[underline #FFA500]Legal test detector[/underline #FFA500]\n")
    citations = citation_extractor(file)
    legal_tests = detect_legal_tests(citations)

    return legal_tests


@app.command()
def preprocess_text(file_path: str, write: bool = False) -> str:
    """
    Preprocesses text for GPT-3. Enabling the write flag will overwrite the
    original file with the pre-process text.
    """
    os.system("clear")
    print("\n[underline #FFA500]Preprocess text[/underline #FFA500]\n")

    # Verify that the file is a text file. If not, exit.
    if not file_path.endswith(".txt"):
        print("[bold red]File type not supported.[/bold red]")
        sys.exit()

    verify_file_path(file_path)

    with open(file_path, "r", encoding="utf-8") as file:
        text = file.read()

    processed_text = preprocess_text_for_gpt(text)
    print("Text preprocessed.")
    if write:
        write_text(processed_text, file_path)

    return processed_text


@app.command()
# Text optional
def compile_text(text: Optional[str] = None, auto: bool = None) -> dict:
    """
    Runs local-only functions and returns the results. 
    """
    os.system("clear")
    print("[bold #FFA500]FIRAC[/bold #FFA500]\n")

    if auto:
        if text is None:
            print("[bold red]No file path provided.[/bold red]")
            sys.exit()
        else:
            print("[bold #FFA500]Automatic summarization[/bold #FFA500]\n")
            summary = firac_auto(text)
            print(summary)
            return summary

    else:
        print("[bold #FFA500]Manual summarization[/bold #FFA500]\n")
        # User input determines whether to call firac_manual() or firac_json().
        # Use an ordered list and verify input
        user_input = input("(N)ew or (E)xisting summary?\n")
        if user_input.lower() == "n":
            summary = firac_manual()
            return summary
        elif user_input.lower() == "e":
            summary = firac_json()
            return summary
        else:
            print("[bold red]Invalid input.[/bold red]")
            sys.exit()

    return summary


@app.command()
def create_firac_auto(file: str):
    text = extract_text(file)
    firac = classify_firac(text)
    citations = extract_citations(text)
    summary = local_text_summary(firac)
    analysis = local_text_analysis(citations)

    return summary, analysis


@app.command()
def create_firac_manual():
    firac = compile_text()
    # Extract the text from the various sections
    text = ""
    for key in firac:
        text += firac[key]
    citations = extract_citations(text)
    summary = local_text_summary(firac)
    analysis = local_text_analysis(citations)
    report = gpt_hybrid_analysis_manual(summary)

    return report, analysis


# Functions
# Text extraction and file verification

def verify_file_path(file_path: str):
    """
    Verifies that a file exists at the specified path.
    """
    print("Verifying file path: ", end="")
    if not os.path.exists(file_path):
        print("File not found.")
        sys.exit()
    else:
        print("[green]Done.[/green]")

def extract_text(file_path: str):
    """
    Extracts text from an HTML file.
    """
    verify_file_path(file_path)

    if file_path.endswith(".html"):
        text = canlii_html_to_txt(file_path)
        write_text(text, file_path)
        return text

    elif file_path.endswith(".txt"):
        with open(file_path, "r", encoding="utf-8") as file:
            text = file.read()
        print("[green]Text file found:[/green] returning file contents.")
        return text

    else:
        print("[bold red]File type not supported.[/bold red]")
        sys.exit()


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
    print(f"\u2022 CanLII citations (no jurisdiction/court listed): {len(unknown_citations)}")

    return citations


def detect_legal_tests(citations: dict):
    """
    Scans a list of citations to determine if any of them correspond to a legal
    test.
    """
    print("\n[underline #FFA500]Analysis[/underline #FFA500]")
    print("Analyzing text: ", end="")
    legal_tests = get_legal_test(citations)
    print("[green]Done.[/green]")
    test_list = []

    if legal_tests:
        print("\nTests found:")
        for test in legal_tests:
            print(f" \u2022 {test['short_form']}")
            test_list.append(test["short_form"])
    else:
        print("\nTests found: [red]None[/red]")

    return test_list


def firac_manual():
    """
    Takes user input to create the FIRAC structure. Returns the structure as a
    dictionary and saves it as a JSON file.
    """
    firac = {}
    # Allow the user to select which FIRAC category to include text in
    # The program displays a prompt and asks the user to input [F]acts, [I]ssue,
    # [R]ule, [A]pplication, or [C]onclusion, or [Q]uit. After entering a letter,
    # the program displays the prompt again and asks the user to input text.
    # The program continues to display the prompt and ask for input until the
    # user enters [Q]uit. The program then saves the FIRAC structure as a JSON
    # file and returns the structure as a dictionary.
    print("Enter [F]acts, [I]ssue, [R]ule, [A]pplication, [C]onclusion, or [Q]uit.")
    while True:
        user_input = input("[F]acts, [I]ssue, [R]ule, [A]pplication, [C]onclusion, or [Q]uit: ")
        if user_input.lower() == "f":
            facts = input("Enter facts: ")
            firac["facts"] = facts
        elif user_input.lower() == "i":
            issue = input("Enter issue: ")
            firac["opinions"]["issue"] = issue
        elif user_input.lower() == "r":
            rule = input("Enter rule: ")
            firac["opinions"]["rule"] = rule
        elif user_input.lower() == "a":
            application = input("Enter application: ")
            firac["opinions"]["application"] = application
        elif user_input.lower() == "c":
            conclusion = input("Enter conclusion: ")
            firac["opinions"]["conclusion"] = conclusion
        elif user_input.lower() == "q":
            opinion = input("Enter the opinion type ([M]ajority; [D]issenting; [Con]curring; [Cur]iam; [Cou]rt): ")
            # Validate the opinion type
            if opinion.lower() == "m":
                firac["opinions"]["opinion_type"] = "majority"
            elif opinion.lower() == "d":
                firac["opinions"]["opinion_type"] = "dissenting"
            elif opinion.lower() == "con":
                firac["opinions"]["opinion_type"] = "concurring"
            elif opinion.lower() == "cur":
                firac["opinions"]["opinion_type"] = "curiam"
            elif opinion.lower() == "cou":
                firac["opinions"]["opinion_type"] = "court"
            else:
                print("[bold red]Invalid input.[/bold red]")
                continue


            break
        else:
            print("[bold red]Invalid input.[/bold red]")
            continue

    return firac


def firac_auto(text: str):
    """
    Creates the FIRAC structure using a custom trained spaCy model and saves it
    as a JSON file.
    """
    firac = classify_firac(text)
    return firac


def firac_json():
    """
    Creates the FIRAC structure using a JSON file in the same format as the
    manual and auto functions use.
    """
    file_path = input("Enter the path to the JSON file: ")
    verify_file_path(file_path)

    with open(file_path, "r", encoding="utf-8") as file:
        firac = json.load(file)

    return firac


def local_text_summary(firac: dict) -> dict:
    """
    Summarizes a text locally using the local summarization function. This
    function ranks sentences based on a simple word frequency algorithm. Future
    verions will allow more sophisticated summarization methods.
    """
    print("\n[bold underline #FFA500]Summarization[/bold underline #FFA500]")
    print("Summarizing text: ", end="")
    summary = {}
    table = PrettyTable()
    table.field_names = ["", "Total spaCy Tokens", "Percentage Included"]

    def process_key(key: str):
        """
        Processes the key and returns the summary.
        """
        # Remove extraneous spaces and characters
        firac[key] = preprocess_text_for_gpt(firac[key])

        # Summarize the text
        firac[key] = extraction_text_summarizer(firac[key])

        # Add the summary to the summary dictionary
        summary[key] = firac[key]
        table.add_row(
            [f"{key.title()}", round(firac[key][1] * 100, 2), firac[key][2]]
        )

    # Each FIRAC key contains a list of sentences. Go through each list and
    # remove \n characters. Then, join the sentences into a single string.
    
    keys = ["opinion_type", "facts", "issues", "rules", "analysis", "conclusion"]

    for key in keys:
        process_key(key)


    print("[green]Done.[/green]\n")

    typer.echo(table)
    return summary


def local_text_analysis(citations: list):
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

    text_string = ""

    if legal_tests:
        print("\nTests found:")
        text_string += "\nTests found:\n"

        for test in legal_tests:
            print(f" \u2022 {test['short_form']}")
            text_string += f" \u2022 {test['short_form']}\n"
    else:
        print("\nTests found: [red]None[/red]")
        text_string += "\nTests found: None\n"

    return text_string


# Calls the app
if __name__ == "__main__":
    app()
