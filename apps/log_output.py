"""
These functions call the OpenAI API and log output to a file. This will allow
me to review the parameters used to generate the output over several tests.
"""

import os
import json
import openai

# Set the API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Set the output file
output_file = "output.txt"


def call_openai(
    prompt,
    engine,
    temperature,
    max_tokens,
    top_p,
    frequency_penalty,
    presence_penalty,
    stop,
):
    """
    This function calls the OpenAI API and logs the output to a file.
    """
    response = openai.Completion.create(
        engine=engine,
        prompt=prompt,
        temperature=temperature,
        max_tokens=max_tokens,
        top_p=top_p,
        frequency_penalty=frequency_penalty,
        presence_penalty=presence_penalty,
        stop=stop,
    )

    # Log the output to a file
    with open(output_file, "a") as file:
        file.write(json.dumps(response, indent=4))

    return response
