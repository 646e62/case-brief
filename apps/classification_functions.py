"""
Classify reported court cases using spaCy and a custom model trained to detect
FIRAC elements. V2 and onward are trained on the text from the cases the 
Supreme Court of Canada cases decided in 2022. Model development is ongoing.
"""

import spacy
from rich import print

def majority_minority(text: str) -> list:
    """
    Identifies the number of different opinions in a case, the type of opinion,
    the judge(s) who wrote the opinion, and the text attributable to the 
    faction. Returns a list of dictionaries with the citation, the name of the 
    judge(s) who wrote the decision, and the type of decision, as well as the
    decision text.

    The four types of decisions are:
    - Curium: The whole court agrees on the outcome of the case.
    - Majority: The majority of the court agrees with the decision.
    - Dissent: The minority of the court disagrees with the decision.
    - Concurring: The concurrance agrees with the decision but for different
      reasons.

    Depending on how well I'm able to clean the data, I may be able to use 
    rule-based matching to identify the judge names. If not, I'll have to 
    incorporate a named entity recognition model.
    """

    pass


def classify_firac(text: str, auto: bool = False) -> dict:
    """
    This function splits the document into sentences and then classifies each
    sentence with the closest corresponding FIRAC element. The function returns
    a dictionary with the FIRAC elements as keys and the sentences in a list as
    values.
    """
    if auto:
        print("\n[bold underline #FFA500]Clasifying FIRAC using textcat_firac_v3[/bold underline #FFA500]")
        print("Classifying FIRAC elements: ", end="")
        nlp = spacy.load("./models/textcat_firac_v3/model-last/")
        nlp.add_pipe("sentencizer")
        doc = nlp(text)
        firac = {}

        for sentence in doc.sents:
            categories = nlp(sentence.text).cats
            max_key = max(categories, key=lambda k: categories[k])
            max_key = max_key.lower()

            # Append the sentence to the FIRAC element that achieved the highest
            # score, and the value of the score to the sentence_values list. Append
            # a blank list to the FIRAC element if it doesn't exist.
            firac.setdefault(max_key, []).append(sentence.text)
        
        print("[green]Done.[/green]\n")

        return firac
    else:
        print("\n[bold underline #FFA500]Clasifying FIRAC manually[/bold underline #FFA500]")
        firac = {
            "facts": [],
            "issues": [],
            "rules": [],
            "analysis": [],
            "conclusion": [],
        }

        # Prompt the user to select a FIRAC element from a list. Once selected, prompt the
        # user to enter a string. If the string is empty, the user is prompted
        # to select a FIRAC element again. If the string is not empty, the
        # string is appended to the FIRAC element list. The user is prompted
        # to enter another string until they select the "Done" option.

        while True:

            print("\nSelect a FIRAC element:")
            print("1. Facts")
            print("2. Issues")
            print("3. Rules")
            print("4. Analysis")
            print("5. Conclusion")
            print("6. Done")

            try:
                selection = int(input("Selection: "))
            except ValueError:
                print("[red]Invalid selection.[/red]")
                continue

            if selection == 1:
                element = "facts"
            elif selection == 2:
                element = "issues"
            elif selection == 3:
                element = "rules"
            elif selection == 4:
                element = "analysis"
            elif selection == 5:
                element = "conclusion"
            elif selection == 6:
                return firac
            else:
                print("[red]Invalid selection.[/red]")
                continue

            print("\nEnter a string corresponding to the selected FIRAC element. Enter an empty string to select a different FIRAC element.")
            sentence = input("Sentence: ")

            if sentence == "":
                continue
            else:
                firac[element].append(sentence)
