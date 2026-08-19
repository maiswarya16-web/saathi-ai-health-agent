import streamlit as st
from google import genai
import time
import re

# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Saathi AI Health Agent",
    page_icon="🩺",
    layout="centered"
)


# =========================================================
# GEMINI API CLIENT
# =========================================================

client = genai.Client(
    api_key=st.secrets["GEMINI_API_KEY"]
)
# =========================================================
# GEMINI SAFE RESPONSE WITH RETRY + FALLBACK
# =========================================================

PRIMARY_MODEL = "gemini-3.6-flash"
FALLBACK_MODEL = "gemini-2.5-flash"


def generate_gemini_response(prompt, max_retries=3):

    models_to_try = [
        PRIMARY_MODEL,
        FALLBACK_MODEL
    ]

    last_error = None

    for model_name in models_to_try:

        for attempt in range(max_retries):

            try:

                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt
                )

                if response and response.text:
                    return response.text

            except Exception as e:

                last_error = e
                error_text = str(e).lower()

                # Temporary Gemini problems
                temporary_error = (
                    "503" in error_text
                    or "unavailable" in error_text
                    or "429" in error_text
                    or "resource_exhausted" in error_text
                    or "high demand" in error_text
                    or "overloaded" in error_text
                )

                if temporary_error:

                    # Exponential backoff
                    wait_time = 2 ** attempt

                    time.sleep(wait_time)

                    continue

                # Other errors should not be retried repeatedly
                break

    return None

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
        "empty": "Please enter or speak a health question first."
    },

    "Hindi": {
        "topic": "स्वास्थ्य विषय चुनें:",
        "question": "साथी से स्वास्थ्य संबंधी प्रश्न पूछें:",
        "placeholder": "उदाहरण: गर्भावस्था के दौरान किन चेतावनी संकेतों पर ध्यान देना चाहिए?",
        "button": "साथी से पूछें",
        "guidance": "🩺 साथी की सलाह",
        "empty": "कृपया पहले अपना स्वास्थ्य प्रश्न लिखें या बोलें।"
    },

    "Tamil": {
        "topic": "சுகாதார தலைப்பைத் தேர்ந்தெடுக்கவும்:",
        "question": "சாத்தியிடம் சுகாதார கேள்வியைக் கேளுங்கள்:",
        "placeholder": "உதாரணம்: கர்ப்ப காலத்தில் கவனிக்க வேண்டிய ஆபத்து அறிகுறிகள் என்ன?",
        "button": "சாத்தியிடம் கேளுங்கள்",
        "guidance": "🩺 சாத்தியின் வழிகாட்டுதல்",
        "empty": "முதலில் உங்கள் சுகாதார கேள்வியை எழுதவும் அல்லது பேசவும்."
    },

    "Telugu": {
        "topic": "ఆరోగ్య అంశాన్ని ఎంచుకోండి:",
        "question": "సాతీని ఆరోగ్య ప్రశ్న అడగండి:",
        "placeholder": "ఉదాహరణ: గర్భధారణ సమయంలో ఏ ప్రమాద సంకేతాలను గమనించాలి?",
        "button": "సాతీని అడగండి",
        "guidance": "🩺 సాతీ మార్గదర్శకం",
        "empty": "దయచేసి ముందుగా మీ ఆరోగ్య ప్రశ్నను రాయండి లేదా మాట్లాడండి."
    },

    "Malayalam": {
        "topic": "ആരോഗ്യ വിഷയം തിരഞ്ഞെടുക്കുക:",
        "question": "സാത്തിയോട് ആരോഗ്യ ചോദ്യം ചോദിക്കുക:",
        "placeholder": "ഉദാഹരണം: ഗർഭകാലത്ത് ശ്രദ്ധിക്കേണ്ട അപകട സൂചനകൾ എന്തൊക്കെയാണ്?",
        "button": "സാത്തിയോട് ചോദിക്കുക",
        "guidance": "🩺 സാത്തിയുടെ മാർഗനിർദ്ദേശം",
        "empty": "ദയവായി ആദ്യം നിങ്ങളുടെ ആരോഗ്യ ചോദ്യം എഴുതുകയോ സംസാരിക്കുകയോ ചെയ്യുക."
    },

    "Kannada": {
        "topic": "ಆರೋಗ್ಯ ವಿಷಯವನ್ನು ಆಯ್ಕೆಮಾಡಿ:",
        "question": "ಸಾಥಿಗೆ ಆರೋಗ್ಯ ಪ್ರಶ್ನೆಯನ್ನು ಕೇಳಿ:",
        "placeholder": "ಉದಾಹರಣೆ: ಗರ್ಭಾವಸ್ಥೆಯಲ್ಲಿ ಯಾವ ಅಪಾಯದ ಸೂಚನೆಗಳನ್ನು ಗಮನಿಸಬೇಕು?",
        "button": "ಸಾಥಿಯನ್ನು ಕೇಳಿ",
        "guidance": "🩺 ಸಾಥಿಯ ಮಾರ್ಗದರ್ಶನ",
        "empty": "ದಯವಿಟ್ಟು ಮೊದಲು ನಿಮ್ಮ ಆರೋಗ್ಯ ಪ್ರಶ್ನೆಯನ್ನು ಬರೆಯಿರಿ ಅಥವಾ ಮಾತನಾಡಿ."
    },

    "Bengali": {
        "topic": "স্বাস্থ্য বিষয় নির্বাচন করুন:",
        "question": "সাথীকে স্বাস্থ্য সম্পর্কিত প্রশ্ন করুন:",
        "placeholder": "উদাহরণ: গর্ভাবস্থায় কোন বিপদের লক্ষণগুলির দিকে নজর রাখা উচিত?",
        "button": "সাথীকে জিজ্ঞাসা করুন",
        "guidance": "🩺 সাথীর নির্দেশনা",
        "empty": "দয়া করে প্রথমে আপনার স্বাস্থ্য প্রশ্ন লিখুন বা বলুন।"
    },

    "Marathi": {
        "topic": "आरोग्य विषय निवडा:",
        "question": "साथीला आरोग्याशी संबंधित प्रश्न विचारा:",
        "placeholder": "उदाहरण: गर्भधारणेदरम्यान कोणती धोक्याची चिन्हे लक्षात घ्यावीत?",
        "button": "साथीला विचारा",
        "guidance": "🩺 साथीचे मार्गदर्शन",
        "empty": "कृपया प्रथम तुमचा आरोग्य प्रश्न लिहा किंवा बोला."
    }
}


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
# LANGUAGE
# =========================================================

language = st.selectbox(
    "🌐 Select your language:",
    [
        "English",
        "Hindi",
        "Tamil",
        "Telugu",
        "Malayalam",
        "Kannada",
        "Bengali",
        "Marathi"
    ]
)

ui = UI_TEXT[language]


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
    "General Symptoms"

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
        "सामान्य लक्षण"
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
        "பொதுவான அறிகுறிகள்"
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
        "సాధారణ లక్షణాలు"
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
        "പൊതുവായ ലക്ഷണങ്ങൾ"
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
        "ಸಾಮಾನ್ಯ ಲಕ್ಷಣಗಳು"
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
        "সাধারণ উপসর্গ"
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
        "सामान्य लक्षणे"
    ]
}


# =========================================================
# TOPIC SELECTION
# =========================================================

selected_topic_display = st.selectbox(
    ui["topic"],
    TOPICS[language]
)

topic_index = TOPICS[language].index(selected_topic_display)

topic = TOPIC_KEYS[topic_index]


# =========================================================
# TEXT QUESTION
# =========================================================

question = st.text_area(
    ui["question"],
    placeholder=ui["placeholder"],
    height=120
)


# =========================================================
# VOICE INPUT
# =========================================================

st.subheader("🎤 Voice Input")

st.write(
    "Tap the microphone and speak your health question."
)

audio_value = st.audio_input(
    "Record your question:"
)

voice_question = ""


if audio_value is not None:

    try:

        audio_bytes = audio_value.read()

        if audio_bytes:

            # Try to get the actual MIME type from Streamlit.
            audio_mime = getattr(
                audio_value,
                "type",
                "audio/wav"
            )

            voice_response = client.models.generate_content(

                model=PRIMARY_MODEL,

                contents=[
                    {
                        "role": "user",
                        "parts": [

                            {
                                "text": f"""
Transcribe this audio recording.

The speaker may use:
English, Hindi, Tamil, Telugu,
Malayalam, Kannada, Bengali, or Marathi.

Return ONLY the spoken words.

Do not translate.
Do not summarize.
Do not explain.

Language context:
{language}
"""
                            },

                            {
                                "inline_data": {
                                    "mime_type": audio_mime,
                                    "data": audio_bytes
                                }
                            }

                        ]
                    }
                ]
            )

            if voice_response.text:

                voice_question = voice_response.text.strip()

                st.success("🎤 Voice detected")

                st.write("**You said:**")

                st.write(voice_question)

    except Exception as e:

        st.warning(
            "⚠️ Voice transcription is temporarily unavailable. "
            "You can type the question instead."
        )


# =========================================================
# RED FLAG DATABASE
# =========================================================
#
# IMPORTANT:
# This is symptom/emergency detection, NOT diagnosis.
#
# We include disease names AND emergency symptoms because
# users may type "heart attack" without typing "chest pain".
# =========================================================

RED_FLAGS = [

    # =====================================================
    # HEART / CARDIAC EMERGENCIES
    # =====================================================

    "heart attack",
    "heart attack symptoms",
    "myocardial infarction",
    "cardiac arrest",
    "cardiac emergency",
    "heart failure emergency",
    "severe chest pain",
    "chest pain",
    "pressure in chest",
    "tightness in chest",
    "heaviness in chest",
    "crushing chest pain",
    "pain spreading to arm",
    "pain spreading to jaw",
    "pain spreading to shoulder",
    "cold sweat with chest pain",
    "palpitations with fainting",

    # Hindi
    "हार्ट अटैक",
    "दिल का दौरा",
    "हृदयाघात",
    "सीने में तेज दर्द",
    "सीने में दर्द",
    "सीने में दबाव",
    "सीने में जकड़न",
    "बांह में फैलता दर्द",
    "जबड़े में फैलता दर्द",

    # Tamil
    "மாரடைப்பு",
    "இதயத் தாக்குதல்",
    "மார்பில் கடுமையான வலி",
    "மார்பு வலி",
    "மார்பில் அழுத்தம்",
    "மார்பு இறுக்கம்",

    # Telugu
    "గుండెపోటు",
    "హార్ట్ అటాక్",
    "తీవ్రమైన ఛాతీ నొప్పి",
    "ఛాతీ నొప్పి",
    "ఛాతీలో ఒత్తిడి",
    "ఛాతీ బిగుతు",

    # Malayalam
    "ഹൃദയാഘാതം",
    "ഹാർട്ട് അറ്റാക്ക്",
    "കടുത്ത നെഞ്ചുവേദന",
    "നെഞ്ചുവേദന",
    "നെഞ്ചിൽ സമ്മർദ്ദം",
    "നെഞ്ച് മുറുക്കം",

    # Kannada
    "ಹೃದಯಾಘಾತ",
    "ಹಾರ್ಟ್ ಅಟ್ಯಾಕ್",
    "ತೀವ್ರವಾದ ಎದೆ ನೋವು",
    "ಎದೆ ನೋವು",
    "ಎದೆಯಲ್ಲಿ ಒತ್ತಡ",
    "ಎದೆ ಬಿಗಿತ",

    # Bengali
    "হার্ট অ্যাটাক",
    "হৃদরোগে আক্রমণ",
    "তীব্র বুক ব্যথা",
    "বুকে ব্যথা",
    "বুকে চাপ",
    "বুক ধড়ফড়",

    # Marathi
    "हृदयविकाराचा झटका",
    "हार्ट अटॅक",
    "तीव्र छातीत दुखणे",
    "छातीत दुखणे",
    "छातीत दडपण",
    "छातीत घट्टपणा",


    # =====================================================
    # STROKE
    # =====================================================

    "stroke",
    "brain stroke",
    "ischemic stroke",
    "hemorrhagic stroke",
    "face drooping",
    "facial drooping",
    "sudden weakness",
    "one sided weakness",
    "one side weakness",
    "arm weakness",
    "leg weakness",
    "slurred speech",
    "difficulty speaking",
    "unable to speak",
    "sudden confusion",
    "sudden vision loss",
    "sudden severe headache",

    # Hindi
    "स्ट्रोक",
    "ब्रेन स्ट्रोक",
    "लकवा",
    "चेहरा टेढ़ा",
    "अचानक कमजोरी",
    "एक तरफ कमजोरी",
    "बोलने में दिक्कत",
    "अचानक भ्रम",
    "अचानक दिखाई न देना",

    # Tamil
    "பக்கவாதம்",
    "மூளை பக்கவாதம்",
    "முகம் கோணல்",
    "திடீர் பலவீனம்",
    "ஒரு பக்க பலவீனம்",
    "பேசுவதில் சிரமம்",
    "திடீர் குழப்பம்",

    # Telugu
    "స్ట్రోక్",
    "బ్రెయిన్ స్ట్రోక్",
    "పక్షవాతం",
    "ముఖం వంగిపోవడం",
    "ఆకస్మిక బలహీనత",
    "ఒక వైపు బలహీనత",
    "మాట్లాడటంలో ఇబ్బంది",

    # Malayalam
    "സ്ട്രോക്ക്",
    "ബ്രെയിൻ സ്ട്രോക്ക്",
    "പക്ഷാഘാതം",
    "മുഖം കോടുക",
    "പെട്ടെന്നുള്ള ബലഹീനത",
    "സംസാരിക്കാൻ ബുദ്ധിമുട്ട്",

    # Kannada
    "ಸ್ಟ್ರೋಕ್",
    "ಬ್ರೈನ್ ಸ್ಟ್ರೋಕ್",
    "ಪಾರ್ಶ್ವವಾಯು",
    "ಮುಖ ವಾಲುವುದು",
    "ಹಠಾತ್ ದೌರ್ಬಲ್ಯ",
    "ಒಂದು ಬದಿಯ ದೌರ್ಬಲ್ಯ",
    "ಮಾತನಾಡಲು ತೊಂದರೆ",

    # Bengali
    "স্ট্রোক",
    "ব্রেন স্ট্রোক",
    "পক্ষাঘাত",
    "মুখ বেঁকে যাওয়া",
    "হঠাৎ দুর্বলতা",
    "এক পাশ দুর্বল",
    "কথা বলতে অসুবিধা",

    # Marathi
    "स्ट्रोक",
    "ब्रेन स्ट्रोक",
    "पक्षाघात",
    "चेहरा वाकडा",
    "अचानक अशक्तपणा",
    "एका बाजूची कमजोरी",
    "बोलण्यात अडचण",


    # =====================================================
    # BREATHING EMERGENCIES
    # =====================================================

    "difficulty breathing",
    "severe difficulty breathing",
    "cannot breathe",
    "can't breathe",
    "shortness of breath",
    "severe breathlessness",
    "choking",
    "not breathing",
    "stopped breathing",
    "blue lips",
    "blue skin",
    "severe asthma attack",
    "asthma attack",

    # Hindi
    "सांस लेने में कठिनाई",
    "सांस लेने में दिक्कत",
    "सांस नहीं आ रही",
    "सांस फूलना",
    "दम घुटना",
    "सांस बंद",
    "होंठ नीले",

    # Tamil
    "சுவாசிப்பதில் சிரமம்",
    "மூச்சு விடுவதில் சிரமம்",
    "மூச்சு விட முடியவில்லை",
    "மூச்சுத்திணறல்",
    "மூச்சு நின்றுவிட்டது",

    # Telugu
    "శ్వాస తీసుకోవడంలో ఇబ్బంది",
    "ఊపిరి తీసుకోవడం కష్టం",
    "ఊపిరి తీసుకోలేకపోతున్నాను",
    "ఊపిరి ఆడటం లేదు",
    "ఊపిరి ఆగిపోయింది",

    # Malayalam
    "ശ്വസിക്കാൻ ബുദ്ധിമുട്ട്",
    "ശ്വാസം എടുക്കാൻ കഴിയുന്നില്ല",
    "ശ്വാസം മുട്ടൽ",
    "ശ്വാസം നിലച്ചു",

    # Kannada
    "ಉಸಿರಾಟದ ತೊಂದರೆ",
    "ಉಸಿರಾಡಲು ಸಾಧ್ಯವಾಗುತ್ತಿಲ್ಲ",
    "ಉಸಿರುಗಟ್ಟುವಿಕೆ",
    "ಉಸಿರು ನಿಂತಿದೆ",

    # Bengali
    "শ্বাস নিতে অসুবিধা",
    "শ্বাস নিতে পারছি না",
    "শ্বাসকষ্ট",
    "শ্বাস বন্ধ",

    # Marathi
    "श्वास घेण्यास त्रास",
    "श्वास घेता येत नाही",
    "श्वास लागणे",
    "श्वास बंद",


    # =====================================================
    # UNCONSCIOUSNESS / SEIZURE
    # =====================================================

    "unconscious",
    "unresponsive",
    "not responding",
    "loss of consciousness",
    "fainted and not waking",
    "seizure",
    "convulsion",
    "fits",
    "continuous seizure",
    "repeated seizures",

    # Hindi
    "बेहोश",
    "होश नहीं है",
    "प्रतिक्रिया नहीं दे रहा",
    "दौरा",
    "दौरे",
    "फिट",

    # Tamil
    "நினைவிழந்த",
    "சுயநினைவு இல்லை",
    "வலிப்பு",
    "தொடர் வலிப்பு",

    # Telugu
    "స్పృహ కోల్పోవడం",
    "స్పృహలో లేరు",
    "మూర్ఛ",
    "ఫిట్స్",

    # Malayalam
    "ബോധരഹിതൻ",
    "ബോധം നഷ്ടപ്പെടൽ",
    "അപസ്മാരം",
    "വലിപ്പ്",

    # Kannada
    "ಪ್ರಜ್ಞಾಹೀನ",
    "ಪ್ರಜ್ಞೆ ಕಳೆದುಕೊಳ್ಳುವುದು",
    "ಅಪಸ್ಮಾರ",
    "ಫಿಟ್ಸ್",

    # Bengali
    "অজ্ঞান",
    "চেতনা হারানো",
    "খিঁচুনি",

    # Marathi
    "बेशुद्ध",
    "शुद्ध हरपणे",
    "फिट",
    "झटके",


    # =====================================================
    # SEVERE BLEEDING
    # =====================================================

    "severe bleeding",
    "heavy bleeding",
    "uncontrolled bleeding",
    "bleeding won't stop",
    "vomiting blood",
    "coughing blood",
    "blood in vomit",
    "blood in stool",
    "black stool with weakness",

    # Hindi
    "बहुत ज्यादा खून बहना",
    "तेज रक्तस्राव",
    "खून बंद नहीं हो रहा",
    "खून की उल्टी",
    "खून वाली उल्टी",
    "खून की खांसी",

    # Tamil
    "கடுமையான இரத்தப்போக்கு",
    "அதிக இரத்தப்போக்கு",
    "இரத்தம் நிற்கவில்லை",
    "இரத்த வாந்தி",
    "இரத்தம் இருமல்",

    # Telugu
    "తీవ్రమైన రక్తస్రావం",
    "ఎక్కువ రక్తస్రావం",
    "రక్తం ఆగడం లేదు",
    "రక్తం వాంతి",
    "రక్తం దగ్గు",

    # Malayalam
    "കടുത്ത രക്തസ്രാവം",
    "അമിതമായ രക്തസ്രാവം",
    "രക്തം നിൽക്കുന്നില്ല",
    "രക്തം ഛർദ്ദിക്കുക",
    "രക്തം ചുമയ്ക്കുക",

    # Kannada
    "ತೀವ್ರ ರಕ್ತಸ್ರಾವ",
    "ಹೆಚ್ಚಿನ ರಕ್ತಸ್ರಾವ",
    "ರಕ್ತಸ್ರಾವ ನಿಲ್ಲುತ್ತಿಲ್ಲ",
    "ರಕ್ತ ವಾಂತಿ",
    "ರಕ್ತ ಕೆಮ್ಮು",

    # Bengali
    "তীব্র রক্তপাত",
    "অতিরিক্ত রক্তপাত",
    "রক্তপাত বন্ধ হচ্ছে না",
    "রক্ত বমি",
    "রক্ত কাশি",

    # Marathi
    "तीव्र रक्तस्त्राव",
    "जास्त रक्तस्त्राव",
    "रक्तस्त्राव थांबत नाही",
    "रक्ताची उलटी",
    "रक्ताची खोकला",


    # =====================================================
    # SEVERE ABDOMINAL / INTERNAL EMERGENCY
    # =====================================================

    "severe abdominal pain",
    "severe stomach pain",
    "sudden severe abdominal pain",
    "severe belly pain",
    "abdomen rigid",
    "swollen abdomen with severe pain",

    # Hindi
    "पेट में तेज दर्द",
    "बहुत तेज पेट दर्द",
    "अचानक तेज पेट दर्द",

    # Tamil
    "வயிற்றில் கடுமையான வலி",
    "திடீர் கடுமையான வயிற்று வலி",

    # Telugu
    "తీవ్రమైన కడుపు నొప్పి",
    "ఆకస్మిక తీవ్రమైన కడుపు నొప్పి",

    # Malayalam
    "കടുത്ത വയറുവേദന",
    "പെട്ടെന്നുള്ള കടുത്ത വയറുവേദന",

    # Kannada
    "ತೀವ್ರ ಹೊಟ್ಟೆ ನೋವು",
    "ಹಠಾತ್ ತೀವ್ರ ಹೊಟ್ಟೆ ನೋವು",

    # Bengali
    "তীব্র পেট ব্যথা",
    "হঠাৎ তীব্র পেট ব্যথা",

    # Marathi
    "तीव्र पोटदुखी",
    "अचानक तीव्र पोटदुखी",


    # =====================================================
    # SEVERE HEADACHE / BRAIN EMERGENCY
    # =====================================================

    "worst headache of my life",
    "worst headache",
    "thunderclap headache",
    "sudden severe headache",
    "severe headache with vomiting",
    "severe headache with weakness",
    "severe headache with confusion",

    # Hindi
    "बहुत तेज सिरदर्द",
    "अचानक बहुत तेज सिरदर्द",
    "जीवन का सबसे तेज सिरदर्द",

    # Tamil
    "மிகவும் கடுமையான தலைவலி",
    "திடீர் கடுமையான தலைவலி",

    # Telugu
    "తీవ్రమైన తలనొప్పి",
    "ఆకస్మిక తీవ్రమైన తలనొప్పి",

    # Malayalam
    "കടുത്ത തലവേദന",
    "പെട്ടെന്നുള്ള കടുത്ത തലവേദന",

    # Kannada
    "ತೀವ್ರ ತಲೆನೋವು",
    "ಹಠಾತ್ ತೀವ್ರ ತಲೆನೋವು",

    # Bengali
    "তীব্র মাথাব্যথা",
    "হঠাৎ তীব্র মাথাব্যথা",

    # Marathi
    "तीव्र डोकेदुखी",
    "अचानक तीव्र डोकेदुखी",


    # =====================================================
    # SEVERE ALLERGIC REACTION
    # =====================================================

    "anaphylaxis",
    "anaphylactic shock",
    "severe allergic reaction",
    "throat swelling",
    "swelling of throat",
    "face swelling with breathing difficulty",
    "tongue swelling with breathing difficulty",

    # Hindi
    "गंभीर एलर्जी",
    "गला सूजना",
    "चेहरा सूजना",
    "जीभ सूजना",

    # Tamil
    "கடுமையான ஒவ்வாமை",
    "தொண்டை வீக்கம்",
    "முகம் வீக்கம்",
    "நாக்கு வீக்கம்",

    # Telugu
    "తీవ్రమైన అలర్జీ",
    "గొంతు వాపు",
    "ముఖం వాపు",
    "నాలుక వాపు",

    # Malayalam
    "ഗുരുതരമായ അലർജി",
    "തൊണ്ട വീക്കം",
    "മുഖം വീക്കം",
    "നാവ് വീക്കം",

    # Kannada
    "ತೀವ್ರ ಅಲರ್ಜಿ",
    "ಗಂಟಲಿನ ಊತ",
    "ಮುಖದ ಊತ",
    "ನಾಲಿಗೆ ಊತ",

    # Bengali
    "গুরুতর অ্যালার্জি",
    "গলা ফুলে যাওয়া",
    "মুখ ফুলে যাওয়া",
    "জিভ ফুলে যাওয়া",

    # Marathi
    "गंभीर ऍलर्जी",
    "घसा सुजणे",
    "चेहरा सुजणे",
    "जीभ सुजणे",


    # =====================================================
    # POISONING / OVERDOSE
    # =====================================================

    "poisoning",
    "poisoned",
    "poison ingestion",
    "swallowed poison",
    "chemical poisoning",
    "drug overdose",
    "overdose",
    "pesticide poisoning",
    "insecticide poisoning",
    "toxic chemical",

    # Hindi
    "जहर",
    "जहर खा लिया",
    "विषाक्तता",
    "दवा की ओवरडोज",
    "कीटनाशक जहर",

    # Tamil
    "விஷம்",
    "விஷம் குடித்தார்",
    "மருந்து அதிகமாக எடுத்துக்கொண்டார்",
    "பூச்சிக்கொல்லி விஷம்",

    # Telugu
    "విషం",
    "విషం తాగారు",
    "మందులు ఎక్కువగా తీసుకున్నారు",
    "పురుగుమందు విషం",

    # Malayalam
    "വിഷം",
    "വിഷം കഴിച്ചു",
    "മരുന്ന് അമിതമായി കഴിച്ചു",
    "കീടനാശിനി വിഷബാധ",

    # Kannada
    "ವಿಷ",
    "ವಿಷ ಸೇವಿಸಿದ್ದಾರೆ",
    "ಔಷಧಿ ಓವರ್‌ಡೋಸ್",
    "ಕೀಟನಾಶಕ ವಿಷ",

    # Bengali
    "বিষ",
    "বিষ খেয়েছে",
    "ওষুধের অতিরিক্ত মাত্রা",
    "কীটনাশকের বিষক্রিয়া",

    # Marathi
    "विष",
    "विष घेतले",
    "औषधांचा ओव्हरडोस",
    "कीटकनाशक विषबाधा",


    # =====================================================
    # BURNS / ELECTRIC SHOCK
    # =====================================================

    "severe burn",
    "major burn",
    "electrical burn",
    "electric shock",
    "electrocution",
    "chemical burn",
    "burn with difficulty breathing",

    # Hindi
    "गंभीर जलना",
    "बिजली का झटका",
    "बिजली लगना",
    "रासायनिक जलन",

    # Tamil
    "கடுமையான தீக்காயம்",
    "மின்சார அதிர்ச்சி",
    "மின்சாரம் தாக்கியது",

    # Telugu
    "తీవ్రమైన కాలిన గాయం",
    "విద్యుత్ షాక్",
    "కరెంట్ షాక్",

    # Malayalam
    "ഗുരുതരമായ പൊള്ളൽ",
    "വൈദ്യുതാഘാതം",

    # Kannada
    "ತೀವ್ರ ಸುಟ್ಟ ಗಾಯ",
    "ವಿದ್ಯುತ್ ಆಘಾತ",

    # Bengali
    "গুরুতর পোড়া",
    "বৈদ্যুতিক শক",

    # Marathi
    "गंभीर भाजणे",
    "वीज लागणे",


    # =====================================================
    # PREGNANCY / MATERNAL EMERGENCIES
    # =====================================================

    "pregnancy bleeding",
    "pregnant and bleeding",
    "heavy bleeding during pregnancy",
    "severe abdominal pain during pregnancy",
    "severe headache during pregnancy",
    "blurred vision during pregnancy",
    "seizure during pregnancy",
    "unconscious during pregnancy",
    "severe swelling during pregnancy",
    "water broke with complications",
    "baby not moving",
    "decreased fetal movement",
    "no fetal movement",

    # Hindi
    "गर्भावस्था में रक्तस्राव",
    "गर्भवती और खून बहना",
    "गर्भावस्था में तेज पेट दर्द",
    "गर्भावस्था में तेज सिरदर्द",
    "गर्भ में बच्चे की हलचल नहीं",
    "बच्चा हिल नहीं रहा",

    # Tamil
    "கர்ப்ப கால இரத்தப்போக்கு",
    "கர்ப்ப காலத்தில் கடுமையான வயிற்று வலி",
    "கர்ப்ப காலத்தில் கடுமையான தலைவலி",
    "குழந்தை அசைவில்லை",

    # Telugu
    "గర్భధారణలో రక్తస్రావం",
    "గర్భధారణలో తీవ్రమైన కడుపు నొప్పి",
    "గర్భధారణలో తీవ్రమైన తలనొప్పి",
    "బిడ్డ కదలడం లేదు",

    # Malayalam
    "ഗർഭകാല രക്തസ്രാവം",
    "ഗർഭകാലത്ത് കടുത്ത വയറുവേദന",
    "ഗർഭകാലത്ത് കടുത്ത തലവേദന",
    "കുഞ്ഞ് അനങ്ങുന്നില്ല",

    # Kannada
    "ಗರ್ಭಾವಸ್ಥೆಯಲ್ಲಿ ರಕ್ತಸ್ರಾವ",
    "ಗರ್ಭಾವಸ್ಥೆಯಲ್ಲಿ ತೀವ್ರ ಹೊಟ್ಟೆ ನೋವು",
    "ಗರ್ಭಾವಸ್ಥೆಯಲ್ಲಿ ತೀವ್ರ ತಲೆನೋವು",
    "ಮಗು ಚಲಿಸುತ್ತಿಲ್ಲ",

    # Bengali
    "গর্ভাবস্থায় রক্তপাত",
    "গর্ভাবস্থায় তীব্র পেট ব্যথা",
    "গর্ভাবস্থায় তীব্র মাথাব্যথা",
    "বাচ্চা নড়ছে না",

    # Marathi
    "गर्भावस्थेत रक्तस्त्राव",
    "गर्भावस्थेत तीव्र पोटदुखी",
    "गर्भावस्थेत तीव्र डोकेदुखी",
    "बाळाची हालचाल नाही",


    # =====================================================
    # CHILD EMERGENCIES
    # =====================================================

    "child not breathing",
    "baby not breathing",
    "child unconscious",
    "baby unconscious",
    "child seizure",
    "baby seizure",
    "child severe dehydration",
    "baby severe dehydration",
    "child blue lips",
    "baby blue lips",
    "child severe difficulty breathing",

    # Hindi
    "बच्चा सांस नहीं ले रहा",
    "बच्चा बेहोश",
    "बच्चे को दौरा",
    "बच्चे के होंठ नीले",

    # Tamil
    "குழந்தை மூச்சு விடவில்லை",
    "குழந்தை நினைவிழந்தது",
    "குழந்தைக்கு வலிப்பு",

    # Telugu
    "పిల్లవాడు శ్వాస తీసుకోవడం లేదు",
    "పిల్లవాడు స్పృహలో లేడు",
    "పిల్లవాడికి మూర్ఛ",

    # Malayalam
    "കുട്ടി ശ്വസിക്കുന്നില്ല",
    "കുട്ടി ബോധരഹിതനാണ്",
    "കുട്ടിക്ക് അപസ്മാരം",

    # Kannada
    "ಮಗು ಉಸಿರಾಡುತ್ತಿಲ್ಲ",
    "ಮಗು ಪ್ರಜ್ಞಾಹೀನ",
    "ಮಗುವಿಗೆ ಅಪಸ್ಮಾರ",

    # Bengali
    "শিশু শ্বাস নিচ্ছে না",
    "শিশু অজ্ঞান",
    "শিশুর খিঁচুনি",

    # Marathi
    "मूल श्वास घेत नाही",
    "मूल बेशुद्ध",
    "मुलाला फिट",


    # =====================================================
    # MENTAL HEALTH EMERGENCY
    # =====================================================

    "suicidal",
    "suicide",
    "suicide attempt",
    "attempted suicide",
    "self harm",
    "self-harm",
    "trying to kill myself",
    "want to die",
    "overdose suicide",

    # Hindi
    "आत्महत्या",
    "आत्महत्या की कोशिश",
    "खुद को नुकसान",
    "मरना चाहता हूं",
    "मरना चाहती हूं",

    # Tamil
    "தற்கொலை",
    "தற்கொலை முயற்சி",
    "சுய காயம்",
    "சாக வேண்டும்",

    # Telugu
    "ఆత్మహత్య",
    "ఆత్మహత్య ప్రయత్నం",
    "స్వీయ హాని",
    "చనిపోవాలని ఉంది",

    # Malayalam
    "ആത്മഹത്യ",
    "ആത്മഹത്യ ശ്രമം",
    "സ്വയം ഉപദ്രവിക്കൽ",
    "മരിക്കണം",

    # Kannada
    "ಆತ್ಮಹತ್ಯೆ",
    "ಆತ್ಮಹತ್ಯೆ ಪ್ರಯತ್ನ",
    "ಸ್ವಯಂ ಹಾನಿ",
    "ಸಾಯಬೇಕು",

    # Bengali
    "আত্মহত্যা",
    "আত্মহত্যার চেষ্টা",
    "নিজেকে আঘাত করা",
    "মরে যেতে চাই",

    # Marathi
    "आत्महत्या",
    "आत्महत्येचा प्रयत्न",
    "स्वतःला इजा करणे",
    "मला मरायचे आहे",


    # =====================================================
    # DROWNING / CHOKING
    # =====================================================

    "drowning",
    "near drowning",
    "choking",
    "foreign body airway",
    "object stuck in throat",
    "food stuck in throat",

    # Hindi
    "डूबना",
    "गले में खाना फंसना",
    "गले में वस्तु फंसना",

    # Tamil
    "மூழ்குதல்",
    "தொண்டையில் உணவு சிக்கியது",

    # Telugu
    "మునిగిపోయారు",
    "గొంతులో ఆహారం ఇరుక్కుంది",

    # Malayalam
    "മുങ്ങി",
    "തൊണ്ടയിൽ ഭക്ഷണം കുടുങ്ങി",

    # Kannada
    "ಮುಳುಗುವುದು",
    "ಗಂಟಲಿನಲ್ಲಿ ಆಹಾರ ಸಿಕ್ಕಿಕೊಂಡಿದೆ",

    # Bengali
    "ডুবে যাওয়া",
    "গলায় খাবার আটকে গেছে",

    # Marathi
    "बुडणे",
    "घशात अन्न अडकले",


    # =====================================================
    # SEPSIS / SERIOUS INFECTION WARNING
    # =====================================================

    "sepsis",
    "septic shock",
    "very high fever with confusion",
    "fever with unconsciousness",
    "fever with severe breathing difficulty",
    "infection with confusion",
    "infection with very low blood pressure",

    # Hindi
    "सेप्सिस",
    "बहुत तेज बुखार और बेहोशी",
    "बुखार और सांस लेने में बहुत दिक्कत",

    # Tamil
    "செப்சிஸ்",
    "அதிக காய்ச்சல் மற்றும் நினைவிழப்பு",

    # Telugu
    "సెప్సిస్",
    "తీవ్రమైన జ్వరం మరియు స్పృహ కోల్పోవడం",

    # Malayalam
    "സെപ്സിസ്",
    "കടുത്ത പനിയും ബോധക്ഷയവും",

    # Kannada
    "ಸೆಪ್ಸಿಸ್",
    "ತೀವ್ರ ಜ್ವರ ಮತ್ತು ಪ್ರಜ್ಞಾಹೀನತೆ",

    # Bengali
    "সেপসিস",
    "তীব্র জ্বর এবং অজ্ঞান",

    # Marathi
    "सेप्सिस",
    "तीव्र ताप आणि बेशुद्धपणा"
]
# =========================================================
# RED FLAG DETECTION
# =========================================================

# This list contains emergency warning phrases in multiple
# languages and for multiple important health conditions.

RED_FLAG_GROUPS = {

    # =====================================================
    # HEART / CARDIAC EMERGENCIES
    # =====================================================

    "Heart / Cardiac Emergency": [

        # English
        "heart attack",
        "heart attack symptoms",
        "severe chest pain",
        "crushing chest pain",
        "pressure in chest",
        "tightness in chest",
        "chest pain spreading to arm",
        "chest pain spreading to jaw",
        "chest pain spreading to back",
        "chest pain with sweating",
        "chest pain with nausea",
        "chest pain with vomiting",
        "chest pain with shortness of breath",

        # Hindi
        "दिल का दौरा",
        "हार्ट अटैक",
        "सीने में तेज दर्द",
        "सीने में दबाव",
        "सीने में जकड़न",
        "सीने का दर्द हाथ तक",
        "सीने का दर्द जबड़े तक",

        # Tamil
        "மாரடைப்பு",
        "மார்பில் கடுமையான வலி",
        "மார்பில் அழுத்தம்",
        "மார்பில் இறுக்கம்",
        "மார்பு வலி கைக்கு பரவுகிறது",

        # Telugu
        "గుండెపోటు",
        "తీవ్రమైన ఛాతీ నొప్పి",
        "ఛాతీలో ఒత్తిడి",
        "ఛాతీలో బిగుతు",
        "ఛాతీ నొప్పి చేతికి వ్యాపించడం",

        # Malayalam
        "ഹൃദയാഘാതം",
        "കടുത്ത നെഞ്ചുവേദന",
        "നെഞ്ചിൽ സമ്മർദ്ദം",
        "നെഞ്ചിൽ മുറുക്കം",

        # Kannada
        "ಹೃದಯಾಘಾತ",
        "ತೀವ್ರವಾದ ಎದೆ ನೋವು",
        "ಎದೆಯಲ್ಲಿ ಒತ್ತಡ",
        "ಎದೆಯಲ್ಲಿ ಬಿಗಿತ",

        # Bengali
        "হার্ট অ্যাটাক",
        "হৃদরোগে আক্রমণ",
        "তীব্র বুক ব্যথা",
        "বুকে চাপ",
        "বুকে শক্তভাব",

        # Marathi
        "हृदयविकाराचा झटका",
        "हार्ट अटॅक",
        "तीव्र छातीत दुखणे",
        "छातीत दाब",
        "छातीत घट्टपणा"
    ],


    # =====================================================
    # BREATHING / RESPIRATORY EMERGENCIES
    # =====================================================

    "Breathing Emergency": [

        # English
        "difficulty breathing",
        "severe difficulty breathing",
        "cannot breathe",
        "can't breathe",
        "unable to breathe",
        "shortness of breath",
        "severe shortness of breath",
        "gasping for air",
        "choking",
        "blue lips",
        "blue skin",

        # Hindi
        "सांस लेने में कठिनाई",
        "सांस लेने में दिक्कत",
        "सांस नहीं आ रही",
        "सांस नहीं ले पा रहा",
        "बहुत ज्यादा सांस फूलना",
        "होंठ नीले",

        # Tamil
        "சுவாசிப்பதில் சிரமம்",
        "மூச்சு விடுவதில் சிரமம்",
        "மூச்சு விட முடியவில்லை",
        "மூச்சுத் திணறல்",
        "உதடுகள் நீலமாக",

        # Telugu
        "శ్వాస తీసుకోవడంలో ఇబ్బంది",
        "ఊపిరి తీసుకోవడం కష్టం",
        "ఊపిరి తీసుకోలేకపోతున్నాను",
        "తీవ్రమైన శ్వాస సమస్య",
        "పెదవులు నీలం",

        # Malayalam
        "ശ്വസിക്കാൻ ബുദ്ധിമുട്ട്",
        "ശ്വാസം എടുക്കാൻ കഴിയുന്നില്ല",
        "ശ്വാസം മുട്ടൽ",
        "ചുണ്ടുകൾ നീലനിറം",

        # Kannada
        "ಉಸಿರಾಟದ ತೊಂದರೆ",
        "ಉಸಿರಾಡಲು ಸಾಧ್ಯವಾಗುತ್ತಿಲ್ಲ",
        "ತೀವ್ರ ಉಸಿರಾಟದ ತೊಂದರೆ",
        "ತುಟಿಗಳು ನೀಲಿ",

        # Bengali
        "শ্বাস নিতে অসুবিধা",
        "শ্বাস নিতে পারছি না",
        "শ্বাসকষ্ট",
        "ঠোঁট নীল",

        # Marathi
        "श्वास घेण्यास त्रास",
        "श्वास घेता येत नाही",
        "श्वास घेण्यास खूप त्रास",
        "ओठ निळे पडणे"
    ],


    # =====================================================
    # STROKE / BRAIN EMERGENCIES
    # =====================================================

    "Stroke / Neurological Emergency": [

        # English
        "stroke",
        "signs of stroke",
        "face drooping",
        "facial drooping",
        "sudden weakness",
        "sudden numbness",
        "one sided weakness",
        "one-sided weakness",
        "slurred speech",
        "difficulty speaking",
        "cannot speak",
        "sudden confusion",
        "sudden loss of vision",
        "sudden severe headache",
        "paralysis",

        # Hindi
        "स्ट्रोक",
        "लकवा",
        "चेहरा टेढ़ा",
        "अचानक कमजोरी",
        "अचानक सुन्नपन",
        "बोलने में दिक्कत",
        "बोल नहीं पा रहा",
        "अचानक भ्रम",
        "अचानक दिखाई नहीं देना",
        "बहुत तेज सिरदर्द",

        # Tamil
        "பக்கவாதம்",
        "முகம் கோணல்",
        "திடீர் பலவீனம்",
        "திடீர் உணர்வின்மை",
        "பேசுவதில் சிரமம்",
        "பேச முடியவில்லை",
        "திடீர் குழப்பம்",
        "திடீர் பார்வை இழப்பு",

        # Telugu
        "స్ట్రోక్",
        "పక్షవాతం",
        "ముఖం వంగిపోవడం",
        "ఆకస్మిక బలహీనత",
        "ఆకస్మిక మొద్దుబారడం",
        "మాట్లాడటంలో ఇబ్బంది",
        "మాట్లాడలేకపోవడం",
        "ఆకస్మిక గందరగోళం",

        # Malayalam
        "സ്ട്രോക്ക്",
        "പക്ഷാഘാതം",
        "മുഖം കോടൽ",
        "പെട്ടെന്നുള്ള ബലഹീനത",
        "സംസാരിക്കാൻ ബുദ്ധിമുട്ട്",
        "സംസാരിക്കാൻ കഴിയുന്നില്ല",
        "പെട്ടെന്നുള്ള കാഴ്ച നഷ്ടം",

        # Kannada
        "ಸ್ಟ್ರೋಕ್",
        "ಪಾರ್ಶ್ವವಾಯು",
        "ಮುಖ ವಕ್ರವಾಗುವುದು",
        "ಹಠಾತ್ ದೌರ್ಬಲ್ಯ",
        "ಮಾತನಾಡಲು ತೊಂದರೆ",
        "ಮಾತನಾಡಲು ಸಾಧ್ಯವಾಗುತ್ತಿಲ್ಲ",
        "ಹಠಾತ್ ದೃಷ್ಟಿ ಕಳೆದುಕೊಳ್ಳುವುದು",

        # Bengali
        "স্ট্রোক",
        "পক্ষাঘাত",
        "মুখ বেঁকে যাওয়া",
        "হঠাৎ দুর্বলতা",
        "হঠাৎ অসাড়তা",
        "কথা বলতে অসুবিধা",
        "কথা বলতে পারছি না",
        "হঠাৎ দৃষ্টি হারানো",

        # Marathi
        "स्ट्रोक",
        "पक्षाघात",
        "चेहरा वाकडा",
        "अचानक अशक्तपणा",
        "अचानक बधिरपणा",
        "बोलण्यात अडचण",
        "बोलता येत नाही",
        "अचानक दृष्टी जाणे"
    ],


    # =====================================================
    # UNCONSCIOUSNESS / SEIZURE
    # =====================================================

    "Unconsciousness / Seizure": [

        # English
        "unconscious",
        "unresponsive",
        "not responding",
        "loss of consciousness",
        "passed out",
        "fainted and not waking",
        "seizure",
        "convulsion",
        "fits",
        "continuous seizure",

        # Hindi
        "बेहोश",
        "होश नहीं है",
        "प्रतिक्रिया नहीं दे रहा",
        "दौरा",
        "दौरे",
        "मिर्गी का दौरा",

        # Tamil
        "நினைவிழந்த",
        "சுயநினைவு இல்லை",
        "பதில் அளிக்கவில்லை",
        "வலிப்பு",
        "வலிப்பு நோய்",

        # Telugu
        "స్పృహ కోల్పోవడం",
        "స్పృహలో లేరు",
        "స్పందించడం లేదు",
        "మూర్ఛ",
        "ఫిట్స్",

        # Malayalam
        "ബോധരഹിതൻ",
        "ബോധം നഷ്ടപ്പെട്ടു",
        "പ്രതികരിക്കുന്നില്ല",
        "അപസ്മാരം",
        "വലിവ്",

        # Kannada
        "ಪ್ರಜ್ಞಾಹೀನ",
        "ಪ್ರಜ್ಞೆ ಕಳೆದುಕೊಳ್ಳುವುದು",
        "ಪ್ರತಿಕ್ರಿಯಿಸುತ್ತಿಲ್ಲ",
        "ಅಪಸ್ಮಾರ",
        "ಫಿಟ್ಸ್",

        # Bengali
        "অজ্ঞান",
        "চেতনা হারানো",
        "সাড়া দিচ্ছে না",
        "খিঁচুনি",
        "ফিট",

        # Marathi
        "बेशुद्ध",
        "शुद्ध हरपणे",
        "प्रतिसाद देत नाही",
        "फिट",
        "आकडी"
    ],


    # =====================================================
    # SEVERE BLEEDING
    # =====================================================

    "Severe Bleeding": [

        # English
        "severe bleeding",
        "heavy bleeding",
        "uncontrolled bleeding",
        "bleeding won't stop",
        "blood vomiting",
        "vomiting blood",
        "coughing blood",
        "blood in vomit",
        "large amount of blood",

        # Hindi
        "बहुत ज्यादा खून बहना",
        "तेज रक्तस्राव",
        "खून नहीं रुक रहा",
        "खून की उल्टी",
        "खून वाली खांसी",

        # Tamil
        "கடுமையான இரத்தப்போக்கு",
        "அதிக இரத்தப்போக்கு",
        "இரத்தம் நிற்கவில்லை",
        "இரத்த வாந்தி",
        "இரத்தம் இருமல்",

        # Telugu
        "తీవ్రమైన రక్తస్రావం",
        "ఎక్కువ రక్తస్రావం",
        "రక్తం ఆగడం లేదు",
        "రక్తం వాంతి",
        "రక్తం దగ్గు",

        # Malayalam
        "കടുത്ത രക്തസ്രാവം",
        "അമിതമായ രക്തസ്രാവം",
        "രക്തസ്രാവം നിർത്തുന്നില്ല",
        "രക്തം ഛർദ്ദിക്കുക",
        "രക്തം ചുമയ്ക്കുക",

        # Kannada
        "ತೀವ್ರ ರಕ್ತಸ್ರಾವ",
        "ಹೆಚ್ಚಿನ ರಕ್ತಸ್ರಾವ",
        "ರಕ್ತಸ್ರಾವ ನಿಲ್ಲುತ್ತಿಲ್ಲ",
        "ರಕ್ತ ವಾಂತಿ",
        "ರಕ್ತ ಕೆಮ್ಮು",

        # Bengali
        "তীব্র রক্তপাত",
        "অতিরিক্ত রক্তপাত",
        "রক্তপাত বন্ধ হচ্ছে না",
        "রক্ত বমি",
        "রক্ত কাশি",

        # Marathi
        "तीव्र रक्तस्त्राव",
        "जास्त रक्तस्त्राव",
        "रक्तस्त्राव थांबत नाही",
        "रक्ताची उलटी",
        "रक्ताची खोकला"
    ],


    # =====================================================
    # SEVERE ABDOMINAL / INTERNAL PROBLEMS
    # =====================================================

    "Severe Abdominal Emergency": [

        # English
        "severe abdominal pain",
        "severe stomach pain",
        "sudden severe abdominal pain",
        "rigid abdomen",
        "swollen abdomen with severe pain",
        "vomiting blood",
        "black stool with weakness",

        # Hindi
        "पेट में तेज दर्द",
        "पेट में बहुत तेज दर्द",
        "अचानक तेज पेट दर्द",
        "पेट बहुत सख्त",
        "काला मल और कमजोरी",

        # Tamil
        "வயிற்றில் கடுமையான வலி",
        "திடீர் கடுமையான வயிற்று வலி",
        "வயிறு மிகவும் கடினமாக உள்ளது",

        # Telugu
        "తీవ్రమైన కడుపు నొప్పి",
        "ఆకస్మిక తీవ్రమైన కడుపు నొప్పి",
        "కడుపు గట్టిగా ఉంది",

        # Malayalam
        "കടുത്ത വയറുവേദന",
        "പെട്ടെന്നുള്ള കടുത്ത വയറുവേദന",
        "വയർ വളരെ കട്ടിയാകുന്നു",

        # Kannada
        "ತೀವ್ರ ಹೊಟ್ಟೆ ನೋವು",
        "ಹಠಾತ್ ತೀವ್ರ ಹೊಟ್ಟೆ ನೋವು",
        "ಹೊಟ್ಟೆ ಗಟ್ಟಿಯಾಗಿದೆ",

        # Bengali
        "তীব্র পেট ব্যথা",
        "হঠাৎ তীব্র পেট ব্যথা",
        "পেট শক্ত হয়ে গেছে",

        # Marathi
        "तीव्र पोटदुखी",
        "अचानक तीव्र पोटदुखी",
        "पोट खूप कडक होणे"
    ],


    # =====================================================
    # PREGNANCY / MATERNAL EMERGENCIES
    # =====================================================

    "Pregnancy Emergency": [

        # English
        "pregnancy heavy bleeding",
        "pregnancy severe bleeding",
        "pregnant and bleeding",
        "severe abdominal pain during pregnancy",
        "severe headache during pregnancy",
        "blurred vision during pregnancy",
        "seizure during pregnancy",
        "unconscious during pregnancy",
        "water broke early",
        "baby movement stopped",
        "baby not moving",
        "pregnancy chest pain",
        "pregnancy difficulty breathing",

        # Hindi
        "गर्भावस्था में ज्यादा खून",
        "गर्भावस्था में रक्तस्राव",
        "गर्भावस्था में तेज पेट दर्द",
        "गर्भावस्था में तेज सिरदर्द",
        "गर्भावस्था में धुंधला दिखाई देना",
        "गर्भावस्था में दौरा",
        "बच्चा हिल नहीं रहा",

        # Tamil
        "கர்ப்ப காலத்தில் அதிக இரத்தப்போக்கு",
        "கர்ப்ப காலத்தில் இரத்தப்போக்கு",
        "கர்ப்ப காலத்தில் கடுமையான வயிற்று வலி",
        "கர்ப்ப காலத்தில் கடுமையான தலைவலி",
        "குழந்தை அசையவில்லை",

        # Telugu
        "గర్భధారణలో తీవ్రమైన రక్తస్రావం",
        "గర్భధారణలో రక్తస్రావం",
        "గర్భధారణలో తీవ్రమైన కడుపు నొప్పి",
        "గర్భధారణలో తీవ్రమైన తలనొప్పి",
        "బిడ్డ కదలడం లేదు",

        # Malayalam
        "ഗർഭകാലത്ത് കടുത്ത രക്തസ്രാവം",
        "ഗർഭകാലത്ത് രക്തസ്രാവം",
        "ഗർഭകാലത്ത് കടുത്ത വയറുവേദന",
        "ഗർഭകാലത്ത് കടുത്ത തലവേദന",
        "കുഞ്ഞ് അനങ്ങുന്നില്ല",

        # Kannada
        "ಗರ್ಭಾವಸ್ಥೆಯಲ್ಲಿ ತೀವ್ರ ರಕ್ತಸ್ರಾವ",
        "ಗರ್ಭಾವಸ್ಥೆಯಲ್ಲಿ ರಕ್ತಸ್ರಾವ",
        "ಗರ್ಭಾವಸ್ಥೆಯಲ್ಲಿ ತೀವ್ರ ಹೊಟ್ಟೆ ನೋವು",
        "ಗರ್ಭಾವಸ್ಥೆಯಲ್ಲಿ ತೀವ್ರ ತಲೆನೋವು",
        "ಮಗು ಚಲಿಸುತ್ತಿಲ್ಲ",

        # Bengali
        "গর্ভাবস্থায় তীব্র রক্তপাত",
        "গর্ভাবস্থায় রক্তপাত",
        "গর্ভাবস্থায় তীব্র পেট ব্যথা",
        "গর্ভাবস্থায় তীব্র মাথাব্যথা",
        "শিশু নড়ছে না",

        # Marathi
        "गर्भावस्थेत तीव्र रक्तस्त्राव",
        "गर्भावस्थेत रक्तस्त्राव",
        "गर्भावस्थेत तीव्र पोटदुखी",
        "गर्भावस्थेत तीव्र डोकेदुखी",
        "बाळ हालचाल करत नाही"
    ],


    # =====================================================
    # SEVERE ALLERGIC REACTION
    # =====================================================

    "Severe Allergic Reaction": [

        # English
        "anaphylaxis",
        "severe allergic reaction",
        "swelling of throat",
        "throat swelling",
        "swelling of tongue",
        "tongue swelling",
        "face swelling with breathing difficulty",
        "allergic reaction with difficulty breathing",

        # Hindi
        "गंभीर एलर्जी",
        "गले में सूजन",
        "जीभ में सूजन",
        "चेहरे पर सूजन और सांस में दिक्कत",

        # Tamil
        "கடுமையான ஒவ்வாமை",
        "தொண்டை வீக்கம்",
        "நாக்கு வீக்கம்",
        "முக வீக்கம் மற்றும் மூச்சுத்திணறல்",

        # Telugu
        "తీవ్రమైన అలెర్జీ",
        "గొంతు వాపు",
        "నాలుక వాపు",
        "ముఖం వాపు మరియు శ్వాసలో ఇబ్బంది",

        # Malayalam
        "ഗുരുതരമായ അലർജി",
        "തൊണ്ട വീക്കം",
        "നാവ് വീക്കം",
        "മുഖം വീക്കം ശ്വാസതടസ്സത്തോടൊപ്പം",

        # Kannada
        "ತೀವ್ರ ಅಲರ್ಜಿ",
        "ಗಂಟಲಿನ ಊತ",
        "ನಾಲಿಗೆಯ ಊತ",
        "ಮುಖದ ಊತ ಮತ್ತು ಉಸಿರಾಟದ ತೊಂದರೆ",

        # Bengali
        "তীব্র অ্যালার্জি",
        "গলা ফুলে যাওয়া",
        "জিহ্বা ফুলে যাওয়া",
        "মুখ ফুলে যাওয়া এবং শ্বাসকষ্ট",

        # Marathi
        "गंभीर ऍलर्जी",
        "घशावर सूज",
        "जीभेला सूज",
        "चेहऱ्यावर सूज आणि श्वास घेण्यास त्रास"
    ],


    # =====================================================
    # KIDNEY / URINARY EMERGENCIES
    # =====================================================

    "Kidney / Urinary Emergency": [

        # English
        "unable to urinate",
        "cannot urinate",
        "no urine",
        "severe kidney pain",
        "severe flank pain",
        "blood in urine with severe pain",
        "kidney pain with fever",
        "severe swelling with no urine",

        # Hindi
        "पेशाब नहीं हो रहा",
        "पेशाब नहीं आ रहा",
        "किडनी में तेज दर्द",
        "कमर के पास तेज दर्द",
        "पेशाब में खून और तेज दर्द",

        # Tamil
        "சிறுநீர் வரவில்லை",
        "சிறுநீர் கழிக்க முடியவில்லை",
        "சிறுநீரகத்தில் கடுமையான வலி",
        "சிறுநீரில் இரத்தம் மற்றும் கடுமையான வலி",

        # Telugu
        "మూత్రం రావడం లేదు",
        "మూత్రం పోయలేకపోతున్నాను",
        "కిడ్నీలో తీవ్రమైన నొప్పి",
        "మూత్రంలో రక్తం మరియు తీవ్రమైన నొప్పి",

        # Malayalam
        "മൂത്രം വരുന്നില്ല",
        "മൂത്രമൊഴിക്കാൻ കഴിയുന്നില്ല",
        "വൃക്കയിൽ കടുത്ത വേദന",
        "മൂത്രത്തിൽ രക്തവും കടുത്ത വേദനയും",

        # Kannada
        "ಮೂತ್ರ ಬರುತ್ತಿಲ್ಲ",
        "ಮೂತ್ರ ವಿಸರ್ಜನೆ ಮಾಡಲು ಸಾಧ್ಯವಾಗುತ್ತಿಲ್ಲ",
        "ಮೂತ್ರಪಿಂಡದಲ್ಲಿ ತೀವ್ರ ನೋವು",
        "ಮೂತ್ರದಲ್ಲಿ ರಕ್ತ ಮತ್ತು ತೀವ್ರ ನೋವು",

        # Bengali
        "প্রস্রাব হচ্ছে না",
        "প্রস্রাব করতে পারছি না",
        "কিডনিতে তীব্র ব্যথা",
        "প্রস্রাবে রক্ত এবং তীব্র ব্যথা",

        # Marathi
        "लघवी होत नाही",
        "लघवी करता येत नाही",
        "मूत्रपिंडात तीव्र वेदना",
        "लघवीत रक्त आणि तीव्र वेदना"
    ],


    # =====================================================
    # DIABETES EMERGENCIES
    # =====================================================

    "Diabetes Emergency": [

        # English
        "diabetic emergency",
        "very low blood sugar",
        "severe hypoglycemia",
        "unconscious diabetic",
        "diabetic unconscious",
        "confused diabetic",
        "very high blood sugar with vomiting",
        "diabetic ketoacidosis",
        "ketones with vomiting",

        # Hindi
        "बहुत कम ब्लड शुगर",
        "शुगर बहुत कम",
        "मधुमेह में बेहोशी",
        "डायबिटीज में बेहोश",
        "बहुत ज्यादा शुगर और उल्टी",

        # Tamil
        "இரத்த சர்க்கரை மிகவும் குறைவு",
        "சர்க்கரை மிகவும் குறைவு",
        "நீரிழிவு நோயாளி மயக்கம்",
        "சர்க்கரை அதிகம் மற்றும் வாந்தி",

        # Telugu
        "బ్లడ్ షుగర్ చాలా తక్కువ",
        "షుగర్ చాలా తక్కువ",
        "డయాబెటిస్‌లో స్పృహ కోల్పోవడం",
        "షుగర్ ఎక్కువగా ఉండి వాంతులు",

        # Malayalam
        "രക്തത്തിലെ പഞ്ചസാര വളരെ കുറവ്",
        "പ്രമേഹ രോഗി ബോധരഹിതൻ",
        "പഞ്ചസാര വളരെ കുറവ്",
        "പഞ്ചസാര വളരെ കൂടുതലും ഛർദ്ദിയും",

        # Kannada
        "ರಕ್ತದಲ್ಲಿನ ಸಕ್ಕರೆ ತುಂಬಾ ಕಡಿಮೆ",
        "ಸಕ್ಕರೆ ತುಂಬಾ ಕಡಿಮೆ",
        "ಮಧುಮೇಹದಲ್ಲಿ ಪ್ರಜ್ಞೆ ಕಳೆದುಕೊಳ್ಳುವುದು",
        "ಸಕ್ಕರೆ ಹೆಚ್ಚಾಗಿ ವಾಂತಿ",

        # Bengali
        "রক্তে শর্করা খুব কম",
        "শর্করা খুব কম",
        "ডায়াবেটিসে অজ্ঞান",
        "শর্করা বেশি এবং বমি",

        # Marathi
        "रक्तातील साखर खूप कमी",
        "साखर खूप कमी",
        "मधुमेहात बेशुद्ध",
        "साखर खूप जास्त आणि उलटी"
    ],


    # =====================================================
    # SEVERE INFECTION / SEPSIS WARNING
    # =====================================================

    "Severe Infection": [

        # English
        "severe infection",
        "sepsis",
        "septic shock",
        "very high fever with confusion",
        "fever with unconsciousness",
        "fever with difficulty breathing",
        "fever with severe weakness",
        "cold clammy skin with infection",

        # Hindi
        "गंभीर संक्रमण",
        "सेप्सिस",
        "बहुत तेज बुखार और भ्रम",
        "बुखार के साथ बेहोशी",
        "बुखार और सांस लेने में दिक्कत",

        # Tamil
        "கடுமையான தொற்று",
        "செப்சிஸ்",
        "அதிக காய்ச்சலுடன் குழப்பம்",
        "காய்ச்சலுடன் மயக்கம்",
        "காய்ச்சல் மற்றும் மூச்சுத்திணறல்",

        # Telugu
        "తీవ్రమైన ఇన్ఫెక్షన్",
        "సెప్సిస్",
        "చాలా ఎక్కువ జ్వరం మరియు గందరగోళం",
        "జ్వరంతో స్పృహ కోల్పోవడం",
        "జ్వరం మరియు శ్వాసలో ఇబ్బంది",

        # Malayalam
        "ഗുരുതരമായ അണുബാധ",
        "സെപ്സിസ്",
        "വളരെ ഉയർന്ന പനിയും ആശയക്കുഴപ്പവും",
        "പനിയോടൊപ്പം ബോധക്ഷയം",
        "പനിയും ശ്വാസതടസ്സവും",

        # Kannada
        "ತೀವ್ರ ಸೋಂಕು",
        "ಸೆಪ್ಸಿಸ್",
        "ಹೆಚ್ಚಿನ ಜ್ವರ ಮತ್ತು ಗೊಂದಲ",
        "ಜ್ವರದೊಂದಿಗೆ ಪ್ರಜ್ಞೆ ಕಳೆದುಕೊಳ್ಳುವುದು",
        "ಜ್ವರ ಮತ್ತು ಉಸಿರಾಟದ ತೊಂದರೆ",

        # Bengali
        "গুরুতর সংক্রমণ",
        "সেপসিস",
        "অতিরিক্ত জ্বর এবং বিভ্রান্তি",
        "জ্বরের সঙ্গে অজ্ঞান",
        "জ্বর এবং শ্বাসকষ্ট",

        # Marathi
        "गंभीर संसर्ग",
        "सेप्सिस",
        "खूप जास्त ताप आणि गोंधळ",
        "तापासोबत बेशुद्ध",
        "ताप आणि श्वास घेण्यास त्रास"
    ],


    # =====================================================
    # BURNS / ELECTRIC SHOCK / TRAUMA
    # =====================================================

    "Trauma / Burn Emergency": [

        # English
        "severe burn",
        "major burn",
        "burn on face",
        "burn on neck",
        "electrical burn",
        "electric shock",
        "severe electric shock",
        "major head injury",
        "head injury with loss of consciousness",
        "severe accident",
        "uncontrolled bleeding after accident",

        # Hindi
        "गंभीर जलना",
        "बहुत ज्यादा जलना",
        "चेहरे पर जलना",
        "बिजली का झटका",
        "सिर में गंभीर चोट",
        "चोट के बाद बेहोशी",
        "गंभीर दुर्घटना",

        # Tamil
        "கடுமையான தீக்காயம்",
        "முகத்தில் தீக்காயம்",
        "மின்சார அதிர்ச்சி",
        "தலையில் கடுமையான காயம்",
        "காயத்திற்குப் பிறகு மயக்கம்",
        "கடுமையான விபத்து",

        # Telugu
        "తీవ్రమైన కాలిన గాయం",
        "ముఖంపై కాలిన గాయం",
        "విద్యుత్ షాక్",
        "తలకు తీవ్రమైన గాయం",
        "గాయం తర్వాత స్పృహ కోల్పోవడం",
        "తీవ్రమైన ప్రమాదం",

        # Malayalam
        "ഗുരുതരമായ പൊള്ളൽ",
        "മുഖത്ത് പൊള്ളൽ",
        "വൈദ്യുതാഘാതം",
        "തലയ്ക്ക് ഗുരുതരമായ പരിക്ക്",
        "പരിക്കിന് ശേഷം ബോധക്ഷയം",
        "ഗുരുതരമായ അപകടം",

        # Kannada
        "ತೀವ್ರ ಸುಟ್ಟ ಗಾಯ",
        "ಮುಖದಲ್ಲಿ ಸುಟ್ಟ ಗಾಯ",
        "ವಿದ್ಯುತ್ ಆಘಾತ",
        "ತಲೆಗೆ ತೀವ್ರ ಗಾಯ",
        "ಗಾಯದ ನಂತರ ಪ್ರಜ್ಞೆ ಕಳೆದುಕೊಳ್ಳುವುದು",
        "ತೀವ್ರ ಅಪಘಾತ",

        # Bengali
        "গুরুতর পোড়া",
        "মুখে পোড়া",
        "বৈদ্যুতিক শক",
        "মাথায় গুরুতর আঘাত",
        "আঘাতের পর অজ্ঞান",
        "গুরুতর দুর্ঘটনা",

        # Marathi
        "गंभीर भाजणे",
        "चेहऱ्यावर भाजणे",
        "वीज लागणे",
        "डोक्याला गंभीर दुखापत",
        "दुखापतीनंतर बेशुद्ध",
        "गंभीर अपघात"
    ],


    # =====================================================
    # MENTAL HEALTH / SELF-HARM EMERGENCY
    # =====================================================

    "Mental Health Emergency": [

        # English
        "suicidal",
        "suicide",
        "want to die",
        "kill myself",
        "end my life",
        "self harm",
        "self-harm",
        "hurt myself",
        "overdose",

        # Hindi
        "आत्महत्या",
        "मरना चाहता हूं",
        "मरना चाहती हूं",
        "खुद को नुकसान",
        "खुद को मारना",

        # Tamil
        "தற்கொலை",
        "சாக வேண்டும்",
        "என்னை நானே காயப்படுத்த",
        "சுய காயம்",

        # Telugu
        "ఆత్మహత్య",
        "చనిపోవాలని ఉంది",
        "నన్ను నేను చంపుకోవాలి",
        "స్వీయ హాని",

        # Malayalam
        "ആത്മഹത്യ",
        "മരിക്കണം",
        "സ്വയം ഉപദ്രവിക്കൽ",

        # Kannada
        "ಆತ್ಮಹತ್ಯೆ",
        "ಸಾಯಬೇಕು",
        "ಸ್ವಯಂ ಹಾನಿ",

        # Bengali
        "আত্মহত্যা",
        "মরে যেতে চাই",
        "নিজেকে আঘাত করা",

        # Marathi
        "आत्महत्या",
        "मरावेसे वाटते",
        "स्वतःला इजा करणे"
    ]
}


# =========================================================
# ADDITIONAL GENERAL EMERGENCY PHRASES
# =========================================================

GENERAL_RED_FLAGS = [

    # English
    "emergency",
    "medical emergency",
    "dying",
    "near death",
    "very serious",
    "condition getting worse quickly",
    "suddenly collapsed",
    "collapsed",
    "not waking up",
    "cannot wake up",

    # Hindi
    "आपातकाल",
    "बहुत गंभीर",
    "अचानक गिर गया",
    "अचानक गिर गई",
    "होश में नहीं आ रहा",

    # Tamil
    "அவசரநிலை",
    "மிகவும் மோசமான நிலை",
    "திடீரென விழுந்தார்",
    "எழுந்திருக்க முடியவில்லை",

    # Telugu
    "అత్యవసర పరిస్థితి",
    "చాలా తీవ్రమైన పరిస్థితి",
    "అకస్మాత్తుగా కుప్పకూలారు",
    "లేవడం లేదు",

    # Malayalam
    "അടിയന്തരാവസ്ഥ",
    "വളരെ ഗുരുതരമായ അവസ്ഥ",
    "പെട്ടെന്ന് വീണു",
    "എഴുന്നേൽക്കുന്നില്ല",

    # Kannada
    "ತುರ್ತು ಪರಿಸ್ಥಿತಿ",
    "ತುಂಬಾ ಗಂಭೀರ ಸ್ಥಿತಿ",
    "ಹಠಾತ್ ಕುಸಿದು ಬಿದ್ದರು",
    "ಎಚ್ಚರವಾಗುತ್ತಿಲ್ಲ",

    # Bengali
    "জরুরি অবস্থা",
    "খুব গুরুতর অবস্থা",
    "হঠাৎ পড়ে গেছে",
    "জ্ঞান ফিরছে না",

    # Marathi
    "आपत्कालीन परिस्थिती",
    "खूप गंभीर स्थिती",
    "अचानक कोसळला",
    "शुद्धीवर येत नाही"
]


# =========================================================
# RED FLAG DETECTION FUNCTION
# =========================================================

def detect_red_flags(text):

    if not text:
        return []

    text_lower = text.lower().strip()

    detected = []

    # Check disease-specific emergency groups
    for category, phrases in RED_FLAG_GROUPS.items():

        matched_phrases = []

        for phrase in phrases:

            if phrase.lower() in text_lower:

                matched_phrases.append(phrase)

        if matched_phrases:

            detected.append({
                "category": category,
                "matches": matched_phrases
            })

    # Check general emergency phrases
    general_matches = []

    for phrase in GENERAL_RED_FLAGS:

        if phrase.lower() in text_lower:

            general_matches.append(phrase)

    if general_matches:

        detected.append({
            "category": "General Emergency",
            "matches": general_matches
        })

    return detected

# =========================================================
# MULTILINGUAL RED FLAG MESSAGES
# =========================================================

RED_FLAG_MESSAGES = {

    "English": (
        "🚨 RED FLAG / URGENT WARNING",
        "The question contains a possible emergency warning sign. "
        "The person may need urgent medical assessment."
    ),

    "Hindi": (
        "🚨 गंभीर चेतावनी / तत्काल चिकित्सा सहायता",
        "आपके प्रश्न में एक संभावित आपातकालीन चेतावनी संकेत है। "
        "व्यक्ति को तुरंत चिकित्सकीय जांच की आवश्यकता हो सकती है।"
    ),

    "Tamil": (
        "🚨 ஆபத்து அறிகுறி / அவசர எச்சரிக்கை",
        "உங்கள் கேள்வியில் அவசர நிலைக்கான சாத்தியமான அறிகுறி உள்ளது. "
        "நபருக்கு உடனடி மருத்துவ பரிசோதனை தேவைப்படலாம்."
    ),

    "Telugu": (
        "🚨 ప్రమాద సూచన / అత్యవసర హెచ్చరిక",
        "మీ ప్రశ్నలో అత్యవసర పరిస్థితికి సంబంధించిన ప్రమాద సూచన ఉండవచ్చు. "
        "వ్యక్తికి వెంటనే వైద్య పరీక్ష అవసరం కావచ్చు."
    ),

    "Malayalam": (
        "🚨 അപകട സൂചന / അടിയന്തര മുന്നറിയിപ്പ്",
        "നിങ്ങളുടെ ചോദ്യത്തിൽ അടിയന്തരാവസ്ഥയുടെ സാധ്യതയുള്ള സൂചനയുണ്ട്. "
        "വ്യക്തിക്ക് ഉടൻ മെഡിക്കൽ പരിശോധന ആവശ്യമായേക്കാം."
    ),

    "Kannada": (
        "🚨 ಅಪಾಯದ ಸೂಚನೆ / ತುರ್ತು ಎಚ್ಚರಿಕೆ",
        "ನಿಮ್ಮ ಪ್ರಶ್ನೆಯಲ್ಲಿ ತುರ್ತು ಪರಿಸ್ಥಿತಿಯ ಸಾಧ್ಯತೆಯ ಸೂಚನೆ ಇದೆ. "
        "ವ್ಯಕ್ತಿಗೆ ತಕ್ಷಣ ವೈದ್ಯಕೀಯ ಪರೀಕ್ಷೆ ಅಗತ್ಯವಾಗಬಹುದು."
    ),

    "Bengali": (
        "🚨 বিপদের লক্ষণ / জরুরি সতর্কতা",
        "আপনার প্রশ্নে জরুরি অবস্থার একটি সম্ভাব্য লক্ষণ রয়েছে। "
        "ব্যক্তির অবিলম্বে চিকিৎসা পরীক্ষার প্রয়োজন হতে পারে।"
    ),

    "Marathi": (
        "🚨 धोक्याची चिन्हे / तातडीची सूचना",
        "तुमच्या प्रश्नामध्ये आपत्कालीन स्थितीचे संभाव्य धोक्याचे चिन्ह आहे. "
        "व्यक्तीला तातडीने वैद्यकीय तपासणीची गरज असू शकते."
    )
}


# =========================================================
# EMERGENCY ACTION MESSAGE
# =========================================================

EMERGENCY_ACTION = {

    "English":
        "⚠️ Do not rely only on Saathi. "
        "If the person is seriously unwell, arrange urgent medical evaluation "
        "and contact appropriate local emergency medical services or the nearest suitable healthcare facility.",

    "Hindi":
        "⚠️ केवल साथी पर निर्भर न रहें। "
        "यदि व्यक्ति गंभीर रूप से अस्वस्थ है, तो तुरंत चिकित्सा जांच की व्यवस्था करें "
        "और स्थानीय आपातकालीन चिकित्सा सेवा या निकटतम उपयुक्त स्वास्थ्य केंद्र से संपर्क करें।",

    "Tamil":
        "⚠️ சாத்தியை மட்டும் நம்ப வேண்டாம். "
        "நபர் மிகவும் உடல்நிலை பாதிக்கப்பட்டிருந்தால் உடனடியாக மருத்துவ உதவியை ஏற்பாடு செய்து "
        "அருகிலுள்ள பொருத்தமான மருத்துவ நிலையத்தை தொடர்பு கொள்ளுங்கள்.",

    "Telugu":
        "⚠️ సాతీపై మాత్రమే ఆధారపడవద్దు. "
        "వ్యక్తి తీవ్రంగా అనారోగ్యంగా ఉంటే వెంటనే వైద్య సహాయం ఏర్పాటు చేసి "
        "సమీపంలోని తగిన ఆరోగ్య కేంద్రాన్ని సంప్రదించండి.",

    "Malayalam":
        "⚠️ സാത്തിയെ മാത്രം ആശ്രയിക്കരുത്. "
        "വ്യക്തിക്ക് ഗുരുതരമായ അസുഖമുണ്ടെങ്കിൽ ഉടൻ മെഡിക്കൽ സഹായം ഏർപ്പെടുത്തി "
        "അടുത്തുള്ള അനുയോജ്യമായ ആരോഗ്യ കേന്ദ്രവുമായി ബന്ധപ്പെടുക.",

    "Kannada":
        "⚠️ ಸಾಥಿಯನ್ನು ಮಾತ್ರ ಅವಲಂಬಿಸಬೇಡಿ. "
        "ವ್ಯಕ್ತಿಯ ಸ್ಥಿತಿ ಗಂಭೀರವಾಗಿದ್ದರೆ ತಕ್ಷಣ ವೈದ್ಯಕೀಯ ಸಹಾಯವನ್ನು ಏರ್ಪಡಿಸಿ "
        "ಹತ್ತಿರದ ಸೂಕ್ತ ಆರೋಗ್ಯ ಕೇಂದ್ರವನ್ನು ಸಂಪರ್ಕಿಸಿ.",

    "Bengali":
        "⚠️ শুধুমাত্র সাথীর উপর নির্ভর করবেন না। "
        "ব্যক্তি গুরুতর অসুস্থ হলে অবিলম্বে চিকিৎসার ব্যবস্থা করুন "
        "এবং নিকটবর্তী উপযুক্ত স্বাস্থ্যকেন্দ্রের সঙ্গে যোগাযোগ করুন।",

    "Marathi":
        "⚠️ फक्त साथीवर अवलंबून राहू नका. "
        "व्यक्तीची प्रकृती गंभीर असल्यास त्वरित वैद्यकीय मदतीची व्यवस्था करा "
        "आणि जवळच्या योग्य आरोग्य केंद्राशी संपर्क साधा."
}


# =========================================================
# GEMINI REQUEST WITH RETRY
# =========================================================

def generate_with_retry(prompt):

    models_to_try = [
        PRIMARY_MODEL,
        FALLBACK_MODEL
    ]

    last_error = None

    for model in models_to_try:

        for attempt in range(3):

            try:

                response = client.models.generate_content(
                    model=model,
                    contents=prompt
                )

                if response and response.text:

                    return response.text, model

                last_error = Exception(
                    "Gemini returned an empty response."
                )

            except Exception as e:

                last_error = e

                error_text = str(e).lower()

                # Retry temporary server/rate-limit errors.
                transient_error = (
                    "503" in error_text
                    or "unavailable" in error_text
                    or "429" in error_text
                    or "resource_exhausted" in error_text
                    or "timeout" in error_text
                    or "500" in error_text
                )

                if transient_error and attempt < 2:

                    wait_time = 2 ** attempt

                    time.sleep(wait_time)

                    continue

                break

    raise last_error


# =========================================================
# ASK SAATHI
# =========================================================

if st.button(
    ui["button"],
    type="primary"
):

    # -----------------------------------------------------
    # SELECT TEXT OR VOICE QUESTION
    # -----------------------------------------------------

    final_question = question.strip()

    if not final_question and voice_question:

        final_question = voice_question.strip()


    # -----------------------------------------------------
    # EMPTY QUESTION
    # -----------------------------------------------------

    if not final_question:

        st.warning(ui["empty"])


    else:

        # -------------------------------------------------
        # SHOW QUESTION
        # -------------------------------------------------

        st.info(
            f"📝 Question received:\n\n{final_question}"
        )


        # -------------------------------------------------
        # RED FLAG CHECK
        # -------------------------------------------------

        detected_flags = detect_red_flags(
            final_question
        )


        # -------------------------------------------------
        # SHOW RED FLAG IMMEDIATELY
        # -------------------------------------------------

        if detected_flags:

            title, message = RED_FLAG_MESSAGES[
                language
            ]

            st.error(
                f"{title}\n\n{message}"
            )

            st.warning(
                EMERGENCY_ACTION[language]
            )

            # Show what triggered the detector
            with st.expander(
                "🔎 Detected warning signs"
            ):

                for flag in detected_flags:

                    st.write(
                        f"• {flag}"
                    )


        # -------------------------------------------------
        # GEMINI PROMPT
        # -------------------------------------------------

        prompt = f"""
You are Saathi AI Health Agent.

You are a digital health-information assistant designed
to support frontline health workers such as ASHA and ANM
workers in India.

Selected health topic:
{topic}

Selected language:
{language}

Health question:
{final_question}

Possible red flags detected by Saathi:
{detected_flags}

IMPORTANT LANGUAGE RULE:

Respond ONLY in {language}.

Use simple, clear and practical language that a frontline
health worker can understand and explain to a patient.

=========================================================
SAFETY RULES
=========================================================

1. Do NOT diagnose the patient.

2. Do NOT prescribe medicines.

3. Do NOT provide medicine dosages.

4. Do NOT replace a qualified doctor.

5. If the question contains possible emergency symptoms,
   treat it as potentially urgent.

6. Never tell the user to wait when serious warning signs
   are present.

7. Clearly recommend urgent medical evaluation when needed.

8. Encourage referral to an appropriate healthcare facility.

9. Give practical first-level health guidance.

10. Do not make assumptions about the patient's diagnosis.

11. If vital measurements are available, explain that they
    should be checked according to appropriate health-worker
    protocols.

12. If the question involves pregnancy, infants, elderly
    people, or other vulnerable people, use extra caution.

13. For emergencies, prioritize immediate safety and referral
    rather than lengthy explanations.

=========================================================
RESPONSE STRUCTURE
=========================================================

### 1. What it may mean

Give a simple explanation of possible health concerns.
Do not diagnose.

### 2. Important warning signs

List important symptoms that require urgent attention.

### 3. What the health worker can do

Give safe first-level actions.

Examples may include:

- Observe the person's condition.
- Check available vital signs when appropriate.
- Ask relevant basic questions.
- Keep the person safe.
- Arrange referral.
- Avoid unsafe treatment.
- Communicate important information to the receiving
  healthcare professional.

### 4. When to refer urgently

Clearly explain when urgent referral or emergency care
is required.

### 5. Safety note

Remind the health worker that Saathi provides information
support and does not provide a diagnosis or replace
professional medical care.

=========================================================
EMERGENCY PRIORITY
=========================================================

If the question appears to describe a possible emergency,
start the response with:

🚨 URGENT MEDICAL ATTENTION MAY BE NEEDED

Then give concise practical guidance and recommend
immediate professional medical evaluation.

Do not provide medicine doses.
"""


        # -------------------------------------------------
        # CALL GEMINI
        # -------------------------------------------------

        try:

            with st.spinner(
                "🩺 Saathi is preparing guidance..."
            ):

                answer, used_model = generate_with_retry(
                    prompt
                )


            # -------------------------------------------------
            # DISPLAY ANSWER
            # -------------------------------------------------

            st.success(
                ui["guidance"]
            )

            st.write(answer)


            # Optional technical information
            with st.expander(
                "ℹ️ AI service information"
            ):

                st.write(
                    f"Response generated using: `{used_model}`"
                )


        # -------------------------------------------------
        # API ERROR
        # -------------------------------------------------

        except Exception as e:

            st.error(
                "❌ Saathi's AI service is temporarily unavailable."
            )

            error_text = str(e)

            # If red flag exists, do NOT hide emergency advice.
            if detected_flags:

                st.warning(
                    "🚨 IMPORTANT: A possible emergency warning "
                    "sign was detected before the AI request."
                )

                st.warning(
                    EMERGENCY_ACTION[language]
                )

            st.info(
                "The Gemini service may be temporarily busy. "
                "Please try again after a short time."
            )

            # Show technical error only in expandable section.
            with st.expander(
                "Technical error details"
            ):

                st.code(
                    error_text
                )
