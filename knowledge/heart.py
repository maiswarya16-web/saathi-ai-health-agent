# Saathi AI - Heart & Cardiovascular Health Knowledge
# Source basis: WHO cardiovascular disease guidance

HEART_HEALTH = {
    "overview": """
Cardiovascular diseases affect the heart and blood vessels.
Common risk factors include high blood pressure, tobacco use,
unhealthy diet, physical inactivity, diabetes, obesity, and
unhealthy alcohol use.

Early recognition of serious symptoms and timely medical care
are important.
""",

    "risk_factors": [
        "High blood pressure",
        "Diabetes",
        "Tobacco use",
        "Unhealthy diet",
        "Physical inactivity",
        "Overweight or obesity",
        "High cholesterol",
        "Family history of cardiovascular disease"
    ],

    "important_warning_signs": [
        "Severe or persistent chest pain or pressure",
        "Difficulty breathing",
        "Sudden severe weakness",
        "Fainting or loss of consciousness",
        "Sudden difficulty speaking",
        "Sudden weakness or numbness, especially on one side of the body",
        "Blue lips or skin",
        "Severe palpitations with fainting or serious symptoms"
    ],

    "health_worker_actions": [
        "Ask about the person's symptoms, medical history, and known risk factors.",
        "Check available blood-pressure or other health records when appropriate.",
        "Encourage regular follow-up for people with known cardiovascular risk factors.",
        "Encourage tobacco cessation and a healthy lifestyle.",
        "Do not diagnose a heart condition based only on the AI response.",
        "Follow local clinical protocols for assessment and referral."
    ],

    "urgent_referral": """
Severe or persistent chest pain, serious difficulty breathing,
loss of consciousness, or sudden neurological symptoms can indicate
a medical emergency.

Arrange urgent medical evaluation and do not delay referral while
relying on an AI tool.
""",

    "prevention": [
        "Avoid tobacco use.",
        "Encourage a balanced diet with appropriate portions.",
        "Encourage regular physical activity when medically appropriate.",
        "Maintain a healthy body weight.",
        "Monitor blood pressure and blood sugar when indicated.",
        "Follow treatment and follow-up advice from qualified healthcare professionals."
    ],

    "safety_note": """
This information is for health education and frontline support only.
It does not provide a diagnosis or replace examination by a qualified
doctor, nurse, or other healthcare professional.

For suspected emergencies, seek urgent medical care.
Always follow current local and national clinical guidelines.
"""
}


def get_heart_health_knowledge():
    """Return the heart health knowledge base for Saathi."""
    return HEART_HEALTH
