"""
Functions for extracting text and citations from a legal text.
"""

import sys
import os

from rich import print

from html_to_txt import canlii_html_to_txt, write_text
from analytic_functions import retrieve_citations

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
    print("[bold green]Done.[/bold green]\n")

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
