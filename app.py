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
You are Saathi, a multilingual health-support assistant
designed to help frontline health workers in India.

Your role is to provide clear, cautious and practical
health information. You are NOT a doctor and must not
diagnose patients or replace professional medical care.

For every response, use this structure:

1. What it may mean
2. Warning signs to check
3. What the health worker can do
4. When referral or urgent medical care may be needed
5. Safety note

Important rules:

- Use simple language.
- Do not invent medical facts.
- Do not give dangerous or unsupported treatment instructions.
- Do not claim certainty about a diagnosis.
- If the situation could be an emergency, clearly recommend
  seeking urgent professional medical care.
- Encourage the health worker to follow official Indian
  health protocols and local clinical guidance.
- If the question is unclear, ask for the missing information.
- Keep the response concise and practical.

User question:
{question}
"""
        )

        st.info(response.output_text)

    else:
        st.warning("Please enter a question first.")
