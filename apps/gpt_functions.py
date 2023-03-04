"""
OpenAI recently released an API for GPT-3.5, which is the model used for 
ChatGPT. GPT-3.5 is a chat model, rather than a completion model, but in early
tests it appears to perform better than the completion model. These functions
is designed around the new chat model.
"""

import os
import openai
from 

openai.api_key = os.getenv("OPENAI_API_KEY")
output_file = "output.txt"

def message_generator(
    facts, 
    history, 
    issues, 
    rules, 
    analysis, 
    conclusion
) -> list[dict]:
    """
    This function generates the messages for the chatbot. It takes the 
    arguments from the main function and uses them to generate the messages.
    """

    messages = [facts, history, issues, rules, analysis, conclusion]

    return messages


def call_openai(
    messages: list[dict],
    engine: str ="gpt-3.5-turbo",
    temperature: float = 0.5,
    max_tokens: int = 100,
    top_p: float = 1,
    frequency_penalty: float = 0,
    presence_penalty: float = 0,
) -> list:
    """
    This function calls the OpenAI API and logs the output to a file. This call
    is designed for the GPT-3.5 API.
    """

    response = openai.Completion.create(
        engine = engine,
        messages = messages,
        temperature = temperature,
        max_tokens = max_tokens,
        top_p = top_p,
        frequency_penalty = frequency_penalty,
        presence_penalty = presence_penalty,
    )

    # Log the output to a file
    with open(output_file, "a") as file:
        file.write(json.dumps(response, indent=4))

    return response

