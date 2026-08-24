import re
import difflib
import streamlit as st
from google import genai

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

# Keep the model name that your API project supports.
MODEL_NAME = "gemini-3.6-flash"


@st.cache_resource
def get_gemini_client():
    return genai.Client(api_key=st.secrets["GEMINI_API_KEY"])


client = get_gemini_client()


def call_gemini(contents):
    """Make one Gemini request."""
    return client.models.generate_content(
        model=MODEL_NAME,
        contents=contents,
    )


def classify_gemini_error(error):
    """Return a user-friendly error category without crashing the app."""
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
            "The health red-flag checker still works locally. "
            "Please wait for the Gemini limit to become available."
        )

    elif category == "temporary":
        st.warning("⚠️ Saathi's AI service is temporarily unavailable.")
        st.info("Gemini may be busy. Please try again shortly.")

    elif category == "model":
        st.error(f"❌ Gemini model '{MODEL_NAME}' was not found.")
        st.info("Check the model name in Google AI Studio/API documentation.")

    elif category == "auth":
        st.error("❌ Gemini API authentication failed.")
        st.info("Check GEMINI_API_KEY in Streamlit Secrets.")

    else:
        st.error("❌ Saathi encountered a technical error.")
        st.info("Please check the technical details below.")

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
language = st.selectbox("🌐 Select your language:", LANGUAGES)
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
        "मातृ स्वास्थ्य", "बाल स्वास्थ्य", "हृदय स्वास्थ्य", "किडनी स्वास्थ्य",
        "त्वचा की समस्याएं", "मधुमेह", "उच्च रक्तचाप", "बुखार और संक्रमण",
        "श्वसन संबंधी समस्याएं", "यकृत स्वास्थ्य", "आंखों का स्वास्थ्य",
        "मुंह और दांतों का स्वास्थ्य", "पोषण", "टीकाकरण", "मानसिक स्वास्थ्य",
        "महिला स्वास्थ्य", "पुरुष स्वास्थ्य", "वृद्ध स्वास्थ्य", "प्राथमिक उपचार",
        "आपातकालीन स्थिति", "सामान्य लक्षण",
    ],
    "Tamil": [
        "தாய்மை நலம்", "குழந்தைகள் நலம்", "இதய நலம்", "சிறுநீரக நலம்",
        "தோல் பிரச்சினைகள்", "நீரிழிவு", "உயர் இரத்த அழுத்தம்",
        "காய்ச்சல் மற்றும் தொற்றுகள்", "சுவாச பிரச்சினைகள்", "கல்லீரல் நலம்",
        "கண் நலம்", "வாய் மற்றும் பல் நலம்", "ஊட்டச்சத்து", "தடுப்பூசி",
        "மனநலம்", "பெண்கள் நலம்", "ஆண்கள் நலம்", "முதியோர் நலம்",
        "முதலுதவி", "அவசர நிலை", "பொதுவான அறிகுறிகள்",
    ],
    "Telugu": [
        "మాతృ ఆరోగ్యం", "శిశు ఆరోగ్యం", "గుండె ఆరోగ్యం", "కిడ్నీ ఆరోగ్యం",
        "చర్మ సమస్యలు", "మధుమేహం", "అధిక రక్తపోటు", "జ్వరం మరియు ఇన్ఫెక్షన్లు",
        "శ్వాస సంబంధిత సమస్యలు", "కాలేయ ఆరోగ్యం", "కంటి ఆరోగ్యం",
        "నోటి మరియు దంత ఆరోగ్యం", "పోషణ", "టీకాలు", "మానసిక ఆరోగ్యం",
        "మహిళల ఆరోగ్యం", "పురుషుల ఆరోగ్యం", "వృద్ధుల ఆరోగ్యం", "ప్రథమ చికిత్స",
        "అత్యవసర పరిస్థితి", "సాధారణ లక్షణాలు",
    ],
    "Malayalam": [
        "മാതൃ ആരോഗ്യം", "കുട്ടികളുടെ ആരോഗ്യം", "ഹൃദയ ആരോഗ്യം", "വൃക്ക ആരോഗ്യം",
        "ചർമ്മ പ്രശ്നങ്ങൾ", "പ്രമേഹം", "ഉയർന്ന രക്തസമ്മർദ്ദം",
        "പനിയും അണുബാധകളും", "ശ്വാസകോശ പ്രശ്നങ്ങൾ", "കരൾ ആരോഗ്യം",
        "കണ്ണിന്റെ ആരോഗ്യം", "വായയും പല്ലുകളും", "പോഷണം",
        "പ്രതിരോധ കുത്തിവയ്പ്പ്", "മാനസിക ക്ഷേമം", "സ്ത്രീകളുടെ ആരോഗ്യം",
        "പുരുഷന്മാരുടെ ആരോഗ്യം", "മുതിർന്നവരുടെ ആരോഗ്യം", "പ്രഥമ ശുശ്രൂഷ",
        "അടിയന്തര സാഹചര്യം", "പൊതുവായ ലക്ഷണങ്ങൾ",
    ],
    "Kannada": [
        "ತಾಯಿಯ ಆರೋಗ್ಯ", "ಮಕ್ಕಳ ಆರೋಗ್ಯ", "ಹೃದಯದ ಆರೋಗ್ಯ", "ಮೂತ್ರಪಿಂಡದ ಆರೋಗ್ಯ",
        "ಚರ್ಮದ ಸಮಸ್ಯೆಗಳು", "ಮಧುಮೇಹ", "ಅಧಿಕ ರಕ್ತದೊತ್ತಡ", "ಜ್ವರ ಮತ್ತು ಸೋಂಕುಗಳು",
        "ಉಸಿರಾಟದ ಸಮಸ್ಯೆಗಳು", "ಯಕೃತ್ತಿನ ಆರೋಗ್ಯ", "ಕಣ್ಣಿನ ಆರೋಗ್ಯ",
        "ಬಾಯಿ ಮತ್ತು ಹಲ್ಲಿನ ಆರೋಗ್ಯ", "ಪೌಷ್ಟಿಕಾಂಶ", "ಲಸಿಕೆ", "ಮಾನಸಿಕ ಆರೋಗ್ಯ",
        "ಮಹಿಳೆಯರ ಆರೋಗ್ಯ", "ಪುರುಷರ ಆರೋಗ್ಯ", "ವಯೋವೃದ್ಧರ ಆರೋಗ್ಯ", "ಪ್ರಥಮ ಚಿಕಿತ್ಸೆ",
        "ತುರ್ತು ಪರಿಸ್ಥಿತಿ", "ಸಾಮಾನ್ಯ ಲಕ್ಷಣಗಳು",
    ],
    "Bengali": [
        "মাতৃস্বাস্থ্য", "শিশু স্বাস্থ্য", "হৃদযন্ত্রের স্বাস্থ্য", "কিডনি স্বাস্থ্য",
        "ত্বকের সমস্যা", "ডায়াবেটিস", "উচ্চ রক্তচাপ", "জ্বর ও সংক্রমণ",
        "শ্বাসযন্ত্রের সমস্যা", "লিভারের স্বাস্থ্য", "চোখের স্বাস্থ্য",
        "মুখ ও দাঁতের স্বাস্থ্য", "পুষ্টি", "টিকাদান", "মানসিক সুস্থতা",
        "নারী স্বাস্থ্য", "পুরুষ স্বাস্থ্য", "বয়স্কদের স্বাস্থ্য", "প্রাথমিক চিকিৎসা",
        "জরুরি পরিস্থিতি", "সাধারণ উপসর্গ",
    ],
    "Marathi": [
        "माता आरोग्य", "बाल आरोग्य", "हृदयाचे आरोग्य", "मूत्रपिंडाचे आरोग्य",
        "त्वचेच्या समस्या", "मधुमेह", "उच्च रक्तदाब", "ताप आणि संसर्ग",
        "श्वसनाच्या समस्या", "यकृताचे आरोग्य", "डोळ्यांचे आरोग्य",
        "तोंड आणि दातांचे आरोग्य", "पोषण", "लसीकरण", "मानसिक आरोग्य",
        "महिलांचे आरोग्य", "पुरुषांचे आरोग्य", "ज्येष्ठ नागरिकांचे आरोग्य",
        "प्रथमोपचार", "आपत्कालीन परिस्थिती", "सामान्य लक्षणे",
    ],
}

selected_topic_display = st.selectbox(ui["topic"], TOPICS[language])
topic_index = TOPICS[language].index(selected_topic_display)
topic = TOPIC_KEYS[topic_index]

# =========================================================
# PATIENT INFORMATION
# =========================================================

st.subheader("👤 Patient Information")

patient_id = st.text_input(
    "Patient ID",
    placeholder="Example: P001"
)

patient_age = st.number_input(
    "Age",
    min_value=0,
    max_value=120,
    value=0,
    step=1
)

patient_gender = st.selectbox(
    "Gender",
    ["Not specified", "Female", "Male", "Other"]
)

patient_notes = st.text_area(
    "Relevant Patient Notes",
    placeholder="Example: History of diabetes, hypertension, pregnancy, etc.",
    height=100
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

# Only detect a NEW recording.
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
# RED-FLAG DETECTION
# =========================================================

RED_FLAG_GROUPS = {
    "Possible heart emergency": [
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
        "chest pain",
        "pain spreading to arm", "pain spreading to jaw",
        "दिल का दौरा", "हार्ट अटैक", "सीने में तेज दर्द", "सीने में दर्द",
        "सीने में दबाव", "सीने में जकड़न",
        "மாரடைப்பு", "மார்பில் கடுமையான வலி", "மார்பு வலி",
        "గుండెపోటు", "హార్ట్ అటాక్", "తీవ్రమైన ఛాతీ నొప్పి", "ఛాతీ నొప్పి",
        "ഹൃദയാഘാതം", "ഹാർട്ട് അറ്റാക്ക്", "കടുത്ത നെഞ്ചുവേദന", "നെഞ്ചുവേദന",
        "ಹೃದಯಾಘಾತ", "ಹಾರ್ಟ್ ಅಟ್ಯಾಕ್", "ತೀವ್ರವಾದ ಎದೆ ನೋವು", "ಎದೆ ನೋವು",
        "হার্ট অ্যাটাক", "তীব্র বুক ব্যথা", "বুকে ব্যথা",
        "हृदयविकाराचा झटका", "हार्ट अटॅक", "तीव्र छातीत दुखणे", "छातीत दुखणे",
    ],
    "Possible stroke / brain emergency": [
        "stroke", "signs of stroke", "face drooping", "slurred speech",
        "difficulty speaking", "cannot speak", "sudden weakness",
        "sudden numbness", "one sided weakness", "paralysis",
        "sudden confusion", "sudden severe headache", "worst headache",
        "स्ट्रोक", "लकवा", "चेहरा टेढ़ा", "बोलने में दिक्कत", "अचानक कमजोरी",
        "பக்கவாதம்", "முகம் கோணல்", "பேசுவதில் சிரமம்", "திடீர் பலவீனம்",
        "స్ట్రోక్", "పక్షవాతం", "మాట్లాడటంలో ఇబ్బంది", "ఆకస్మిక బలహీనత",
        "പക്ഷാഘാതം", "സംസാരിക്കാൻ ബുദ്ധിമുട്ട്", "പെട്ടെന്നുള്ള ബലഹീനത",
        "ಪಾರ್ಶ್ವವಾಯು", "ಮಾತನಾಡಲು ತೊಂದರೆ", "ಹಠಾತ್ ದೌರ್ಬಲ್ಯ",
        "পক্ষাঘাত", "স্ট্রোক", "কথা বলতে অসুবিধা", "হঠাৎ দুর্বলতা",
    ],
    "Severe breathing emergency": [
        "difficulty breathing", "severe difficulty breathing", "shortness of breath",
        "cannot breathe", "can't breathe", "breathing stopped", "not breathing",
        "blue lips", "blue skin", "choking",
        "सांस लेने में कठिनाई", "सांस लेने में दिक्कत", "सांस नहीं आ रही",
        "सांस नहीं ले पा रहा", "होंठ नीले", "त्वचा नीली",
        "மூச்சு விட முடியவில்லை", "சுவாசிப்பதில் சிரமம்",
        "శ్వాస తీసుకోవడంలో ఇబ్బంది", "ఊపిరి తీసుకోలేకపోతున్నాను",
        "ശ്വസിക്കാൻ ബുദ്ധിമുട്ട്", "ശ്വാസം എടുക്കാൻ കഴിയുന്നില്ല",
        "ಉಸಿರಾಟದ ತೊಂದರೆ", "ಉಸಿರಾಡಲು ಸಾಧ್ಯವಾಗುತ್ತಿಲ್ಲ",
        "শ্বাস নিতে অসুবিধা", "শ্বাস নিতে পারছি না",
        "श्वास घेण्यास त्रास", "श्वास घेता येत नाही",
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
        "bleeding won't stop", "vomiting blood", "coughing blood",
        "blood in vomit", "blood in stool", "black stool",
        "बहुत ज्यादा खून बहना", "तेज रक्तस्राव", "खून नहीं रुक रहा",
        "खून की उल्टी", "खून की खांसी", "मल में खून", "काला मल",
        "கடுமையான இரத்தப்போக்கு", "அதிக இரத்தப்போக்கு", "இரத்தம் நிற்கவில்லை",
        "இரத்த வாந்தி", "இரத்தம் இருமல்", "மலத்தில் இரத்தம்", "கருப்பு மலம்",
        "తీవ్రమైన రక్తస్రావం", "ఎక్కువ రక్తస్రావం", "రక్తస్రావం ఆగడం లేదు",
        "రక్తం వాంతి", "రక్తం దగ్గు", "మలంలో రక్తం", "నల్ల మలం",
        "കടുത്ത രക്തസ്രാവം", "അമിതമായ രക്തസ്രാവം", "രക്തം നിൽക്കുന്നില്ല",
        "രക്തം ഛർദ്ദിക്കുക", "രക്തം ചുമയ്ക്കുക", "മലത്തിൽ രക്തം", "കറുത്ത മലം",
        "ತೀವ್ರ ರಕ್ತಸ್ರಾವ", "ಹೆಚ್ಚಿನ ರಕ್ತಸ್ರಾವ", "ರಕ್ತಸ್ರಾವ ನಿಲ್ಲುತ್ತಿಲ್ಲ",
        "ರಕ್ತ ವಾಂತಿ", "ರಕ್ತ ಕೆಮ್ಮು", "ಮಲದಲ್ಲಿ ರಕ್ತ", "ಕಪ್ಪು ಮಲ",
        "তীব্র রক্তপাত", "অতিরিক্ত রক্তপাত", "রক্তপাত বন্ধ হচ্ছে না",
        "রক্ত বমি", "রক্ত কাশি", "পায়খানায় রক্ত", "কালো পায়খানা",
        "तीव्र रक्तस्त्राव", "जास्त रक्तस्त्राव", "रक्तस्त्राव थांबत नाही",
        "रक्ताची उलटी", "रक्ताची खोकला", "मलात रक्त", "काळा मल",
    ],
    "Unconsciousness / seizure": [
        "unconscious", "loss of consciousness", "not responding",
        "unresponsive", "seizure", "convulsion", "fainted and not waking",
        "बेहोश", "होश नहीं है", "जवाब नहीं दे रहा", "दौरा", "दौरे",
        "மயக்கம்", "நினைவிழந்த", "சுயநினைவு இல்லை", "வலிப்பு",
        "స్పృహ కోల్పోవడం", "స్పృహలో లేరు", "స్పందించడం లేదు", "మూర్ఛ",
        "ബോധരഹിതൻ", "ബോധം നഷ്ടപ്പെടൽ", "പ്രതികരിക്കുന്നില്ല", "അപസ്മാരം",
        "ಪ್ರಜ್ಞಾಹೀನ", "ಪ್ರಜ್ಞೆ ಕಳೆದುಕೊಳ್ಳುವುದು", "ಪ್ರತಿಕ್ರಿಯಿಸುತ್ತಿಲ್ಲ", "ಅಪಸ್ಮಾರ",
        "অজ্ঞান", "চেতনা হারানো", "সাড়া দিচ্ছে না", "খিঁচুনি",
        "बेशुद्ध", "शुद्ध हरपणे", "प्रतिसाद देत नाही", "फिट",
    ],
    "Severe allergic reaction": [
        "anaphylaxis", "severe allergic reaction", "throat swelling",
        "swelling of throat", "swelling of face", "cannot swallow",
        "गंभीर एलर्जी", "गला सूजना", "चेहरा सूजना",
        "கடுமையான ஒவ்வாமை", "தொண்டை வீக்கம்", "முகம் வீக்கம்",
        "తీవ్రమైన అలెర్జీ", "గొంతు వాపు", "ముఖం వాపు",
        "ഗുരുതരമായ അലർജി", "തൊണ്ട വീക്കം", "മുഖം വീക്കം",
        "ತೀವ್ರ ಅಲರ್ಜಿ", "ಗಂಟಲಿನ ಊತ", "ಮುಖದ ಊತ",
        "তীব্র অ্যালার্জি", "গলা ফুলে যাওয়া", "মুখ ফুলে যাওয়া",
        "गंभीर ऍलर्जी", "घशावर सूज", "चेहऱ्यावर सूज",
    ],
    "Severe abdominal / surgical emergency": [
        "severe abdominal pain", "severe stomach pain", "severe belly pain",
        "rigid abdomen", "severe abdominal swelling",
        "पेट में तेज दर्द", "बहुत तेज पेट दर्द",
        "வயிற்றில் கடுமையான வலி", "கடுமையான வயிற்றுவலி",
        "తీవ్రమైన కడుపు నొప్పి",
        "കടുത്ത വയറുവേദന",
        "ತೀವ್ರ ಹೊಟ್ಟೆ ನೋವು",
        "তীব্র পেট ব্যথা",
        "तीव्र पोटदुखी",
    ],
    "Severe headache / brain warning": [
        "severe headache", "worst headache", "sudden severe headache",
        "thunderclap headache",
        "बहुत तेज सिरदर्द", "अचानक बहुत तेज सिरदर्द",
        "கடுமையான தலைவலி", "திடீர் கடுமையான தலைவலி",
        "తీవ్రమైన తలనొప్పి", "ఆకస్మిక తీవ్రమైన తలనొప్పి",
        "കടുത്ത തലവേദന",
        "ತೀವ್ರ ತಲೆನೋವು",
        "তীব্র মাথাব্যথা",
        "तीव्र डोकेदुखी",
    ],
    "Poisoning / envenomation": [
        "poisoning", "poison", "overdose", "chemical poisoning",
        "snake bite", "snakebite", "scorpion sting",
        "जहर", "जहर पी लिया", "सांप ने काटा", "बिच्छू ने काटा",
        "விஷம்", "பாம்பு கடி",
        "విషం", "పాము కాటు",
        "വിഷബാധ", "പാമ്പുകടി",
        "ವಿಷ", "ಹಾವು ಕಡಿತ",
        "বিষক্রিয়া", "সাপের কামড়",
        "विषबाधा", "साप चावणे",
    ],
    "Severe dehydration / heat emergency": [
        "severe dehydration", "cannot keep fluids down", "no urine",
        "heat stroke", "heatstroke", "severe heat exhaustion",
        "गंभीर निर्जलीकरण", "पेशाब नहीं हो रहा", "लू लगना",
        "கடுமையான நீரிழப்பு", "சிறுநீர் வரவில்லை", "வெப்ப அதிர்ச்சி",
        "తీవ్రమైన డీహైడ్రేషన్", "మూత్రం రావడం లేదు", "హీట్ స్ట్రోక్",
        "കടുത്ത നിർജ്ജലീകരണം", "മൂത്രമില്ല", "ഹീറ്റ് സ്ട്രോക്ക്",
        "ತೀವ್ರ ನಿರ್ಜಲೀಕರಣ", "ಮೂತ್ರ ಬರುತ್ತಿಲ್ಲ", "ಹೀಟ್ ಸ್ಟ್ರೋಕ್",
        "তীব্র পানিশূন্যতা", "প্রস্রাব হচ্ছে না", "হিট স্ট্রোক",
        "तीव्र निर्जलीकरण", "लघवी होत नाही", "उष्माघात",
    ],
    "Serious injury / burns / electric shock": [
        "severe burn", "major burn", "deep burn", "electric shock",
        "serious head injury", "head injury with loss of consciousness",
        "major trauma", "severe injury",
        "गंभीर जलना", "बिजली का झटका", "सिर पर गंभीर चोट", "गंभीर चोट",
        "கடுமையான தீக்காயம்", "மின்சார அதிர்ச்சி", "கடுமையான காயம்",
        "తీవ్రమైన కాలిన గాయం", "విద్యుత్ షాక్", "తీవ్రమైన గాయం",
        "ഗുരുതരമായ പൊള്ളൽ", "വൈദ്യുതാഘാതം", "ഗുരുതരമായ പരിക്ക്",
        "ತೀವ್ರ ಸುಟ್ಟ ಗಾಯ", "ವಿದ್ಯುತ್ ಆಘಾತ", "ತೀವ್ರ ಗಾಯ",
        "গুরুতর পোড়া", "বৈদ্যুতিক শক", "গুরুতর আঘাত",
        "गंभीर भाजणे", "वीज लागणे", "गंभीर दुखापत",
    ],
    "Pregnancy / newborn emergency": [
        "pregnancy bleeding", "heavy bleeding during pregnancy",
        "severe pregnancy pain", "seizure during pregnancy",
        "pregnancy seizure", "baby not moving", "baby movement stopped",
        "newborn not breathing", "child not breathing",
        "pregnant and unconscious", "water broke with bleeding",
        "गर्भावस्था में रक्तस्राव", "गर्भावस्था में तेज दर्द",
        "गर्भ में बच्चा नहीं हिल रहा", "गर्भावस्था में दौरा",
        "கர்ப்ப கால இரத்தப்போக்கு", "கர்ப்ப கால கடுமையான வலி",
        "குழந்தை அசைவில்லை", "பிறந்த குழந்தை மூச்சுவிடவில்லை",
        "గర్భధారణలో రక్తస్రావం", "గర్భధారణలో తీవ్రమైన నొప్పి",
        "బిడ్డ కదలడం లేదు", "నవజాత శిశువు శ్వాస తీసుకోవడం లేదు",
        "ഗർഭകാല രക്തസ്രാവം", "ഗർഭകാല കടുത്ത വേദന",
        "കുഞ്ഞ് ചലിക്കുന്നില്ല", "നവജാത ശിശു ശ്വസിക്കുന്നില്ല",
        "ಗರ್ಭಾವಸ್ಥೆಯಲ್ಲಿ ರಕ್ತಸ್ರಾವ", "ಗರ್ಭಾವಸ್ಥೆಯಲ್ಲಿ ತೀವ್ರ ನೋವು",
        "ಮಗು ಚಲಿಸುತ್ತಿಲ್ಲ", "ನವಜಾತ ಶಿಶು ಉಸಿರಾಡುತ್ತಿಲ್ಲ",
        "গর্ভাবস্থায় রক্তপাত", "গর্ভাবস্থায় তীব্র ব্যথা",
        "শিশু নড়ছে না", "নবজাতক শ্বাস নিচ্ছে না",
        "गर्भावस्थेत रक्तस्त्राव", "गर्भावस्थेत तीव्र वेदना",
        "बाळाची हालचाल नाही", "नवजात बाळ श्वास घेत नाही",
    ],
    "Mental health crisis": [
        "suicidal", "suicide", "suicidal thoughts", "want to die",
        "self harm", "self-harm", "kill myself", "harm myself",
        "आत्महत्या", "आत्महत्या के विचार", "खुद को नुकसान", "मरना चाहता हूं",
        "தற்கொலை", "தற்கொலை எண்ணம்", "சுய காயம்",
        "ఆత్మహత్య", "ఆత్మహత్య ఆలోచనలు", "స్వీయ హాని",
        "ആത്മഹത്യ", "ആത്മഹത്യ ചിന്തകൾ", "സ്വയം ഉപദ്രവിക്കൽ",
        "ಆತ್ಮಹತ್ಯೆ", "ಆತ್ಮಹತ್ಯೆ ಆಲೋಚನೆಗಳು", "ಸ್ವಯಂ ಹಾನಿ",
        "আত্মহত্যা", "আত্মহত্যার চিন্তা", "নিজেকে আঘাত করা",
        "आत्महत्या", "आत्महत्येचे विचार", "स्वतःला इजा करणे",
    ],
}

RED_FLAG_GROUPS.update({
    "Possible severe infection / sepsis": [
        "sepsis", "septic shock", "very confused with fever",
        "confusion with fever", "rapid breathing with fever",
        "very sick with fever",
        "बहुत तेज बुखार और भ्रम", "बुखार के साथ बेहोशी",
    ],
    "Possible diabetic emergency": [
        "severe low blood sugar", "very low blood sugar",
        "hypoglycemia with unconsciousness", "diabetic coma",
        "very high blood sugar with vomiting",
        "मधुमेह में बेहोशी", "बहुत कम शुगर", "बहुत ज्यादा शुगर और उल्टी",
    ],
    "Possible hypertensive emergency": [
        "very high blood pressure with chest pain",
        "very high blood pressure with severe headache",
        "high bp with chest pain", "high bp with weakness",
        "बहुत ज्यादा रक्तचाप और सीने में दर्द",
        "बहुत ज्यादा बीपी और तेज सिरदर्द",
    ],
    "Possible severe asthma / airway emergency": [
        "severe asthma attack", "asthma attack cannot speak",
        "wheezing and cannot breathe", "breathing too difficult to speak",
        "गंभीर अस्थमा का दौरा", "अस्थमा में सांस नहीं आ रही",
    ],
    "Possible meningitis / serious brain infection": [
        "stiff neck with fever", "fever and stiff neck",
        "severe headache with stiff neck",
        "बुखार और गर्दन अकड़ना", "तेज सिरदर्द और गर्दन अकड़ना",
    ],
    "Possible kidney / urinary emergency": [
        "no urine", "unable to pass urine", "severe flank pain with fever",
        "severe kidney pain with fever", "पेशाब बिल्कुल नहीं हो रहा",
        "बुखार के साथ तेज कमर दर्द",
    ],
    "Possible eye emergency": [
        "sudden loss of vision", "sudden blindness",
        "chemical in eye with severe pain",
        "अचानक दिखाई नहीं दे रहा", "अचानक दृष्टि चली गई",
    ],
})

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
def detect_multilingual_emergency_patterns(text):
    """
    Detect common emergency symptom combinations across
    English, Hindi, Tamil, Telugu, Malayalam, Kannada,
    Bengali, and Marathi.

# =========================================================
# FIRST-AID DETECTION
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
    ],
}
def detect_first_aid(text):
    """Detect whether the question matches a first-aid situation."""
    if not text:
        return None

    normalized = normalize_text(text)

    for guide_name, keywords in FIRST_AID_GUIDES.items():
        for keyword in keywords:
            if normalize_text(keyword) in normalized:
                return guide_name

    return None
# =========================================================
# FIRST-AID VISUAL GUIDE
# =========================================================

def show_first_aid_guide(language, first_aid_type):

    if first_aid_type == "Severe Bleeding":

        st.image(
            "first_aid_severe_bleeding.png",
            width=350
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
            width=350
        )

        st.error("🔥 Burn")

        st.write(
            "• Cool the burn with clean, cool running water.\n"
            "• Do not apply ice, toothpaste, or oil.\n"
            "• Get medical help for serious burns."
        )


def normalize_text(text):
    """Normalize text for reliable multilingual keyword matching."""
    text = str(text).lower().replace("’", "'")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def collapse_repeated_letters(text):
    """Reduce accidental repeated letters in typed English words."""
    return re.sub(r"(.)\1{1,}", r"\1", normalize_text(text))


def detect_red_flags(text):
    """Return emergency categories and matched terms."""
    if not text:
        return []

    normalized = normalize_text(text)
    detected = []
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
                ["possible severe/heavy bleeding"]
            )
        )

    for category, keywords in RED_FLAG_GROUPS.items():
        exact_matches = []

        for keyword in keywords:
            if normalize_text(keyword) in normalized:
                exact_matches.append(keyword)

        if exact_matches:
            detected.append((category, exact_matches[:3]))

    english_words = re.findall(r"[a-z]+(?:'[a-z]+)?", normalized)
    english_text = " ".join(english_words)
    collapsed_text = collapse_repeated_letters(english_text)

    for phrase in FUZZY_RED_FLAGS:
        phrase = normalize_text(phrase)
        collapsed_phrase = collapse_repeated_letters(phrase)

        if collapsed_phrase in collapsed_text:
            for category, keywords in RED_FLAG_GROUPS.items():
                normalized_keywords = [normalize_text(k) for k in keywords]

                if phrase in normalized_keywords:
                    existing = next(
                        (item for item in detected if item[0] == category),
                        None,
                    )

                    if existing is None:
                        detected.append(
                            (category, [f"possible match: {phrase}"])
                        )

                    break

            continue

        phrase_words = collapsed_phrase.split()
        text_words = collapsed_text.split()
        best_ratio = 0.0

        if len(text_words) >= len(phrase_words):
            n = len(phrase_words)

            for i in range(len(text_words) - n + 1):
                window = " ".join(text_words[i:i + n])

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
                normalized_keywords = [normalize_text(k) for k in keywords]

                if phrase in normalized_keywords:
                    existing = next(
                        (item for item in detected if item[0] == category),
                        None,
                    )

                    if existing is None:
                        detected.append(
                            (category, [f"possible match: {phrase}"])
                        )

                    break

    return detected


# =========================================================
# RED FLAG UI
# =========================================================

RED_FLAG_TITLE = {
    "English": "🚨 POSSIBLE RED FLAG / URGENT WARNING",
    "Hindi": "🚨 संभावित गंभीर चेतावनी / तत्काल चिकित्सा सहायता",
    "Tamil": "🚨 சாத்தியமான ஆபத்து அறிகுறி / அவசர எச்சரிக்கை",
    "Telugu": "🚨 ప్రమాద సూచన / అత్యవసర హెచ్చరిక",
    "Malayalam": "🚨 സാധ്യതയുള്ള അപകട സൂചന / അടിയന്തര മുന്നറിയിപ്പ്",
    "Kannada": "🚨 ಸಾಧ್ಯವಾದ ಅಪಾಯದ ಸೂಚನೆ / ತುರ್ತು ಎಚ್ಚರಿಕೆ",
    "Bengali": "🚨 সম্ভাব্য বিপদের লক্ষণ / জরুরি সতর্কতা",
    "Marathi": "🚨 संभाव्य धोक्याची चिन्हे / तातडीची सूचना",
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
    """Show emergency information with clickable call buttons."""

    st.error("🚨 EMERGENCY")

    # -----------------------------------------------------
    # EMERGENCY MESSAGE
    # -----------------------------------------------------

    if language == "Tamil":
        st.markdown("## 🚨 அவசர நிலை")
        st.markdown("### 🏥 அருகிலுள்ள மருத்துவமனைக்குச் செல்லுங்கள்")
        st.markdown("### ⚠️ காத்திருக்க வேண்டாம்")

    elif language == "Hindi":
        st.markdown("## 🚨 आपातकाल")
        st.markdown("### 🏥 निकटतम अस्पताल जाएं")
        st.markdown("### ⚠️ इंतज़ार न करें")

    elif language == "Telugu":
        st.markdown("## 🚨 అత్యవసర పరిస్థితి")
        st.markdown("### 🏥 సమీప ఆసుపత్రికి వెళ్లండి")
        st.markdown("### ⚠️ ఆలస్యం చేయవద్దు")

    elif language == "Malayalam":
        st.markdown("## 🚨 അടിയന്തര സാഹചര്യം")
        st.markdown("### 🏥 അടുത്തുള്ള ആശുപത്രിയിലേക്ക് പോകുക")
        st.markdown("### ⚠️ കാത്തിരിക്കരുത്")

    elif language == "Kannada":
        st.markdown("## 🚨 ತುರ್ತು ಪರಿಸ್ಥಿತಿ")
        st.markdown("### 🏥 ಹತ್ತಿರದ ಆಸ್ಪತ್ರೆಗೆ ಹೋಗಿ")
        st.markdown("### ⚠️ ಕಾಯಬೇಡಿ")

    elif language == "Bengali":
        st.markdown("## 🚨 জরুরি পরিস্থিতি")
        st.markdown("### 🏥 নিকটস্থ হাসপাতালে যান")
        st.markdown("### ⚠️ অপেক্ষা করবেন না")

    elif language == "Marathi":
        st.markdown("## 🚨 आपत्कालीन परिस्थिती")
        st.markdown("### 🏥 जवळच्या रुग्णालयात जा")
        st.markdown("### ⚠️ विलंब करू नका")

    else:
        st.markdown("## 🚨 EMERGENCY")
        st.markdown("### 🏥 Go to the nearest hospital")
        st.markdown("### ⚠️ DO NOT WAIT")

    # -----------------------------------------------------
    # EMERGENCY BUTTON TEST
    # -----------------------------------------------------

    st.markdown("### 🚨 Emergency Contacts")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("📞 Call 112", key="emergency_112", use_container_width=True):
            st.info("📞 Please call 112 from your phone.")

    with col2:
        if st.button("🚑 Call 108", key="emergency_108", use_container_width=True):
            st.info("🚑 Please call 108 from your phone.")

# =========================================================
# ASK SAATHI
# =========================================================

if st.button(
    ui["button"],
    type="primary",
    key="ask_saathi_button",
):

    final_question = question.strip()

    # -----------------------------------------------------
    # VOICE TRANSCRIPTION: ONLY ON BUTTON CLICK
    # -----------------------------------------------------

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

            if voice_response and voice_response.text:
                final_question = voice_response.text.strip()
              

                st.session_state.voice_question = final_question
                st.session_state.last_audio_bytes = new_audio_bytes

                st.success("🎤 Voice detected")
                st.write("**You said:**")
                st.write(final_question)

        except Exception as e:
            show_gemini_error(e)

    # -----------------------------------------------------
    # PATIENT VISIT RECORD
    # -----------------------------------------------------

    patient_record = {
        "patient_id": patient_id.strip() if patient_id else "",
        "age": patient_age,
        "gender": patient_gender,
        "notes": patient_notes.strip() if patient_notes else "",
        "health_topic": topic,
        "language": language,
        "question": final_question,
    }
    
    # -----------------------------------------------------
    # USE LAST SUCCESSFUL VOICE TRANSCRIPTION
    # -----------------------------------------------------

    if not final_question and st.session_state.voice_question:
        final_question = st.session_state.voice_question.strip()

        # Clear the old transcription so it is not reused
        # accidentally on a later button click.
        st.session_state.voice_question = ""

    # -----------------------------------------------------
    # EMPTY QUESTION
    # -----------------------------------------------------

    if not final_question:
        st.warning(ui["empty"])

    else:
        st.info(
            f"📝 Question received:\n\n{final_question}"
        )

              # -------------------------------------------------
        # LOCAL RED-FLAG CHECK
        # -------------------------------------------------

        detected_flags = detect_red_flags(final_question)
        first_aid_type = detect_first_aid(final_question)

        # -------------------------------------------------
        # FIRST-AID GUIDE
        # -------------------------------------------------

        if first_aid_type:
            show_first_aid_guide(
                language,
                first_aid_type
            )

        # -------------------------------------------------
        # EMERGENCY MODE
        # -------------------------------------------------

        if detected_flags:
           show_emergency_alert(language)

           st.markdown(
                f"### {RED_FLAG_TITLE[language]}"
            )

           st.warning(
                f"🚨 {RED_FLAG_MESSAGE[language]}"
            )

           st.markdown("### 🆘 What to do now")

           if language == "Tamil":
                st.write(
                    "• நபரை தனியாக விடாதீர்கள்.\n"
                    "• உடனடி மருத்துவ உதவியை பெறுங்கள்.\n"
                    "• இந்தியாவில் 112 அல்லது உள்ளூர் ஆம்புலன்ஸ் சேவையை தொடர்பு கொள்ளுங்கள்.\n"
                    "• அருகிலுள்ள மருத்துவமனைக்கு செல்லுங்கள்."
                )

           elif language == "Hindi":
                st.write(
                    "• व्यक्ति को अकेला न छोड़ें।\n"
                    "• तुरंत चिकित्सा सहायता लें।\n"
                    "• भारत में 112 या स्थानीय एम्बुलेंस सेवा से संपर्क करें।\n"
                    "• निकटतम अस्पताल जाएं।"
                )

           else:
                st.write(
                    "• Do not leave the person alone.\n"
                    "• Seek immediate medical help.\n"
                    "• In India, call 112 or the local ambulance service.\n"
                    "• Go to the nearest appropriate hospital."
                )

           st.markdown("### 🚨 Warning signs detected")

           for category, matches in detected_flags:
                st.markdown(
                    f"**{category}** — {', '.join(matches)}"
                )

           st.error(
                "⚠️ Do not wait for Saathi's AI response if the person "
                "has a serious or life-threatening condition."
            )

           st.info(
                "🛑 Emergency detected — normal AI guidance will be skipped."
            )

           st.stop()

        # -------------------------------------------------
        # GEMINI PROMPT
        # -------------------------------------------------

        detected_text = (
            "; ".join(
                f"{category}: {', '.join(matches)}"
                for category, matches in detected_flags
            )
            if detected_flags
            else "No local red-flag keyword was detected."
        )
        prompt = f"""
You are Saathi AI Health Agent.

You are a fast, practical digital health assistant designed for
frontline health workers such as ASHA and ANM workers in India.

The health worker may have only a few seconds to read your response.

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
{detected_text}

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

If the local safety screen detected a red flag:

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
        # -------------------------------------------------
        # GEMINI RESPONSE
        # -------------------------------------------------

        try:
            with st.spinner("🩺 Saathi is preparing guidance..."):
                response = call_gemini(prompt)

            if response and response.text:
                st.success(ui["guidance"])
                st.write(response.text)
            else:
                st.warning(
                    "⚠️ Saathi could not generate a response right now."
                )

        except Exception as e:
            # Local red-flag screening remains usable even
            # when Gemini is unavailable or rate-limited.
            show_local_fallback(
                language,
                detected_flags,
            )
            show_gemini_error(e)
