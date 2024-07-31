from openai import OpenAI

import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.environ.get("OPEN_AI_KEY")
)

def createInstitutionCode(institutionName):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages = [
            {"role": "system", "content": "Generate 1 code for name (2-5 chars). Make it understandable. Try to make it first letters of word if possible. Return only code."},
            {"role": "user", "content": institutionName}
        ],
        max_tokens=200
    )

    return response.choices[0].message.content.upper()