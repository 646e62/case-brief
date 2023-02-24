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

def export_all(jurisdiction_list: list):
    '''
    Takes file paths from the jurisdiction list and exports them to text en
    masse.
    '''
    for court_list in jurisdiction_list:
        for decision in court_list:
            decision_text = compile_decision_text(decision)
            decision_text_file = export_to_file(decision_text, decision)
            
