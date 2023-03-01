"""
The decision class contains the functions that parse the decision sentences 
into lists. The lists are then used to generate the decision summary.



The summarization functions are designed to minimize the amount of text that
needs to be sent to the GPT-3 functions for further summarization and analysis.
"""

import json
import spacy
import re
from collections import Counter
from spacy.lang.en.stop_words import STOP_WORDS
from spacy.lang.en import English
from string import punctuation
from heapq import nlargest


# Create a decision class that will include the extracted textual portions.


class Decision:
    def __init__(self, pfirac: dict):
        """
        This class creates a decision object that contains the extracted
        textual portions of a decision.

        The "meta" parameter should contain the following items:

            * Case citation
            * Judge or judges signing onto the decision
            * The position the decision takes with respect to the case as a whole (majority, dissent, etc.)

        Taken together, these items can be used to create a unique class identifier.

        Each of the remaining parameters should be lists of sentences. They
        should be combined into a single string before being passed to the
        summarization function.
        """

        self.meta = pfirac.get("meta", {})
        self.id = f"{self.meta.get('citation', '')} — {self.meta.get('judges', '')} — {self.meta.get('decision_type', '')}"
        self.facts = pfirac.get("facts", {})
        self.history = pfirac.get("history", {})
        self.issues = pfirac.get("issues", {})
        self.rules = pfirac.get("rules", {})
        self.analysis = pfirac.get("analysis", {})
        self.conclusion = pfirac.get("conclusion", {})

    def __str__(self):
        return self.id


def text_summarizer(
    text: str, percentage: float, abbreviations: list[str] | None = None
) -> str:
    """
    Summarizes text using extractive summarization methods. First, the function
    tokenizes the text and then calculates the frequency of each word. Then, it
    calculates the weighted frequency of each word. Finally, it calculates the
    weighted frequency of each sentence and returns the top sentences based on
    the percentage of the original text.

    This function is designed to minimize the amount of text that needs to be
    sent to the GPT-3 functions for further summarization and analysis. It is
    not designed to be a perfect summarization of the text.
    """

    # Create a regex pattern to match the abbreviations with periods at the end
    # then loops through each word and remove the period if it matches an 
    # abbreviation. This ostensibly resolves Issue #7.
    # Future versions should also target paragraph numbers and citations.
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

    # Tokenize the formatted text

    nlp = spacy.load("en_core_web_md")
    doc = nlp(text)
    stopwords = list(STOP_WORDS)

    # Calculates the frequency of each substantive word and generates the
    # frequency table. Future versions should also exclude citations and
    # paragraph numbers.
    word_frequency = Counter(
        [
            token.text
            for token in doc
            if token.text.lower() not in stopwords
            and token.text not in punctuation
            and token.text not in abbreviations
        ]
    )

    # Calculates a word's weighted frequency
    word_frequency_counter = Counter(word_frequency)
    max_frequency = max(word_frequency.values())
    for word in word_frequency.keys():
        word_frequency[word] = word_frequency[word] / max_frequency

    # Removes the stop words and punctuation from the sentences
    sentence_tokens = [sentence for sentence in doc.sents]
    sentence_scores = Counter(
        {
            sentence: sum(
                word_frequency_counter.get(word.text.lower(), 0) for word in sentence
            )
            for sentence in sentence_tokens
        }
    )

    len_tokens = int(len(sentence_tokens) * percentage)

    # Returns the top sentences based on the percentage of the original text.
    summary = [sentence for sentence, score in sentence_scores.most_common(len_tokens)]
    final_summary = [word.text for word in summary]
    summary = " ".join(final_summary)

    return summary


# Abbreviations
abbreviations = ["para.", "paras.", "p.", "pp.", "Cst", "Csts."]

# Test values
# Facts and procedural history can usually be combined when dealing with divergent opinions.

test_facts = [
    "the police had confidential source information that their target was in possession of a large quantity of cocaine and that he kept most of his drugs on his person. Mr. Ali was found next to a table with drugs, other than cocaine, and with items consistent with drug trafficking, including a scale, money, and a ringing cell phone. Mr. Ali’s pants were partially down as he was being arrested; and one of the officers reported seeing Mr. Ali reaching towards the back of his pants. As in Golden, I acknowledge that Mr. Ali has already served his custodial sentence. , Cst. Darroch believed in good faith that he had the requisite grounds to strip search Mr. Ali. He relayed his grounds to his superior officer, who authorized the search at the police station. Mr. Ali was in possession of 65 grams of crack cocaine."
]

test_history = [
    "A majority of the Alberta Court of Appeal affirmed his conviction for possession of cocaine for the purpose of trafficking., They found that the trial judge did not err in determining that the police’s strip search of Mr. Ali, incident to his lawful arrest, complied with s. 8 of the Canadian Charter of Rights and Freedoms in accordance with the principles governing strip searches set out by this Court in R. v. Golden, 2001 SCC 83, [2001] 3 S.C.R. 679., We would not give effect to Mr. Ali’s argument that a hearsay error arose because the officer who requested the strip search, Cst. Darroch, testified that he was told by another officer, Cst. Odorski, that Mr. Ali was reaching towards the back of his pants, and Cst. Odorski did not refer to this in his testimony at trial. , Mr. Ali now concedes that Cst. Darroch’s testimony was not inadmissible hearsay because it was not entered for the truth of its contents; the question, he maintains, was whether Cst. Darroch could reasonably rely on the information from Cst. Odorski as a factor in deciding whether he had reasonable and probable grounds to request the strip search., Defence counsel chose not to cross‑examine either officer about this information. It stood uncontradicted., This tactical choice undermines Mr. Ali’s submission that it was unreasonable for Cst. Darroch to rely on Cst. Odorski’s information. I further acknowledge that, as the courts below found no breach of s. 8 in this case, they did not consider whether the evidence should be excluded under s. 24(2)., At trial, counsel for Mr. Ali noted the search was “as humane as possible given the circumstances” (trial transcript, A.R., at p. 173)., The Crown would have no case without this evidence."
]

## Majority opinion

test_id_1 = "2022 SCC 1 — Moldaver J, Brown J, RoweJ, Jamal J — Majority"

test_issues_1 = [
    "Like the majority of the Court of Appeal, we are satisfied that there were reasonable and probable grounds justifying the strip search",
    "We would not give effect to Mr. Ali’s argument that a hearsay error arose because the officer who requested the strip search, Cst. Darroch, testified that he was told by another officer, Cst. Odorski, that Mr. Ali was reaching towards the back of his pants, and Cst. Odorski did not refer to this in his testimony at trial.",
]

test_rules_1 = [
    "Where a strip search is conducted as an incident to a person’s lawful arrest, there must be reasonable and probable grounds justifying the strip search, in addition to reasonable and probable grounds justifying the arrest (see Golden, at para. 99).",
    "These grounds are met for the strip search where there is some evidence suggesting the possibility of concealment of weapons or other evidence related to the reason for the arrest (see Golden, at paras. 94 and 111).",
]

test_analysis_1 = [
    "Like the majority of the Court of Appeal, we are satisfied that there were reasonable and probable grounds justifying the strip search:"
]

test_conclusions_1 = [
    "A majority of this Court agrees with the conclusion of the majority of the Court of Appeal and would dismiss the appeal.",
    "We would not give effect to Mr. Ali’s argument that a hearsay error arose because the officer who requested the strip search, Cst. Darroch, testified that he was told by another officer, Cst. Odorski, that Mr. Ali was reaching towards the back of his pants, and Cst. Odorski did not refer to this in his testimony at trial.",
    "For these reasons, we would dismiss the appeal.",
]


## Concurring opinion

test_id_2 = "2022 SCC 1 — Côté J — Concurring"

test_issues_2 = [
    "In my view, the respondent Crown failed to discharge its burden of establishing the legal basis for the strip search of Mr. Ali in accordance with the principles set out by this Court in Golden.",
    "As such, I find that Mr. Ali’s s. 8 Charter rights were violated, substantially for the reasons of Veldhuis J.A., at paras. 27‑61.",
    "Relying on Golden, at paras. 118‑19, Mr. Ali argues that this Court should substitute an acquittal because conducting an analysis under s. 24(2) of the Charter would be a mere theoretical exercise.",
    "First, the seriousness of the police conduct in this case was at the lowest end of the spectrum.",
    "Second, the impact of the strip search on Mr. Ali’s privacy interests, while serious, was somewhat attenuated by the reasonable manner in which it was conducted.",
    "The final Grant inquiry strongly favours admission.",
    "On balance, I conclude that excluding the evidence would bring the administration of justice into disrepute.",
]

test_rules_2 = [
    "In my view, the respondent Crown failed to discharge its burden of establishing the legal basis for the strip search of Mr. Ali in accordance with the principles set out by this Court in Golden.",
    "Applying the three lines of inquiry from R. v. Grant, 2009 SCC 32, [2009] 2 S.C.R. 353, I would not exclude the evidence.",
]

test_analysis_2 = [
    "As such, I find that Mr. Ali’s s. 8 Charter rights were violated, substantially for the reasons of Veldhuis J.A., at paras. 27‑61.",
    "However, I part ways with Veldhuis J.A. with respect to the proper remedy.",
    "Relying on Golden, at paras. 118‑19, Mr. Ali argues that this Court should substitute an acquittal because conducting an analysis under s. 24(2) of the Charter would be a mere theoretical exercise.",
    "I disagree.",
    "As in Golden, I acknowledge that Mr. Ali has already served his custodial sentence.",
    "Nevertheless, he remains subject to restrictions to his liberty, including a firearms prohibition and a DNA order.",
    "As such, determining whether the evidence ought to be admitted will have tangible consequences, both for Mr. Ali and for the public.",
    "Moreover, the facts of this case are plainly distinguishable from Golden.",
    "The strip search in Golden was coercive and forceful, conducted in a public area without authorization from a senior officer, and may have jeopardized the accused’s health and safety.",
    "The search of Mr. Ali has none of these characteristics.",
    "In my view, it is worthwhile to assess whether admitting evidence obtained as a result of the Charter breach would do further damage to the repute of the justice system.",
    "However, I accept the Crown’s submission that the record before this Court is sufficient to determine whether the admission of the evidence would bring the administration of justice into disrepute.",
    "Therefore, I see no utility in sending the matter back for redetermination.",
    "In these circumstances, it is open to this Court to conduct its own first‑instance s. 24(2) analysis (R. v. Spencer, 2014 SCC 43, [2014] 2 S.C.R. 212, at para. 75).",
    "I see no basis to suggest that the police wilfully disregarded Mr. Ali’s Charter rights.",
    "This factor favours admission.",
    "In my view, this factor tips only moderately in favour of exclusion.",
    "To be clear, I would emphatically re‑affirm the principles arising from Golden and the high threshold the Crown must meet to justify a warrantless strip search.",
]

test_conclusions_2 = [
    "As such, I find that Mr. Ali’s s. 8 Charter rights were violated, substantially for the reasons of Veldhuis J.A., at paras. 27‑61.",
    " Applying the three lines of inquiry from R. v. Grant, 2009 SCC 32, [2009] 2 S.C.R. 353, I would not exclude the evidence.",
    " First, the seriousness of the police conduct in this case was at the lowest end of the spectrum.",
    "This factor favours admission.",
    "Second, the impact of the strip search on Mr. Ali’s privacy interests, while serious, was somewhat attenuated by the reasonable manner in which it was conducted.",
    "In my view, this factor tips only moderately in favour of exclusion.",
    "The final Grant inquiry strongly favours admission.",
    "On balance, I conclude that excluding the evidence would bring the administration of justice into disrepute.",
    "Therefore, I would not exclude the evidence.",
    "For the foregoing reasons, I would dismiss the appeal and affirm the conviction.",
]
