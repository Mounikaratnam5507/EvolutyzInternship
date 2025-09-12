import os
from dotenv import load_dotenv
from openai import OpenAI
import os
from dotenv import load_dotenv
from openai import OpenAI

try:
    import streamlit as st
except Exception:
    st = None

load_dotenv()

# Prefer env var; fall back to Streamlit secrets if present
env_key = os.getenv("OPENAI_API_KEY")
secrets_key = None
if st is not None:
    try:
        # st.secrets behaves like a mapping
        secrets_key = st.secrets.get("OPENAI_API_KEY")
    except Exception:
        secrets_key = None

openai_api_key = (env_key or secrets_key or "").strip()

if not openai_api_key:
    raise RuntimeError(
        "OPENAI_API_KEY is not set. Set it in your environment or in Streamlit secrets."
    )

client = OpenAI(api_key=openai_api_key)

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
