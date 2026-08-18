import streamlit as st
from google import genai

# Page configuration
st.set_page_config(
    page_title="Saathi AI Health Agent",
    page_icon="🩺",
    layout="centered"
)

# Gemini API client
client = genai.Client(
    api_key=st.secrets["GEMINI_API_KEY"]
)

# Title
st.title("🩺 Saathi AI Health Agent")

st.write(
    "A digital assistant designed to support frontline health workers."
)

# Question input
question = st.text_area(
    "Ask Saathi a health-related question:",
    placeholder=(
        "Example: What warning signs should I look for during pregnancy?"
    )
)

# Ask button
if st.button("Ask Saathi"):
    if question.strip():

        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=(
                    "You are Saathi AI, a health-information assistant "
                    "designed to support frontline health workers such as "
                    "ASHA and ANM workers in India. "
                    "Provide clear, simple and safe health information. "
                    "Cover topics such as maternal health, child health, "
                    "diabetes, skin problems, nutrition, fever, common "
                    "illnesses and warning signs. "
                    "Do not claim to diagnose a patient. "
                    "For serious or emergency symptoms, advise the user "
                    "to seek appropriate medical care.\n\n"
                    f"Health question: {question}"
                )
            )

            answer = response.text

            st.success("Saathi's guidance:")
            st.write(answer)

        except Exception as e:
            st.error(
                "Sorry, Saathi could not answer right now. "
                "Please check the API key and try again."
            )

    else:
        st.warning("Please enter a question first.")
