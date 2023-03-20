"""
OpenAI recently released an API for GPT-3.5, which is the model used for 
ChatGPT. GPT-3.5 is a chat model, rather than a completion model, but in early
tests it appears to perform better than the completion model. These functions
are designed around the new chat model.
"""

import os
import json
import openai

from transformers import AutoTokenizer
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
OUTPUT_FILE = "../output.txt"

# Tests on smaller cases using manual input and hybrid models are yielding
# comparable results to GPT-4 alone at 1/5th the cost. Trying a new test with
# dynamically adjusted messaging.

# Progressively removing information and labelling previous responses turned
# out well. I was able to reduce costs from $0.22 to $0.05 per report.

def gpt_token_counter(text: str) -> int:
    """
    Counts the number of tokens in a string. This is used to calculate the
    number of tokens that will be charged to the user's account.
    """
    tokenizer = AutoTokenizer.from_pretrained('gpt2')
    
    # Count the number of tokens in a sentence
    encoding = tokenizer.encode(text)
    num_tokens = len(encoding)
    
    return num_tokens

def gpt_hybrid_analysis_manual(sorted_text: dict, auto: bool = False) -> dict:
    """
    Although GPT-4 is far more capable than GPT-3.5 at handling larger strings,
    it is currently prohibitively expensive. This function uses GPT-3.5 to
    analyze the text and GPT-4 to summarize the text.

    This function is designed to be used with manual input. In the future,
    local NLP models will be used to sort the text into the appropriate
    categories. Future versions may also be trained to detect whether a case
    is being heard at first instance or on appeal.

    For now, the sorted_text dictionary should be formatted as follows:
    {
        "opinion": "court", "curium", "majority opinion", "dissenting opinion", or "concurring opinion",
        "facts": "string",
        "issues": "string",
        "rules": "string",
        "analysis": "string",
        "conclusion": "string",
    }
    """
    print("Using GPT-3.5 and GPT-4 hybrid model (manual input).")
    # Default parameters for GPT-3.5
    parameters = {
        "model": "gpt-3.5-turbo",
        "messages": [],
        "temperature": 0.4,
        "max_tokens": 750,
        "top_p": 1,
        "frequency_penalty": 0.0,
        "presence_penalty": 0.0,
    }
    if sorted_text["opinion_type"] == "court's":
        case_type = "first instance"
    else:
        case_type = "appeal"

    opinion_type = sorted_text["opinion_type"]
    facts = sorted_text["facts"]
    issues = sorted_text["issues"]
    rules = sorted_text["rules"]
    analysis = sorted_text["analysis"]
    conclusion = sorted_text["conclusion"]
    print("Adjusting system prompt")
    system_prompt = "You are an assistant helping summarize Canadian criminal legal cases into a FIRAC case brief. FIRAC stands for facts, issues, rules, analysis, and conclusion.\nFacts include everything before the court heard the case it was reporting. For appeal cases, this will usually include procedural history. Facts should be one or a few more paragraphs.\nIssues are the questions that the parties are asking the court to answer. Issues should be listed as brief questions to be answered in an ordered list.\nRules are the legal rules and procedures the court must apply to answer the questions.\nAnalysis refers to the court's reasons for how it answers the questions raised in the issues section. Analysis can include justification for the rules used and how they should be applied to the facts in the case. Analysis should address each distinct issue in one or more paragraphs\nThe conclusion is a brief summary of what happened. In trials, it will be whether the defendant was acquitted or convicted. In appeals, it will be whether the appeal was allowed or dismissed.\nSome cases may have multiple opnions. One common example is an appeal, which may have majority, dissenting, and concurring opinions. Where there are multiple opinions, the FIRAC analysis should be done for each of them.\nThe entire brief should be between 500 - 1500 words per opinion but may be somewhat more or less for larger and smaller cases."

    # Adjust the system prompt based on whether the text was sorted through NLP
    # or manually.
    if auto:
        system_prompt += "\nThis text was sorted by a spaCy model that is still being developed. You should assume that the text is generally sorted correctly, but not always. Some sections may be incomplete or inaccurate."
    else:
        system_prompt += "\nThe following text was sorted by a human and you should assume it's complete and accurate."
    print("Loading hybrid prompts")
    # Hybrid prompts
    fact_prompt = f"These are the facts in the case: {facts}\nPlease summarize the facts in this case."
    if case_type == "appeal":
        fact_prompt += "Because this is an appeal, please also summarize the procedural history."
    issue_prompt = f"These are the issues the  {opinion_type} found in the case:\n{issues}\nList the issues the  {opinion_type} found in this case in an ordered list. Phrase the issues as questions to be answered."
    analysis_prompt = f"This is the analysis the  {opinion_type} conducted in the case:\n{analysis}\nHow did the  {opinion_type} answer the issues in the case? Please use the issues as headings and provide one or more brief paragraphs as answers."
    rules_prompt = f"These are legal rules the  {opinion_type} applied in this case:\n{rules}\nOther rules may be contained in the above analysis. What legal rules did the  {opinion_type} apply in this case? Please list the rules as brief sentences in an ordered list."
    conclusion_prompt = f"This is the conclusion the  {opinion_type} reached in this case:\n{conclusion}\nOther conclusive statements may be in the analysis, or inferred from the issues. What was the conclusion of the  {opinion_type} in this case? Answer in one brief sentence."
    
    print("Steps 1 - 3")
    # 1. {system_prompt} is sent to GPT-3.5
    # 2. {fact_prompt} is sent to GPT-3.5
    # 3. GPT-3.5 responds with a summary of the facts {fact_summary}
    parameters["messages"].append({"role": "system", "content": system_prompt})
    parameters["messages"].append({"role": "user", "content": fact_prompt})
    response = gpt_chat_completion(parameters)
    fact_summary = response["choices"][0]["message"]["content"]
    print(f"Facts:\n{fact_summary}")

    print("Steps 4 & 5")
    # 4. The {fact_summary} and {issue_prompt} are sent to GPT-3.5
    # 5. GPT-3.5 responds with a summary of the issues {issue_summary}
    parameters["messages"].append({"role": "assistant", "content": fact_summary})
    parameters["messages"].append({"role": "user", "content": issue_prompt})
    response = gpt_chat_completion(parameters)
    issue_summary = response["choices"][0]["message"]["content"]
    print(f"Issues:\n{issue_summary}")

    print("Steps 6 & 7")
    # 6. {fact_summary}, {issue_summary}, and analysis_prompt are sent to GPT-3.5
    # 7. GPT-3.5 responds with a summary of the analysis {analysis_summary}
    parameters["messages"].append({"role": "assistant", "content": fact_summary})
    parameters["messages"].append({"role": "assistant", "content": issue_summary})
    parameters["messages"].append({"role": "user", "content": analysis_prompt})

    response = gpt_chat_completion(parameters)
    analysis_summary = response["choices"][0]["message"]["content"]
    

    print("Steps 8 & 9")
    # 8. {issue_summary}, {analysis_summary}, and {rules_prompt} are sent to GPT-4
    # 9. GPT-4 responds with a summary of the rules {rules_summary}
    parameters["messages"].append({"role": "assistant", "content": issue_summary})
    parameters["messages"].append({"role": "assistant", "content": analysis_summary})
    parameters["messages"].append({"role": "user", "content": rules_prompt})

    parameters["model"] = "gpt-4"
    response = gpt_chat_completion(parameters)
    rules_summary = response["choices"][0]["message"]["content"]
    print(f"Rules:\n{rules_summary}")
    print(f"Analysis:\n{analysis_summary}")

    print("Steps 10 & 11")
    # 10. {issue_summary}, {analysis_summary}, {rules_summary}, and {conclusion_prompt} are sent to GPT-3.5
    # 11. GPT-3.5 responds with a summary of the conclusion {conclusion_summary}
    parameters["messages"].append({"assistant": issue_summary})
    parameters["messages"].append({"assistant": analysis_summary})
    parameters["messages"].append({"assistant": rules_summary})
    parameters["messages"].append({"user": conclusion_prompt},)
    parameters["model"] = "gpt-3.5-turbo"
    response = gpt_chat_completion(parameters)
    conclusion_summary = response["choices"][0]["message"]["content"]
    print(f"Conclusion:\n{conclusion_summary}")
    report = f"[bold underline]Facts[/bold underline]\n{fact_summary}\n[bold underline]Issues[/bold underline]\n{issue_summary}\n[bold underline]Rules[/bold underline]\n{rules_summary}\n[bold underline]Analysis[/bold underline]\n{analysis_summary}\n[bold underline]Conclusion[/bold underline]\n{conclusion_summary}"

    print(report)
    return report


def gpt_chat_completion(parameters: dict) -> dict:
    """
    This function uses a GPT chat completion model to complete a prompt.
    """
    response = openai.ChatCompletion.create(
        model = parameters["model"],
        messages = parameters["messages"],
        temperature = parameters["temperature"],
        max_tokens = parameters["max_tokens"],
        top_p = parameters["top_p"],
        frequency_penalty = parameters["frequency_penalty"],
        presence_penalty = parameters["presence_penalty"],
    )

    return response
