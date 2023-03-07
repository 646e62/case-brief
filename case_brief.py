#!/usr/bin/env python3
"""
Runs the case brief program from the command line.
"""

import argparse
import os.path
import sys
import time

# from typing import List, Tuple

from apps.analytic_functions import retrieve_citations, get_legal_test
from apps.classification_functions import classify_firac
from apps.html_to_txt import canlii_html_to_txt
from apps.summarization_functions import text_summarizer

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


# File functions

print("Retrieving citations: ", end="")
text = canlii_html_to_txt(args.file_path)
citations = retrieve_citations(text)
firac = classify_firac(text)

# Isolate the citations into a set
# If the underlying list is empty, a "None" string is added to the set

with open("timings.log", "a") as f:
    perf_end = f"start list building: {int(time.time())}"
    f.write(perf_end)

decision_list = []
legislation_list = []
section_list = []

decision_list = set([
    decision
    for citation in citations
    if citation["type"] == "decisions"
    for decision in citation["citations"]
])

legislation_list = set([
    statute
    for citation in citations
    if citation["type"] == "legislation"
    for statute in citation["citations"]
])

section_list = set([
    section
    for citation in citations
    if citation["type"] == "legislation"
    for section in citation["sections"]
])

with open("timings.log", "a") as f:
    perf_end = f"end list building: {int(time.time())}"
    f.write(perf_end)

print(
    f"\nDecisions:\n{decision_list}\n\nLegislation:\n{legislation_list}\n\nSections:\n{section_list}"
)

for key in firac:
    print(f"\n{key.upper()}: \n{firac[key]}")

# Check to see if any of the citations are in the legal tests
if get_legal_test(decision_list):
    print("\nLegal test(s) found:")
    # Find the "short_form" key for any legal tests that match the citation and
    # print it in title case
    for test in get_legal_test(decision_list):
        print("* " + test["short_form"].title())
else:
    print("\nNo legal tests found.")

# Take the list from each key and join them into a single string

section_text = ""
for key in firac:
    section_text += " ".join(firac[key])

section_text = text_summarizer(section_text, 0.5)
print(section_text)

# Write a local copy of the text file
# Take the HTML file name and change the extension to .txt
file_name = os.path.basename(args.file_path)
file_name = os.path.splitext(file_name)[0]
file_name = file_name + ".txt"

# Check to see if a file copy exists. If not, create one.
if not os.path.exists(f"./data/training_data/{file_name}"):
    with open("./data/training_data/" + file_name, "w", encoding="utf-8") as file:
        file.write(text)
