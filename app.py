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
# LANGUAGE
# -----------------------------
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
# MULTILINGUAL RED FLAG DETECTION
# -----------------------------

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
    "खून वाली उल्टी",
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


def detect_red_flags(text):
    text = text.lower()
    detected = []

    for flag in RED_FLAGS:
        if flag.lower() in text:
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

    RED_FLAG_MESSAGES = {
        "English": (
            "🚨 RED FLAG / URGENT WARNING\n\n"
            "The question contains a possible warning sign "
            "that may require urgent medical evaluation.",
            "Please do not rely only on this AI tool. "
            "Seek appropriate emergency medical care immediately "
            "if the person is seriously unwell."
        ),

        "Hindi": (
            "🚨 गंभीर चेतावनी / तत्काल चिकित्सा सहायता\n\n"
            "आपके प्रश्न में एक संभावित चेतावनी संकेत है "
            "जिसके लिए तुरंत चिकित्सकीय जांच की आवश्यकता हो सकती है।",
            "केवल इस AI टूल पर निर्भर न रहें। "
            "यदि व्यक्ति गंभीर रूप से अस्वस्थ है, तो तुरंत "
            "उचित आपातकालीन चिकित्सा सहायता लें।"
        ),

        "Tamil": (
            "🚨 ஆபத்து அறிகுறி / அவசர எச்சரிக்கை\n\n"
            "உங்கள் கேள்வியில் அவசர மருத்துவ பரிசோதனை "
            "தேவைப்படக்கூடிய ஆபத்து அறிகுறி உள்ளது.",
            "இந்த AI கருவியை மட்டும் நம்ப வேண்டாம். "
            "நபர் மிகவும் உடல்நிலை பாதிக்கப்பட்டிருந்தால், "
            "உடனடியாக அவசர மருத்துவ உதவியைப் பெறுங்கள்."
        ),

        "Telugu": (
            "🚨 ప్రమాద సూచన / అత్యవసర హెచ్చరిక\n\n"
            "మీ ప్రశ్నలో తక్షణ వైద్య పరీక్ష అవసరమయ్యే "
            "ప్రమాద సూచన ఉండవచ్చు.",
            "ఈ AI సాధనంపై మాత్రమే ఆధారపడవద్దు. "
            "వ్యక్తి తీవ్రంగా అనారోగ్యంగా ఉంటే వెంటనే "
            "అత్యవసర వైద్య సహాయం పొందండి."
        ),

        "Malayalam": (
            "🚨 അപകട സൂചന / അടിയന്തര മുന്നറിയിപ്പ്\n\n"
            "നിങ്ങളുടെ ചോദ്യത്തിൽ അടിയന്തര മെഡിക്കൽ പരിശോധന "
            "ആവശ്യമായേക്കാവുന്ന ഒരു അപകട സൂചനയുണ്ട്.",
            "ഈ AI ഉപകരണത്തെ മാത്രം ആശ്രയിക്കരുത്. "
            "വ്യക്തിക്ക് ഗുരുതരമായ അസുഖമുണ്ടെങ്കിൽ ഉടൻ "
            "അടിയന്തര മെഡിക്കൽ സഹായം തേടുക."
        ),

        "Kannada": (
            "🚨 ಅಪಾಯದ ಸೂಚನೆ / ತುರ್ತು ಎಚ್ಚರಿಕೆ\n\n"
            "ನಿಮ್ಮ ಪ್ರಶ್ನೆಯಲ್ಲಿ ತಕ್ಷಣ ವೈದ್ಯಕೀಯ ಪರೀಕ್ಷೆಯ "
            "ಅಗತ್ಯವಿರುವ ಅಪಾಯದ ಸೂಚನೆ ಇರಬಹುದು.",
            "ಈ AI ಸಾಧನವನ್ನು ಮಾತ್ರ ಅವಲಂಬಿಸಬೇಡಿ. "
            "ವ್ಯಕ್ತಿಯ ಆರೋಗ್ಯ ಸ್ಥಿತಿ ಗಂಭೀರವಾಗಿದ್ದರೆ ತಕ್ಷಣ "
            "ತುರ್ತು ವೈದ್ಯಕೀಯ ಸಹಾಯ ಪಡೆಯಿರಿ."
        ),

        "Bengali": (
            "🚨 বিপদের লক্ষণ / জরুরি সতর্কতা\n\n"
            "আপনার প্রশ্নে এমন একটি সম্ভাব্য বিপদের লক্ষণ রয়েছে "
            "যার জন্য জরুরি চিকিৎসা পরীক্ষার প্রয়োজন হতে পারে।",
            "শুধু এই AI টুলের উপর নির্ভর করবেন না। "
            "ব্যক্তি গুরুতর অসুস্থ হলে অবিলম্বে "
            "জরুরি চিকিৎসা সহায়তা নিন।"
        ),

        "Marathi": (
            "🚨 धोक्याची चिन्हे / तातडीची सूचना\n\n"
            "तुमच्या प्रश्नामध्ये तातडीच्या वैद्यकीय तपासणीची "
            "गरज असू शकणारे धोक्याचे चिन्ह आहे.",
            "फक्त या AI साधनावर अवलंबून राहू नका. "
            "व्यक्ती गंभीर आजारी असल्यास त्वरित "
            "आपत्कालीन वैद्यकीय मदत घ्या."
        )
    }

    red_flag_title, red_flag_advice = RED_FLAG_MESSAGES[language]

    st.error(red_flag_title)

    st.warning(red_flag_advice)

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

Response language:
{language}

IMPORTANT LANGUAGE RULES:
- Answer entirely in {language}.
- Use simple, clear language suitable for frontline health workers.
- Do not switch to English unless a medical term is necessary.
- If a medical term is necessary, explain it simply in {language}.

SAFETY RULES:
- Do not diagnose the patient.
- Do not prescribe medicines or dosages.
- Mention important warning signs when relevant.
- If symptoms could indicate an emergency, clearly recommend
  urgent medical evaluation.
- Do not tell the user to wait when serious warning signs are present.
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
                model="gemini-3.6-flash",
                contents=prompt
            )

            answer = response.text

            st.success("🩺 Saathi's Guidance")
            st.write(answer)

        except Exception as e:

            st.error("❌ Saathi encountered an error.")
            st.code(str(e))

    else:

        st.warning("Please enter a health question first.")
