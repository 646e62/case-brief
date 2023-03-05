import re
from bs4 import BeautifulSoup

# nlp = spacy.load("en_core_web_md")

# Reads an HTML file and returns the text as a string
def canlii_html_to_txt(filename: str) -> tuple[str, list]:
    """
    Reads a CanLII HTML file and saves a text file. Although CanLII HTML isn't
    uniform, this function should work for most cases.
    """
    text_string = ""
    text_list = []

    with open(filename, 'r', encoding="utf-8") as file:
        soup: BeautifulSoup = BeautifulSoup(file, 'html.parser')
        text = soup.get_text()

        # Removes extraneous line breaks
        text = re.sub(r"\n+", " ", text)
        
        # Find spaces larger than a single space and replace them with a single
        # space
        text = re.sub(r"\s{2,}", " ", text)

    return text

