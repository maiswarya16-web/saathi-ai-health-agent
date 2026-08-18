import streamlit as st

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
        st.info(
            "Thank you. Saathi received your question. "
            "AI guidance will be connected in the next step."
        )
    else:
        st.warning("Please enter a question first.")
