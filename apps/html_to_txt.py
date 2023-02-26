import re
from bs4 import BeautifulSoup

nlp = spacy.load("en_core_web_md")

# Reads an HTML file and returns the text as a string
def html_to_text_file(filename: str)->str:
    '''
    Reads an HTML file and saves a text file.
    '''

    with open(filename, 'r', encoding="utf-8") as file:
        soup: BeautifulSoup = BeautifulSoup(file, 'html.parser')
        text = soup.get_text()

    # Remove extra whitespace
    text = re.sub(r"\s+", " ", text)

    # Remove leading and trailing whitespace
    text = text.strip()

    return text


# Reads a text file and removes extraneous whitespace
def clean_text_file(filename: str)->str:
    '''
    Reads a text file and removes extraneous whitespace.
    '''
    with open(filename, 'r', encoding="utf-8") as file:
        text = file.read()

    # Remove extra whitespace
    text = re.sub(r"\s+", " ", text)

    # Remove leading and trailing whitespace
    text = text.strip()

    return text
