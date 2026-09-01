import re
import difflib
import streamlit as st
from google import genai
import sqlite3
from datetime import datetime

# =========================================================
# PATIENT DATABASE CONNECTION
# =========================================================

def get_db_connection():
    return sqlite3.connect(
        "saathi_patients.db",
        check_same_thread=False
    )

def get_patient_by_id(patient_id):

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            patient_id,
            patient_name,
            age,
            gender,
            village,
            created_at
        FROM patients
        WHERE patient_id = ?
        """,
        (patient_id,),
    )

    patient = cursor.fetchone()

    conn.close()

    return patient
    
# =========================================================
# CREATE PATIENT DATABASE TABLES
# =========================================================

def create_patient_database():

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS patients (
        patient_id TEXT PRIMARY KEY,
        patient_name TEXT NOT NULL,
        age INTEGER,
        gender TEXT,
        village TEXT,
        created_at TEXT
    )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS visits (
            visit_id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id TEXT,
            visit_date TEXT,
            complaint TEXT,
            temperature TEXT,
            blood_pressure TEXT,
            blood_sugar TEXT,
            weight TEXT,
            risk_level TEXT,
            notes TEXT
        )
    """)

    conn.commit()
    conn.close()


create_patient_database()
# =========================================================
# ADD NEW PATIENT
# =========================================================

def add_new_patient(
    patient_id,
    patient_name,
    age,
    gender,
    village
):

    conn = get_db_connection()
    cursor = conn.cursor()

    try:

        cursor.execute(
            """
            INSERT INTO patients (
                patient_id,
                patient_name,
                age,
                gender,
                village,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                patient_id,
                patient_name,
                age,
                gender,
                village,
                datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
            ),
        )

        conn.commit()
        return True, "Patient added successfully."

    except sqlite3.IntegrityError:

        return (
            False,
            "This Patient ID already exists."
        )

    finally:

        conn.close()

# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Saathi AI Health Agent",
    page_icon="🩺",
    layout="centered",
)

# =========================================================
# GEMINI CONFIGURATION
# =========================================================

MODEL_NAME = "gemini-3.6-flash"


@st.cache_resource
def get_gemini_client():
    return genai.Client(api_key=st.secrets["GEMINI_API_KEY"])


client = get_gemini_client()


def call_gemini(contents):
    return client.models.generate_content(
        model=MODEL_NAME,
        contents=contents,
    )


def classify_gemini_error(error):
    text = str(error)
    upper = text.upper()

    if (
        "429" in upper
        or "RESOURCE_EXHAUSTED" in upper
        or "RATE LIMIT" in upper
        or "QUOTA" in upper
        or "QUOTA_EXCEEDED" in upper
    ):
        return "limit", text

    if (
        "503" in upper
        or "UNAVAILABLE" in upper
        or "OVERLOADED" in upper
        or "SERVICE_UNAVAILABLE" in upper
        or "500" in upper
        or "502" in upper
        or "504" in upper
    ):
        return "temporary", text

    if "404" in upper or "MODEL_NOT_FOUND" in upper:
        return "model", text

    if "401" in upper or "403" in upper or "API KEY" in upper:
        return "auth", text

    return "other", text


def show_gemini_error(error):
    category, details = classify_gemini_error(error)

    if category == "limit":
        st.warning("⏳ Gemini API request limit reached.")
        st.info(
            "The local health red-flag checker still works. "
            "Please try again after the Gemini limit is available."
        )

    elif category == "temporary":
        st.warning("⚠️ Saathi's AI service is temporarily unavailable.")
        st.info("Please try again shortly.")

    elif category == "model":
        st.error(f"❌ Gemini model '{MODEL_NAME}' was not found.")

    elif category == "auth":
        st.error("❌ Gemini API authentication failed.")
        st.info("Check GEMINI_API_KEY in Streamlit Secrets.")

    else:
        st.error("❌ Saathi encountered a technical error.")

    with st.expander("Technical error details"):
        st.code(details)


# =========================================================
# MULTILINGUAL UI TEXT
# =========================================================

UI_TEXT = {
    "English": {
        "topic": "Select a health topic:",
        "question": "Ask Saathi a health-related question:",
        "placeholder": "Example: What warning signs should I look for during pregnancy?",
        "button": "Ask Saathi",
        "guidance": "🩺 Saathi's Guidance",
        "empty": "Please enter or speak a health question first.",
        "voice": "Record your question:",
        "voice_help": "Tap the microphone and speak your health question.",
    },

    "Hindi": {
        "topic": "स्वास्थ्य विषय चुनें:",
        "question": "साथी से स्वास्थ्य संबंधी प्रश्न पूछें:",
        "placeholder": "उदाहरण: गर्भावस्था के दौरान किन चेतावनी संकेतों पर ध्यान देना चाहिए?",
        "button": "साथी से पूछें",
        "guidance": "🩺 साथी की सलाह",
        "empty": "कृपया पहले अपना स्वास्थ्य संबंधी प्रश्न लिखें या बोलें।",
        "voice": "अपना प्रश्न रिकॉर्ड करें:",
        "voice_help": "माइक्रोफोन दबाकर अपना स्वास्थ्य प्रश्न बोलें।",
    },

    "Tamil": {
        "topic": "சுகாதார தலைப்பைத் தேர்ந்தெடுக்கவும்:",
        "question": "சாத்தியிடம் சுகாதார கேள்வியைக் கேளுங்கள்:",
        "placeholder": "உதாரணம்: கர்ப்ப காலத்தில் கவனிக்க வேண்டிய ஆபத்து அறிகுறிகள் என்ன?",
        "button": "சாத்தியிடம் கேளுங்கள்",
        "guidance": "🩺 சாத்தியின் வழிகாட்டுதல்",
        "empty": "முதலில் உங்கள் சுகாதார கேள்வியை எழுதவும் அல்லது பேசவும்.",
        "voice": "உங்கள் கேள்வியை பதிவு செய்யவும்:",
        "voice_help": "மைக்ரோஃபோனை அழுத்தி உங்கள் சுகாதார கேள்வியைப் பேசுங்கள்.",
    },

    "Telugu": {
        "topic": "ఆరోగ్య అంశాన్ని ఎంచుకోండి:",
        "question": "సాతీని ఆరోగ్య ప్రశ్న అడగండి:",
        "placeholder": "ఉదాహరణ: గర్భధారణ సమయంలో ఏ ప్రమాద సంకేతాలను గమనించాలి?",
        "button": "సాతీని అడగండి",
        "guidance": "🩺 సాతీ మార్గదర్శకం",
        "empty": "దయచేసి ముందుగా మీ ఆరోగ్య ప్రశ్నను రాయండి లేదా మాట్లాడండి.",
        "voice": "మీ ప్రశ్నను రికార్డ్ చేయండి:",
        "voice_help": "మైక్రోఫోన్ నొక్కి మీ ఆరోగ్య ప్రశ్నను మాట్లాడండి.",
    },

    "Malayalam": {
        "topic": "ആരോഗ്യ വിഷയം തിരഞ്ഞെടുക്കുക:",
        "question": "സാത്തിയോട് ആരോഗ്യ ചോദ്യം ചോദിക്കുക:",
        "placeholder": "ഉദാഹരണം: ഗർഭകാലത്ത് ശ്രദ്ധിക്കേണ്ട അപകട സൂചനകൾ എന്തൊക്കെയാണ്?",
        "button": "സാത്തിയോട് ചോദിക്കുക",
        "guidance": "🩺 സാത്തിയുടെ മാർഗനിർദ്ദേശം",
        "empty": "ദയവായി ആദ്യം നിങ്ങളുടെ ആരോഗ്യ ചോദ്യം എഴുതുകയോ സംസാരിക്കുകയോ ചെയ്യുക.",
        "voice": "നിങ്ങളുടെ ചോദ്യം റെക്കോർഡ് ചെയ്യുക:",
        "voice_help": "മൈക്രോഫോൺ അമർത്തി നിങ്ങളുടെ ആരോഗ്യ ചോദ്യം സംസാരിക്കുക.",
    },

    "Kannada": {
        "topic": "ಆರೋಗ್ಯ ವಿಷಯವನ್ನು ಆಯ್ಕೆಮಾಡಿ:",
        "question": "ಸಾಥಿಗೆ ಆರೋಗ್ಯ ಪ್ರಶ್ನೆಯನ್ನು ಕೇಳಿ:",
        "placeholder": "ಉದಾಹರಣೆ: ಗರ್ಭಾವಸ್ಥೆಯಲ್ಲಿ ಯಾವ ಅಪಾಯದ ಸೂಚನೆಗಳನ್ನು ಗಮನಿಸಬೇಕು?",
        "button": "ಸಾಥಿಯನ್ನು ಕೇಳಿ",
        "guidance": "🩺 ಸಾಥಿಯ ಮಾರ್ಗದರ್ಶನ",
        "empty": "ದಯವಿಟ್ಟು ಮೊದಲು ನಿಮ್ಮ ಆರೋಗ್ಯ ಪ್ರಶ್ನೆಯನ್ನು ಬರೆಯಿರಿ ಅಥವಾ ಮಾತನಾಡಿ.",
        "voice": "ನಿಮ್ಮ ಪ್ರಶ್ನೆಯನ್ನು ರೆಕಾರ್ಡ್ ಮಾಡಿ:",
        "voice_help": "ಮೈಕ್ರೋಫೋನ್ ಒತ್ತಿ ನಿಮ್ಮ ಆರೋಗ್ಯ ಪ್ರಶ್ನೆಯನ್ನು ಮಾತನಾಡಿ.",
    },

    "Bengali": {
        "topic": "স্বাস্থ্য বিষয় নির্বাচন করুন:",
        "question": "সাথীকে স্বাস্থ্য সম্পর্কিত প্রশ্ন করুন:",
        "placeholder": "উদাহরণ: গর্ভাবস্থায় কোন বিপদের লক্ষণগুলির দিকে নজর রাখা উচিত?",
        "button": "সাথীকে জিজ্ঞাসা করুন",
        "guidance": "🩺 সাথীর নির্দেশনা",
        "empty": "দয়া করে প্রথমে আপনার স্বাস্থ্য প্রশ্ন লিখুন বা বলুন।",
        "voice": "আপনার প্রশ্ন রেকর্ড করুন:",
        "voice_help": "মাইক্রোফোন টিপে আপনার স্বাস্থ্য প্রশ্ন বলুন।",
    },

    "Marathi": {
        "topic": "आरोग्य विषय निवडा:",
        "question": "साथीला आरोग्याशी संबंधित प्रश्न विचारा:",
        "placeholder": "उदाहरण: गर्भधारणेदरम्यान कोणती धोक्याची चिन्हे लक्षात घ्यावीत?",
        "button": "साथीला विचारा",
        "guidance": "🩺 साथीचे मार्गदर्शन",
        "empty": "कृपया प्रथम तुमचा आरोग्य प्रश्न लिहा किंवा बोला.",
        "voice": "तुमचा प्रश्न रेकॉर्ड करा:",
        "voice_help": "मायक्रोफोन दाबून तुमचा आरोग्य प्रश्न बोला.",
    },
}


LANGUAGES = list(UI_TEXT.keys())

language = st.selectbox(
    "🌐 Select your language:",
    LANGUAGES,
)

ui = UI_TEXT[language]


# =========================================================
# TITLE
# =========================================================

st.title("🩺 Saathi AI Health Agent")

st.write(
    "A digital health assistant designed to support "
    "frontline health workers such as ASHA and ANM workers."
)

st.info(
    "Saathi provides health information and referral guidance. "
    "It does not replace a qualified doctor or emergency medical service."
)


# =========================================================
# HEALTH TOPICS
# =========================================================

TOPIC_KEYS = [
    "Maternal Health",
    "Child Health",
    "Heart Health",
    "Kidney Health",
    "Skin Problems",
    "Diabetes",
    "Hypertension (High Blood Pressure)",
    "Fever & Infections",
    "Respiratory Problems",
    "Liver Health",
    "Eye Health",
    "Oral Health",
    "Nutrition",
    "Immunization",
    "Mental Wellbeing",
    "Women's Health",
    "Men's Health",
    "Elderly Health",
    "First Aid",
    "Emergency Situations",
    "General Symptoms",
]


TOPICS = {
    "English": TOPIC_KEYS,

    "Hindi": [
        "मातृ स्वास्थ्य",
        "बाल स्वास्थ्य",
        "हृदय स्वास्थ्य",
        "किडनी स्वास्थ्य",
        "त्वचा की समस्याएं",
        "मधुमेह",
        "उच्च रक्तचाप",
        "बुखार और संक्रमण",
        "श्वसन संबंधी समस्याएं",
        "यकृत स्वास्थ्य",
        "आंखों का स्वास्थ्य",
        "मुंह और दांतों का स्वास्थ्य",
        "पोषण",
        "टीकाकरण",
        "मानसिक स्वास्थ्य",
        "महिला स्वास्थ्य",
        "पुरुष स्वास्थ्य",
        "वृद्ध स्वास्थ्य",
        "प्राथमिक उपचार",
        "आपातकालीन स्थिति",
        "सामान्य लक्षण",
    ],

    "Tamil": [
        "தாய்மை நலம்",
        "குழந்தைகள் நலம்",
        "இதய நலம்",
        "சிறுநீரக நலம்",
        "தோல் பிரச்சினைகள்",
        "நீரிழிவு",
        "உயர் இரத்த அழுத்தம்",
        "காய்ச்சல் மற்றும் தொற்றுகள்",
        "சுவாச பிரச்சினைகள்",
        "கல்லீரல் நலம்",
        "கண் நலம்",
        "வாய் மற்றும் பல் நலம்",
        "ஊட்டச்சத்து",
        "தடுப்பூசி",
        "மனநலம்",
        "பெண்கள் நலம்",
        "ஆண்கள் நலம்",
        "முதியோர் நலம்",
        "முதலுதவி",
        "அவசர நிலை",
        "பொதுவான அறிகுறிகள்",
    ],

    "Telugu": [
        "మాతృ ఆరోగ్యం",
        "శిశు ఆరోగ్యం",
        "గుండె ఆరోగ్యం",
        "కిడ్నీ ఆరోగ్యం",
        "చర్మ సమస్యలు",
        "మధుమేహం",
        "అధిక రక్తపోటు",
        "జ్వరం మరియు ఇన్ఫెక్షన్లు",
        "శ్వాస సంబంధిత సమస్యలు",
        "కాలేయ ఆరోగ్యం",
        "కంటి ఆరోగ్యం",
        "నోటి మరియు దంత ఆరోగ్యం",
        "పోషణ",
        "టీకాలు",
        "మానసిక ఆరోగ్యం",
        "మహిళల ఆరోగ్యం",
        "పురుషుల ఆరోగ్యం",
        "వృద్ధుల ఆరోగ్యం",
        "ప్రథమ చికిత్స",
        "అత్యవసర పరిస్థితి",
        "సాధారణ లక్షణాలు",
    ],

    "Malayalam": [
        "മാതൃ ആരോഗ്യം",
        "കുട്ടികളുടെ ആരോഗ്യം",
        "ഹൃദയ ആരോഗ്യം",
        "വൃക്ക ആരോഗ്യം",
        "ചർമ്മ പ്രശ്നങ്ങൾ",
        "പ്രമേഹം",
        "ഉയർന്ന രക്തസമ്മർദ്ദം",
        "പനിയും അണുബാധകളും",
        "ശ്വാസകോശ പ്രശ്നങ്ങൾ",
        "കരൾ ആരോഗ്യം",
        "കണ്ണിന്റെ ആരോഗ്യം",
        "വായയും പല്ലുകളും",
        "പോഷണം",
        "പ്രതിരോധ കുത്തിവയ്പ്പ്",
        "മാനസിക ക്ഷേമം",
        "സ്ത്രീകളുടെ ആരോഗ്യം",
        "പുരുഷന്മാരുടെ ആരോഗ്യം",
        "മുതിർന്നവരുടെ ആരോഗ്യം",
        "പ്രഥമ ശുശ്രൂഷ",
        "അടിയന്തര സാഹചര്യം",
        "പൊതുവായ ലക്ഷണങ്ങൾ",
    ],

    "Kannada": [
        "ತಾಯಿಯ ಆರೋಗ್ಯ",
        "ಮಕ್ಕಳ ಆರೋಗ್ಯ",
        "ಹೃದಯದ ಆರೋಗ್ಯ",
        "ಮೂತ್ರಪಿಂಡದ ಆರೋಗ್ಯ",
        "ಚರ್ಮದ ಸಮಸ್ಯೆಗಳು",
        "ಮಧುಮೇಹ",
        "ಅಧಿಕ ರಕ್ತದೊತ್ತಡ",
        "ಜ್ವರ ಮತ್ತು ಸೋಂಕುಗಳು",
        "ಉಸಿರಾಟದ ಸಮಸ್ಯೆಗಳು",
        "ಯಕೃತ್ತಿನ ಆರೋಗ್ಯ",
        "ಕಣ್ಣಿನ ಆರೋಗ್ಯ",
        "ಬಾಯಿ ಮತ್ತು ಹಲ್ಲಿನ ಆರೋಗ್ಯ",
        "ಪೌಷ್ಟಿಕಾಂಶ",
        "ಲಸಿಕೆ",
        "ಮಾನಸಿಕ ಆರೋಗ್ಯ",
        "ಮಹಿಳೆಯರ ಆರೋಗ್ಯ",
        "ಪುರುಷರ ಆರೋಗ್ಯ",
        "ವಯೋವೃದ್ಧರ ಆರೋಗ್ಯ",
        "ಪ್ರಥಮ ಚಿಕಿತ್ಸೆ",
        "ತುರ್ತು ಪರಿಸ್ಥಿತಿ",
        "ಸಾಮಾನ್ಯ ಲಕ್ಷಣಗಳು",
    ],

    "Bengali": [
        "মাতৃস্বাস্থ্য",
        "শিশু স্বাস্থ্য",
        "হৃদযন্ত্রের স্বাস্থ্য",
        "কিডনি স্বাস্থ্য",
        "ত্বকের সমস্যা",
        "ডায়াবেটিস",
        "উচ্চ রক্তচাপ",
        "জ্বর ও সংক্রমণ",
        "শ্বাসযন্ত্রের সমস্যা",
        "লিভারের স্বাস্থ্য",
        "চোখের স্বাস্থ্য",
        "মুখ ও দাঁতের স্বাস্থ্য",
        "পুষ্টি",
        "টিকাদান",
        "মানসিক সুস্থতা",
        "নারী স্বাস্থ্য",
        "পুরুষ স্বাস্থ্য",
        "বয়স্কদের স্বাস্থ্য",
        "প্রাথমিক চিকিৎসা",
        "জরুরি পরিস্থিতি",
        "সাধারণ উপসর্গ",
    ],

    "Marathi": [
        "माता आरोग्य",
        "बाल आरोग्य",
        "हृदयाचे आरोग्य",
        "मूत्रपिंडाचे आरोग्य",
        "त्वचेच्या समस्या",
        "मधुमेह",
        "उच्च रक्तदाब",
        "ताप आणि संसर्ग",
        "श्वसनाच्या समस्या",
        "यकृताचे आरोग्य",
        "डोळ्यांचे आरोग्य",
        "तोंड आणि दातांचे आरोग्य",
        "पोषण",
        "लसीकरण",
        "मानसिक आरोग्य",
        "महिलांचे आरोग्य",
        "पुरुषांचे आरोग्य",
        "ज्येष्ठ नागरिकांचे आरोग्य",
        "प्रथमोपचार",
        "आपत्कालीन परिस्थिती",
        "सामान्य लक्षणे",
    ],
}


selected_topic_display = st.selectbox(
    ui["topic"],
    TOPICS[language],
)

topic_index = TOPICS[language].index(selected_topic_display)

topic = TOPIC_KEYS[topic_index]

# =========================================================
# PATIENT REGISTRATION
# =========================================================

st.markdown("## 👤 Patient Records")

with st.expander("➕ Add New Patient", expanded=False):

    new_patient_id = st.text_input(
        "Patient ID",
        key="new_patient_id"
    )

    new_patient_name = st.text_input(
        "Patient Name",
        key="new_patient_name"
    )

    new_patient_age = st.number_input(
        "Age",
        min_value=0,
        max_value=120,
        value=0,
        key="new_patient_age"
    )

    new_patient_gender = st.selectbox(
        "Gender",
        ["Select", "Female", "Male", "Other"],
        key="new_patient_gender"
    )

    new_patient_village = st.text_input(
        "Village / Area",
        key="new_patient_village"
    )

    if st.button(
        "💾 Save Patient",
        key="save_new_patient"
    ):

        if (
            not new_patient_id.strip()
            or not new_patient_name.strip()
        ):

            st.warning(
                "Please enter Patient ID and Patient Name."
            )

        else:

            success, message = add_new_patient(
                new_patient_id.strip(),
                new_patient_name.strip(),
                new_patient_age,
                new_patient_gender,
                new_patient_village.strip(),
            )

            if success:

                st.success(
                    "✅ Patient saved successfully!"
                )

            else:

                st.error(message)



# =========================================================
# CONSULTATION DETAILS
# =========================================================

st.subheader("👤 Consultation Details")

patient_id = st.text_input(
    "Patient ID for this consultation",
    placeholder="Example: P001",
)

patient_age = st.number_input(
    "Patient Age",
    min_value=0,
    max_value=120,
    value=0,
    step=1,
)

patient_gender = st.selectbox(
    "Patient Gender",
    [
        "Not specified",
        "Female",
        "Male",
        "Other",
    ],
)

patient_notes = st.text_area(
    "Relevant Patient Notes",
    placeholder=(
        "Example: History of diabetes, hypertension, pregnancy, etc."
    ),
    height=100,
)


# =========================================================
# TEXT QUESTION
# =========================================================

question = st.text_area(
    ui["question"],
    placeholder=ui["placeholder"],
    height=120,
)


# =========================================================
# VOICE INPUT
# =========================================================

st.subheader("🎤 Voice Input")

st.write(ui["voice_help"])

audio_value = st.audio_input(ui["voice"])


if "voice_question" not in st.session_state:
    st.session_state.voice_question = ""

if "last_audio_bytes" not in st.session_state:
    st.session_state.last_audio_bytes = None


new_audio_bytes = None


if audio_value is not None:
    try:
        candidate_audio = audio_value.getvalue()

        if (
            candidate_audio
            and candidate_audio != st.session_state.last_audio_bytes
        ):
            new_audio_bytes = candidate_audio

    except Exception:
        new_audio_bytes = None


# =========================================================
# RED-FLAG DETECTION DATA
# =========================================================

RED_FLAG_GROUPS = {

    "Possible heart emergency": [
        "heart attack",
        "heart pain",
        "severe chest pain",
        "chest pain",
        "pressure in chest",
        "pressure in the chest",
        "severe pressure in chest",
        "severe pressure in the chest",
        "chest pressure",
        "tightness in chest",
        "tightness in the chest",
        "crushing chest pain",
        "pain spreading to arm",
        "pain spreading to the arm",
        "pain spreading to jaw",
        "pain spreading to the jaw",
        "pain spreading to shoulder",
        "pain spreading to the shoulder",

        "दिल का दौरा",
        "हार्ट अटैक",
        "सीने में तेज दर्द",
        "सीने में दर्द",
        "सीने में दबाव",
        "सीने में जकड़न",
        "दर्द बांह तक",
        "दर्द हाथ तक",
        "दर्द जबड़े तक",
        "दर्द कंधे तक",

        "மாரடைப்பு",
        "மார்பில் கடுமையான வலி",
        "மார்பு வலி",
        "மார்பில் அழுத்தம்",
        "மார்பு இறுக்கம்",
        "கைக்கு பரவும் வலி",
        "தாடைக்கு பரவும் வலி",
        "தோளுக்கு பரவும் வலி",

        "గుండెపోటు",
        "హార్ట్ అటాక్",
        "తీవ్రమైన ఛాతీ నొప్పి",
        "ఛాతీ నొప్పి",
        "ఛాతీలో ఒత్తిడి",
        "చేతికి వ్యాపించే నొప్పి",
        "దవడకు వ్యాపించే నొప్పి",
        "భుజానికి వ్యాపించే నొప్పి",

        "ഹൃദയാഘാതം",
        "ഹാർട്ട് അറ്റാക്ക്",
        "കടുത്ത നെഞ്ചുവേദന",
        "നെഞ്ചുവേദന",
        "നെഞ്ചിൽ സമ്മർദ്ദം",
        "കൈയിലേക്ക് പടരുന്ന വേദന",
        "താടിയിലേക്ക് പടരുന്ന വേദന",
        "തോളിലേക്ക് പടരുന്ന വേദന",

        "ಹೃದಯಾಘಾತ",
        "ಹಾರ್ಟ್ ಅಟ್ಯಾಕ್",
        "ತೀವ್ರವಾದ ಎದೆ ನೋವು",
        "ಎದೆ ನೋವು",
        "ಎದೆಯಲ್ಲಿ ಒತ್ತಡ",
        "ತೋಳಿಗೆ ಹರಡುವ ನೋವು",
        "ದವಡೆಗೆ ಹರಡುವ ನೋವು",
        "ಭುಜಕ್ಕೆ ಹರಡುವ ನೋವು",

        "হার্ট অ্যাটাক",
        "তীব্র বুক ব্যথা",
        "বুকে ব্যথা",
        "বুকে চাপ",
        "হাতে ছড়িয়ে পড়া ব্যথা",
        "চোয়ালে ছড়িয়ে পড়া ব্যথা",
        "কাঁধে ছড়িয়ে পড়া ব্যথা",

        "हृदयविकाराचा झटका",
        "हार्ट अटॅक",
        "तीव्र छातीत दुखणे",
        "छातीत दुखणे",
        "छातीत दाब",
        "हाताकडे पसरणारी वेदना",
        "जबड्याकडे पसरणारी वेदना",
        "खांद्याकडे पसरणारी वेदना",
    ],

    "Possible stroke / brain emergency": [
        "stroke",
        "signs of stroke",
        "face drooping",
        "slurred speech",
        "difficulty speaking",
        "cannot speak",
        "sudden weakness",
        "sudden numbness",
        "one sided weakness",
        "paralysis",
        "sudden confusion",
        "sudden severe headache",
        "worst headache",

        "स्ट्रोक",
        "लकवा",
        "चेहरा टेढ़ा",
        "बोलने में दिक्कत",
        "अचानक कमजोरी",

        "பக்கவாதம்",
        "முகம் கோணல்",
        "பேசுவதில் சிரமம்",
        "திடீர் பலவீனம்",
        "ஸ்ட்ரோக்",

        "స్ట్రోక్",
        "పక్షవాతం",
        "మాట్లాడటంలో ఇబ్బంది",
        "ఆకస్మిక బలహీనత",

        "പക്ഷാഘാതം",
        "സംസാരിക്കാൻ ബുദ്ധിമുട്ട്",
        "പെട്ടെന്നുള്ള ബലഹീനത",

        "ಪಾರ್ಶ್ವವಾಯು",
        "ಮಾತನಾಡಲು ತೊಂದರೆ",
        "ಹಠಾತ್ ದೌರ್ಬಲ್ಯ",

        "পক্ষাঘাত",
        "স্ট্রোক",
        "কথা বলতে অসুবিধা",
        "হঠাৎ দুর্বলতা",

        "स्ट्रोक",
        "पक्षाघात",
        "बोलताना त्रास",
        "अचानक अशक्तपणा",
    ],

    "Severe breathing emergency": [
        "difficulty breathing",
        "severe difficulty breathing",
        "shortness of breath",
        "cannot breathe",
        "can't breathe",
        "breathing stopped",
        "not breathing",
        "blue lips",
        "blue skin",
        "choking",

        "सांस लेने में कठिनाई",
        "सांस लेने में दिक्कत",
        "सांस नहीं आ रही",
        "सांस नहीं ले पा रहा",
        "होंठ नीले",
        "त्वचा नीली",

        "மூச்சு விட முடியவில்லை",
        "சுவாசிப்பதில் சிரமம்",
        "மூச்சு விடுவதில் சிரமம்",

        "శ్వాస తీసుకోవడంలో ఇబ్బంది",
        "ఊపిరి తీసుకోలేకపోతున్నాను",

        "ശ്വസിക്കാൻ ബുദ്ധിമുട്ട്",
        "ശ്വാസം എടുക്കാൻ കഴിയുന്നില്ല",

        "ಉಸಿರಾಟದ ತೊಂದರೆ",
        "ಉಸಿರಾಡಲು ಸಾಧ್ಯವಾಗುತ್ತಿಲ್ಲ",

        "শ্বাস নিতে অসুবিধা",
        "শ্বাস নিতে পারছি না",

        "श्वास घेण्यास त्रास",
        "श्वास घेता येत नाही",
    ],

    "Severe bleeding / internal bleeding": [
        "severe bleeding",
        "heavy bleeding",
        "bleeding heavily",
        "uncontrolled bleeding",
        "bleeding won't stop",
        "bleeding does not stop",
        "bleeding is not stopping",
        "the bleeding won't stop",
        "the bleeding does not stop",
        "the bleeding is not stopping",
        "wound is bleeding heavily",
        "wound is bleeding and won't stop",
        "wound is bleeding and does not stop",
        "cut is bleeding heavily",
        "cut is bleeding and won't stop",
        "blood won't stop",
        "blood is not stopping",
        "continuous bleeding",
        "profuse bleeding",
        "vomiting blood",
        "coughing blood",
        "blood in vomit",
        "blood in stool",
        "black stool",

        "बहुत ज्यादा खून बहना",
        "तेज रक्तस्राव",
        "खून नहीं रुक रहा",
        "खून की उल्टी",
        "खून की खांसी",
        "मल में खून",
        "काला मल",

        "கடுமையான இரத்தப்போக்கு",
        "அதிக இரத்தப்போக்கு",
        "இரத்தம் நிற்கவில்லை",
        "இரத்த வாந்தி",
        "இரத்தம் இருமல்",
        "மலத்தில் இரத்தம்",
        "கருப்பு மலம்",

        "తీవ్రమైన రక్తస్రావం",
        "ఎక్కువ రక్తస్రావం",
        "రక్తస్రావం ఆగడం లేదు",
        "రక్తం వాంతి",
        "రక్తం దగ్గు",
        "మలంలో రక్తం",
        "నల్ల మలం",

        "കടുത്ത രക്തസ്രാവം",
        "അമിതമായ രക്തസ്രാവം",
        "രക്തം നിൽക്കുന്നില്ല",
        "രക്തം ഛർദ്ദിക്കുക",
        "രക്തം ചുമയ്ക്കുക",
        "മലത്തിൽ രക്തം",
        "കറുത്ത മലം",

        "ತೀವ್ರ ರಕ್ತಸ್ರಾವ",
        "ಹೆಚ್ಚಿನ ರಕ್ತಸ್ರಾವ",
        "ರಕ್ತಸ್ರಾವ ನಿಲ್ಲುತ್ತಿಲ್ಲ",
        "ರಕ್ತ ವಾಂತಿ",
        "ರಕ್ತ ಕೆಮ್ಮು",
        "ಮಲದಲ್ಲಿ ರಕ್ತ",
        "ಕಪ್ಪು ಮಲ",

        "তীব্র রক্তপাত",
        "অতিরিক্ত রক্তপাত",
        "রক্তপাত বন্ধ হচ্ছে না",
        "রক্ত বমি",
        "রক্ত কাশি",
        "পায়খানায় রক্ত",
        "কালো পায়খানা",

        "तीव्र रक्तस्त्राव",
        "जास्त रक्तस्त्राव",
        "रक्तस्त्राव थांबत नाही",
        "रक्ताची उलटी",
        "मलात रक्त",
        "काळा मल",
    ],

    "Unconsciousness / seizure": [
        "unconscious",
        "loss of consciousness",
        "not responding",
        "unresponsive",
        "seizure",
        "convulsion",
        "fainted and not waking",
        "not waking",

        "बेहोश",
        "होश नहीं है",
        "जवाब नहीं दे रहा",
        "दौरा",
        "दौरे",

        "நினைவிழந்த",
        "சுயநினைவு இல்லை",
        "வலிப்பு",

        "స్పృహ కోల్పోవడం",
        "స్పృహలో లేరు",
        "స్పందించడం లేదు",
        "మూర్ఛ",

        "ബോധരഹിതൻ",
        "ബോധം നഷ്ടപ്പെടൽ",
        "പ്രതികരിക്കുന്നില്ല",
        "അപസ്മാരം",

        "ಪ್ರಜ್ಞಾಹೀನ",
        "ಪ್ರಜ್ಞೆ ಕಳೆದುಕೊಳ್ಳುವುದು",
        "ಪ್ರತಿಕ್ರಿಯಿಸುತ್ತಿಲ್ಲ",
        "ಅಪಸ್ಮಾರ",

        "অজ্ঞান",
        "চেতনা হারানো",
        "সাড়া দিচ্ছে না",
        "খিঁচুনি",

        "बेशुद्ध",
        "शुद्ध हरपणे",
        "प्रतिसाद देत नाही",
        "फिट",
    ],

    "Severe allergic reaction": [
        "anaphylaxis",
        "severe allergic reaction",
        "throat swelling",
        "swelling of throat",
        "swelling of face",
        "cannot swallow",

        "गंभीर एलर्जी",
        "गला सूजना",
        "चेहरा सूजना",

        "கடுமையான ஒவ்வாமை",
        "தொண்டை வீக்கம்",
        "முகம் வீக்கம்",

        "తీవ్రమైన అలెర్జీ",
        "గొంతు వాపు",
        "ముఖం వాపు",

        "ഗുരുതരമായ അലർജി",
        "തൊണ്ട വീക്കം",
        "മുഖം വീക്കം",

        "ತೀವ್ರ ಅಲರ್ಜಿ",
        "ಗಂಟಲಿನ ಊತ",
        "ಮುಖದ ಊತ",

        "তীব্র অ্যালার্জি",
        "গলা ফুলে যাওয়া",
        "মুখ ফুলে যাওয়া",

        "गंभीर ऍलर्जी",
        "घशावर सूज",
        "चेहऱ्यावर सूज",
    ],

    "Severe abdominal / surgical emergency": [
        "severe abdominal pain",
        "severe stomach pain",
        "severe belly pain",
        "rigid abdomen",
        "severe abdominal swelling",

        "पेट में तेज दर्द",
        "बहुत तेज पेट दर्द",

        "வயிற்றில் கடுமையான வலி",
        "கடுமையான வயிற்றுவலி",

        "తీవ్రమైన కడుపు నొప్పి",

        "കടുത്ത വയറുവേദന",

        "ತೀವ್ರ ಹೊಟ್ಟೆ ನೋವು",

        "তীব্র পেট ব্যথা",

        "तीव्र पोटदुखी",
    ],

    "Severe headache / brain warning": [
        "severe headache",
        "worst headache",
        "sudden severe headache",
        "thunderclap headache",

        "बहुत तेज सिरदर्द",
        "अचानक बहुत तेज सिरदर्द",

        "கடுமையான தலைவலி",
        "திடீர் கடுமையான தலைவலி",

        "తీవ్రమైన తలనొప్పి",
        "ఆకస్మిక తీవ్రమైన తలనొప్పి",

        "കടുത്ത തലവേദന",

        "ತೀವ್ರ ತಲೆನೋವು",

        "তীব্র মাথাব্যথা",

        "तीव्र डोकेदुखी",
    ],

    "Poisoning / envenomation": [
        "poisoning",
        "poison",
        "overdose",
        "chemical poisoning",
        "snake bite",
        "snakebite",
        "scorpion sting",

        "जहर",
        "जहर पी लिया",
        "सांप ने काटा",
        "बिच्छू ने काटा",

        "விஷம்",
        "பாம்பு கடி",
        "தேள் கடி",

        "విషం",
        "పాము కాటు",
        "తేలు కాటు",

        "വിഷബാധ",
        "പാമ്പുകടി",
        "തേൾ കുത്ത്",

        "ವಿಷ",
        "ಹಾವು ಕಡಿತ",
        "ಚೇಳಿನ ಕಚ್ಚು",

        "বিষক্রিয়া",
        "সাপের কামড়",
        "বিছার কামড়",

        "विषबाधा",
        "साप चावणे",
        "विंचू दंश",
    ],

    "Severe dehydration / heat emergency": [
        "severe dehydration",
        "cannot keep fluids down",
        "no urine",
        "heat stroke",
        "heatstroke",
        "severe heat exhaustion",

        "गंभीर निर्जलीकरण",
        "पेशाब नहीं हो रहा",
        "लू लगना",

        "கடுமையான நீரிழப்பு",
        "சிறுநீர் வரவில்லை",
        "வெப்ப அதிர்ச்சி",

        "తీవ్రమైన డీహైడ్రేషన్",
        "మూత్రం రావడం లేదు",
        "హీట్ స్ట్రోక్",

        "കടുത്ത നിർജ്ജലീകരണം",
        "മൂത്രമില്ല",
        "ഹീറ്റ് സ്ട്രോക്ക്",

        "ತೀವ್ರ ನಿರ್ಜಲೀಕರಣ",
        "ಮೂತ್ರ ಬರುತ್ತಿಲ್ಲ",
        "ಹೀಟ್ ಸ್ಟ್ರೋಕ್",

        "তীব্র পানিশূন্যতা",
        "প্রস্রাব হচ্ছে না",
        "হিট স্ট্রোক",

        "तीव्र निर्जलीकरण",
        "लघवी होत नाही",
        "उष्माघात",
    ],

    "Serious injury / burns / electric shock": [
        "severe burn",
        "major burn",
        "deep burn",
        "electric shock",
        "serious head injury",
        "head injury with loss of consciousness",
        "major trauma",
        "badly burned",
        "burn is deep", 
        "severe injury",

        "गंभीर जलना",
        "बिजली का झटका",
        "सिर पर गंभीर चोट",
        "गंभीर चोट",

        "கடுமையான தீக்காயம்",
        "மின்சார அதிர்ச்சி",
        "கடுமையான காயம்",

        "తీవ్రమైన కాలిన గాయం",
        "విద్యుత్ షాక్",
        "తీవ్రమైన గాయం",

        "ഗുരുതരമായ പൊള്ളൽ",
        "വൈദ്യുതാഘാതം",
        "ഗുരുതരമായ പരിക്ക്",

        "ತೀವ್ರ ಸುಟ್ಟ ಗಾಯ",
        "ವಿದ್ಯುತ್ ಆಘಾತ",
        "ತೀವ್ರ ಗಾಯ",

        "গুরুতর পোড়া",
        "বৈদ্যুতিক শক",
        "গুরুতর আঘাত",

        "गंभीर भाजणे",
        "वीज लागणे",
        "गंभीर दुखापत",
    ],

    "Pregnancy / newborn emergency": [
        "pregnancy bleeding",
        "heavy bleeding during pregnancy",
        "severe pregnancy pain",
        "seizure during pregnancy",
        "pregnancy seizure",
        "baby not moving",
        "difficult to wake up",
        "baby movement stopped",
        "child is unable to drink",
        "newborn not breathing",
        "child not breathing",
        "pregnant and unconscious",
        "water broke with bleeding",

        "गर्भावस्था में रक्तस्राव",
        "गर्भावस्था में तेज दर्द",
        "गर्भ में बच्चा नहीं हिल रहा",
        "गर्भावस्था में दौरा",

        "கர்ப்ப கால இரத்தப்போக்கு",
        "கர்ப்ப கால கடுமையான வலி",
        "குழந்தை அசைவில்லை",
        "பிறந்த குழந்தை மூச்சுவிடவில்லை",

        "గర్భధారణలో రక్తస్రావం",
        "గర్భధారణలో తీవ్రమైన నొప్పి",
        "బిడ్డ కదలడం లేదు",
        "నవజాత శిశువు శ్వాస తీసుకోవడం లేదు",

        "ഗർഭകാല രക്തസ്രാവം",
        "ഗർഭകാല കടുത്ത വേദന",
        "കുഞ്ഞ് ചലിക്കുന്നില്ല",
        "നവജാത ശിശു ശ്വസിക്കുന്നില്ല",

        "ಗರ್ಭಾವಸ್ಥೆಯಲ್ಲಿ ರಕ್ತಸ್ರಾವ",
        "ಗರ್ಭಾವಸ್ಥೆಯಲ್ಲಿ ತೀವ್ರ ನೋವು",
        "ಮಗು ಚಲಿಸುತ್ತಿಲ್ಲ",
        "ನವಜಾತ ಶಿಶು ಉಸಿರಾಡುತ್ತಿಲ್ಲ",

        "গর্ভাবস্থায় রক্তপাত",
        "গর্ভাবস্থায় তীব্র ব্যথা",
        "শিশু নড়ছে না",
        "নবজাতক শ্বাস নিচ্ছে না",

        "गर्भावस्थेत रक्तस्त्राव",
        "गर्भावस्थेत तीव्र वेदना",
        "बाळाची हालचाल नाही",
        "नवजात बाळ श्वास घेत नाही",
    ],

    "Mental health crisis": [
        "suicidal",
        "suicide",
        "suicidal thoughts",
        "want to die",
        "self harm",
        "self-harm",
        "kill myself",
        "harm myself",

        "आत्महत्या",
        "आत्महत्या के विचार",
        "खुद को नुकसान",
        "मरना चाहता हूं",

        "தற்கொலை",
        "தற்கொலை எண்ணம்",
        "சுய காயம்",

        "ఆత్మహత్య",
        "ఆత్మహత్య ఆలోచనలు",
        "స్వీయ హాని",

        "ആത്മഹത്യ",
        "ആത്മഹത്യ ചിന്തകൾ",
        "സ്വയം ഉപദ്രവിക്കൽ",

        "ಆತ್ಮಹತ್ಯೆ",
        "ಆತ್ಮಹತ್ಯೆ ಆಲೋಚನೆಗಳು",
        "ಸ್ವಯಂ ಹಾನಿ",

        "আত্মহত্যা",
        "আত্মহত্যার চিন্তা",
        "নিজেকে আঘাত করা",

        "आत्महत्या",
        "आत्महत्येचे विचार",
        "स्वतःला इजा करणे",
    ],
}


# =========================================================
# ADDITIONAL RED FLAG GROUPS
# =========================================================

RED_FLAG_GROUPS.update({

    "Possible severe infection / sepsis": [
        "sepsis",
        "septic shock",
        "very confused with fever",
        "confusion with fever",
        "rapid breathing with fever",
        "very sick with fever",

        "बहुत तेज बुखार और भ्रम",
        "बुखार के साथ बेहोशी",

        "காய்ச்சலுடன் குழப்பம்",
        "காய்ச்சலுடன் மயக்கம்",

        "జ్వరంతో గందరగోళం",
        "జ్వరంతో అపస్మారం",

        "പനിയോടൊപ്പം ആശയക്കുഴപ്പം",
        "പനിയോടൊപ്പം ബോധക്ഷയം",

        "ಜ್ವರದೊಂದಿಗೆ ಗೊಂದಲ",
        "ಜ್ವರದೊಂದಿಗೆ ಪ್ರಜ್ಞಾಹೀನತೆ",

        "জ্বরের সঙ্গে বিভ্রান্তি",
        "জ্বরের সঙ্গে অজ্ঞান",

        "तापासोबत गोंधळ",
        "तापासोबत बेशुद्ध",
    ],

    "Possible diabetic emergency": [
        "severe low blood sugar",
        "very low blood sugar",
        "hypoglycemia with unconsciousness",
        "diabetic coma",
        "very high blood sugar with vomiting",

        "मधुमेह में बेहोशी",
        "बहुत कम शुगर",
        "बहुत ज्यादा शुगर और उल्टी",

        "நீரிழிவு மயக்கம்",
        "மிகக் குறைந்த சர்க்கரை",

        "చాలా తక్కువ షుగర్",
        "మధుమేహంలో స్పృహ కోల్పోవడం",

        "വളരെ കുറഞ്ഞ പഞ്ചസാര",
        "പ്രമേഹത്തിൽ ബോധക്ഷയം",

        "ತುಂಬಾ ಕಡಿಮೆ ಸಕ್ಕರೆ",
        "ಮಧುಮೇಹದಲ್ಲಿ ಪ್ರಜ್ಞಾಹೀನತೆ",

        "খুব কম শর্করা",
        "ডায়াবেটিসে অজ্ঞান",

        "खूप कमी साखर",
        "मधुमेहात बेशुद्ध",
    ],

    "Possible hypertensive emergency": [
        "very high blood pressure with chest pain",
        "very high blood pressure with severe headache",
        "high bp with chest pain",
        "high bp with weakness",

        "बहुत ज्यादा रक्तचाप और सीने में दर्द",
        "बहुत ज्यादा बीपी और तेज सिरदर्द",

        "மிகவும் அதிக இரத்த அழுத்தம் மற்றும் மார்பு வலி",

        "అధిక బీపీతో ఛాతీ నొప్పి",
        "అధిక బీపీతో తీవ్రమైన తలనొప్పి",

        "വളരെ ഉയർന്ന രക്തസമ്മർദ്ദവും നെഞ്ചുവേദനയും",

        "ಅತಿ ಹೆಚ್ಚು ರಕ್ತದೊತ್ತಡ ಮತ್ತು ಎದೆ ನೋವು",

        "খুব বেশি রক্তচাপ ও বুক ব্যথা",

        "खूप जास्त रक्तदाब आणि छातीत दुखणे",
    ],

    "Possible severe asthma / airway emergency": [
        "severe asthma attack",
        "asthma attack cannot speak",
        "wheezing and cannot breathe",
        "breathing too difficult to speak",

        "गंभीर अस्थमा का दौरा",
        "अस्थमा में सांस नहीं आ रही",

        "கடுமையான ஆஸ்துமா",
        "ஆஸ்துமாவில் மூச்சு வரவில்லை",

        "తీవ్రమైన ఆస్తమా",
        "ఆస్తమాలో శ్వాస రావడం లేదు",

        "ഗുരുതരമായ ആസ്ത്മ",
        "ആസ്ത്മയിൽ ശ്വാസം കിട്ടുന്നില്ല",

        "ತೀವ್ರ ಆಸ್ತಮಾ",
        "ಆಸ್ತಮಾದಲ್ಲಿ ಉಸಿರಾಟ ಆಗುತ್ತಿಲ್ಲ",

        "তীব্র হাঁপানি",
        "হাঁপানিতে শ্বাস নিতে পারছি না",

        "तीव्र दमा",
        "दम्यामध्ये श्वास घेता येत नाही",
    ],

    "Possible meningitis / serious brain infection": [
        "stiff neck with fever",
        "fever and stiff neck",
        "severe headache with stiff neck",

        "बुखार और गर्दन अकड़ना",
        "तेज सिरदर्द और गर्दन अकड़ना",

        "காய்ச்சல் மற்றும் கழுத்து விறைப்பு",
        "கடுமையான தலைவலி மற்றும் கழுத்து விறைப்பு",

        "జ్వరం మరియు మెడ బిగుతు",
        "తీవ్రమైన తలనొప్పి మరియు మెడ బిగుతు",

        "പനിയും കഴുത്ത് മുറുക്കവും",
        "കടുത്ത തലവേദനയും കഴുത്ത് മുറുക്കവും",

        "ಜ್ವರ ಮತ್ತು ಕುತ್ತಿಗೆ ಬಿಗಿತ",
        "ತೀವ್ರ ತಲೆನೋವು ಮತ್ತು ಕುತ್ತಿಗೆ ಬಿಗಿತ",

        "জ্বর ও ঘাড় শক্ত হয়ে যাওয়া",
        "তীব্র মাথাব্যথা ও ঘাড় শক্ত",

        "ताप आणि मान आखडणे",
        "तीव्र डोकेदुखी आणि मान आखडणे",
    ],

    "Possible kidney / urinary emergency": [
        "no urine",
        "unable to pass urine",
        "severe flank pain with fever",
        "severe kidney pain with fever",

        "पेशाब बिल्कुल नहीं हो रहा",
        "बुखार के साथ तेज कमर दर्द",

        "சிறுநீர் வரவில்லை",
        "காய்ச்சலுடன் கடுமையான இடுப்பு வலி",

        "మూత్రం రావడం లేదు",
        "జ్వరంతో తీవ్రమైన నడుము నొప్పి",

        "മൂത്രമില്ല",
        "പനിയോടൊപ്പം കടുത്ത പാർശ്വ വേദന",

        "ಮೂತ್ರ ಬರುತ್ತಿಲ್ಲ",
        "ಜ್ವರದೊಂದಿಗೆ ತೀವ್ರ ಸೊಂಟ ನೋವು",

        "প্রস্রাব হচ্ছে না",
        "জ্বরের সঙ্গে তীব্র কোমর ব্যথা",

        "लघवी होत नाही",
        "तापासोबत तीव्र कंबरदुखी",
    ],

    "Possible eye emergency": [
        "sudden loss of vision",
        "sudden blindness",
        "chemical in eye with severe pain",

        "अचानक दिखाई नहीं दे रहा",
        "अचानक दृष्टि चली गई",

        "திடீரென பார்வை இழப்பு",
        "திடீரென பார்வை தெரியவில்லை",

        "అకస్మాత్తుగా చూపు పోయింది",
        "అకస్మాత్తుగా కనిపించడం లేదు",

        "പെട്ടെന്ന് കാഴ്ച നഷ്ടപ്പെട്ടു",
        "പെട്ടെന്ന് കാണുന്നില്ല",

        "ಹಠಾತ್ ದೃಷ್ಟಿ ಕಳೆದುಕೊಂಡಿತು",
        "ಹಠಾತ್ ಕಾಣುತ್ತಿಲ್ಲ",

        "হঠাৎ দৃষ্টি হারানো",
        "হঠাৎ দেখতে পাচ্ছে না",

        "अचानक दृष्टी गेली",
        "अचानक दिसत नाही",
    ],
})


# =========================================================
# FUZZY RED FLAGS
# =========================================================

FUZZY_RED_FLAGS = [
    "heart attack",
    "stroke",
    "anaphylaxis",
    "severe bleeding",
    "cannot breathe",
    "severe difficulty breathing",
    "unconscious",
    "seizure",
    "poisoning",
    "snake bite",
    "heat stroke",
    "suicide",
    "self harm",
    "severe burn",
    "electric shock",
    "pregnancy bleeding",
    "baby not breathing",
]


# =========================================================
# TEXT NORMALIZATION
# =========================================================

def normalize_text(text):
    text = str(text).lower().replace("’", "'")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def collapse_repeated_letters(text):
    return re.sub(
        r"(.)\1{1,}",
        r"\1",
        normalize_text(text),
    )


# =========================================================
# MULTILINGUAL EMERGENCY PATTERN DETECTION
# =========================================================

def detect_multilingual_emergency_patterns(text):

    if not text:
        return []

    normalized = normalize_text(text)
    detected = []

    def has_any(words):
        return any(
            normalize_text(word) in normalized
            for word in words
        )

    # -----------------------------------------------------
    # SEVERE BLEEDING
    # -----------------------------------------------------

    bleeding = [
        "bleeding",
        "blood",
        "bleed",
        "खून",
        "रक्तस्राव",
        "இரத்தம்",
        "ரத்தம்",
        "రక్తం",
        "രക്തം",
        "ರಕ್ತ",
        "রক্ত",
        "रक्त",
    ]

    heavy_bleeding = [
        "heavy",
        "heavily",
        "severe",
        "a lot",
        "won't stop",
        "does not stop",
        "not stopping",
        "continuous",
        "uncontrolled",
        "profuse",

        "बहुत ज्यादा",
        "तेज",
        "नहीं रुक",

        "அதிக",
        "நிற்கவில்லை",
        "நிறுத்த முடியவில்லை",

        "ఎక్కువ",
        "ఆగడం లేదు",

        "അമിതമായ",
        "നിൽക്കുന്നില്ല",

        "ಹೆಚ್ಚಿನ",
        "ನಿಲ್ಲುತ್ತಿಲ್ಲ",

        "অতিরিক্ত",
        "বন্ধ হচ্ছে না",

        "जास्त",
        "थांबत नाही",
    ]

    if has_any(bleeding) and has_any(heavy_bleeding):
        detected.append(
            (
                "Severe bleeding / internal bleeding",
                ["possible severe/heavy bleeding"],
            )
        )

    # -----------------------------------------------------
    # HEART EMERGENCY
    # -----------------------------------------------------

    chest = [
        "chest",
        "heart",
        "सीना",
        "सीने",
        "दिल",
        "மார்பு",
        "இதயம்",
        "ఛాతీ",
        "గుండె",
        "നെഞ്ച്",
        "ഹൃദയം",
        "ಎದೆ",
        "ಹೃದಯ",
        "বুক",
        "হৃদয়",
        "छाती",
        "हृदय",
    ]

    severe_chest = [
        "pain",
        "pressure",
        "tightness",
        "crushing",
        "severe",
        "heavy",
        "squeezing",

        "दर्द",
        "दबाव",
        "जकड़न",
        "तेज",

        "வலி",
        "அழுத்தம்",
        "இறுக்கம்",
        "கடுமையான",

        "నొప్పి",
        "ఒత్తిడి",
        "బిగుతు",
        "తీవ్రమైన",

        "വേദന",
        "സമ്മർദ്ദം",
        "മുറുക്കം",
        "കടുത്ത",

        "ನೋವು",
        "ಒತ್ತಡ",
        "ಬಿಗಿತ",
        "ತೀವ್ರ",

        "ব্যথা",
        "চাপ",
        "টান",
        "তীব্র",

        "वेदना",
        "दाब",
        "घट्टपणा",
        "तीव्र",
    ]

    spreading_pain = [
        "arm",
        "jaw",
        "shoulder",

        "बांह",
        "हाथ",
        "जबड़ा",
        "कंधा",

        "கை",
        "தாடை",
        "தோள்",

        "చేయి",
        "దవడ",
        "భుజం",

        "കൈ",
        "താടി",
        "തോൾ",

        "ತೋಳು",
        "ದವಡೆ",
        "ಭುಜ",

        "হাত",
        "চোয়াল",
        "কাঁধ",

        "हात",
        "जबडा",
        "खांदा",
    ]

    if has_any(chest) and has_any(severe_chest):
        detected.append(
            (
                "Possible heart emergency",
                ["possible severe chest/heart symptoms"],
            )
        )

    elif has_any(chest) and has_any(spreading_pain):
        detected.append(
            (
                "Possible heart emergency",
                ["possible pain spreading to arm/jaw/shoulder"],
            )
        )

    # -----------------------------------------------------
    # BREATHING EMERGENCY
    # -----------------------------------------------------

    breathing = [
        "breathing",
        "breathe",
        "breath",
        "सांस",
        "श्वास",
        "மூச்சு",
        "சுவாசம்",
        "శ్వాస",
        "ఊపిరి",
        "ശ്വാസം",
        "ശ്വസനം",
        "ಉಸಿರು",
        "ಉಸಿರಾಟ",
        "শ্বাস",
    ]

    breathing_danger = [
        "cannot",
        "can't",
        "difficulty",
        "difficult",
        "struggling",
        "stopped",
        "not",

        "नहीं",
        "मुश्किल",
        "दिक्कत",

        "முடியவில்லை",
        "சிரமம்",

        "లేకపోతున్న",
        "ఇబ్బంది",

        "കഴിയുന്നില്ല",
        "ബുദ്ധിമുട്ട്",

        "ಆಗುತ್ತಿಲ್ಲ",
        "ತೊಂದರೆ",

        "পারছি না",
        "অসুবিধা",

        "जमत नाही",
        "त्रास",
    ]

    if has_any(breathing) and has_any(breathing_danger):
        detected.append(
            (
                "Severe breathing emergency",
                ["possible severe breathing difficulty"],
            )
        )

    # -----------------------------------------------------
    # UNCONSCIOUSNESS
    # -----------------------------------------------------

    unconscious = [
        "unconscious",
        "unresponsive",
        "not responding",
        "not waking",
        "fainted",

        "बेहोश",
        "होश नहीं",
        "जवाब नहीं",

        "நினைவிழந்த",
        "சுயநினைவு இல்லை",

        "స్పృహ కోల్పోయ",
        "స్పందించడం లేదు",

        "ബോധരഹിത",
        "പ്രതികരിക്കുന്നില്ല",

        "ಪ್ರಜ್ಞಾಹೀನ",
        "ಪ್ರತಿಕ್ರಿಯಿಸುತ್ತಿಲ್ಲ",

        "অজ্ঞান",
        "সাড়া দিচ্ছে না",

        "बेशुद्ध",
        "प्रतिसाद देत नाही",
    ]

    if has_any(unconscious):
        detected.append(
            (
                "Unconsciousness / seizure",
                ["possible unconsciousness"],
            )
        )

    return detected


# =========================================================
# FIRST AID DETECTION
# =========================================================

FIRST_AID_GUIDES = {

    "Severe Bleeding": [
        "severe bleeding",
        "wound is bleeding heavily",
        "wound is bleeding",
        "bleeding heavily",
        "heavy bleeding",
        "uncontrolled bleeding",
        "bleeding won't stop",
        "bleeding does not stop",
        "profuse bleeding",
        "cut bleeding heavily",
        "deep cut",
        "deep wound",

        "बहुत ज्यादा खून बहना",
        "तेज रक्तस्राव",
        "खून नहीं रुक रहा",

        "கடுமையான இரத்தப்போக்கு",
        "அதிக இரத்தப்போக்கு",
        "இரத்தம் நிற்கவில்லை",

        "తీవ్రమైన రక్తస్రావం",
        "ఎక్కువ రక్తస్రావం",

        "രക്തം നിൽക്കുന്നില്ല",

        "ತೀವ್ರ ರಕ್ತಸ್ರಾವ",

        "রক্তপাত বন্ধ হচ্ছে না",

        "रक्तस्त्राव थांबत नाही",
    ],

    "Burn": [
        "burn",
        "burned",
        "burnt",
        "scald",
        "hot water burn",
        "fire burn",
        "oil burn",

        "காயம் சுட்டது",
        "தீக்காயம்",
        "சூடு காயம்",
        "சூடான தண்ணீரால் சுட்டது",

        "जलना",
        "जल गया",
        "गर्म पानी से जलना",

        "తీవ్రమైన కాలిన గాయం",
        "కాలిన గాయం",

        "പൊള്ളൽ",
        "ചൂടുവെള്ളത്തിൽ പൊള്ളൽ",

        "ಸುಟ್ಟ ಗಾಯ",
        "ಬಿಸಿ ನೀರಿನಿಂದ ಸುಟ್ಟ ಗಾಯ",

        "পোড়া",
        "গরম পানিতে পোড়া",

        "भाजणे",
        "गरम पाण्याने भाजणे",
    ],
}


def detect_first_aid(text):

    if not text:
        return None

    normalized = normalize_text(text)

    for guide_name, keywords in FIRST_AID_GUIDES.items():

        for keyword in keywords:

            if normalize_text(keyword) in normalized:
                return guide_name

    return None


# =========================================================
# FIRST AID VISUAL GUIDE
# =========================================================

def show_first_aid_guide(language, first_aid_type):

    if first_aid_type == "Severe Bleeding":

        st.image(
            "first_aid_severe_bleeding.png",
            width=350,
        )

        st.error("🩸 Severe bleeding")

        st.write(
            "• Apply firm pressure to the wound.\n"
            "• Do not remove soaked cloth; add another cloth on top.\n"
            "• Get urgent medical help."
        )

    elif first_aid_type == "Burn":

        st.image(
            "first_aid_burn.png",
            width=350,
        )

        st.error("🔥 Burn")

        st.write(
            "• Cool the burn with clean, cool running water.\n"
            "• Do not apply ice, toothpaste, or oil.\n"
            "• Get medical help for serious burns."
        )


# =========================================================
# RED FLAG DETECTION
# =========================================================

def detect_red_flags(text):
    """
    Detect genuine emergency red flags while avoiding
    false positives from negative/normal statements.
    """
    if not text:
        return []

    normalized = normalize_text(text)

    # ---------------------------------------------------------
    # NEGATIVE / REASSURING PHRASES
    # These prevent phrases such as:
    # "I can breathe normally"
    # "no difficulty breathing"
    # "I don't have chest pain"
    # from being treated as emergencies.
    # ---------------------------------------------------------
    negative_phrases = [
        "no difficulty breathing",
        "no breathing difficulty",
        "no shortness of breath",
        "no chest pain",
        "no severe chest pain",
        "no bleeding",
        "no severe bleeding",
        "no heavy bleeding",
        "no unconsciousness",
        "not unconscious",
        "not having a seizure",
        "no seizure",
        "no convulsion",
        "no choking",
        "not choking",
        "can breathe normally",
        "breathing normally",
        "breathing is normal",
        "breathing fine",
        "breathing is fine",
        "can speak normally",
        "speaking normally",
        "no severe pain",
        "no severe abdominal pain",
        "no severe headache",
        "no sudden weakness",
        "no sudden numbness",
        "no stroke symptoms",
        "no signs of stroke",
    ]

    # ---------------------------------------------------------
    # Check whether a phrase is explicitly negated.
    # ---------------------------------------------------------
    def is_negated(keyword):
        keyword = normalize_text(keyword)

        # Direct negative phrase before the keyword
        direct_negative_patterns = [
            f"no {keyword}",
            f"not {keyword}",
            f"without {keyword}",
            f"does not have {keyword}",
            f"doesn't have {keyword}",
            f"do not have {keyword}",
            f"don't have {keyword}",
            f"there is no {keyword}",
            f"there are no {keyword}",
        ]

        for pattern in direct_negative_patterns:
            if pattern in normalized:
                return True

        # Check a small word window before the keyword.
        words = normalized.split()
        keyword_words = keyword.split()

        if len(words) >= len(keyword_words):
            for i in range(len(words) - len(keyword_words) + 1):
                window = words[i:i + len(keyword_words)]

                if window == keyword_words:
                    previous_words = words[max(0, i - 5):i]
                    previous_text = " ".join(previous_words)

                    if any(
                        neg in previous_text
                        for neg in [
                            "no",
                            "not",
                            "without",
                            "never",
                            "don't",
                            "doesn't",
                            "do not",
                            "does not",
                        ]
                    ):
                        return True

        return False

    # ---------------------------------------------------------
    # Special protection for normal breathing statements.
    # ---------------------------------------------------------
    normal_breathing = any(
        phrase in normalized
        for phrase in [
            "can breathe normally",
            "breathing normally",
            "breathing is normal",
            "breathing fine",
            "breathing is fine",
            "no difficulty breathing",
            "no breathing difficulty",
            "no shortness of breath",
        ]
    )

    detected = []

    # ---------------------------------------------------------
    # EXACT RED-FLAG MATCHING
    # ---------------------------------------------------------
    for category, keywords in RED_FLAG_GROUPS.items():

        exact_matches = []

        for keyword in keywords:
            keyword_normalized = normalize_text(keyword)

            if keyword_normalized in normalized:

                # Do not trigger for explicitly negated statements.
                if is_negated(keyword_normalized):
                    continue

                # Do not trigger breathing emergency when
                # the person explicitly says breathing is normal.
                if category == "Severe breathing emergency" and normal_breathing:
                    continue

                exact_matches.append(keyword)

        if exact_matches:
            detected.append(
                (category, exact_matches[:3])
            )

    # ---------------------------------------------------------
    # FUZZY MATCHING
    # Only use fuzzy matching for English.
    # Make it stricter to prevent false emergencies.
    # ---------------------------------------------------------
    english_words = re.findall(
        r"[a-z]+(?:'[a-z]+)?",
        normalized
    )

    english_text = " ".join(english_words)
    collapsed_text = collapse_repeated_letters(english_text)
    text_words = collapsed_text.split()

    for phrase in FUZZY_RED_FLAGS:

        phrase = normalize_text(phrase)

        # Skip fuzzy detection when the exact phrase is
        # explicitly negated.
        if is_negated(phrase):
            continue

        # Normal breathing statements must never fuzzy-match
        # a severe breathing emergency.
        if (
            phrase in [
                "cannot breathe",
                "severe difficulty breathing",
                "difficulty breathing",
            ]
            and normal_breathing
        ):
            continue

        collapsed_phrase = collapse_repeated_letters(phrase)
        phrase_words = collapsed_phrase.split()

        if not phrase_words:
            continue

        best_ratio = 0.0

        # -----------------------------------------------------
        # Fuzzy matching requires the same number of words.
        # This prevents unrelated short sentences from
        # accidentally matching emergency phrases.
        # -----------------------------------------------------
        n = len(phrase_words)

        if len(text_words) >= n:

            for i in range(len(text_words) - n + 1):

                window = " ".join(
                    text_words[i:i + n]
                )

                ratio = difflib.SequenceMatcher(
                    None,
                    window,
                    collapsed_phrase,
                ).ratio()

                best_ratio = max(
                    best_ratio,
                    ratio
                )

        # Stricter threshold than the previous 0.86.
        if best_ratio >= 0.92:

            for category, keywords in RED_FLAG_GROUPS.items():

                normalized_keywords = [
                    normalize_text(k)
                    for k in keywords
                ]

                if phrase in normalized_keywords:

                    # Breathing protection
                    if (
                        category == "Severe breathing emergency"
                        and normal_breathing
                    ):
                        continue

                    existing = next(
                        (
                            item
                            for item in detected
                            if item[0] == category
                        ),
                        None,
                    )

                    if existing is None:
                        detected.append(
                            (
                                category,
                                [f"possible match: {phrase}"]
                            )
                        )

                    break

    return detected

    # -----------------------------------------------------
    # MULTILINGUAL COMBINATION PATTERNS
    # -----------------------------------------------------

    detected.extend(
        detect_multilingual_emergency_patterns(text)
    )

    # -----------------------------------------------------
    # SMART SEVERE BLEEDING DETECTION
    # -----------------------------------------------------

    bleeding_words = [
        "bleeding",
        "blood",
        "bleed",
        "रक्तस्राव",
        "खून",
        "இரத்தம்",
        "ரத்தம்",
        "రక్తం",
        "രക്തം",
        "ರಕ್ತ",
        "রক্ত",
        "रक्त",
    ]

    severe_bleeding_words = [
        "heavy",
        "heavily",
        "severe",
        "severely",
        "a lot",
        "lot of blood",
        "won't stop",
        "does not stop",
        "not stopping",
        "continuous",
        "uncontrolled",
        "profuse",

        "बहुत ज्यादा",
        "तेज",
        "नहीं रुक",

        "நிற்கவில்லை",
        "நிறுத்த முடியவில்லை",
        "அதிக",

        "ఆగడం లేదు",
        "ఎక్కువ",

        "നിൽക്കുന്നില്ല",
        "അമിതമായ",

        "ನಿಲ್ಲುತ್ತಿಲ್ಲ",
        "ಹೆಚ್ಚಿನ",

        "বন্ধ হচ্ছে না",
        "অতিরিক্ত",

        "थांबत नाही",
        "जास्त",
    ]

    has_bleeding = any(
        word in normalized
        for word in bleeding_words
    )

    has_severe_bleeding = any(
        word in normalized
        for word in severe_bleeding_words
    )

    if has_bleeding and has_severe_bleeding:

        detected.append(
            (
                "Severe bleeding / internal bleeding",
                ["possible severe/heavy bleeding"],
            )
        )

    # -----------------------------------------------------
    # EXACT RED-FLAG KEYWORD MATCHING
    # -----------------------------------------------------

    for category, keywords in RED_FLAG_GROUPS.items():

        exact_matches = []

        for keyword in keywords:

            if normalize_text(keyword) in normalized:
                exact_matches.append(keyword)

        if exact_matches:

            existing = next(
                (
                    item
                    for item in detected
                    if item[0] == category
                ),
                None,
            )

            if existing is None:

                detected.append(
                    (
                        category,
                        exact_matches[:3],
                    )
                )

    # -----------------------------------------------------
    # FUZZY ENGLISH MATCHING
    # -----------------------------------------------------

    english_words = re.findall(
        r"[a-z]+(?:'[a-z]+)?",
        normalized,
    )

    english_text = " ".join(english_words)

    collapsed_text = collapse_repeated_letters(
        english_text
    )

    for phrase in FUZZY_RED_FLAGS:

        phrase = normalize_text(phrase)

        collapsed_phrase = collapse_repeated_letters(
            phrase
        )

        if collapsed_phrase in collapsed_text:

            for category, keywords in RED_FLAG_GROUPS.items():

                normalized_keywords = [
                    normalize_text(k)
                    for k in keywords
                ]

                if phrase in normalized_keywords:

                    existing = next(
                        (
                            item
                            for item in detected
                            if item[0] == category
                        ),
                        None,
                    )

                    if existing is None:

                        detected.append(
                            (
                                category,
                                [f"possible match: {phrase}"],
                            )
                        )

                    break

            continue

        phrase_words = collapsed_phrase.split()
        text_words = collapsed_text.split()

        best_ratio = 0.0

        if len(text_words) >= len(phrase_words):

            n = len(phrase_words)

            for i in range(
                len(text_words) - n + 1
            ):

                window = " ".join(
                    text_words[i:i + n]
                )

                best_ratio = max(
                    best_ratio,
                    difflib.SequenceMatcher(
                        None,
                        window,
                        collapsed_phrase,
                    ).ratio(),
                )

        if best_ratio >= 0.86:

            for category, keywords in RED_FLAG_GROUPS.items():

                normalized_keywords = [
                    normalize_text(k)
                    for k in keywords
                ]

                if phrase in normalized_keywords:

                    existing = next(
                        (
                            item
                            for item in detected
                            if item[0] == category
                        ),
                        None,
                    )

                    if existing is None:

                        detected.append(
                            (
                                category,
                                [f"possible match: {phrase}"],
                            )
                        )

                    break

    # -----------------------------------------------------
    # REMOVE DUPLICATE CATEGORIES
    # -----------------------------------------------------

    unique_detected = []
    seen_categories = set()

    for item in detected:

        if item[0] not in seen_categories:

            unique_detected.append(item)

            seen_categories.add(item[0])

    return unique_detected


# =========================================================
# RISK PRIORITY
# =========================================================

def get_risk_priority(detected_flags, question):
    """
    Determine local risk priority before Gemini.

    Emergency red flags always have the highest priority.
    Burns are treated intelligently:
    - ordinary/minor burns -> LOW/MODERATE
    - severe/major/deep/large burns -> EMERGENCY
    """

    if detected_flags:
        return "EMERGENCY"

    text = normalize_text(question)

    # -------------------------------------------------
    # BURN EMERGENCY DETECTION
    # -------------------------------------------------

    burn_words = [
        "burn",
        "burned",
        "burnt",
        "scald",
        "जलना",
        "जल गया",
        "जलने",
        "जलने की चोट",
        "தீக்காயம்",
        "சுட்டது",
        "காயம் சுட்டது",
        "కాలిన గాయం",
        "పొలికిన గాయం",
        "పొള്ളൽ",
        "ചൂടേറ്റ പൊള്ളൽ",
        "ಸುಟ್ಟ ಗಾಯ",
        "ಬಿಸಿ ನೀರಿನಿಂದ ಸುಟ್ಟ ಗಾಯ",
        "পোড়া",
        "গরম পানিতে পোড়া",
        "भाजणे",
        "भाजले",
    ]

    severe_burn_words = [
        "severe burn",
        "major burn",
        "deep burn",
        "large burn",
        "extensive burn",
        "serious burn",
        "very bad burn",
        "badly burned",
        "burn is deep",
        "deeply burned",

        "गंभीर जलना",
        "गंभीर जलने की चोट",
        "बहुत गंभीर जलना",
        "बड़ा जलना",

        "கடுமையான தீக்காயம்",
        "ஆழமான தீக்காயம்",
        "பெரிய தீக்காயம்",

        "తీవ్రమైన కాలిన గాయం",
        "లోతైన కాలిన గాయం",
        "పెద్ద కాలిన గాయం",

        "ഗുരുതരമായ പൊള്ളൽ",
        "ആഴത്തിലുള്ള പൊള്ളൽ",
        "വലിയ പൊള്ളൽ",

        "ತೀವ್ರ ಸುಟ್ಟ ಗಾಯ",
        "ಆಳವಾದ ಸುಟ್ಟ ಗಾಯ",
        "ದೊಡ್ಡ ಸುಟ್ಟ ಗಾಯ",

        "গুরুতর পোড়া",
        "গভীর পোড়া",
        "বড় পোড়া",

        "गंभीर भाजणे",
        "खोल भाजणे",
        "मोठे भाजणे",
    ]

    # -------------------------------------------------
    # BURN WITH AIRWAY / BREATHING PROBLEM
    # -------------------------------------------------

    burn_airway_words = [
        "burn and difficulty breathing",
        "burn with difficulty breathing",
        "burn and cannot breathe",
        "burn with breathing difficulty",
        "smoke inhalation",
        "inhaled smoke",
        "face burn and breathing",
        "burned face and cannot breathe",

        "चेहरा जला और सांस लेने में दिक्कत",
        "जलने के बाद सांस लेने में दिक्कत",

        "தீக்காயம் மற்றும் மூச்சு விடுவதில் சிரமம்",
        "தீக்காயத்திற்குப் பிறகு மூச்சு விட முடியவில்லை",

        "కాలిన గాయంతో శ్వాస తీసుకోవడంలో ఇబ్బంది",
        "కాలిన తర్వాత శ్వాస తీసుకోలేకపోతున్నాను",

        "പൊള്ളലിനൊപ്പം ശ്വസിക്കാൻ ബുദ്ധിമുട്ട്",
        "പൊള്ളലിന് ശേഷം ശ്വാസം എടുക്കാൻ കഴിയുന്നില്ല",

        "ಸುಟ್ಟ ಗಾಯದೊಂದಿಗೆ ಉಸಿರಾಟದ ತೊಂದರೆ",
        "ಸುಟ್ಟ ನಂತರ ಉಸಿರಾಡಲು ಸಾಧ್ಯವಾಗುತ್ತಿಲ್ಲ",

        "পোড়ার সঙ্গে শ্বাস নিতে অসুবিধা",
        "পোড়ার পরে শ্বাস নিতে পারছি না",

        "भाजल्यावर श्वास घेण्यास त्रास",
        "भाजल्यानंतर श्वास घेता येत नाही",
    ]

    # -------------------------------------------------
    # ELECTRICAL BURN / ELECTRIC SHOCK
    # -------------------------------------------------

    electrical_words = [
        "electric shock",
        "electrical burn",
        "electrical injury",
        "electric burn",

        "बिजली का झटका",
        "बिजली से जलना",

        "மின்சார அதிர்ச்சி",
        "மின்சார தீக்காயம்",

        "విద్యుత్ షాక్",
        "విద్యుత్ కాలిన గాయం",

        "വൈദ്യുതാഘാതം",
        "വൈദ്യുത പൊള്ളൽ",

        "ವಿದ್ಯುತ್ ಆಘಾತ",
        "ವಿದ್ಯುತ್ ಸುಟ್ಟ ಗಾಯ",

        "বৈদ্যুতিক শক",
        "বৈদ্যুতিক পোড়া",

        "वीज लागणे",
        "वीजेमुळे भाजणे",
    ]

    # -------------------------------------------------
    # CHECK BURN EMERGENCIES
    # -------------------------------------------------

    if any(pattern in text for pattern in severe_burn_words):
        return "EMERGENCY"

    if any(pattern in text for pattern in burn_airway_words):
        return "EMERGENCY"

    if any(pattern in text for pattern in electrical_words):
        return "EMERGENCY"

    # -------------------------------------------------
    # CLEAR HIGH-RISK PATTERNS
    # -------------------------------------------------

    high_risk_patterns = [
        "pregnancy",
        "pregnant",
        "newborn",
        "baby",
        "infant",
        "severe pain",
        "persistent vomiting",
        "very high fever",
        "difficult to wake up",
        "confused", 
        "blood pressure very high",
        "very high bp",
        "blood sugar very high",
        "blood sugar very low",
        "difficulty eating",
        "difficulty drinking",
        "dehydration",
        "repeated vomiting",
        "severe weakness",
    ]

    # -------------------------------------------------
    # MODERATE-RISK PATTERNS
    # -------------------------------------------------

    moderate_risk_patterns = [
        "fever",
        "cough",
        "vomiting",
        "diarrhea",
        "dizziness",
        "abdominal pain",
        "stomach pain",
        "back pain",
        "rash",
        "swelling",
        "persistent pain",
        "weakness",
    ]

    # -------------------------------------------------
    # COMMON MILD SYMPTOMS
    # -------------------------------------------------

    low_risk_patterns = [
        "mild headache",
        "slight headache",
        "minor headache",
        "small headache",
        "mild pain",
        "slight pain",
        "small burn",
        "minor burn",
        "mild burn",
    ]

    # -------------------------------------------------
    # LOW RISK
    # -------------------------------------------------

    if any(pattern in text for pattern in low_risk_patterns):
        return "LOW"

    # -------------------------------------------------
    # HIGH RISK
    # -------------------------------------------------

    if any(pattern in text for pattern in high_risk_patterns):
        return "HIGH"

    # -------------------------------------------------
    # MODERATE RISK
    # -------------------------------------------------

    if any(pattern in text for pattern in moderate_risk_patterns):
        return "MODERATE"

    # -------------------------------------------------
    # ORDINARY BURN
    # -------------------------------------------------

    if any(pattern in text for pattern in burn_words):
        return "LOW"

    return "LOW"

    # -----------------------------------------------------
    # HIGH-RISK PATTERNS
    # -----------------------------------------------------

    high_risk_patterns = [
        "pregnancy",
        "pregnant",
        "newborn",
        "baby",
        "infant",
        "severe pain",
        "persistent vomiting",
        "very high fever",
        "blood pressure very high",
        "very high bp",
        "blood sugar very high",
        "blood sugar very low",
        "difficulty eating",
        "difficulty drinking",
        "dehydration",
        "repeated vomiting",
        "severe weakness",
    ]

    # -----------------------------------------------------
    # MODERATE-RISK PATTERNS
    # -----------------------------------------------------

    moderate_risk_patterns = [
        "fever",
        "cough",
        "vomiting",
        "diarrhea",
        "dizziness",
        "abdominal pain",
        "stomach pain",
        "back pain",
        "rash",
        "swelling",
        "persistent pain",
        "weakness",
    ]

    # -----------------------------------------------------
    # LOW-RISK PATTERNS
    # -----------------------------------------------------

    low_risk_patterns = [
        "mild headache",
        "slight headache",
        "minor headache",
        "small headache",
        "mild pain",
        "slight pain",
    ]

    # Check LOW first
    if any(
        pattern in text
        for pattern in low_risk_patterns
    ):
        return "LOW"

    # Check HIGH
    if any(
        pattern in text
        for pattern in high_risk_patterns
    ):
        return "HIGH"

    # Check MODERATE
    if any(
        pattern in text
        for pattern in moderate_risk_patterns
    ):
        return "MODERATE"

    return "LOW"


# =========================================================
# RED FLAG UI
# =========================================================

RED_FLAG_TITLE = {

    "English":
        "🚨 POSSIBLE RED FLAG / URGENT WARNING",

    "Hindi":
        "🚨 संभावित गंभीर चेतावनी / तत्काल चिकित्सा सहायता",

    "Tamil":
        "🚨 சாத்தியமான ஆபத்து அறிகுறி / அவசர எச்சரிக்கை",

    "Telugu":
        "🚨 ప్రమాద సూచన / అత్యవசర హెచ్చరిక",

    "Malayalam":
        "🚨 സാധ്യതയുള്ള അപകട സൂചന / അടിയന്തര മുന്നറിയിപ്പ്",

    "Kannada":
        "🚨 ಸಾಧ್ಯವಾದ ಅಪಾಯದ ಸೂಚನೆ / ತುರ್ತು ಎಚ್ಚರಿಕೆ",

    "Bengali":
        "🚨 সম্ভাব্য বিপদের লক্ষণ / জরুরি সতর্কতা",

    "Marathi":
        "🚨 संभाव्य धोक्याची चिन्हे / तातडीची सूचना",
}


RED_FLAG_MESSAGE = {

    "English": (
        "The question contains a possible emergency warning sign. "
        "Do not rely only on Saathi. Arrange urgent assessment by "
        "appropriate emergency medical services or a suitable healthcare facility."
    ),

    "Hindi": (
        "प्रश्न में संभावित आपातकालीन चेतावनी संकेत है। "
        "केवल साथी पर निर्भर न रहें। उचित आपातकालीन चिकित्सा सेवा या "
        "स्वास्थ्य सुविधा में तुरंत जांच की व्यवस्था करें।"
    ),

    "Tamil": (
        "கேள்வியில் சாத்தியமான அவசர ஆபத்து அறிகுறி உள்ளது. "
        "சாத்தியை மட்டும் நம்ப வேண்டாம். உடனடி மருத்துவ மதிப்பீட்டை ஏற்பாடு செய்யுங்கள்."
    ),

    "Telugu": (
        "మీ ప్రశ్నలో సాధ్యమైన అత్యవసర ప్రమాద సూచన ఉంది. "
        "సాతీపై మాత్రమే ఆధారపడకండి. తక్షణ వైద్య పరీక్షను ఏర్పాటు చేయండి."
    ),

    "Malayalam": (
        "ചോദ്യത്തിൽ അടിയന്തര അപകട സൂചന ഉണ്ടാകാം. "
        "സാത്തിയെ മാത്രം ആശ്രയിക്കരുത്. ഉടൻ മെഡിക്കൽ വിലയിരുത്തൽ ഏർപ്പെടുത്തുക."
    ),

    "Kannada": (
        "ನಿಮ್ಮ ಪ್ರಶ್ನೆಯಲ್ಲಿ ತುರ್ತು ಅಪಾಯದ ಸೂಚನೆ ಇರಬಹುದು. "
        "ಸಾಥಿಯನ್ನು ಮಾತ್ರ ಅವಲಂಬಿಸಬೇಡಿ. ತಕ್ಷಣ ವೈದ್ಯಕೀಯ ಪರೀಕ್ಷೆ ವ್ಯವಸ್ಥೆ ಮಾಡಿ."
    ),

    "Bengali": (
        "আপনার প্রশ্নে সম্ভাব্য জরুরি বিপদের লক্ষণ রয়েছে। "
        "শুধু সাথীর উপর নির্ভর করবেন না। দ্রুত চিকিৎসা মূল্যায়নের ব্যবস্থা করুন।"
    ),

    "Marathi": (
        "तुमच्या प्रश्नामध्ये संभाव्य आपत्कालीन धोक्याचे चिन्ह आहे. "
        "फक्त साथीवर अवलंबून राहू नका. तातडीची वैद्यकीय तपासणी करून घ्या."
    ),
}


# =========================================================
# BIG EMERGENCY ACTION PANEL
# =========================================================

def show_emergency_alert(language):

    st.error("🚨 EMERGENCY")

    if language == "Tamil":

        st.markdown("## 🚨 அவசர நிலை")
        st.markdown(
            "### 🏥 அருகிலுள்ள மருத்துவமனைக்குச் செல்லுங்கள்"
        )
        st.markdown(
            "### ⚠️ காத்திருக்க வேண்டாம்"
        )

    elif language == "Hindi":

        st.markdown("## 🚨 आपातकाल")
        st.markdown(
            "### 🏥 निकटतम अस्पताल जाएं"
        )
        st.markdown(
            "### ⚠️ इंतज़ार न करें"
        )

    elif language == "Telugu":

        st.markdown("## 🚨 అత్యవసర పరిస్థితి")
        st.markdown(
            "### 🏥 సమీప ఆసుపత్రికి వెళ్లండి"
        )
        st.markdown(
            "### ⚠️ ఆలస్యం చేయవద్దు"
        )

    elif language == "Malayalam":

        st.markdown("## 🚨 അടിയന്തര സാഹചര്യം")
        st.markdown(
            "### 🏥 അടുത്തുള്ള ആശുപത്രിയിലേക്ക് പോകുക"
        )
        st.markdown(
            "### ⚠️ കാത്തിരിക്കരുത്"
        )

    elif language == "Kannada":

        st.markdown("## 🚨 ತುರ್ತು ಪರಿಸ್ಥಿತಿ")
        st.markdown(
            "### 🏥 ಹತ್ತಿರದ ಆಸ್ಪತ್ರೆಗೆ ಹೋಗಿ"
        )
        st.markdown(
            "### ⚠️ ಕಾಯಬೇಡಿ"
        )

    elif language == "Bengali":

        st.markdown("## 🚨 জরুরি পরিস্থিতি")
        st.markdown(
            "### 🏥 নিকটস্থ হাসপাতালে যান"
        )
        st.markdown(
            "### ⚠️ অপেক্ষা করবেন না"
        )

    elif language == "Marathi":

        st.markdown("## 🚨 आपत्कालीन परिस्थिती")
        st.markdown(
            "### 🏥 जवळच्या रुग्णालयात जा"
        )
        st.markdown(
            "### ⚠️ विलंब करू नका"
        )

    else:

        st.markdown("## 🚨 EMERGENCY")
        st.markdown(
            "### 🏥 Go to the nearest hospital"
        )
        st.markdown(
            "### ⚠️ DO NOT WAIT"
        )

    # -----------------------------------------------------
    # EMERGENCY CONTACTS
    # -----------------------------------------------------

    st.markdown("### 🚨 Emergency Contacts")

    col1, col2 = st.columns(2)

    with col1:

        if st.button(
            "📞 Call 112",
            key="emergency_112",
            use_container_width=True,
        ):
            st.info(
                "📞 Please call 112 from your phone."
            )

    with col2:

        if st.button(
            "🚑 Call 108",
            key="emergency_108",
            use_container_width=True,
        ):
            st.info(
                "🚑 Please call 108 from your phone."
            )



# =========================================================
# ASK SAATHI
# =========================================================

if st.button(
    ui["button"],
    type="primary",
    key="ask_saathi_button",
):

    final_question = question.strip()

    # =====================================================
    # VOICE TRANSCRIPTION
    # =====================================================

    if not final_question and new_audio_bytes:

        try:

            voice_prompt = f"""
Transcribe this audio recording.

The speaker may use:
English, Hindi, Tamil, Telugu, Malayalam, Kannada, Bengali, or Marathi.

Return ONLY the spoken words.
Do not translate.
Do not summarize.
Do not explain.

Language context: {language}
"""

            voice_response = call_gemini(
                [
                    {
                        "role": "user",
                        "parts": [
                            {
                                "text": voice_prompt
                            },
                            {
                                "inline_data": {
                                    "mime_type": "audio/wav",
                                    "data": new_audio_bytes,
                                }
                            },
                        ],
                    }
                ]
            )

            if (
                voice_response
                and voice_response.text
            ):

                final_question = (
                    voice_response.text.strip()
                )

                st.session_state.voice_question = (
                    final_question
                )

                st.session_state.last_audio_bytes = (
                    new_audio_bytes
                )

                st.success("🎤 Voice detected")

                st.write("**You said:**")

                st.write(final_question)

        except Exception as e:

            show_gemini_error(e)

    # =====================================================
    # USE LAST SUCCESSFUL VOICE TRANSCRIPTION
    # =====================================================

    if (
        not final_question
        and st.session_state.voice_question
    ):

        final_question = (
            st.session_state.voice_question.strip()
        )

        st.session_state.voice_question = ""

    # =====================================================
    # EMPTY QUESTION
    # =====================================================

    if not final_question:

        st.warning(ui["empty"])

    else:

        st.info(
            f"📝 Question received:\n\n{final_question}"
        )

        # =================================================
        # LOCAL SAFETY CHECK
        # =================================================

        detected_flags = detect_red_flags(
            final_question
        )

        first_aid_type = detect_first_aid(
            final_question
        )

        risk_priority = get_risk_priority(
            detected_flags,
            final_question,
        )

        # =================================================
        # RISK INSTRUCTION
        # =================================================

        if risk_priority == "LOW":

            risk_instruction = (
                "LOW RISK — do not upgrade this unless "
                "there is a clear warning sign."
            )

        elif risk_priority == "MODERATE":

            risk_instruction = (
                "MODERATE RISK."
            )

        elif risk_priority == "HIGH":

            risk_instruction = (
                "HIGH RISK."
            )

        else:

            risk_instruction = (
                "EMERGENCY — immediate medical attention may be needed."
            )

        # =================================================
        # LOCAL RISK PRIORITY UI
        # =================================================

        if risk_priority == "LOW":

            st.success("🟢 LOW RISK")

        elif risk_priority == "MODERATE":

            st.warning("🟡 MODERATE RISK")

        elif risk_priority == "HIGH":

            st.error("🟠 HIGH RISK")

        else:

            st.error("🔴 EMERGENCY")

        # =================================================
        # FIRST-AID GUIDE
        # =================================================

        if first_aid_type:

            show_first_aid_guide(
                language,
                first_aid_type,
            )

        # =================================================
        # EMERGENCY MODE
        # =================================================

        if detected_flags:

            show_emergency_alert(language)

            st.markdown(
                f"### {RED_FLAG_TITLE[language]}"
            )

            st.warning(
                f"🚨 {RED_FLAG_MESSAGE[language]}"
            )

            st.markdown(
                "### 🆘 What to do now"
            )

            # ---------------------------------------------
            # TAMIL
            # ---------------------------------------------

            if language == "Tamil":

                st.write(
                    "• நபரை தனியாக விடாதீர்கள்.\n"
                    "• உடனடி மருத்துவ உதவியை பெறுங்கள்.\n"
                    "• இந்தியாவில் 112 அல்லது உள்ளூர் ஆம்புலன்ஸ் சேவையை தொடர்பு கொள்ளுங்கள்.\n"
                    "• அருகிலுள்ள மருத்துவமனைக்கு செல்லுங்கள்."
                )

            # ---------------------------------------------
            # HINDI
            # ---------------------------------------------

            elif language == "Hindi":

                st.write(
                    "• व्यक्ति को अकेला न छोड़ें।\n"
                    "• तुरंत चिकित्सा सहायता लें।\n"
                    "• भारत में 112 या स्थानीय एम्बुलेंस सेवा से संपर्क करें।\n"
                    "• निकटतम अस्पताल जाएं।"
                )

            # ---------------------------------------------
            # TELUGU
            # ---------------------------------------------

            elif language == "Telugu":

                st.write(
                    "• వ్యక్తిని ఒంటరిగా వదిలివేయకండి.\n"
                    "• వెంటనే వైద్య సహాయం పొందండి.\n"
                    "• భారతదేశంలో 112 లేదా స్థానిక అంబులెన్స్ సేవకు కాల్ చేయండి.\n"
                    "• సమీప ఆసుపత్రికి వెళ్లండి."
                )

            # ---------------------------------------------
            # MALAYALAM
            # ---------------------------------------------

            elif language == "Malayalam":

                st.write(
                    "• വ്യക്തിയെ ഒറ്റയ്ക്ക് വിടരുത്.\n"
                    "• ഉടൻ മെഡിക്കൽ സഹായം നേടുക.\n"
                    "• ഇന്ത്യയിൽ 112 അല്ലെങ്കിൽ പ്രാദേശിക ആംബുലൻസ് സേവനത്തെ ബന്ധപ്പെടുക.\n"
                    "• അടുത്തുള്ള ആശുപത്രിയിലേക്ക് പോകുക."
                )

            # ---------------------------------------------
            # KANNADA
            # ---------------------------------------------

            elif language == "Kannada":

                st.write(
                    "• ವ್ಯಕ್ತಿಯನ್ನು ಒಬ್ಬರೇ ಬಿಡಬೇಡಿ.\n"
                    "• ತಕ್ಷಣ ವೈದ್ಯಕೀಯ ಸಹಾಯ ಪಡೆಯಿರಿ.\n"
                    "• ಭಾರತದಲ್ಲಿ 112 ಅಥವಾ ಸ್ಥಳೀಯ ಆಂಬ್ಯುಲೆನ್ಸ್ ಸೇವೆಗೆ ಕರೆ ಮಾಡಿ.\n"
                    "• ಹತ್ತಿರದ ಆಸ್ಪತ್ರೆಗೆ ಹೋಗಿ."
                )

            # ---------------------------------------------
            # BENGALI
            # ---------------------------------------------

            elif language == "Bengali":

                st.write(
                    "• ব্যক্তিকে একা রাখবেন না।\n"
                    "• অবিলম্বে চিকিৎসা সহায়তা নিন।\n"
                    "• ভারতে 112 বা স্থানীয় অ্যাম্বুলেন্স পরিষেবায় যোগাযোগ করুন।\n"
                    "• নিকটস্থ হাসপাতালে যান।"
                )

            # ---------------------------------------------
            # MARATHI
            # ---------------------------------------------

            elif language == "Marathi":

                st.write(
                    "• व्यक्तीला एकटे सोडू नका.\n"
                    "• त्वरित वैद्यकीय मदत घ्या.\n"
                    "• भारतात 112 किंवा स्थानिक रुग्णवाहिका सेवेशी संपर्क करा.\n"
                    "• जवळच्या रुग्णालयात जा."
                )

            # ---------------------------------------------
            # ENGLISH
            # ---------------------------------------------

            else:

                st.write(
                    "• Do not leave the person alone.\n"
                    "• Seek immediate medical help.\n"
                    "• In India, call 112 or the local ambulance service.\n"
                    "• Go to the nearest appropriate hospital."
                )

            # =================================================
            # WARNING SIGNS DETECTED
            # =================================================

            st.markdown(
                "### 🚨 Warning signs detected"
            )

            for category, matches in detected_flags:

                st.markdown(
                    f"**{category}** — {', '.join(matches)}"
                )

            st.error(
                "⚠️ Do not wait for Saathi's AI response "
                "if the person has a serious or life-threatening condition."
            )

            st.info(
                "🛑 Emergency detected — normal AI guidance will be skipped."
            )

            # Stop Gemini response
            st.stop()

        # =================================================
        # GEMINI PROMPT
        # =================================================

        prompt = f"""
You are Saathi AI Health Agent.

You are a fast, practical digital health assistant designed for
frontline health workers such as ASHA and ANM workers in India.

Patient information:
Patient ID: {patient_id if patient_id else "Not provided"}
Age: {patient_age}
Gender: {patient_gender}
Relevant notes: {patient_notes if patient_notes else "None provided"}

Selected health topic:
{topic}

Selected language:
{language}

Health question:
{final_question}

Local safety screen:
No local emergency red-flag keyword was detected.

Local Saathi risk priority:
{risk_priority}

Risk instruction:
{risk_instruction}

=========================================================
IMPORTANT RESPONSE RULES
=========================================================

1. Respond ONLY in {language}.
2. Keep the response VERY SHORT and easy to scan.
3. Do NOT give long explanations.
4. Do NOT write textbook-style information.
5. Do NOT repeat the patient's question.
6. Do NOT diagnose.
7. Do NOT prescribe medicines.
8. Do NOT give medicine dosages.
9. Do NOT provide false reassurance.
10. Focus only on what the health worker needs to know and do NOW.
11. Use simple words suitable for frontline health workers.
12. Use short bullet points.
13. Maximum response length: about 120 words.
14. If the situation is an emergency, put the emergency warning FIRST.
15. Do not tell a person with emergency warning signs to wait.

=========================================================
RISK PRIORITY
=========================================================

Classify the situation internally as one of:

🟢 LOW RISK
🟡 MODERATE RISK
🟠 HIGH RISK
🔴 EMERGENCY

Do NOT give a long explanation of the classification.

=========================================================
RESPONSE FORMAT
=========================================================

Start with ONE risk level:

🟢 LOW RISK
or
🟡 MODERATE RISK
or
🟠 HIGH RISK
or
🔴 EMERGENCY

Then provide ONLY these sections:

🔎 Possible:
Give a very short description of what the symptoms may suggest.
Do not diagnose.

⚠️ Check:
List only the most important symptoms/signs the health worker should check.

💡 Do now:
Give 2–3 safe and practical actions.

🏥 Referral:
Clearly say whether routine monitoring, healthcare review,
prompt medical evaluation, or immediate emergency care is needed.

🚨 Emergency:
Only include this section when emergency warning signs are present.
Tell the health worker to seek immediate emergency medical care.

=========================================================
EMERGENCY RULE
=========================================================

If an emergency is identified from the symptoms:

Start with:

🔴 EMERGENCY

Then immediately state:

"🚨 Immediate medical attention may be needed."

Do not bury the emergency warning below other information.

Give only the most important immediate action and referral advice.

=========================================================
FINAL GOAL
=========================================================

Think like a field assistant standing beside the ASHA/ANM worker.

The worker should be able to read the response in approximately
10–15 seconds and understand:

1. What might be happening
2. What to check
3. What to do now
4. Whether referral is needed
5. Whether this is an emergency

Be concise. Be practical. Be safe.
"""

        # =================================================
        # GEMINI RESPONSE
        # =================================================

        try:

            with st.spinner(
                "🩺 Saathi is preparing guidance..."
            ):

                response = call_gemini(prompt)

            if response and response.text:

                st.success(
                    ui["guidance"]
                )

                st.write(
                    response.text
                )

            else:

                st.warning(
                    "⚠️ Saathi could not generate a response right now."
                )

        except Exception as e:

            show_gemini_error(e)
