import os
import openai

# Constants
openai.api_key = os.getenv("OPENAI_API_KEY")

def issue_counter(issue_text: str) -> int:
    """
    Counts the number of issues in the issue text.
    """
    response = openai.Completion.create(
               model="text-davinci-003", 
               prompt = f"Return integer expressing number of issues: {issue_text}", 
               temperature=0, max_tokens=100, top_p=1, frequency_penalty=0, 
               presence_penalty=0
               )

    return response



