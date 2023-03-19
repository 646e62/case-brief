"""
OpenAI recently released an API for GPT-3.5, which is the model used for 
ChatGPT. GPT-3.5 is a chat model, rather than a completion model, but in early
tests it appears to perform better than the completion model. These functions
is designed around the new chat model.
"""

import os
import json
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")
OUTPUT_FILE = "../output.txt"

# Tests on smaller cases using manual input and hybrid models are yielding 
# comparable results to GPT-4 alone at 1/5th the cost. Trying a new test with
# dynamically adjusted messaging.

# Progressively removing information and labelling previous responses turned
# out well. I was able to reduce costs from $0.22 to $0.05 per report.

def gpt_hybrid_analysis_manual() -> dict:
    """
    Although GPT-4 is far more capable than GPT-3.5 at handling larger strings,
    it is currently prohibitively expensive. This function uses GPT-3.5 to
    analyze the text and GPT-4 to summarize the text. This function is designed
    to be used with manual input.
    """
    summary = openai.Completion.create(
              model="text-davinci-003",
              prompt = f"{prompt}: {text}",
              temperature=0.7,
              max_tokens=256,
              top_p=1,
              frequency_penalty=0,
              presence_penalty=0
              )

    return summary

def gpt_chat_completion()