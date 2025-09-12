import os
from dotenv import load_dotenv
from openai import OpenAI

try:
    import streamlit as st
except Exception:
    st = None

load_dotenv()

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
