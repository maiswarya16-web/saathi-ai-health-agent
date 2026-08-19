# Saathi AI - Maternal Health Knowledge
# Source basis: WHO antenatal care guidance

MATERNAL_HEALTH = {
    "overview": """
Pregnancy requires regular antenatal care and monitoring by trained
health professionals. The purpose is to support the health of the
mother and baby, identify risks early, and arrange referral when needed.
""",

    "routine_care": [
        "Encourage regular antenatal care according to local health services.",
        "Keep records of antenatal visits, investigations, vaccinations, and other care received.",
        "Encourage a healthy and balanced diet during pregnancy.",
        "Encourage appropriate physical activity when medically suitable.",
        "Discuss tobacco, alcohol, and other substance use with a healthcare professional.",
        "Follow supplements and treatments prescribed by a qualified healthcare professional.",
        "Plan in advance for delivery and possible complications."
    ],

    "important_warning_signs": [
        "Vaginal bleeding",
        "Severe abdominal or stomach pain",
        "Severe headache, especially with vision problems",
        "Convulsions or seizures",
        "High fever with severe weakness or feeling very unwell",
        "Fast or difficult breathing",
        "Sudden or severe swelling of the face, hands, or legs",
        "Any other symptom that makes the woman seriously unwell"
    ],

    "health_worker_actions": [
        "Listen carefully to the woman's symptoms and concerns.",
        "Check available health records and antenatal information.",
        "Do not diagnose based only on the AI response.",
        "Follow the health worker's local clinical protocol.",
        "Refer the woman to an appropriate healthcare facility when warning signs or concerning symptoms are present.",
        "For severe or emergency symptoms, arrange urgent medical care."
    ],

    "urgent_referral": """
Urgent medical evaluation is needed when serious warning signs are
present, such as significant bleeding, convulsions, severe headache
with visual symptoms, severe abdominal pain, difficult breathing,
or severe illness.

The AI tool must not replace examination by a qualified healthcare
professional.
""",

    "safety_note": """
This information is for health education and frontline support only.
It does not provide a diagnosis or replace a doctor, nurse, midwife,
or other qualified healthcare professional.

Always follow current local and national clinical guidelines.
"""
}


def get_maternal_health_knowledge():
    """Return the maternal health knowledge base for Saathi."""
    return MATERNAL_HEALTH
