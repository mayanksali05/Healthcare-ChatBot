EMERGENCY_KEYWORDS = [

    "chest pain",
    "heart attack",
    "stroke",
    "difficulty breathing",
    "suicide",
    "overdose",
    "severe bleeding",
    "unconscious",
    "seizure",
    "poison",
    "emergency"
]


DIAGNOSIS_KEYWORDS = [

    "diagnose",
    "what disease",
    "what condition",
    "do i have",
    "what illness"
]


MEDICATION_KEYWORDS = [

    "dosage",
    "medicine amount",
    "how many tablets",
    "prescription"
]


def classify_query(query):

    query = query.lower()


    for keyword in EMERGENCY_KEYWORDS:

        if keyword in query:

            return "emergency"


    for keyword in DIAGNOSIS_KEYWORDS:

        if keyword in query:

            return "diagnosis"


    for keyword in MEDICATION_KEYWORDS:

        if keyword in query:

            return "medication"


    return "safe"