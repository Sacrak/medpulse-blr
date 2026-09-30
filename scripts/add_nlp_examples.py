import json

path = "data/nlp/emergency_examples.json"

new_examples = [
    # =========================
    # CARDIAC
    # =========================
    
        # =========================
    # ALLERGIC REACTION + RESPIRATORY
    # =========================

    
        # =========================
    # BURNS BOUNDARY EXAMPLES
    # =========================

   
     # ============================================================
    # CARDIAC — multilingual / symptom-specific
    # ============================================================
    {
        "id": "ex_245",
        "text": "ನನಗೆ ಎದೆ ತುಂಬಾ ಬಿಗಿಯಾಗಿದ್ದು ಬೆವರು ಬರುತ್ತಿದೆ",
        "language": "kn",
        "categories": ["CARDIAC"],
        "severity": "HIGH",
        "symptoms": ["chest tightness", "sweating"],
    },
    {
        "id": "ex_246",
        "text": "எனக்கு திடீரென்று கடுமையான நெஞ்சு வலி மற்றும் வியர்வை வருகிறது",
        "language": "ta",
        "categories": ["CARDIAC"],
        "severity": "HIGH",
        "symptoms": ["severe chest pain", "sweating"],
    },
    {
        "id": "ex_247",
        "text": "मुझे अचानक बहुत तेज सीने में दर्द और पसीना आ रहा है",
        "language": "hi",
        "categories": ["CARDIAC"],
        "severity": "HIGH",
        "symptoms": ["severe chest pain", "sweating"],
    },
    {
        "id": "ex_248",
        "text": "నాకు ఛాతిలో బిగుతుగా ఉంది మరియు నొప్పి చేతికి వెళ్తోంది",
        "language": "te",
        "categories": ["CARDIAC"],
        "severity": "CRITICAL",
        "symptoms": ["chest pressure", "pain radiating to arm"],
    },
    {
        "id": "ex_249",
        "text": "I suddenly have crushing chest pressure and pain spreading to my left arm",
        "language": "en",
        "categories": ["CARDIAC"],
        "severity": "CRITICAL",
        "symptoms": ["chest pressure", "radiating arm pain"],
    },
    {
        "id": "ex_250",
        "text": "എനിക്ക് കഠിനമായ നെഞ്ചുവേദനയും ഇടത് കൈയിൽ വേദനയും ഉണ്ട്",
        "language": "ml",
        "categories": ["CARDIAC"],
        "severity": "CRITICAL",
        "symptoms": ["severe chest pain", "left arm pain"],
    },
    {
        "id": "ex_251",
        "text": "सीने में दबाव जैसा दर्द है और बहुत पसीना आ रहा है",
        "language": "hi",
        "categories": ["CARDIAC"],
        "severity": "HIGH",
        "symptoms": ["chest pressure", "sweating"],
    },
    {
        "id": "ex_252",
        "text": "ನನಗೆ ಎದೆ ನೋವು, ಉಸಿರಾಟದ ತೊಂದರೆ ಮತ್ತು ತಣ್ಣನೆಯ ಬೆವರು ಬರುತ್ತಿದೆ",
        "language": "kn",
        "categories": ["CARDIAC", "RESPIRATORY"],
        "severity": "CRITICAL",
        "symptoms": ["chest pain", "breathing difficulty", "cold sweat"],
    },

    # ============================================================
    # BURNS — multilingual
    # ============================================================
    {
        "id": "ex_253",
        "text": "ನನ್ನ ಕೈಗೆ ಬಿಸಿ ಎಣ್ಣೆ ಬಿದ್ದು ತೀವ್ರವಾಗಿ ಸುಟ್ಟಿದೆ",
        "language": "kn",
        "categories": ["BURNS"],
        "severity": "HIGH",
        "symptoms": ["severe hand burn", "hot oil burn"],
    },
    {
        "id": "ex_254",
        "text": "என் கையில் கொதிக்கும் நீர் விழுந்து மோசமாக சுட்டுவிட்டது",
        "language": "ta",
        "categories": ["BURNS"],
        "severity": "HIGH",
        "symptoms": ["severe hand burn", "hot water burn"],
    },
    {
        "id": "ex_255",
        "text": "నా చేతిపై వేడి నూనె పడడంతో బాగా కాలిపోయింది",
        "language": "te",
        "categories": ["BURNS"],
        "severity": "HIGH",
        "symptoms": ["severe hand burn", "hot oil burn"],
    },
    {
        "id": "ex_256",
        "text": "मेरे हाथ पर गर्म पानी गिर गया और त्वचा बुरी तरह जल गई",
        "language": "hi",
        "categories": ["BURNS"],
        "severity": "HIGH",
        "symptoms": ["hand burn", "hot water burn"],
    },
    {
        "id": "ex_257",
        "text": "എന്റെ കൈയിൽ ചൂടുള്ള എണ്ണ വീണ് ഗുരുതരമായി പൊള്ളിപ്പോയി",
        "language": "ml",
        "categories": ["BURNS"],
        "severity": "HIGH",
        "symptoms": ["severe hand burn", "hot oil burn"],
    },
    {
        "id": "ex_258",
        "text": "My forearm was badly burned by steam and large blisters have formed",
        "language": "en",
        "categories": ["BURNS"],
        "severity": "HIGH",
        "symptoms": ["forearm burn", "steam burn", "blisters"],
    },
    {
        "id": "ex_259",
        "text": "ನನ್ನ ಮುಖದ ಮೇಲೆ ಬಿಸಿ ದ್ರವ ಬಿದ್ದು ಸುಟ್ಟ ಗಾಯವಾಗಿದೆ",
        "language": "kn",
        "categories": ["BURNS"],
        "severity": "HIGH",
        "symptoms": ["facial burn", "hot liquid burn"],
    },
    {
        "id": "ex_260",
        "text": "என் காலில் தீக்காயம் ஏற்பட்டுள்ளது மற்றும் தோல் உரிந்து வருகிறது",
        "language": "ta",
        "categories": ["BURNS"],
        "severity": "HIGH",
        "symptoms": ["leg burn", "peeling skin"],
    },

    # ============================================================
    # ALLERGY ↔ RESPIRATORY ↔ CARDIAC
    # ============================================================
    {
        "id": "ex_261",
        "text": "I ate something and now my lips are swollen and I am struggling to breathe",
        "language": "en",
        "categories": ["ALLERGIC_REACTION", "RESPIRATORY"],
        "severity": "CRITICAL",
        "symptoms": ["swollen lips", "breathing difficulty"],
    },
    {
        "id": "ex_262",
        "text": "மருந்து எடுத்த பிறகு தொண்டை வீங்கி மூச்சு விட கஷ்டமாக உள்ளது",
        "language": "ta",
        "categories": ["ALLERGIC_REACTION", "RESPIRATORY"],
        "severity": "CRITICAL",
        "symptoms": ["throat swelling", "breathing difficulty"],
    },
    {
        "id": "ex_263",
        "text": "ನನಗೆ ಆಹಾರ ತಿಂದ ನಂತರ ದೇಹದಾದ್ಯಂತ ಚರ್ಮದ ಗುಳ್ಳೆಗಳು ಮತ್ತು ಉಸಿರಾಟದ ತೊಂದರೆ ಬಂದಿದೆ",
        "language": "kn",
        "categories": ["ALLERGIC_REACTION", "RESPIRATORY"],
        "severity": "CRITICAL",
        "symptoms": ["hives", "breathing difficulty"],
    },
    {
        "id": "ex_264",
        "text": "दवा लेने के बाद मेरे गले में सूजन और सांस लेने में परेशानी हो रही है",
        "language": "hi",
        "categories": ["ALLERGIC_REACTION", "RESPIRATORY"],
        "severity": "CRITICAL",
        "symptoms": ["throat swelling", "breathing difficulty"],
    },
    {
        "id": "ex_265",
        "text": "After eating peanuts I developed hives but I can breathe normally",
        "language": "en",
        "categories": ["ALLERGIC_REACTION"],
        "severity": "HIGH",
        "symptoms": ["hives", "food exposure"],
    },
    {
        "id": "ex_266",
        "text": "I have chest pressure with sweating but no rash, itching, or throat swelling",
        "language": "en",
        "categories": ["CARDIAC"],
        "severity": "CRITICAL",
        "symptoms": ["chest pressure", "sweating"],
    },
    {
        "id": "ex_267",
        "text": "I have hives and wheezing after eating food",
        "language": "en",
        "categories": ["ALLERGIC_REACTION", "RESPIRATORY"],
        "severity": "CRITICAL",
        "symptoms": ["hives", "wheezing"],
    },
    {
        "id": "ex_268",
        "text": "எனக்கு மார்பு இறுக்கமாக உள்ளது ஆனால் சொறி மற்றும் அரிப்பு கூட உள்ளது",
        "language": "ta",
        "categories": ["ALLERGIC_REACTION", "RESPIRATORY"],
        "severity": "HIGH",
        "symptoms": ["chest tightness", "rash", "itching"],
    },

    # ============================================================
    # POISONING ↔ RESPIRATORY
    # ============================================================
    {
        "id": "ex_269",
        "text": "I accidentally inhaled pesticide fumes and now I am coughing badly",
        "language": "en",
        "categories": ["POISONING", "RESPIRATORY"],
        "severity": "HIGH",
        "symptoms": ["pesticide exposure", "coughing"],
    },
    {
        "id": "ex_270",
        "text": "ಕೀಟನಾಶಕದ ಹೊಗೆಯನ್ನು ಉಸಿರಾಡಿದ ನಂತರ ನನಗೆ ಉಸಿರಾಟದ ತೊಂದರೆ ಇದೆ",
        "language": "kn",
        "categories": ["POISONING", "RESPIRATORY"],
        "severity": "HIGH",
        "symptoms": ["pesticide exposure", "breathing difficulty"],
    },
    {
        "id": "ex_271",
        "text": "कीटनाशक की गैस सांस में जाने के बाद मुझे खांसी और चक्कर आ रहे हैं",
        "language": "hi",
        "categories": ["POISONING", "RESPIRATORY"],
        "severity": "HIGH",
        "symptoms": ["pesticide exposure", "coughing", "dizziness"],
    },
    {
        "id": "ex_272",
        "text": "வேதிப்பொருளை சுவாசித்த பிறகு எனக்கு இருமலும் மூச்சுத்திணறலும் ஏற்பட்டது",
        "language": "ta",
        "categories": ["POISONING", "RESPIRATORY"],
        "severity": "HIGH",
        "symptoms": ["chemical inhalation", "coughing", "breathing difficulty"],
    },
    {
        "id": "ex_273",
        "text": "I swallowed a cleaning liquid and now my throat is burning",
        "language": "en",
        "categories": ["POISONING"],
        "severity": "CRITICAL",
        "symptoms": ["chemical ingestion", "throat burning"],
    },
    {
        "id": "ex_274",
        "text": "ನಾನು ಸ್ವಲ್ಪ ಕ್ಲೀನಿಂಗ್ ದ್ರವವನ್ನು ನುಂಗಿದ್ದೇನೆ ಮತ್ತು ವಾಂತಿ ಬರುತ್ತಿದೆ",
        "language": "kn",
        "categories": ["POISONING"],
        "severity": "CRITICAL",
        "symptoms": ["cleaning liquid ingestion", "vomiting"],
    },
    {
        "id": "ex_275",
        "text": "I was exposed to strong paint thinner fumes and feel dizzy",
        "language": "en",
        "categories": ["POISONING"],
        "severity": "HIGH",
        "symptoms": ["chemical fumes", "dizziness"],
    },
    {
        "id": "ex_276",
        "text": "നീണ്ട സമയം രാസവാതകം ശ്വസിച്ചതിന് ശേഷം തല ചുറ്റുന്നു",
        "language": "ml",
        "categories": ["POISONING", "RESPIRATORY"],
        "severity": "HIGH",
        "symptoms": ["chemical inhalation", "dizziness"],
    },

    # ============================================================
    # HARD NEGATIVES / LOW-SEVERITY
    # ============================================================
    {
        "id": "ex_277",
        "text": "I bumped my knee lightly but I can walk normally",
        "language": "en",
        "categories": [],
        "severity": "LOW",
        "symptoms": ["minor knee bump"],
    },
    {
        "id": "ex_278",
        "text": "ನನ್ನ ಕೈಗೆ ಸಣ್ಣ ಗೀರು ಬಿದ್ದಿದೆ, ರಕ್ತಸ್ರಾವ ಈಗಾಗಲೇ ನಿಂತಿದೆ",
        "language": "kn",
        "categories": [],
        "severity": "LOW",
        "symptoms": ["minor scratch", "bleeding stopped"],
    },
    {
        "id": "ex_279",
        "text": "என் விரலில் சிறிய காயம் மட்டுமே உள்ளது, இரத்தம் வரவில்லை",
        "language": "ta",
        "categories": [],
        "severity": "LOW",
        "symptoms": ["minor finger injury"],
    },
    {
        "id": "ex_280",
        "text": "मेरा पेट थोड़ा दर्द कर रहा था लेकिन अब ठीक हो रहा है",
        "language": "hi",
        "categories": [],
        "severity": "LOW",
        "symptoms": ["mild abdominal pain", "improving"],
    },
    {
        "id": "ex_281",
        "text": "My eyes feel a little tired after looking at the screen",
        "language": "en",
        "categories": [],
        "severity": "LOW",
        "symptoms": ["mild eye tiredness"],
    },
    {
        "id": "ex_282",
        "text": "ನನ್ನ ಕಾಲಿಗೆ ಸಣ್ಣ ಮೂಳೆ ನೋವು ಇದೆ ಆದರೆ ಊತ ಅಥವಾ ಗಾಯ ಇಲ್ಲ",
        "language": "kn",
        "categories": [],
        "severity": "LOW",
        "symptoms": ["mild leg discomfort"],
    },
    {
        "id": "ex_283",
        "text": "I have a tiny bruise and there is no pain or swelling",
        "language": "en",
        "categories": [],
        "severity": "LOW",
        "symptoms": ["minor bruise"],
    },
    {
        "id": "ex_284",
        "text": "எனக்கு லேசான வயிற்று அசௌகரியம் மட்டும் உள்ளது, அது குறைந்து வருகிறது",
        "language": "ta",
        "categories": [],
        "severity": "LOW",
        "symptoms": ["mild abdominal discomfort", "improving"],
    },

    # ============================================================
    # MULTILINGUAL / CODE-SWITCHED BOUNDARY CASES
    # ============================================================
    {
        "id": "ex_285",
        "text": "ನನಗೆ chest pain ತುಂಬಾ ಇದೆ ಮತ್ತು sweating ಆಗುತ್ತಿದೆ",
        "language": "kn",
        "categories": ["CARDIAC"],
        "severity": "HIGH",
        "symptoms": ["chest pain", "sweating"],
    },
    {
        "id": "ex_286",
        "text": "எனக்கு breathing difficulty இருக்கு, மேலும் hives வந்திருக்கிறது",
        "language": "ta",
        "categories": ["ALLERGIC_REACTION", "RESPIRATORY"],
        "severity": "CRITICAL",
        "symptoms": ["breathing difficulty", "hives"],
    },
    {
        "id": "ex_287",
        "text": "ನಾನು chemical fumes inhale ಮಾಡಿದೆ ಮತ್ತು ಈಗ coughing ಆಗುತ್ತಿದೆ",
        "language": "kn",
        "categories": ["POISONING", "RESPIRATORY"],
        "severity": "HIGH",
        "symptoms": ["chemical inhalation", "coughing"],
    },
    {
        "id": "ex_288",
        "text": "मुझे chest tightness है और सांस लेने में बहुत difficulty हो रही है",
        "language": "hi",
        "categories": ["RESPIRATORY"],
        "severity": "HIGH",
        "symptoms": ["chest tightness", "breathing difficulty"],
    },
    {
        "id": "ex_289",
        "text": "నా hand మీద hot oil పడింది, చాలా burn అయింది",
        "language": "te",
        "categories": ["BURNS"],
        "severity": "HIGH",
        "symptoms": ["hand burn", "hot oil burn"],
    },
    {
        "id": "ex_290",
        "text": "எனக்கு severe chest pain இருக்கு, left arm க்கும் pain போகுது",
        "language": "ta",
        "categories": ["CARDIAC"],
        "severity": "CRITICAL",
        "symptoms": ["severe chest pain", "left arm pain"],
    },
    {
        "id": "ex_291",
        "text": "ನನಗೆ food allergy ಆದ ಮೇಲೆ throat swelling ಮತ್ತು breathing problem ಬಂದಿದೆ",
        "language": "kn",
        "categories": ["ALLERGIC_REACTION", "RESPIRATORY"],
        "severity": "CRITICAL",
        "symptoms": ["food allergy", "throat swelling", "breathing difficulty"],
    },
    {
        "id": "ex_292",
        "text": "I fell from my bike, but there is only a small bruise and no pain",
        "language": "en",
        "categories": [],
        "severity": "LOW",
        "symptoms": ["minor bruise", "bike fall", "no pain"],
    },
    
]


with open(path, "r", encoding="utf-8") as file:
    data = json.load(file)

existing_ids = {example["id"] for example in data}

duplicates = [
    example["id"]
    for example in new_examples
    if example["id"] in existing_ids
]

if duplicates:
    raise ValueError(f"Duplicate IDs found: {duplicates}")

data.extend(new_examples)

with open(path, "w", encoding="utf-8") as file:
    json.dump(
        data,
        file,
        ensure_ascii=False,
        indent=2
    )

print(f"Added {len(new_examples)} examples.")
print(f"Total examples: {len(data)}")