import os
from openai import OpenAI

openai_api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(openai_api_key) # Replace with your API key

def summarize_text(text):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",   # You can also use "gpt-4"
        messages=[
            {"role": "system", "content": "You are a helpful assistant that summarizes text."},
            {"role": "user", "content": f"Please summarize the following text:\n\n{text}"}
        ],
        temperature=0.5,
        max_tokens=300
    )
    return response.choices[0].message.content
