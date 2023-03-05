#!/usr/bin/env python3

"""
Runs the case brief program from the command line.
"""

import argparse
import os
#import re
import sys
#from typing import List, Tuple

#from bs4 import BeautifulSoup
#import spacy
#from spacy.tokens import Doc, Span

from apps.analytic_functions import retrieve_citations
from apps.html_to_txt import canlii_html_to_txt

# Prompt the user for a file path
parser = argparse.ArgumentParser()
parser.add_argument(
    "file_path",
    help="The path to the HTML file to be processed.",
    type=str,
)
args = parser.parse_args()

# Check if the file exists
if not os.path.exists(args.file_path):
    print("File not found.")
    sys.exit()

# Read the HTML file and convert it to text
text = canlii_html_to_txt(args.file_path)

# Retrieve the citations from the text
citations = retrieve_citations(text)

# Print the citations
print("Citations:")
for citation in citations:
    if citation["type"] == "decisions":
        print("Decisions:")
        for decision in citation["citations"]:
            print(decision)
    elif citation["type"] == "legislation":
        print("Legislation:")
        for statute in citation["citations"]:
            print(statute)
        print("Sections:")
        for section in citation["sections"]:
            print(section)
