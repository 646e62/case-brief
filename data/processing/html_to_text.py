from bs4 import BeautifulSoup
import re

def create_title(filepath: str)-> str:
    """Create a title for the text file from the html file name"""
    path_list = filepath.split("/")
    title_list = path_list[-1].split(".")
    title = title_list[0]
    
    # title is a string composed of two groups of numbers and one group of
    # letters. This function separes each group into a list.

    # The first group of numbers is the year
    year = re.findall(r"\d+", title)[0]
    # The second group of numbers is the file number
    file_number = re.findall(r"\d+", title)[1]
    # The group of letters is the jurisdiction and court
    jurisdiction = re.findall(r"[A-Z]+", title)[0]

    title = year + " " + jurisdiction.upper() + " " + file_number
    return title

def clean_text(paragraph: str, remove_para_nums=True: bool)->nltk.text:
    '''
    Returns tokenized text. The function can be set to include paragraph 
    numbers for instances where they may provide some semantic value, but 
    defaults to removing them as this generally isn't expected to be the case.

    The function removes paragraphs by checking to see if the first character 
    is a square bracket and if the next character is a number. If so, the 
    function removes the opening bracket and the number, and then removes all
    other characters until it reaches the closing bracket. If the first
    character is not a square bracket, the function returns the paragraph
    unchanged.
    '''
    words = nltk.word_tokenize(paragraph)
    
    if remove_para_nums:
        if paragraph[0] == "[" and paragraph[1].isdigit():
            words = words[2:]
            while words[0] != "]":
                words = words[1:]
            words = words[1:]

    return words
            

def decision_paragraphs(filename: str)->list:
    '''
    Extracts the decision text from the numbered paragraphs. The decision text
    is contained in the <div class="paragWrapper"> tags. This function extracts
    the text from these tags and appends it to a list.
    '''
    
    decision = read_html_file(filename)
    title = create_title(filename)
    
    # Find the first and last instances of the "paragWrapper" div
    first_div = decision.find("div", class_="paragWrapper")
    last_div = decision.find_all("div", class_="paragWrapper")[-1]

    paragraphs = []
    footnotes = []

    # Iterate over all siblings between the first and last instances of the "paragWrapper" div
    sibling = first_div
    paragraphs.append(title)
    paragraphs.append(first_div)
    while sibling != last_div:
        sibling = sibling.find_next_sibling()
        paragraphs.append(sibling)
        
    # Find and append footnotes, where applicable
    # Footnotes exist inside the "SPAN" tags with the class "MSoFootnoteReference"
    # Not all decisions contain footnotes
    if decision.find("SPAN", class_="MsoFootnoteReference"):
        footnote = decision.find("SPAN", class_="MsoFootnoteReference")
        footnotes.append(footnote)
        while footnote.find_next_sibling("SPAN", class_="MsoFootnoteReference"):
            footnote = footnote.find_next_sibling("SPAN", class_="MsoFootnoteReference")
            footnotes.append(footnote)
        paragraphs.append(footnotes)
        
        
    return paragraphs
