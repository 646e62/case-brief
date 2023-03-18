import json
import spacy

def html_path_to_txt(filename: str) -> str:
    file_path_list = filename.split("/")
    del file_path_list[2]
    file_path_list.insert(2,"txt")
    save_path = "/".join(file_path_list)
    
    save_path_corrected = save_path.split(".")
    del save_path_corrected[-1]
    save_path_corrected.append("txt")
    save_path_corrected = ".".join(save_path_corrected)
    
    return save_path_corrected

def export_to_file(clean_decision: list, filename: str):
    '''
    Saves a copy of the cleaned decision text to file.
    '''
    save_path_corrected = html_path_to_txt(filename)    
    with open(save_path_corrected, "w") as f:
        for paragraph in clean_decision:
            try:
                f.write(paragraph + "\n")
            except:
                if paragraph:
                    f.write(paragraph.text + "\n")
   
    print(f"Wrote {save_path_corrected}")

def sentencize_text(file_path):
    '''
    Converts a text file into a list of sentences.
    '''
    with open(file_path, "r", encoding="utf-8") as file:
        text = file.read()
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)
    sentences = list(doc.sents)
    
    new_file_path = file_path.split(".")
    del new_file_path[-1]
    new_file_path.append("sent.txt")
    new_file_path = ".".join(new_file_path)

    with open(new_file_path, "w", encoding="utf-8") as file:
        for sentence in sentences:
            file.write(sentence.text + "\n")

