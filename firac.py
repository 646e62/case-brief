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
from rich.prompt import Prompt

import typer

from apps.analytic_functions import detect_legal_tests, local_text_analysis
from apps.classification_functions import classify_firac
from apps.extraction_functions import extract_text, extract_citations, verify_file_path
from apps.html_to_txt import write_text
from apps.summarization_functions import preprocess_text_for_gpt, local_text_summary
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
def create_firac(file: Optional[str] = None):
    """
    Creates a FIRAC report.

    The file suffix will determine what functions are run. If the file is a
    .txt or .html file, the text will be extracted, classified using the local
    spaCy models, and summarized using the local summarization model before 
    being sent to GPT-3 for further analysis. If the file is a .json file, the
    program will assume that the input is a viable summary file and will send
    it directly to GPT-3 for analysis.

    Future iterations should include some cursory error checking to ensure
    that the input file is compatible with the program. For JSON files, the 
    program will check the file structure and check for blank fields. For
    text and HTML files, the program will check the first bit of header text
    to ensure it's a CanLII decision.
    """
    os.system("clear")
    print("[bold #FFA500]FIRAC[/bold #FFA500]\n")
    print("A command-line tool for analyzing legal texts.\n")

    # Check to see if a file path was provided. If not, direct the user to
    # a menu where they can select a file or input text manually.

    if file is None:
        # Prompt the user to select a file, input text manually, or exit.
        user_input = input("(S)elect a file, (I)nteractive mode, or E(x)it?\n")

        if user_input.lower() == "s":
            file = input("Enter the file path: ")
            create_firac(file)

        elif user_input.lower() == "i":
            summary = firac_manual()
            analysis = local_text_analysis(summary)
            report = gpt_hybrid_analysis_manual(summary)

            return report, analysis

        elif user_input.lower() == "x":
            sys.exit()
    # Check the file suffix to determine what functions to run.
    else:
        if file.endswith(".txt" or ".html"):
            text = extract_text(file)
            firac = classify_firac(text)
            citations = extract_citations(text)
            summary = local_text_summary(firac)
            analysis = local_text_analysis(citations)
            report = gpt_hybrid_analysis_manual(summary)

            return report, analysis

        elif file.endswith(".json"):
            # Load the summary file
            with open(file, "r", encoding="utf-8") as file:
                firac = json.load(file)
            # Extract the text from the various sections
            text = ""
            for key in firac:
                text += firac[key]
            citations = extract_citations(text)
            summary = local_text_summary(firac)
            analysis = local_text_analysis(citations)
            report = gpt_hybrid_analysis_manual(summary)

            return report, analysis

        else:
            print("[bold red]File type not supported.[/bold red]")
            create_firac()


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
        user_input = Prompt.ask("[F]acts, [I]ssue, [R]ule, [A]pplication, [C]onclusion, or [Q]uit: ", 
                                choices=["F", "I", "R", "A", "C", "Q"], 
                                default="Q")
        user_input = input("")
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
            opinion = input("Enter the opinion type ([M]ajority; [D]issenting;\
                             Co[n]curring; Cu[r]iam; Co[u]rt): ")
            # Validate the opinion type
            if opinion.lower() == "m":
                firac["opinions"]["opinion_type"] = "majority"
            elif opinion.lower() == "d":
                firac["opinions"]["opinion_type"] = "dissenting"
            elif opinion.lower() == "n":
                firac["opinions"]["opinion_type"] = "concurring"
            elif opinion.lower() == "r":
                firac["opinions"]["opinion_type"] = "curiam"
            elif opinion.lower() == "u":
                firac["opinions"]["opinion_type"] = "court"
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


# Calls the app
if __name__ == "__main__":
    app()
