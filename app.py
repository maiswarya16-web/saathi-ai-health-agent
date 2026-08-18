import streamlit as st
from openai import OpenAI

st.set_page_config(
    page_title="Saathi AI Health Agent",
    page_icon="🩺"
)

st.title("🩺 Saathi AI Health Agent")

st.write(
    "A digital assistant designed to support frontline health workers."
)

question = st.text_area(
    "Ask Saathi a health-related question:",
    placeholder="Example: What warning signs should I look for during pregnancy?"
)

if st.button("Ask Saathi"):
    if question.strip():
        client = OpenAI(
            api_key=st.secrets["OPENAI_API_KEY"]
        )

        response = client.responses.create(
            model="gpt-5.6",
            input=f"""
You are Saathi AI, a health information assistant
designed to support frontline health workers.

Provide clear, safe and practical health information.
Do not claim to diagnose a patient.
For emergencies, advise seeking urgent medical care.

User question:
{question}
"""
        )

        st.info(response.output_text)

    else:
        st.warning("Please enter a question first.")
