import streamlit as st
from google import genai

# Page configuration
st.set_page_config(
    page_title="Saathi AI Health Agent",
    page_icon="🩺"
)

# Title
st.title("🩺 Saathi AI Health Agent")

st.write(
    "A digital assistant designed to support frontline health workers."
)

# Get Gemini API key from Streamlit Secrets
api_key = st.secrets["GEMINI_API_KEY"]

# Create Gemini client
client = genai.Client(api_key=api_key)

# User question
topic = st.selectbox(
    "Select a health topic:",
    [
        "Maternal Health",
        "Child Health",
        "Skin Problems",
        "Diabetes",
        "Hypertension (High Blood Pressure)",
        "Fever & Infections",
        "Respiratory Problems",
        "Nutrition",
        "Immunization",
        "Mental Wellbeing",
        "Women's Health",
        "Men's Health",
        "Elderly Health",
        "First Aid",
        "General Symptoms"
    ]
)

question = st.text_area(
    "Ask Saathi a health-related question:",
    placeholder="Example: What warning signs should I look for during pregnancy?"
)

# Ask button
if st.button("Ask Saathi"):

    if question.strip():

        prompt = f"""
You are Saathi AI, a helpful health-information assistant
designed to support frontline health workers such as ASHA and ANM workers in India.

Provide clear, simple and practical health information.

Question:
{question}

Important:
- Give general health information.
- Do not claim to diagnose the patient.
- Mention when urgent medical care is needed.
- Use simple language suitable for frontline health workers.
"""

        try:
            response = client.models.generate_content(
    model="gemini-3.6-flash",
    contents=prompt
)

answer = response.text
red_flag_words = [
    "difficulty breathing",
    "severe chest pain",
    "unconscious",
    "heavy bleeding",
    "seizure",
    "severe allergic reaction"
]

if any(word in question.lower() for word in red_flag_words):
    st.error(
        "🚨 Possible emergency warning sign detected. "
        "Seek urgent professional medical assessment "
        "according to the applicable health protocol."
    )
if st.button("Ask Saathi"):
    if question.strip():
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=question
            )

            answer = response.text

            st.success("Saathi's guidance:")
            st.write(answer)

        except Exception as e:
            st.error(f"Sorry, Saathi could not answer right now: {e}")

    else:
        st.warning("Please enter a question first.")
