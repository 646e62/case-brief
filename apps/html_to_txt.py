import re
from bs4 import BeautifulSoup

from .decorators import timing

abbreviations = ["para.", "paras", "p", "pp", "Cst", "Csts", "s", "ss"]


# Reads an HTML file and returns the text as a string
@timing
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
        text = text.replace(u'\xa0', u' ')


        # Create a regex pattern to match the abbreviations with periods at the end
        # then loops through each word and remove the period if it matches an
        # abbreviation. This ostensibly resolves Issue #7.
        # Future versions should also target paragraph numbers and citations.
        pattern = "|".join(
            [re.escape(abreviation) + r"\." for abreviation in abbreviations]
        )

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

        # Insert line breaks at bracketed paragraph numbers
        # In all but the rarest cases, paragraph numbers will be bracketed
        # numbers no greater than 3 digits. This regex should catch all of them.

        text = re.sub(r"\[(\d{1,3})\]", r"\n[\1]", text)

    return text

