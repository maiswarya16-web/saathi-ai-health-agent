# Saathi AI - Child Health Knowledge
# Source basis: WHO child health guidance

CHILD_HEALTH = {
    "overview": """
Child health support includes monitoring growth and development,
nutrition, immunization, hygiene, and early recognition of illness.
Young children can become seriously ill quickly, so warning signs
should be taken seriously.
""",

    "routine_care": [
        "Encourage age-appropriate breastfeeding and complementary feeding.",
        "Ensure the child receives recommended vaccinations.",
        "Monitor growth and development regularly.",
        "Encourage safe drinking water, sanitation, and hand hygiene.",
        "Keep the child's health and immunization records updated.",
        "Encourage parents or caregivers to seek medical advice when the child is unwell.",
        "Use medicines for children only according to advice from a qualified healthcare professional."
    ],

    "important_warning_signs": [
        "Difficulty breathing or very fast breathing",
        "Child is unconscious, unusually sleepy, or difficult to wake",
        "Convulsions or seizures",
        "Child is unable to drink or breastfeed",
        "Repeated vomiting",
        "Severe dehydration or very little urine",
        "Blue lips or blue skin",
        "Severe weakness or unusual behavior",
        "High fever with serious illness",
        "Severe bleeding"
    ],

    "health_worker_actions": [
        "Ask the caregiver about the child's symptoms and how long they have been present.",
        "Check the child's available health and immunization records.",
        "Observe the child's general condition.",
        "Follow local child-health assessment and referral protocols.",
        "Do not diagnose based only on the AI response.",
        "Refer children with danger signs promptly to an appropriate healthcare facility."
    ],

    "urgent_referral": """
Urgent medical evaluation is needed when a child has serious warning
signs such as difficulty breathing, convulsions, unconsciousness,
inability to drink or breastfeed, severe dehydration, blue lips or
skin, severe weakness, or other signs of serious illness.

Do not delay referral while relying on an AI tool.
""",

    "safety_note": """
This information is for health education and frontline support only.
It does not provide a diagnosis or replace examination by a qualified
doctor, nurse, pediatrician, or other healthcare professional.

Always follow current local and national child-health guidelines.
"""
}


def get_child_health_knowledge():
    """Return the child health knowledge base for Saathi."""
    return CHILD_HEALTH
