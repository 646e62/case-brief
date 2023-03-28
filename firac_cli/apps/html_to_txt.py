"""
Functions that handle HTML to TXT conversion and writing to file.
"""

import os
import json
import re
from bs4 import BeautifulSoup

# Import abbreviations from JSON
with open("./data/abbreviations.json", "r", encoding="utf-8") as file:
    abbreviations = json.load(file)


def resolve_abbreviations(text: str) -> str:
    """
    Create a regex pattern to match the abbreviations with periods at the end
    then loops through each word and remove the period if it matches an 
    abbreviation. This ostensibly resolves Issue #7.
    Future versions should also target paragraph numbers and citations.
    """
    pattern = "|".join([re.escape(abreviation) + r"\." for abreviation in abbreviations])

    text = text.split()
    processed_text = []

    for word in text:
        match = re.match(pattern, word)

        if match:
            new_word = match.group(0)[:-1]
            processed_text.append(new_word)
        else:
            processed_text.append(word)

    text = " ".join(processed_text)

    return text


# Reads an HTML file and returns the text as a string
def canlii_html_to_txt(filename: str) -> tuple[str, list]:
    """
    Reads a CanLII HTML file and saves a text file. Although CanLII HTML isn't
    uniform, this function should work for most cases.
    """

    with open(filename, 'r', encoding="utf-8") as file:
        soup: BeautifulSoup = BeautifulSoup(file, 'html.parser')
        text = soup.get_text()
        print(text)
        text = resolve_abbreviations(text)
    print("[green]BS4 text extraction complete.[/green]")
    return text

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
    else:
        file_name = os.path.basename(file_path)

    # Create the file path
    year = file_name[:4]
    court = ''.join(filter(str.isalpha, file_name[4:-3]))

    # Construct the archive directory path based on the year and court/jurisdiction
    archive_dir = os.path.join(os.getcwd(), 'archive', year, court)
    if not os.path.exists(archive_dir):
        os.makedirs(archive_dir)

    # Construct the new file path and move the file to the archive directory
    new_file_path = os.path.join(archive_dir, file_name)
    os.rename(file_path, new_file_path)
    print(file_path, new_file_path)
    # Return the new file path for future use

    with open(new_file_path, "w", encoding="utf-8") as file:
        file.write(text)
    print(f"Wrote {new_file_path}")
