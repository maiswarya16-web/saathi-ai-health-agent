import streamlit as st
from google import genai

# -----------------------------
# PAGE CONFIGURATION
# -----------------------------
st.set_page_config(
    page_title="Saathi AI Health Agent",
    page_icon="🩺",
    layout="centered"
)

# -----------------------------
# GEMINI API CLIENT
# -----------------------------
client = genai.Client(
    api_key=st.secrets["GEMINI_API_KEY"]
)

# -----------------------------
# TITLE
# -----------------------------
st.title("🩺 Saathi AI Health Agent")

st.write(
    "A digital assistant designed to support frontline health workers "
    "such as ASHA and ANM workers."
)

# -----------------------------
# HEALTH TOPIC
# -----------------------------
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

# -----------------------------
# QUESTION
# -----------------------------
question = st.text_area(
    "Ask Saathi a health-related question:",
    placeholder=(
        "Example: What warning signs should I look for during pregnancy?"
    )
)

# -----------------------------
# RED FLAG DETECTION
# -----------------------------
RED_FLAGS = [
    "severe chest pain",
    "chest pain",
    "difficulty breathing",
    "severe difficulty breathing",
    "cannot breathe",
    "unconscious",
    "loss of consciousness",
    "not responding",
    "seizure",
    "convulsion",
    "severe bleeding",
    "heavy bleeding",
    "vomiting blood",
    "coughing blood",
    "blood in vomit",
    "severe abdominal pain",
    "severe headache",
    "sudden weakness",
    "face drooping",
    "slurred speech",
    "difficulty speaking",
    "paralysis",
    "blue lips",
    "blue skin",
    "severe allergic reaction",
    "swelling of face",
    "swelling of throat",
    "suicidal",
    "suicide",
    "self harm",
    "severe burn",
    "electric shock"
]

def detect_red_flags(text):
    text = text.lower()
    detected = []

    for flag in RED_FLAGS:
        if flag in text:
            detected.append(flag)

    return detected


# -----------------------------
# ASK SAATHI
# -----------------------------
if st.button("Ask Saathi"):

    if question.strip():

        detected_flags = detect_red_flags(question)

        # -----------------------------
        # RED FLAG ALERT
        # -----------------------------
        if detected_flags:

            st.error(
                "🚨 RED FLAG / URGENT WARNING\n\n"
                "The question contains a possible warning sign "
                "that may require urgent medical evaluation."
            )

            st.warning(
                "Please do not rely only on this AI tool. "
                "Seek appropriate emergency medical care immediately "
                "if the person is seriously unwell."
            )

        # -----------------------------
        # GEMINI RESPONSE
        # -----------------------------
        try:

            prompt = f"""
You are Saathi AI, a health-information assistant designed
to support frontline health workers such as ASHA and ANM workers in India.

Selected health topic:
{topic}

Health question:
{question}

Provide clear, simple and practical health information.

SAFETY RULES:
- Do not diagnose the patient.
- Do not prescribe medicines or dosages.
- Mention important warning signs when relevant.
- If the symptoms could indicate an emergency, clearly recommend
  urgent medical evaluation.
- Do not tell the user to wait when serious warning signs are present.
- Use simple language suitable for frontline health workers.
- Focus on the selected health topic.
- Encourage referral to an appropriate healthcare professional
  when necessary.

Structure the answer as:

1. What it may mean
2. Important warning signs
3. What the health worker can do
4. When to refer urgently
5. Important safety note
"""

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )

            answer = response.text

            st.success("🩺 Saathi's Guidance")
            st.write(answer)

        except Exception as e:

            st.error(
                "Sorry, Saathi could not answer right now. "
                "Please check the API configuration."
            )

    else:

        st.warning("Please enter a health question first.")
