import time
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

@st.cache_resource
def get_gemini_client():
    return genai.Client(
        api_key=st.secrets["GEMINI_API_KEY"]
    )


client = get_gemini_client()


# =========================================================
# GEMINI RETRY FUNCTION
# =========================================================

def generate_with_retry(contents, max_retries=4):
    """
    Calls Gemini and automatically retries temporary errors
    such as 503, 429, 500, 502 and 504.
    """

    last_error = None

    for attempt in range(max_retries):

        try:

            response = client.models.generate_content(
                model="gemini-3.6-flash",
                contents=contents
            )

            return response

        except Exception as e:

            last_error = e
            error_text = str(e).upper()

            temporary_error = (
                "503" in error_text
                or "UNAVAILABLE" in error_text
                or "429" in error_text
                or "RESOURCE_EXHAUSTED" in error_text
                or "500" in error_text
                or "502" in error_text
                or "504" in error_text
                or "INTERNAL" in error_text
            )

            if temporary_error and attempt < max_retries - 1:

                wait_time = 3 * (2 ** attempt)

                time.sleep(wait_time)

            else:

                raise last_error


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

            voice_prompt = f"""
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

            voice_response = generate_with_retry(
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
                                    "data": audio_bytes
                                }
                            }
                        ]
                    }
                ]
            )

            if voice_response and voice_response.text:

                voice_question = voice_response.text.strip()

                st.success("🎤 Voice detected")

                st.write("**You said:**")

                st.write(voice_question)

    except Exception as e:

        error_text = str(e)

        st.error(
            "❌ Could not process the voice recording."
        )

        with st.expander("Technical error details"):

            st.code(error_text)


# =========================================================
# RED FLAG KEYWORDS
# =========================================================

RED_FLAGS = [

    # =====================================================
    # ENGLISH
    # =====================================================

    "heart attack",
    "myocardial infarction",
    "heart attack symptoms",
    "severe chest pain",
    "chest pain",
    "pressure in chest",
    "tightness in chest",
    "crushing chest pain",
    "difficulty breathing",
    "severe difficulty breathing",
    "shortness of breath",
    "cannot breathe",
    "can't breathe",
    "breathing stopped",
    "unconscious",
    "loss of consciousness",
    "not responding",
    "unresponsive",
    "seizure",
    "convulsion",
    "severe bleeding",
    "heavy bleeding",
    "uncontrolled bleeding",
    "vomiting blood",
    "coughing blood",
    "blood in vomit",
    "blood in stool",
    "black stool",
    "severe abdominal pain",
    "severe stomach pain",
    "severe headache",
    "worst headache",
    "sudden severe headache",
    "sudden weakness",
    "face drooping",
    "slurred speech",
    "difficulty speaking",
    "cannot speak",
    "paralysis",
    "stroke",
    "signs of stroke",
    "blue lips",
    "blue skin",
    "severe allergic reaction",
    "anaphylaxis",
    "swelling of face",
    "swelling of throat",
    "throat swelling",
    "severe burn",
    "electric shock",
    "poisoning",
    "snake bite",
    "snakebite",
    "severe dehydration",
    "fainting",
    "repeated fainting",
    "severe confusion",
    "confusion",
    "suicidal",
    "suicide",
    "suicidal thoughts",
    "self harm",
    "self-harm",
    "want to die",
    "pregnancy bleeding",
    "heavy bleeding during pregnancy",
    "severe pregnancy pain",
    "seizure during pregnancy",
    "baby not moving",
    "baby movement stopped",
    "newborn not breathing",
    "child not breathing",
    "child unconscious",

    # =====================================================
    # HINDI
    # =====================================================

    "हार्ट अटैक",
    "दिल का दौरा",
    "सीने में तेज दर्द",
    "सीने में दर्द",
    "सीने में दबाव",
    "सीने में जकड़न",
    "सांस लेने में कठिनाई",
    "सांस लेने में दिक्कत",
    "सांस नहीं आ रही",
    "सांस नहीं ले पा रहा",
    "बेहोश",
    "होश नहीं है",
    "जवाब नहीं दे रहा",
    "दौरा",
    "दौरे",
    "मिर्गी का दौरा",
    "बहुत ज्यादा खून बहना",
    "तेज रक्तस्राव",
    "खून नहीं रुक रहा",
    "खून की उल्टी",
    "खून की खांसी",
    "मल में खून",
    "काला मल",
    "पेट में तेज दर्द",
    "बहुत तेज सिरदर्द",
    "अचानक कमजोरी",
    "चेहरा टेढ़ा",
    "बोलने में दिक्कत",
    "बोल नहीं पा रहा",
    "लकवा",
    "स्ट्रोक",
    "होंठ नीले",
    "त्वचा नीली",
    "गंभीर एलर्जी",
    "चेहरा सूजना",
    "गला सूजना",
    "गंभीर जलना",
    "बिजली का झटका",
    "जहर",
    "सांप ने काटा",
    "गंभीर निर्जलीकरण",
    "बेहोशी",
    "भ्रम",
    "आत्महत्या",
    "आत्महत्या के विचार",
    "खुद को नुकसान",
    "मरना चाहता हूं",
    "गर्भावस्था में रक्तस्राव",
    "गर्भावस्था में तेज दर्द",
    "गर्भ में बच्चा नहीं हिल रहा",

    # =====================================================
    # TAMIL
    # =====================================================

    "மாரடைப்பு",
    "மாரடைப்பு அறிகுறிகள்",
    "மார்பில் கடுமையான வலி",
    "மார்பு வலி",
    "மார்பில் அழுத்தம்",
    "மார்பு இறுக்கம்",
    "சுவாசிப்பதில் சிரமம்",
    "மூச்சு விடுவதில் சிரமம்",
    "மூச்சு விட முடியவில்லை",
    "நினைவிழந்த",
    "நினைவிழப்பு",
    "சுயநினைவு இல்லை",
    "வலிப்பு",
    "கடுமையான இரத்தப்போக்கு",
    "அதிக இரத்தப்போக்கு",
    "இரத்தம் நிற்கவில்லை",
    "இரத்த வாந்தி",
    "இரத்தம் இருமல்",
    "மலத்தில் இரத்தம்",
    "கருப்பு மலம்",
    "வயிற்றில் கடுமையான வலி",
    "கடுமையான தலைவலி",
    "திடீர் பலவீனம்",
    "முகம் கோணல்",
    "பேசுவதில் சிரமம்",
    "பேச முடியவில்லை",
    "பக்கவாதம்",
    "உதடுகள் நீலமாக",
    "முகம் வீக்கம்",
    "தொண்டை வீக்கம்",
    "கடுமையான ஒவ்வாமை",
    "கடுமையான தீக்காயம்",
    "மின்சார அதிர்ச்சி",
    "விஷம்",
    "பாம்பு கடி",
    "கடுமையான நீரிழப்பு",
    "மயக்கம்",
    "குழப்பம்",
    "தற்கொலை",
    "தற்கொலை எண்ணம்",
    "சுய காயம்",
    "கர்ப்ப கால இரத்தப்போக்கு",
    "கர்ப்ப கால கடுமையான வலி",

    # =====================================================
    # TELUGU
    # =====================================================

    "హార్ట్ అటాక్",
    "గుండెపోటు",
    "తీవ్రమైన ఛాతీ నొప్పి",
    "ఛాతీ నొప్పి",
    "ఛాతీలో ఒత్తిడి",
    "ఛాతీ బిగుతు",
    "శ్వాస తీసుకోవడంలో ఇబ్బంది",
    "ఊపిరి తీసుకోవడం కష్టం",
    "ఊపిరి తీసుకోలేకపోతున్నాను",
    "స్పృహ కోల్పోవడం",
    "స్పృహలో లేరు",
    "స్పందించడం లేదు",
    "మూర్ఛ",
    "తీవ్రమైన రక్తస్రావం",
    "ఎక్కువ రక్తస్రావం",
    "రక్తస్రావం ఆగడం లేదు",
    "రక్తం వాంతి",
    "రక్తం దగ్గు",
    "మలంలో రక్తం",
    "నల్ల మలం",
    "తీవ్రమైన కడుపు నొప్పి",
    "తీవ్రమైన తలనొప్పి",
    "ఆకస్మిక బలహీనత",
    "మాట్లాడటంలో ఇబ్బంది",
    "మాట్లాడలేకపోతున్నాను",
    "పక్షవాతం",
    "స్ట్రోక్",
    "పెదవులు నీలం",
    "ముఖం వాపు",
    "గొంతు వాపు",
    "తీవ్రమైన అలెర్జీ",
    "తీవ్రమైన కాలిన గాయం",
    "విద్యుత్ షాక్",
    "విషం",
    "పాము కాటు",
    "తీవ్రమైన డీహైడ్రేషన్",
    "మూర్ఛపోవడం",
    "గందరగోళం",
    "ఆత్మహత్య",
    "ఆత్మహత్య ఆలోచనలు",
    "స్వీయ హాని",
    "గర్భధారణలో రక్తస్రావం",
    "గర్భధారణలో తీవ్రమైన నొప్పి",

    # =====================================================
    # MALAYALAM
    # =====================================================

    "ഹാർട്ട് അറ്റാക്ക്",
    "ഹൃദയാഘാതം",
    "കടുത്ത നെഞ്ചുവേദന",
    "നെഞ്ചുവേദന",
    "നെഞ്ചിൽ സമ്മർദ്ദം",
    "നെഞ്ചിൽ മുറുക്കം",
    "ശ്വസിക്കാൻ ബുദ്ധിമുട്ട്",
    "ശ്വാസം എടുക്കാൻ കഴിയുന്നില്ല",
    "ബോധരഹിതൻ",
    "ബോധം നഷ്ടപ്പെടൽ",
    "പ്രതികരിക്കുന്നില്ല",
    "അപസ്മാരം",
    "കടുത്ത രക്തസ്രാവം",
    "അമിതമായ രക്തസ്രാവം",
    "രക്തം നിൽക്കുന്നില്ല",
    "രക്തം ഛർദ്ദിക്കുക",
    "രക്തം ചുമയ്ക്കുക",
    "മലത്തിൽ രക്തം",
    "കറുത്ത മലം",
    "കടുത്ത വയറുവേദന",
    "കടുത്ത തലവേദന",
    "പെട്ടെന്നുള്ള ബലഹീനത",
    "സംസാരിക്കാൻ ബുദ്ധിമുട്ട്",
    "സംസാരിക്കാൻ കഴിയുന്നില്ല",
    "പക്ഷാഘാതം",
    "ചുണ്ടുകൾ നീലനിറം",
    "മുഖം വീക്കം",
    "തൊണ്ട വീക്കം",
    "ഗുരുതരമായ അലർജി",
    "ഗുരുതരമായ പൊള്ളൽ",
    "വൈദ്യുതാഘാതം",
    "വിഷബാധ",
    "പാമ്പുകടി",
    "കടുത്ത നിർജ്ജലീകരണം",
    "ബോധക്ഷയം",
    "ആശയക്കുഴപ്പം",
    "ആത്മഹത്യ",
    "ആത്മഹത്യ ചിന്തകൾ",
    "സ്വയം ഉപദ്രവിക്കൽ",
    "ഗർഭകാല രക്തസ്രാവം",
    "ഗർഭകാല കടുത്ത വേദന",

    # =====================================================
    # KANNADA
    # =====================================================

    "ಹಾರ್ಟ್ ಅಟ್ಯಾಕ್",
    "ಹೃದಯಾಘಾತ",
    "ತೀವ್ರವಾದ ಎದೆ ನೋವು",
    "ಎದೆ ನೋವು",
    "ಎದೆಯಲ್ಲಿ ಒತ್ತಡ",
    "ಎದೆ ಬಿಗಿತ",
    "ಉಸಿರಾಟದ ತೊಂದರೆ",
    "ಉಸಿರಾಡಲು ಸಾಧ್ಯವಾಗುತ್ತಿಲ್ಲ",
    "ಪ್ರಜ್ಞಾಹೀನ",
    "ಪ್ರಜ್ಞೆ ಕಳೆದುಕೊಳ್ಳುವುದು",
    "ಪ್ರತಿಕ್ರಿಯಿಸುತ್ತಿಲ್ಲ",
    "ಅಪಸ್ಮಾರ",
    "ತೀವ್ರ ರಕ್ತಸ್ರಾವ",
    "ಹೆಚ್ಚಿನ ರಕ್ತಸ್ರಾವ",
    "ರಕ್ತಸ್ರಾವ ನಿಲ್ಲುತ್ತಿಲ್ಲ",
    "ರಕ್ತ ವಾಂತಿ",
    "ರಕ್ತ ಕೆಮ್ಮು",
    "ಮಲದಲ್ಲಿ ರಕ್ತ",
    "ಕಪ್ಪು ಮಲ",
    "ತೀವ್ರ ಹೊಟ್ಟೆ ನೋವು",
    "ತೀವ್ರ ತಲೆನೋವು",
    "ಹಠಾತ್ ದೌರ್ಬಲ್ಯ",
    "ಮಾತನಾಡಲು ತೊಂದರೆ",
    "ಮಾತನಾಡಲು ಸಾಧ್ಯವಾಗುತ್ತಿಲ್ಲ",
    "ಪಾರ್ಶ್ವವಾಯು",
    "ತುಟಿಗಳು ನೀಲಿ",
    "ಮುಖದ ಊತ",
    "ಗಂಟಲಿನ ಊತ",
    "ತೀವ್ರ ಅಲರ್ಜಿ",
    "ತೀವ್ರ ಸುಟ್ಟ ಗಾಯ",
    "ವಿದ್ಯುತ್ ಆಘಾತ",
    "ವಿಷ",
    "ಹಾವು ಕಡಿತ",
    "ತೀವ್ರ ನಿರ್ಜಲೀಕರಣ",
    "ಮೂರ್ಛೆ",
    "ಗೊಂದಲ",
    "ಆತ್ಮಹತ್ಯೆ",
    "ಆತ್ಮಹತ್ಯೆ ಆಲೋಚನೆಗಳು",
    "ಸ್ವಯಂ ಹಾನಿ",
    "ಗರ್ಭಾವಸ್ಥೆಯಲ್ಲಿ ರಕ್ತಸ್ರಾವ",
    "ಗರ್ಭಾವಸ್ಥೆಯಲ್ಲಿ ತೀವ್ರ ನೋವು",

    # =====================================================
    # BENGALI
    # =====================================================

    "হার্ট অ্যাটাক",
    "হৃদরোগে আক্রান্ত",
    "তীব্র বুক ব্যথা",
    "বুকে ব্যথা",
    "বুকে চাপ",
    "বুকের টান",
    "শ্বাস নিতে অসুবিধা",
    "শ্বাস নিতে পারছি না",
    "অজ্ঞান",
    "চেতনা হারানো",
    "সাড়া দিচ্ছে না",
    "খিঁচুনি",
    "তীব্র রক্তপাত",
    "অতিরিক্ত রক্তপাত",
    "রক্তপাত বন্ধ হচ্ছে না",
    "রক্ত বমি",
    "রক্ত কাশি",
    "পায়খানায় রক্ত",
    "কালো পায়খানা",
    "তীব্র পেট ব্যথা",
    "তীব্র মাথাব্যথা",
    "হঠাৎ দুর্বলতা",
    "কথা বলতে অসুবিধা",
    "কথা বলতে পারছে না",
    "পক্ষাঘাত",
    "স্ট্রোক",
    "ঠোঁট নীল",
    "মুখ ফুলে যাওয়া",
    "গলা ফুলে যাওয়া",
    "তীব্র অ্যালার্জি",
    "গুরুতর পোড়া",
    "বৈদ্যুতিক শক",
    "বিষক্রিয়া",
    "সাপের কামড়",
    "তীব্র পানিশূন্যতা",
    "অজ্ঞান হয়ে যাওয়া",
    "বিভ্রান্তি",
    "আত্মহত্যা",
    "আত্মহত্যার চিন্তা",
    "নিজেকে আঘাত করা",
    "গর্ভাবস্থায় রক্তপাত",
    "গর্ভাবস্থায় তীব্র ব্যথা",

    # =====================================================
    # MARATHI
    # =====================================================

    "हार्ट अटॅक",
    "हृदयविकाराचा झटका",
    "तीव्र छातीत दुखणे",
    "छातीत दुखणे",
    "छातीत दाब",
    "छातीत घट्टपणा",
    "श्वास घेण्यास त्रास",
    "श्वास घेता येत नाही",
    "बेशुद्ध",
    "शुद्ध हरपणे",
    "प्रतिसाद देत नाही",
    "फिट",
    "तीव्र रक्तस्त्राव",
    "जास्त रक्तस्त्राव",
    "रक्तस्त्राव थांबत नाही",
    "रक्ताची उलटी",
    "रक्ताची खोकला",
    "मलात रक्त",
    "काळा मल",
    "तीव्र पोटदुखी",
    "तीव्र डोकेदुखी",
    "अचानक अशक्तपणा",
    "बोलण्यात अडचण",
    "बोलता येत नाही",
    "पक्षाघात",
    "स्ट्रोक",
    "ओठ निळे पडणे",
    "चेहऱ्यावर सूज",
    "घशावर सूज",
    "गंभीर ऍलर्जी",
    "गंभीर भाजणे",
    "वीज लागणे",
    "विषबाधा",
    "साप चावणे",
    "तीव्र निर्जलीकरण",
    "बेशुद्ध पडणे",
    "गोंधळ",
    "आत्महत्या",
    "आत्महत्येचे विचार",
    "स्वतःला इजा करणे",
    "गर्भावस्थेत रक्तस्त्राव",
    "गर्भावस्थेत तीव्र वेदना"
]


# =========================================================
# RED FLAG FUNCTION
# =========================================================

def detect_red_flags(text):

    if not text:
        return []

    text_lower = text.lower()

    detected = []

    for flag in RED_FLAGS:

        if flag.lower() in text_lower:

            if flag not in detected:

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
        # SHOW QUESTION
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
                "or refer the person to the nearest suitable "
                "healthcare facility immediately."
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

Red flag detected by Saathi:
{", ".join(detected_flags) if detected_flags else "None detected"}

IMPORTANT LANGUAGE RULE:

Respond ONLY in {language}.

Use simple, clear and practical language that a frontline
health worker can understand and explain to a patient.

SAFETY RULES:

1. Do not diagnose the patient.

2. Do not prescribe medicines.

3. Do not provide medicine dosages.

4. Do not replace a qualified doctor or healthcare professional.

5. Mention important warning signs when relevant.

6. If symptoms could indicate an emergency,
   clearly recommend urgent medical evaluation.

7. Do not tell the user to wait when serious warning signs
   are present.

8. Encourage referral to an appropriate healthcare facility
   or qualified healthcare professional when necessary.

9. Give practical and safe health information.

10. Focus on the selected health topic.

11. The answer should be useful for a frontline health worker
    during a community visit.

12. If the question mentions heart attack, stroke,
    severe breathing difficulty, severe bleeding,
    unconsciousness, seizure, severe allergic reaction,
    poisoning, serious injury, or another possible emergency,
    make the urgent referral recommendation very clear.

13. Never claim that the person definitely has a disease.

14. Never give false reassurance.

STRUCTURE YOUR RESPONSE:

### 1. What it may mean

Explain the possible general health concern without
making a diagnosis.

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
        # GEMINI RESPONSE WITH RETRY
        # -------------------------------------------------

        # -------------------------------------------------
# GEMINI RESPONSE WITH SAFE ERROR HANDLING
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

        st.warning(
            "⚠️ Saathi could not generate a response right now. "
            "Please try again later."
        )

except Exception as e:

    error_message = str(e).lower()

    # ---------------------------------------------
    # API QUOTA / RATE LIMIT
    # ---------------------------------------------

    if (
        "quota" in error_message
        or "rate limit" in error_message
        or "resource exhausted" in error_message
        or "429" in error_message
    ):

        st.warning(
            "⚠️ Saathi's AI request limit has been reached."
        )

        st.info(
            "The health-safety features such as red-flag detection "
            "can still work locally. Please try the AI response again "
            "after the API limit becomes available."
        )

    # ---------------------------------------------
    # TEMPORARY GEMINI SERVICE ERROR
    # ---------------------------------------------

    elif (
        "503" in error_message
        or "unavailable" in error_message
        or "overloaded" in error_message
    ):

        st.warning(
            "⚠️ Saathi's AI service is temporarily unavailable."
        )

        st.info(
            "Please wait a little and try again. "
            "This is a temporary AI service issue."
        )

    # ---------------------------------------------
    # OTHER ERROR
    # ---------------------------------------------

    else:

        st.error(
            "❌ Saathi encountered a temporary error."
        )

        st.info(
            "Please check your API configuration and try again."
        )
            # -------------------------------------------------
            # 503 / TEMPORARY GEMINI ERROR
            # -------------------------------------------------
            if (
                "503" in error_upper
                or "UNAVAILABLE" in error_upper
            ):

                st.error(
                    "⚠️ Saathi's AI service is temporarily busy."
                )

                st.info(
                    "Gemini is currently experiencing high demand. "
                    "Saathi automatically retried the request several times. "
                    "Please try again after a short time."
                )


            # -------------------------------------------------
            # 429 / RATE LIMIT
            # -------------------------------------------------

            elif (
                "429" in error_upper
                or "RESOURCE_EXHAUSTED" in error_upper
            ):

                st.error(
                    "⚠️ Gemini API request limit reached."
                )

                st.info(
                    "Please wait for the API limit to reset "
                    "and then try again."
                )


            # -------------------------------------------------
            # OTHER SERVER ERRORS
            # -------------------------------------------------

            elif (
                "500" in error_upper
                or "502" in error_upper
                or "504" in error_upper
            ):

                st.error(
                    "⚠️ Saathi's AI service is temporarily unavailable."
                )

                st.info(
                    "This appears to be a temporary Gemini server "
                    "problem. Please try again shortly."
                )


            # -------------------------------------------------
            # OTHER ERRORS
            # -------------------------------------------------

            else:

                st.error(
                    "❌ Saathi encountered a technical error."
                )

                with st.expander(
                    "Technical error details"
                ):

                    st.code(error_text)
