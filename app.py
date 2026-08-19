import streamlit as st
import time
from google import genai


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
# MODELS
# =========================================================

PRIMARY_MODEL = "gemini-3.6-flash"
FALLBACK_MODEL = "gemini-3.5-flash"


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
    "
