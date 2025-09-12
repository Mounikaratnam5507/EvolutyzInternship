import os
from dotenv import load_dotenv
from openai import OpenAI
import streamlit as st

load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY") or st.secrets["OPENAI_API_KEY"].rstrip("/")
client = OpenAI(openai_api_key) # Replace with your API key

def chat_with_gpt(messages):
    """
    text 
    messages: list of dicts like
    [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hi"},
        {"role": "assistant", "content": "Hello! How can I help you?"},
        {"role": "user", "content": "Tell me a joke"}
    ]
    """
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",   # you can also use "gpt-4"
        messages=messages,
        temperature=0.7,
        max_tokens=500
    )
    return response.choices[0].message.content
#chat_with_gpt(prompt)
