import streamlit as st
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
        "empty": "कृपया पहले अपना स्वास्थ्य संबंधी प्रश्न लिखें या बोलें।"
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

            voice_response = client.models.generate_content(
                model="gemini-3.6-flash",
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
                                    "mime_type": "audio/wav",
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

        st.error("❌ Could not process the voice recording.")

        st.error(str(e))

# =========================================================
# RED FLAG DETECTION
# =========================================================

RED_FLAGS = [

    # English
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
    "electric shock",

    # Hindi
    "सीने में तेज दर्द",
    "सीने में दर्द",
    "सांस लेने में कठिनाई",
    "सांस लेने में दिक्कत",
    "सांस नहीं आ रही",
    "बेहोश",
    "होश नहीं है",
    "दौरा",
    "दौरे",
    "बहुत ज्यादा खून बहना",
    "तेज रक्तस्राव",
    "खून की उल्टी",
    "खून की खांसी",
    "पेट में तेज दर्द",
    "बहुत तेज सिरदर्द",
    "अचानक कमजोरी",
    "चेहरा टेढ़ा",
    "बोलने में दिक्कत",
    "लकवा",
    "होंठ नीले",
    "चेहरा सूजना",
    "गला सूजना",
    "आत्महत्या",
    "खुद को नुकसान",
    "गंभीर जलना",
    "बिजली का झटका",

    # Tamil
    "மார்பில் கடுமையான வலி",
    "மார்பு வலி",
    "சுவாசிப்பதில் சிரமம்",
    "மூச்சு விடுவதில் சிரமம்",
    "மூச்சு விட முடியவில்லை",
    "நினைவிழந்த",
    "நினைவிழப்பு",
    "சுயநினைவு இல்லை",
    "வலிப்பு",
    "கடுமையான இரத்தப்போக்கு",
    "அதிக இரத்தப்போக்கு",
    "இரத்த வாந்தி",
    "இரத்தம் இருமல்",
    "வயிற்றில் கடுமையான வலி",
    "கடுமையான தலைவலி",
    "திடீர் பலவீனம்",
    "முகம் கோணல்",
    "பேசுவதில் சிரமம்",
    "பக்கவாதம்",
    "உதடுகள் நீலமாக",
    "முகம் வீக்கம்",
    "தொண்டை வீக்கம்",
    "தற்கொலை",
    "சுய காயம்",
    "கடுமையான தீக்காயம்",
    "மின்சார அதிர்ச்சி",

    # Telugu
    "తీవ్రమైన ఛాతీ నొప్పి",
    "ఛాతీ నొప్పి",
    "శ్వాస తీసుకోవడంలో ఇబ్బంది",
    "ఊపిరి తీసుకోవడం కష్టం",
    "ఊపిరి తీసుకోలేకపోతున్నాను",
    "స్పృహ కోల్పోవడం",
    "స్పృహలో లేరు",
    "మూర్ఛ",
    "తీవ్రమైన రక్తస్రావం",
    "ఎక్కువ రక్తస్రావం",
    "రక్తం వాంతి",
    "రక్తం దగ్గు",
    "తీవ్రమైన కడుపు నొప్పి",
    "తీవ్రమైన తలనొప్పి",
    "ఆకస్మిక బలహీనత",
    "మాట్లాడటంలో ఇబ్బంది",
    "పక్షవాతం",
    "పెదవులు నీలం",
    "ముఖం వాపు",
    "గొంతు వాపు",
    "ఆత్మహత్య",
    "స్వీయ హాని",
    "తీవ్రమైన కాలిన గాయం",
    "విద్యుత్ షాక్",

    # Malayalam
    "കടുത്ത നെഞ്ചുവേദന",
    "നെഞ്ചുവേദന",
    "ശ്വസിക്കാൻ ബുദ്ധിമുട്ട്",
    "ശ്വാസം എടുക്കാൻ കഴിയുന്നില്ല",
    "ബോധരഹിതൻ",
    "ബോധം നഷ്ടപ്പെടൽ",
    "അപസ്മാരം",
    "കടുത്ത രക്തസ്രാവം",
    "അമിതമായ രക്തസ്രാവം",
    "രക്തം ഛർദ്ദിക്കുക",
    "രക്തം ചുമയ്ക്കുക",
    "കടുത്ത വയറുവേദന",
    "കടുത്ത തലവേദന",
    "പെട്ടെന്നുള്ള ബലഹീനത",
    "സംസാരിക്കാൻ ബുദ്ധിമുട്ട്",
    "പക്ഷാഘാതം",
    "ചുണ്ടുകൾ നീലനിറം",
    "മുഖം വീക്കം",
    "തൊണ്ട വീക്കം",
    "ആത്മഹത്യ",
    "സ്വയം ഉപദ്രവിക്കൽ",
    "ഗുരുതരമായ പൊള്ളൽ",
    "വൈദ്യുതാഘാതം",

    # Kannada
    "ತೀವ್ರವಾದ ಎದೆ ನೋವು",
    "ಎದೆ ನೋವು",
    "ಉಸಿರಾಟದ ತೊಂದರೆ",
    "ಉಸಿರಾಡಲು ಸಾಧ್ಯವಾಗುತ್ತಿಲ್ಲ",
    "ಪ್ರಜ್ಞಾಹೀನ",
    "ಪ್ರಜ್ಞೆ ಕಳೆದುಕೊಳ್ಳುವುದು",
    "ಅಪಸ್ಮಾರ",
    "ತೀವ್ರ ರಕ್ತಸ್ರಾವ",
    "ಹೆಚ್ಚಿನ ರಕ್ತಸ್ರಾವ",
    "ರಕ್ತ ವಾಂತಿ",
    "ರಕ್ತ ಕೆಮ್ಮು",
    "ತೀವ್ರ ಹೊಟ್ಟೆ ನೋವು",
    "ತೀವ್ರ ತಲೆನೋವು",
    "ಹಠಾತ್ ದೌರ್ಬಲ್ಯ",
    "ಮಾತನಾಡಲು ತೊಂದರೆ",
    "ಪಾರ್ಶ್ವವಾಯು",
    "ತುಟಿಗಳು ನೀಲಿ",
    "ಮುಖದ ಊತ",
    "ಗಂಟಲಿನ ಊತ",
    "ಆತ್ಮಹತ್ಯೆ",
    "ಸ್ವಯಂ ಹಾನಿ",
    "ತೀವ್ರ ಸುಟ್ಟ ಗಾಯ",
    "ವಿದ್ಯುತ್ ಆಘಾತ",

    # Bengali
    "তীব্র বুক ব্যথা",
    "বুকে ব্যথা",
    "শ্বাস নিতে অসুবিধা",
    "শ্বাস নিতে পারছি না",
    "অজ্ঞান",
    "চেতনা হারানো",
    "খিঁচুনি",
    "তীব্র রক্তপাত",
    "অতিরিক্ত রক্তপাত",
    "রক্ত বমি",
    "রক্ত কাশি",
    "তীব্র পেট ব্যথা",
    "তীব্র মাথাব্যথা",
    "হঠাৎ দুর্বলতা",
    "কথা বলতে অসুবিধা",
    "পক্ষাঘাত",
    "ঠোঁট নীল",
    "মুখ ফুলে যাওয়া",
    "গলা ফুলে যাওয়া",
    "আত্মহত্যা",
    "নিজেকে আঘাত করা",
    "গুরুতর পোড়া",
    "বৈদ্যুতিক শক",

    # Marathi
    "तीव्र छातीत दुखणे",
    "छातीत दुखणे",
    "श्वास घेण्यास त्रास",
    "श्वास घेता येत नाही",
    "बेशुद्ध",
    "शुद्ध हरपणे",
    "फिट",
    "तीव्र रक्तस्त्राव",
    "जास्त रक्तस्त्राव",
    "रक्ताची उलटी",
    "रक्ताची खोकला",
    "तीव्र पोटदुखी",
    "तीव्र डोकेदुखी",
    "अचानक अशक्तपणा",
    "बोलण्यात अडचण",
    "पक्षाघात",
    "ओठ निळे पडणे",
    "चेहऱ्यावर सूज",
    "घशावर सूज",
    "आत्महत्या",
    "स्वतःला इजा करणे",
    "गंभीर भाजणे",
    "वीज लागणे"
]

# =========================================================
# RED FLAG FUNCTION
# =========================================================

def detect_red_flags(text):

    text_lower = text.lower()

    detected = []

    for flag in RED_FLAGS:

        if flag.lower() in text_lower:
            detected.append(flag)

    return detected


# =========================================================
# RED FLAG MESSAGES
# =========================================================

RED_FLAG_MESSAGES = {

    "English": (
        "🚨 RED FLAG / URGENT WARNING",
        "This question contains a possible warning sign that may require urgent medical evaluation."
    ),

    "Hindi": (
        "🚨 गंभीर चेतावनी / तत्काल चिकित्सा सहायता",
        "आपके प्रश्न में एक संभावित चेतावनी संकेत है जिसके लिए तुरंत चिकित्सकीय जांच की आवश्यकता हो सकती है।"
    ),

    "Tamil": (
        "🚨 ஆபத்து அறிகுறி / அவசர எச்சரிக்கை",
        "உங்கள் கேள்வியில் அவசர மருத்துவ பரிசோதனை தேவைப்படக்கூடிய ஆபத்து அறிகுறி உள்ளது."
    ),

    "Telugu": (
        "🚨 ప్రమాద సూచన / అత్యవసర హెచ్చరిక",
        "మీ ప్రశ్నలో తక్షణ వైద్య పరీక్ష అవసరమయ్యే ప్రమాద సూచన ఉండవచ్చు."
    ),

    "Malayalam": (
        "🚨 അപകട സൂചന / അടിയന്തര മുന്നറിയിപ്പ്",
        "നിങ്ങളുടെ ചോദ്യത്തിൽ അടിയന്തര മെഡിക്കൽ പരിശോധന ആവശ്യമായേക്കാവുന്ന ഒരു അപകട സൂചനയുണ്ട്."
    ),

    "Kannada": (
        "🚨 ಅಪಾಯದ ಸೂಚನೆ / ತುರ್ತು ಎಚ್ಚರಿಕೆ",
        "ನಿಮ್ಮ ಪ್ರಶ್ನೆಯಲ್ಲಿ ತಕ್ಷಣ ವೈದ್ಯಕೀಯ ಪರೀಕ್ಷೆಯ ಅಗತ್ಯವಿರುವ ಅಪಾಯದ ಸೂಚನೆ ಇರಬಹುದು."
    ),

    "Bengali": (
        "🚨 বিপদের লক্ষণ / জরুরি সতর্কতা",
        "আপনার প্রশ্নে এমন একটি সম্ভাব্য বিপদের লক্ষণ রয়েছে যার জন্য জরুরি চিকিৎসা পরীক্ষার প্রয়োজন হতে পারে।"
    ),

    "Marathi": (
        "🚨 धोक्याची चिन्हे / तातडीची सूचना",
        "तुमच्या प्रश्नामध्ये तातडीच्या वैद्यकीय तपासणीची गरज असू शकणारे धोक्याचे चिन्ह आहे."
    )
}

# =========================================================
# ASK SAATHI
# =========================================================

if st.button(ui["button"], type="primary"):

    # -----------------------------------------------------
    # USE TEXT QUESTION OR VOICE QUESTION
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
        # SHOW QUESTION BEING PROCESSED
        # -------------------------------------------------

        st.info(
            f"📝 Question received:\n\n{final_question}"
        )

        # -------------------------------------------------
        # RED FLAG CHECK
        # -------------------------------------------------

        detected_flags = detect_red_flags(final_question)

        if detected_flags:

            title, message = RED_FLAG_MESSAGES[language]

            st.error(
                f"{title}\n\n{message}"
            )

            st.warning(
                "⚠️ Do not rely only on this AI tool. "
                "If the person is seriously unwell, "
                "contact appropriate emergency medical services "
                "or refer the person to the nearest suitable healthcare facility immediately."
            )

        # -------------------------------------------------
        # GEMINI PROMPT
        # -------------------------------------------------

        prompt = f"""
You are Saathi AI Health Agent.

You are a digital health-information assistant designed
to support frontline health workers such as ASHA and ANM workers in India.

Selected health topic:
{topic}

Selected language:
{language}

Health question:
{final_question}

IMPORTANT LANGUAGE RULE:
Respond ONLY in {language}.

Use simple and practical language that a frontline
health worker can understand and explain to a patient.

SAFETY RULES:

1. Do not diagnose the patient.

2. Do not prescribe medicines.

3. Do not provide medicine dosages.

4. Do not replace a qualified doctor or healthcare professional.

5. Mention important warning signs when relevant.

6. If the symptoms could indicate an emergency,
   clearly recommend urgent medical evaluation.

7. Do not tell the user to wait when serious warning signs
   are present.

8. Encourage referral to an appropriate healthcare facility
   or qualified healthcare professional when necessary.

9. Give practical and safe health information.

10. Focus on the selected health topic.

11. The answer should be useful for a frontline health worker
    during a community visit.

STRUCTURE YOUR RESPONSE:

### 1. What it may mean
Explain the possible general causes or health concern.

### 2. Important warning signs
List symptoms that require urgent attention.

### 3. What the health worker can do
Give safe first-level actions such as checking available
vital measurements, asking relevant questions, providing
basic supportive guidance, and arranging referral when needed.

### 4. When to refer
Clearly explain when the person should be referred
to a doctor, health centre, hospital, or emergency service.

### 5. Safety note
Remind the health worker that this is information support
and not a diagnosis or replacement for professional care.
"""

        # -------------------------------------------------
        # GEMINI RESPONSE
        # -------------------------------------------------

        try:

            with st.spinner("🩺 Saathi is preparing guidance..."):

                response = client.models.generate_content(
                    model="gemini-3.6-flash",
                    contents=prompt
                )

            if response.text:

                st.success(ui["guidance"])

                st.write(response.text)

            else:

                st.error(
                    "❌ Saathi did not receive a response. Please try again."
                )

        except Exception as e:

            st.error("❌ Saathi encountered an error.")

            st.error(str(e))
