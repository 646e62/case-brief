import os
import openai

# Constants
openai.api_key = os.getenv("OPENAI_API_KEY")

def gpt_summarizer(prompt: str, text: str) -> str:
    """
    Basic text summarization using GPT-3. The presets are set to the 
    recommended levels for "summarize for a 2nd grader" prompt.
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


