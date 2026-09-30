import json

path = "data/nlp/emergency_examples.json"

new_examples = [

    # ============================================================
    # ALLERGIC REACTION <-> RESPIRATORY
    # ============================================================

    {
        "id": "ex_293",
        "text": "My lips suddenly became swollen after eating peanuts and I am struggling to breathe",
        "language": "en",
        "categories": ["ALLERGIC_REACTION", "RESPIRATORY"],
        "severity": "CRITICAL",
        "symptoms": ["lip swelling", "breathing difficulty", "food exposure"]
    },
    {
        "id": "ex_294",
        "text": "After taking the medicine my throat feels tight and I cannot breathe properly",
        "language": "en",
        "categories": ["ALLERGIC_REACTION", "RESPIRATORY"],
        "severity": "CRITICAL",
        "symptoms": ["throat tightness", "breathing difficulty", "medicine exposure"]
    },
    {
        "id": "ex_295",
        "text": "खाना खाने के बाद मेरे होंठ सूज गए और सांस लेने में बहुत परेशानी हो रही है",
        "language": "hi",
        "categories": ["ALLERGIC_REACTION", "RESPIRATORY"],
        "severity": "CRITICAL",
        "symptoms": ["lip swelling", "breathing difficulty", "food exposure"]
    },
    {
        "id": "ex_296",
        "text": "ಆಹಾರ ತಿಂದ ನಂತರ ನನ್ನ ಮುಖ ಊದಿಕೊಂಡಿದೆ ಮತ್ತು ಉಸಿರಾಡಲು ತುಂಬಾ ಕಷ್ಟವಾಗುತ್ತಿದೆ",
        "language": "kn",
        "categories": ["ALLERGIC_REACTION", "RESPIRATORY"],
        "severity": "CRITICAL",
        "symptoms": ["facial swelling", "breathing difficulty", "food exposure"]
    },
    {
        "id": "ex_297",
        "text": "மருந்து எடுத்த பிறகு தொண்டை இறுக்கமாகி மூச்சு விட முடியவில்லை",
        "language": "ta",
        "categories": ["ALLERGIC_REACTION", "RESPIRATORY"],
        "severity": "CRITICAL",
        "symptoms": ["throat tightness", "breathing difficulty", "medicine exposure"]
    },
    {
        "id": "ex_298",
        "text": "ఆహారం తిన్న తర్వాత గొంతు బిగుసుకుపోయి ఊపిరి తీసుకోవడం కష్టంగా ఉంది",
        "language": "te",
        "categories": ["ALLERGIC_REACTION", "RESPIRATORY"],
        "severity": "CRITICAL",
        "symptoms": ["throat tightness", "breathing difficulty", "food exposure"]
    },
    {
        "id": "ex_299",
        "text": "My skin is covered in hives but I am breathing normally",
        "language": "en",
        "categories": ["ALLERGIC_REACTION"],
        "severity": "HIGH",
        "symptoms": ["hives", "no breathing difficulty"]
    },
    {
        "id": "ex_300",
        "text": "I have a rash and swollen lips after eating something, but my breathing is normal",
        "language": "en",
        "categories": ["ALLERGIC_REACTION"],
        "severity": "HIGH",
        "symptoms": ["rash", "lip swelling", "food exposure", "normal breathing"]
    },


    # ============================================================
    # POISONING <-> RESPIRATORY
    # ============================================================

    {
        "id": "ex_301",
        "text": "I inhaled pesticide fumes and now I am coughing and struggling to breathe",
        "language": "en",
        "categories": ["POISONING", "RESPIRATORY"],
        "severity": "CRITICAL",
        "symptoms": ["pesticide inhalation", "coughing", "breathing difficulty"]
    },
    {
        "id": "ex_302",
        "text": "There was a chemical leak and after breathing the fumes I became short of breath",
        "language": "en",
        "categories": ["POISONING", "RESPIRATORY"],
        "severity": "CRITICAL",
        "symptoms": ["chemical exposure", "fume inhalation", "shortness of breath"]
    },
    {
        "id": "ex_303",
        "text": "I accidentally swallowed pesticide and have severe vomiting",
        "language": "en",
        "categories": ["POISONING"],
        "severity": "HIGH",
        "symptoms": ["pesticide ingestion", "vomiting"]
    },
    {
        "id": "ex_304",
        "text": "I inhaled smoke from a chemical spill but I can breathe normally now",
        "language": "en",
        "categories": ["POISONING"],
        "severity": "HIGH",
        "symptoms": ["chemical inhalation", "smoke exposure", "normal breathing"]
    },
    {
        "id": "ex_305",
        "text": "गलती से कीटनाशक की गैस सांस में चली गई और अब मुझे सांस लेने में दिक्कत हो रही है",
        "language": "hi",
        "categories": ["POISONING", "RESPIRATORY"],
        "severity": "CRITICAL",
        "symptoms": ["pesticide inhalation", "breathing difficulty"]
    },
    {
        "id": "ex_306",
        "text": "ರಾಸಾಯನಿಕ ಹೊಗೆಯನ್ನು ಉಸಿರಾಡಿದ ನಂತರ ನನಗೆ ಕೆಮ್ಮು ಮತ್ತು ಉಸಿರಾಟದ ತೊಂದರೆ ಶುರುವಾಗಿದೆ",
        "language": "kn",
        "categories": ["POISONING", "RESPIRATORY"],
        "severity": "CRITICAL",
        "symptoms": ["chemical inhalation", "coughing", "breathing difficulty"]
    },
    {
        "id": "ex_307",
        "text": "தவறுதலாக பூச்சிக்கொல்லியை குடித்துவிட்டேன், தொடர்ந்து வாந்தி வருகிறது",
        "language": "ta",
        "categories": ["POISONING"],
        "severity": "HIGH",
        "symptoms": ["pesticide ingestion", "vomiting"]
    },
    {
        "id": "ex_308",
        "text": "రసాయన వాయువును పీల్చిన తర్వాత దగ్గు వస్తోంది మరియు ఊపిరి తీసుకోవడం కష్టంగా ఉంది",
        "language": "te",
        "categories": ["POISONING", "RESPIRATORY"],
        "severity": "CRITICAL",
        "symptoms": ["chemical inhalation", "coughing", "breathing difficulty"]
    },


    # ============================================================
    # NEUROLOGICAL vs NON-EMERGENCY
    # ============================================================

    {
        "id": "ex_309",
        "text": "The left side of my face suddenly became weak and I cannot speak clearly",
        "language": "en",
        "categories": ["NEUROLOGICAL"],
        "severity": "CRITICAL",
        "symptoms": ["facial weakness", "speech difficulty"]
    },
    {
        "id": "ex_310",
        "text": "I suddenly became confused and cannot understand what people are saying",
        "language": "en",
        "categories": ["NEUROLOGICAL"],
        "severity": "HIGH",
        "symptoms": ["sudden confusion", "difficulty understanding speech"]
    },
    {
        "id": "ex_311",
        "text": "My vision suddenly became blurry in one eye and I feel weak on one side",
        "language": "en",
        "categories": ["NEUROLOGICAL"],
        "severity": "CRITICAL",
        "symptoms": ["sudden visual disturbance", "one-sided weakness"]
    },
    {
        "id": "ex_312",
        "text": "My eyes feel tired after working on the computer but my vision is otherwise normal",
        "language": "en",
        "categories": [],
        "severity": "LOW",
        "symptoms": ["eye tiredness", "computer use", "normal vision"]
    },
    {
        "id": "ex_313",
        "text": "I have a mild headache after studying for several hours and it is getting better",
        "language": "en",
        "categories": [],
        "severity": "LOW",
        "symptoms": ["mild headache", "improving"]
    },
    {
        "id": "ex_314",
        "text": "ನನಗೆ ಕಂಪ್ಯೂಟರ್ ಬಳಸಿದ ನಂತರ ಸ್ವಲ್ಪ ಕಣ್ಣಿನ ದಣಿವು ಇದೆ, ಬೇರೆ ಯಾವುದೇ ಸಮಸ್ಯೆ ಇಲ್ಲ",
        "language": "kn",
        "categories": [],
        "severity": "LOW",
        "symptoms": ["eye tiredness", "computer use"]
    },


    # ============================================================
    # TRAUMA / FRACTURE vs MINOR INJURY
    # ============================================================

    {
        "id": "ex_315",
        "text": "I fell from a bike and now I cannot put any weight on my injured leg",
        "language": "en",
        "categories": ["TRAUMA", "FRACTURE_MUSCULOSKELETAL"],
        "severity": "HIGH",
        "symptoms": ["bike fall", "leg injury", "unable to bear weight"]
    },
    {
        "id": "ex_316",
        "text": "I fell down the stairs and my arm looks deformed and extremely painful",
        "language": "en",
        "categories": ["TRAUMA", "FRACTURE_MUSCULOSKELETAL"],
        "severity": "HIGH",
        "symptoms": ["fall", "arm deformity", "severe pain"]
    },
    {
        "id": "ex_317",
        "text": "I bumped my knee lightly and there is only a small bruise with no pain",
        "language": "en",
        "categories": [],
        "severity": "LOW",
        "symptoms": ["minor bruise", "no pain"]
    },
    {
        "id": "ex_318",
        "text": "I got a tiny cut on my finger and it stopped bleeding quickly",
        "language": "en",
        "categories": [],
        "severity": "LOW",
        "symptoms": ["minor cut", "bleeding stopped"]
    },
    {
        "id": "ex_319",
        "text": "I slipped and hurt my ankle badly; it is swollen and I cannot walk",
        "language": "en",
        "categories": ["TRAUMA", "FRACTURE_MUSCULOSKELETAL"],
        "severity": "HIGH",
        "symptoms": ["fall", "ankle injury", "swelling", "unable to walk"]
    },
    {
        "id": "ex_320",
        "text": "I lightly bumped my shoulder against a door but I can move it normally",
        "language": "en",
        "categories": [],
        "severity": "LOW",
        "symptoms": ["minor impact", "normal movement"]
    },


    # ============================================================
    # MULTILINGUAL BOUNDARY CASES
    # ============================================================

    {
        "id": "ex_321",
        "text": "ನನಗೆ ಎದೆ ನೋವು ಮತ್ತು ಎಡಗೈಗೆ ನೋವು ಹರಡುತ್ತಿದೆ",
        "language": "kn",
        "categories": ["CARDIAC"],
        "severity": "CRITICAL",
        "symptoms": ["chest pain", "pain radiating to left arm"]
    },
    {
        "id": "ex_322",
        "text": "எனக்கு திடீரென்று முகத்தின் ஒரு பக்கம் பலவீனமாகி பேச்சு தெளிவாக வரவில்லை",
        "language": "ta",
        "categories": ["NEUROLOGICAL"],
        "severity": "CRITICAL",
        "symptoms": ["one-sided facial weakness", "speech difficulty"]
    },
    {
        "id": "ex_323",
        "text": "मुझे अचानक चक्कर आ रहा है और बोलने में परेशानी हो रही है",
        "language": "hi",
        "categories": ["NEUROLOGICAL"],
        "severity": "HIGH",
        "symptoms": ["sudden dizziness", "speech difficulty"]
    },
    {
        "id": "ex_324",
        "text": "ആഹാരം കഴിച്ചതിന് ശേഷം ചുണ്ടുകൾ വീങ്ങി, പക്ഷേ ശ്വാസം സാധാരണമാണ്",
        "language": "ml",
        "categories": ["ALLERGIC_REACTION"],
        "severity": "HIGH",
        "symptoms": ["lip swelling", "food exposure", "normal breathing"]
    },
    {
        "id": "ex_325",
        "text": "ರಾಸಾಯನಿಕ ಹೊಗೆ ಉಸಿರಾಡಿದ ನಂತರ ಕೆಮ್ಮು ಬರುತ್ತಿದೆ ಮತ್ತು ಉಸಿರಾಟ ಕಷ್ಟವಾಗಿದೆ",
        "language": "kn",
        "categories": ["POISONING", "RESPIRATORY"],
        "severity": "CRITICAL",
        "symptoms": ["chemical inhalation", "coughing", "breathing difficulty"]
    },
    {
        "id": "ex_326",
        "text": "నా కాలి మీద చిన్న గాయం ఉంది, రక్తస్రావం ఆగిపోయింది మరియు నొప్పి లేదు",
        "language": "te",
        "categories": [],
        "severity": "LOW",
        "symptoms": ["minor leg wound", "bleeding stopped", "no pain"]
    },
    {
        "id": "ex_327",
        "text": "என் கையில் சிறிய காயம் உள்ளது, இரத்தம் உடனே நின்றுவிட்டது",
        "language": "ta",
        "categories": [],
        "severity": "LOW",
        "symptoms": ["minor hand wound", "bleeding stopped"]
    },
    {
        "id": "ex_328",
        "text": "मुझे हल्का पेट दर्द था लेकिन अब ठीक हो रहा है और कोई और लक्षण नहीं हैं",
        "language": "hi",
        "categories": [],
        "severity": "LOW",
        "symptoms": ["mild abdominal pain", "improving", "no other symptoms"]
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