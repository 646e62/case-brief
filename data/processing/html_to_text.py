import spacy
import re
from bs4 import BeautifulSoup

nlp = spacy.load("en_core_web_md")

# Reads an HTML file and returns a BeautifulSoup object
def read_html_file(filename: str)->BeautifulSoup:
    '''
    Reads an HTML file and returns a BeautifulSoup object.
    '''
    with open(filename, 'r', encoding="utf-8") as file:
        soup: BeautifulSoup = BeautifulSoup(file, 'html.parser')
    return soup


def create_title(filepath: str)-> str:
    """Create a title for the text file from the html file name"""
    path_list = filepath.split("/")
    title_list = path_list[-1].split(".")
    title = title_list[0]
    
    # The first group of numbers is the year
    year = re.findall(r"\d+", title)[0]
    # The second group of numbers is the file number
    file_number = re.findall(r"\d+", title)[1]
    # The group of letters is the jurisdiction and court
    jurisdiction = re.findall(r"[a-z]+", title)[0]
    
    if jurisdiction == "canlii":
        jurisdiction = "CanLII"
        title = f"{year} {jurisdiction} {file_number}"
    else:
        title = f"{year} {jurisdiction.upper()} {file_number}"
 
    return title


def decision_paragraphs(filename: str)->tuple:
    '''
    Extracts the decision paragraphs. The decision text
    is contained in the <div class="paragWrapper"> tags. This function extracts
    the text from these tags and appends it to a list.
    '''
    
    decision = read_html_file(filename)
    
    # Find the first and last instances of the "paragWrapper" div
    first_div = decision.find("div", class_="paragWrapper")
    last_div = decision.find_all("div", class_="paragWrapper")[-1]

    paragraphs = []
    footnotes = []

    # Iterate over all siblings between the first and last instances of the "paragWrapper" div
    sibling = first_div
    paragraphs.append(first_div)
    while sibling != last_div:
        sibling = sibling.find_next_sibling()
        paragraphs.append(sibling)
        
    # Finds and appends footnotes where applicable
    if decision.find("SPAN", class_="MsoFootnoteReference"):
        decision_footnotes(decision)
        
    return paragraphs, footnotes


def decision_footnotes(decision: str)->list:
    '''
    Generates a list of footnotes in decisions containing them.
    '''
    footnote = decision.find("SPAN", class_="MsoFootnoteReference")
    footnotes.append(footnote)
    while footnote.find_next_sibling("SPAN", class_="MsoFootnoteReference"):
        footnote = footnote.find_next_sibling("SPAN", class_="MsoFootnoteReference")
        footnotes.append(footnote)
    
    return footnotes


def clean_text(paragraph: str, remove_para_nums: bool=True)->list:
    '''
    Returns text with problematic characters removed. These include paragraph
    numbers enclosed in square brackets and superfluous periods after paragraph
    and section pinpoints, as these can sometimes confuse the sentence 
    detectors.
    '''
    doc = nlp(paragraph)
    try:
        if remove_para_nums and paragraph[0] == "[" and paragraph[1].isdigit():
            doc = re.sub(r"\[\d+\]\s", "", paragraph)
            return nlp(doc)
        else:
            return doc
    except:
        pass


def export_to_file(clean_decision: list, filename: str):
    '''
    Saves a copy of the cleaned decision text to file.
    '''
    
    file_path_list = filename.split("/")
    del file_path_list[2]
    file_path_list.insert(2,"txt")
    save_path = "/".join(file_path_list)
    
    save_path_corrected = save_path.split(".")
    del save_path_corrected[-1]
    save_path_corrected.append("txt")
    save_path_corrected = ".".join(save_path_corrected)
    
    with open(save_path_corrected, "w") as f:
        #for item in clean_decision:
            #f.write(str(item) + "\n")
        
        for paragraph in clean_decision:
            try:
                f.write(paragraph + "\n")
            except:
                if paragraph:
                    f.write(paragraph.text + "\n")
    
    print(save_path_corrected)


def compile_decision_text(filename)->list:
    '''
    The aggregate function that runs the others.
    '''
    
    decision = decision_paragraphs(filename)[0]
    footnotes = decision_paragraphs(filename)[1]
    clean_decision = []
    clean_decision.append(filename)
    
    for paragraph in decision:
        clean_decision.append(clean_text(paragraph.text))

    for item in clean_decision:
        try:
            if len(item) == 0:
                clean_decision.remove(item)
        except:
            pass
        
    if footnotes:
        for footnote in footnotes:
            decision.append(clean_text(footnote, False))
    
    return clean_decision


