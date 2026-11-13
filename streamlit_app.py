
# ==========================================================
# SHERZOD AI ASSISTANT 1.0
# Creator: Fayzullayev Sherzodbek
# API-FREE EDITION
# ==========================================================

import streamlit as st
import requests
import random
import re
import ast
import operator
import difflib
import json
from datetime import datetime
from urllib.parse import quote

# ---------------- CONFIGURATION ----------------

st.set_page_config(
    page_title="SHERZOD AI ASSISTANT 1.0",
    page_icon="👑",
    layout="wide"
)

APP_NAME = "SHERZOD AI ASSISTANT 1.0"

# ---------------- DESIGN ----------------

st.markdown("""
<style>
.stApp {
    background-color: #080808;
    color: #eeeeee;
}
[data-testid="stSidebar"] {
    background-color: #111111;
    border-right: 1px solid #555;
}
h1,h2,h3 {
    color: #eeeeee !important;
}
p, label, span {
    color: #dddddd;
}
.stChatMessage {
    background: #151515;
    border: 1px solid #353535;
    border-radius: 15px;
}
.stChatInput textarea {
    color: white !important;
}
.stButton button {
    background: #202020;
    color: white;
    border: 1px solid #888;
    border-radius: 10px;
}
.stButton button:hover {
    border-color: white;
}
.sherzod-title {
    text-align: center;
    font-size: 34px;
    font-weight: 900;
    letter-spacing: 2px;
    color: #eeeeee;
}
.sherzod-subtitle {
    text-align: center;
    color: #999999;
    letter-spacing: 3px;
}
</style>
""", unsafe_allow_html=True)

# ---------------- SESSION ----------------

DEFAULTS = {
    "messages": [],
    "user_name": "",
    "last_topic": "",
    "last_answer": "",
    "last_quiz": None,
    "last_riddle": None,
    "language": "uz",
    "game_number": None
}

for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value

# ---------------- CONNECTION ----------------

HTTP = requests.Session()
HTTP.headers.update({
    "User-Agent": "SHERZOD-AI-ASSISTANT/1.0"
})

TIMEOUT = 12

# ---------------- TIME ----------------

def current_time():
    return datetime.now().strftime("%H:%M:%S")

def current_date():
    return datetime.now().strftime("%d-%m-%Y")

# ---------------- TEXT PROCESSING ----------------

def clean_text(text):
    text = str(text).lower().strip()
    text = re.sub(r"[^\w\s'’-]", " ", text)
    return re.sub(r"\s+", " ", text)

def similarity(a, b):
    return difflib.SequenceMatcher(
        None,
        clean_text(a),
        clean_text(b)
    ).ratio()

def contains_any(text, words):
    return any(word in text for word in words)

def save_topic(topic):
    st.session_state.last_topic = topic

def save_answer(answer):
    st.session_state.last_answer = answer

# ---------------- KNOWLEDGE DATABASE ----------------

KNOWLEDGE = {
    "amir temur": """
Amir Temur 1336-yil 9-aprelda tug‘ilgan.
U buyuk davlat arbobi va sarkarda bo‘lgan.
1370-yilda Movarounnahrda hokimiyatni
qo‘lga kiritgan. Samarqandni poytaxt qilgan.
Temuriylar davrida ilm-fan va me’morchilik
rivojlangan.
""",

    "mirzo ulugbek": """
Mirzo Ulug‘bek 1394-yilda tug‘ilgan.
U buyuk astronom va hukmdor bo‘lgan.
Samarqandda mashhur rasadxona qurdirgan.
Zij-i Sultoniy astronomiya tarixidagi
muhim asarlardan biridir.
""",

    "alisher navoiy": """
Alisher Navoiy 1441-yilda Hirotda tug‘ilgan.
U buyuk shoir va mutafakkir bo‘lgan.
Uning mashhur asarlaridan biri Xamsadir.
""",

    "shayboniyxon": """
Muhammad Shayboniyxon 1451-yilda tug‘ilgan.
U Shayboniylar davlatiga asos solgan.
1500-yildan boshlab Movarounnahrda
hokimiyatni egallash uchun kurashgan.
""",

    "bobur": """
Zahiriddin Muhammad Bobur 1483-yilda
Andijonda tug‘ilgan. U shoir, davlat arbobi
va sarkarda bo‘lgan. 1526-yilda Hindistonda
Boburiylar davlatiga asos solgan.
""",

    "jaloliddin manguberdi": """
Jaloliddin Manguberdi Xorazmshohlar
davlatining hukmdori bo‘lgan.
U mo‘g‘ullar bosqiniga qarshi kurashgan.
""",

    "birinchi jahon urushi": """
Birinchi jahon urushi 1914-yilda boshlangan
va 1918-yilda yakunlangan. Unda ko‘plab
davlatlar qatnashgan.
""",

    "ikkinchi jahon urushi": """
Ikkinchi jahon urushi 1939-yilda boshlangan
va 1945-yilda tugagan. Bu insoniyat
tarixidagi eng yirik urushlardan biri.
""",

    "ozbekiston mustaqilligi": """
O‘zbekiston 1991-yil 31-avgustda
mustaqilligini e’lon qilgan.
1-sentabr Mustaqillik kuni hisoblanadi.
""",

    "qadimgi misr": """
Qadimgi Misr Nil daryosi vodiysida
rivojlangan sivilizatsiya edi.
Misrliklar piramidalar va yozuv tizimi
bilan mashhur bo‘lgan.
""",

    "rim imperiyasi": """
Rim imperiyasi qadimgi dunyoning
eng yirik davlatlaridan biri bo‘lgan.
Uning huquq, me’morchilik va muhandislik
merosi hozirgacha o‘rganiladi.
""",

    "quyosh tizimi": """
Quyosh tizimida sakkizta sayyora bor:
Merkuriy, Venera, Yer, Mars, Yupiter,
Saturn, Uran va Neptun.
""",

    "python": """
Python — sodda va kuchli dasturlash tili.
U sun’iy intellekt, veb-dasturlash,
ma’lumotlar tahlili va avtomatlashtirishda
ishlatiladi.
""",

    "suniy intellekt": """
Sun’iy intellekt kompyuterlarning
ma’lumotlarni tahlil qilish, naqshlarni
aniqlash va turli vazifalarni bajarish
imkoniyatlarini o‘rganuvchi sohadir.
""",

    "internet": """
Internet — dunyo bo‘ylab qurilmalarni
bog‘laydigan global tarmoq.
U orqali ma’lumot almashish va
aloqa qilish mumkin.
""",

    "fotosintez": """
Fotosintez — o‘simliklarning yorug‘lik
yordamida suv va karbonat angidriddan
organik moddalar hosil qilish jarayoni.
""",

    "gravitatsiya": """
Gravitatsiya — jismlarning bir-birini
tortish hodisasi. Yer gravitatsiyasi
jismlarni Yer markaziga tortadi.
"""
}

# ---------------- RESPONSES ----------------

GREETINGS = [
    "Salom! Qanday yordam bera olaman?",
    "Assalomu alaykum! Savolingizni kutaman.",
    "Salom! Bugun nimalarni o‘rganamiz?",
    "Salom! Men SHERZOD AI ASSISTANT 1.0."
]

UNKNOWN = [
    "Bu mavzu haqida aniqroq ma’lumot kerak. Wikipedia orqali qidirib ko‘rishimiz mumkin.",
    "Qiziqarli savol! Savolingni biroz batafsilroq yoz.",
    "Hozir bu savolga ishonchli javobim yo‘q. Mavzuni aniqlashtirib bera olasanmi?"
]

FACTS = [
    "Quyosh yorug‘ligi Yerga taxminan 8 daqiqada yetib keladi.",
    "Asalarilar gullar orasida changlanishga yordam beradi.",
    "Yupiter Quyosh tizimidagi eng katta sayyoradir.",
    "Suv normal atmosfera bosimida 100°C da qaynaydi.",
    "Odam skeleti kattalarda odatda 206 ta suyakdan iborat."
]

JOKES = [
    "Kompyuter nega sovqotmaydi? Chunki uning Windows oynalari bor!",
    "Dasturchi choy ichibdi. Keyin yana bir piyola: bugni tuzatish kerak ekan!",
    "Nega kompyuter maktabga boradi? Bilimini yangilash uchun!"
]

# ---------------- CALCULATOR ----------------

OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos
}

def calculate_node(node):
    if isinstance(node, ast.Constant):
        if type(node.value) in (int, float):
            return node.value
        raise ValueError("Faqat sonlar ishlatiladi")

    if isinstance(node, ast.BinOp):
        op = OPERATORS.get(type(node.op))
        if op is None:
            raise ValueError("Noto‘g‘ri amal")
        return op(
            calculate_node(node.left),
            calculate_node(node.right)
        )

    if isinstance(node, ast.UnaryOp):
        op = OPERATORS.get(type(node.op))
        if op is None:
            raise ValueError("Noto‘g‘ri amal")
        return op(calculate_node(node.operand))

    raise ValueError("Hisoblash ifodasi noto‘g‘ri")

def calculate(expression):
    expression = expression.replace("^", "**")
    if len(expression) > 100:
        raise ValueError("Ifoda juda uzun")
    tree = ast.parse(expression, mode="eval")
    return calculate_node(tree.body)

# ==========================================================
# 2-QISM: LANGUAGE, TRANSLATION AND WIKIPEDIA
# ==========================================================

# ---------------- LANGUAGE DETECTION ----------------

def detect_language(text):
    text = str(text).lower()

    russian_chars = sum(
        1 for c in text
        if "а" <= c <= "я" or c == "ё"
    )

    english_words = [
        "hello", "how", "what", "where",
        "why", "when", "who", "is", "are",
        "the", "you", "your", "good", "morning"
    ]

    words = clean_text(text).split()

    if russian_chars >= 2:
        return "ru"

    if any(word in english_words for word in words):
        return "en"

    return "uz"


# ---------------- LANGUAGE NAMES ----------------

LANGUAGE_NAMES = {
    "uz": "O‘zbek tili",
    "ru": "Rus tili",
    "en": "Ingliz tili"
}


# ---------------- TRANSLATION ----------------

def translate_text(text, source, target):
    """
    MyMemory tarjima xizmati.
    Internet talab qilinadi.
    """

    if not text.strip():
        return "Tarjima uchun matn yozing."

    if source == target:
        return text

    try:
        url = "https://api.mymemory.translated.net/get"

        response = HTTP.get(
            url,
            params={
                "q": text[:450],
                "langpair": f"{source}|{target}"
            },
            timeout=TIMEOUT
        )

        response.raise_for_status()
        data = response.json()

        result = data.get(
            "responseData", {}
        ).get("translatedText", "")

        if result:
            return result

        return "Tarjima topilmadi."

    except requests.RequestException:
        return "Tarjima xizmati vaqtincha ishlamayapti."

    except (ValueError, KeyError, TypeError):
        return "Tarjima javobini o‘qishda xatolik."


# ---------------- TRANSLATION COMMANDS ----------------

TRANSLATION_COMMANDS = {
    "uz-en": ("uz", "en"),
    "uz-ru": ("uz", "ru"),
    "en-uz": ("en", "uz"),
    "ru-uz": ("ru", "uz"),
    "en-ru": ("en", "ru"),
    "ru-en": ("ru", "en")
}


def handle_translation(text):
    for prefix, languages in TRANSLATION_COMMANDS.items():

        if text.lower().startswith(prefix + ":"):
            content = text[len(prefix) + 1:].strip()

            if not content:
                return "Tarjima qilinadigan matnni ham yozing."

            source, target = languages

            result = translate_text(
                content,
                source,
                target
            )

            return (
                f"**Tarjima:**\n\n"
                f"{result}\n\n"
                f"**Yo‘nalish:** "
                f"{LANGUAGE_NAMES[source]} → "
                f"{LANGUAGE_NAMES[target]}"
            )

    return None


# ---------------- WIKIPEDIA SEARCH ----------------

def wikipedia_search(query, language="uz"):
    """
    Wikipedia API orqali maqola izlaydi.
    """

    query = query.strip()

    if not query:
        return "Qidirish uchun mavzu yozing."

    if language not in ("uz", "ru", "en"):
        language = "uz"

    url = (
        f"https://{language}.wikipedia.org/"
        "w/api.php"
    )

    try:
        response = HTTP.get(
            url,
            params={
                "action": "query",
                "list": "search",
                "srsearch": query,
                "format": "json",
                "utf8": 1,
                "srlimit": 3
            },
            timeout=TIMEOUT
        )

        response.raise_for_status()
        data = response.json()

        results = data.get(
            "query", {}
        ).get("search", [])

        if not results:
            return "Wikipedia'dan natija topilmadi."

        output = []

        for item in results:
            title = item.get("title", "")
            page_id = item.get("pageid")

            if not page_id:
                continue

            summary_response = HTTP.get(
                f"https://{language}.wikipedia.org/"
                "w/api.php",
                params={
                    "action": "query",
                    "prop": "extracts",
                    "exintro": 1,
                    "explaintext": 1,
                    "pageids": page_id,
                    "format": "json"
                },
                timeout=TIMEOUT
            )

            summary_response.raise_for_status()

            summary_data = summary_response.json()

            page = summary_data.get(
                "query", {}
            ).get("pages", {}).get(str(page_id), {})

            extract = page.get("extract", "")

            extract = extract[:1800]

            if extract:
                output.append(
                    f"### {title}\n\n{extract}"
                )

        if output:
            return "\n\n---\n\n".join(output)

        return "Maqola topildi, lekin matn olinmadi."

    except requests.Timeout:
        return "Wikipedia javob berishi uchun ko‘proq vaqt kerak."

    except requests.RequestException:
        return "Wikipedia bilan bog‘lanib bo‘lmadi."

    except (ValueError, KeyError, TypeError):
        return "Wikipedia ma’lumotlarini o‘qishda xatolik."


# ---------------- WIKIPEDIA COMMANDS ----------------

def handle_wikipedia(text):

    commands = {
        "wiki-uz:": "uz",
        "wiki-ru:": "ru",
        "wiki-en:": "en",
        "wiki:": "uz"
    }

    for prefix, language in commands.items():

        if text.lower().startswith(prefix):

            query = text[len(prefix):].strip()

            if not query:
                return "Wikipedia uchun mavzu yozing."

            result = wikipedia_search(
                query,
                language
            )

            return (
                f"**Wikipedia qidiruvi**\n\n"
                f"{result}"
            )

    return None


# ---------------- ENGLISH DICTIONARY ----------------

ENGLISH_DICTIONARY = {
    "hello": "Salom",
    "goodbye": "Xayr",
    "thanks": "Rahmat",
    "thank you": "Rahmat",
    "please": "Iltimos",
    "yes": "Ha",
    "no": "Yo‘q",
    "friend": "Do‘st",
    "family": "Oila",
    "school": "Maktab",
    "teacher": "O‘qituvchi",
    "student": "O‘quvchi",
    "book": "Kitob",
    "computer": "Kompyuter",
    "phone": "Telefon",
    "water": "Suv",
    "food": "Ovqat",
    "beautiful": "Chiroyli",
    "strong": "Kuchli",
    "intelligent": "Aqlli",
    "knowledge": "Bilim",
    "history": "Tarix",
    "science": "Fan",
    "technology": "Texnologiya",
    "programming": "Dasturlash",
    "language": "Til",
    "world": "Dunyo",
    "country": "Mamlakat",
    "city": "Shahar",
    "time": "Vaqt",
    "today": "Bugun",
    "tomorrow": "Ertaga",
    "yesterday": "Kecha",
    "love": "Sevgi",
    "happy": "Baxtli",
    "good": "Yaxshi",
    "bad": "Yomon",
    "morning": "Ertalab",
    "night": "Tun",
    "work": "Ish",
    "game": "O‘yin",
    "music": "Musiqa",
    "computer science": "Kompyuter fanlari",
    "artificial intelligence": "Sun’iy intellekt",
    "future": "Kelajak",
    "dream": "Orzu"
}


# ---------------- RUSSIAN DICTIONARY ----------------

RUSSIAN_DICTIONARY = {
    "привет": "Salom",
    "здравствуйте": "Assalomu alaykum",
    "пока": "Xayr",
    "спасибо": "Rahmat",
    "пожалуйста": "Iltimos",
    "да": "Ha",
    "нет": "Yo‘q",
    "друг": "Do‘st",
    "семья": "Oila",
    "школа": "Maktab",
    "учитель": "O‘qituvchi",
    "ученик": "O‘quvchi",
    "книга": "Kitob",
    "компьютер": "Kompyuter",
    "телефон": "Telefon",
    "вода": "Suv",
    "еда": "Ovqat",
    "красивый": "Chiroyli",
    "сильный": "Kuchli",
    "умный": "Aqlli",
    "знание": "Bilim",
    "история": "Tarix",
    "наука": "Fan",
    "технология": "Texnologiya",
    "программирование": "Dasturlash",
    "язык": "Til",
    "мир": "Dunyo",
    "страна": "Mamlakat",
    "город": "Shahar",
    "время": "Vaqt",
    "сегодня": "Bugun",
    "завтра": "Ertaga",
    "вчера": "Kecha",
    "любовь": "Sevgi",
    "счастливый": "Baxtli",
    "хороший": "Yaxshi",
    "плохой": "Yomon",
    "утро": "Ertalab",
    "ночь": "Tun",
    "работа": "Ish",
    "игра": "O‘yin",
    "музыка": "Musiqa",
    "будущее": "Kelajak",
    "мечта": "Orzu"
}


# ---------------- DICTIONARY LOOKUP ----------------

def dictionary_lookup(word):

    word = clean_text(word)

    if word in ENGLISH_DICTIONARY:
        return (
            f"🇬🇧 Inglizcha: {word}\n"
            f"🇺🇿 O‘zbekcha: "
            f"{ENGLISH_DICTIONARY[word]}"
        )

    if word in RUSSIAN_DICTIONARY:
        return (
            f"🇷🇺 Ruscha: {word}\n"
            f"🇺🇿 O‘zbekcha: "
            f"{RUSSIAN_DICTIONARY[word]}"
        )

    all_words = (
        list(ENGLISH_DICTIONARY.keys())
        + list(RUSSIAN_DICTIONARY.keys())
    )

    matches = difflib.get_close_matches(
        word,
        all_words,
        n=3,
        cutoff=0.75
    )

    if matches:
        return (
            "Balki quyidagi so‘zlardan birini "
            "nazarda tutgandirsan:\n"
            + "\n".join(matches)
        )

    return None


# ---------------- DICTIONARY COMMAND ----------------

def handle_dictionary(text):

    prefixes = [
        "lugat:",
        "lug'at:",
        "soz:",
        "so'z:",
        "word:"
    ]

    for prefix in prefixes:

        if text.lower().startswith(prefix):

            word = text[len(prefix):].strip()

            if not word:
                return "So‘z yozing. Masalan: word: hello"

            result = dictionary_lookup(word)

            if result:
                return result

            return (
                "Bu so‘z mening kichik lug‘atimda yo‘q. "
                "Tarjima uchun uz-en: yoki en-uz: "
                "buyrug‘idan foydalan."
            )

    return None


# ---------------- END OF PART 2 ----------------

# ==========================================================
# 3-QISM: WEATHER, CURRENCY, CALCULATOR AND KNOWLEDGE
# ==========================================================

# ---------------- CITY COORDINATES ----------------

def get_city_coordinates(city):

    url = "https://geocoding-api.open-meteo.com/v1/search"

    try:
        response = HTTP.get(
            url,
            params={
                "name": city,
                "count": 1,
                "language": "en",
                "format": "json"
            },
            timeout=TIMEOUT
        )

        response.raise_for_status()
        data = response.json()

        results = data.get("results", [])

        if not results:
            return None

        place = results[0]

        return {
            "name": place.get("name", city),
            "country": place.get("country", ""),
            "latitude": place["latitude"],
            "longitude": place["longitude"]
        }

    except (requests.RequestException, ValueError, KeyError):
        return None


# ---------------- WEATHER ----------------

WEATHER_CODES = {
    0: "Ochiq osmon",
    1: "Asosan ochiq",
    2: "Qisman bulutli",
    3: "Bulutli",
    45: "Tuman",
    48: "Qalin tuman",
    51: "Yengil mayda yomg‘ir",
    53: "Mayda yomg‘ir",
    55: "Kuchli mayda yomg‘ir",
    61: "Yengil yomg‘ir",
    63: "Yomg‘ir",
    65: "Kuchli yomg‘ir",
    71: "Yengil qor",
    73: "Qor",
    75: "Kuchli qor",
    80: "Yomg‘irli",
    81: "Jala",
    82: "Kuchli jala",
    95: "Momaqaldiroq",
    96: "Do‘l ehtimoli bilan momaqaldiroq",
    99: "Kuchli momaqaldiroq"
}


def get_weather(city):

    place = get_city_coordinates(city)

    if not place:
        return "Shahar topilmadi. Nomini tekshirib yozing."

    url = "https://api.open-meteo.com/v1/forecast"

    try:
        response = HTTP.get(
            url,
            params={
                "latitude": place["latitude"],
                "longitude": place["longitude"],
                "current": (
                    "temperature_2m,"
                    "relative_humidity_2m,"
                    "apparent_temperature,"
                    "is_day,"
                    "precipitation,"
                    "weather_code,"
                    "wind_speed_10m"
                ),
                "timezone": "auto"
            },
            timeout=TIMEOUT
        )

        response.raise_for_status()

        data = response.json()
        current = data.get("current", {})

        code = current.get("weather_code", -1)
        description = WEATHER_CODES.get(
            code,
            "Ob-havo holati aniqlanmadi"
        )

        temperature = current.get("temperature_2m", "Noma’lum")
        feels = current.get("apparent_temperature", "Noma’lum")
        humidity = current.get("relative_humidity_2m", "Noma’lum")
        wind = current.get("wind_speed_10m", "Noma’lum")

        return f"""
### 🌦️ {place['name']}, {place['country']}

- **Holat:** {description}
- **Harorat:** {temperature} °C
- **His qilinadigan harorat:** {feels} °C
- **Namlik:** {humidity} %
- **Shamol:** {wind} km/soat

<small>Ma’lumot: Open-Meteo. Joriy ob-havo ko‘rsatkichlari.</small>
"""

    except requests.Timeout:
        return "Ob-havo xizmati javob bermadi. Keyinroq urinib ko‘ring."

    except requests.RequestException:
        return "Ob-havo ma’lumotlarini olishda xatolik."


def handle_weather(text):

    prefixes = [
        "ob havo ",
        "ob-havo ",
        "ob havo:",
        "weather:",
        "weather "
    ]

    lowered = text.lower()

    for prefix in prefixes:

        if lowered.startswith(prefix):

            city = text[len(prefix):].strip()

            if not city:
                return "Shahar nomini yozing. Masalan: ob havo Toshkent"

            return get_weather(city)

    return None


# ---------------- CURRENCY ----------------

def get_currency():

    try:
        response = HTTP.get(
            "https://open.er-api.com/v6/latest/USD",
            timeout=TIMEOUT
        )

        response.raise_for_status()

        data = response.json()

        if data.get("result") != "success":
            return "Valyuta xizmatidan ma’lumot olinmadi."

        rates = data.get("rates", {})

        uzs = rates.get("UZS")
        eur = rates.get("EUR")
        rub = rates.get("RUB")

        if not uzs:
            return "UZS kursi mavjud emas."

        return f"""
### 💱 Valyuta kurslari

1 USD:
- 🇺🇿 UZS: {uzs:,.2f}
- 🇪🇺 EUR: {eur if eur else 'Noma’lum'}
- 🇷🇺 RUB: {rub if rub else 'Noma’lum'}

**Eslatma:** Bu ma’lumot axborot uchun.
Bankdagi haqiqiy ayirboshlash kursi farq qilishi mumkin.
"""

    except requests.RequestException:
        return "Valyuta xizmati vaqtincha ishlamayapti."

    except (ValueError, TypeError, KeyError):
        return "Valyuta ma’lumotlarini o‘qishda xatolik."


def handle_currency(text):

    commands = [
        "valyuta",
        "kurs",
        "dollar kursi",
        "dollar necha",
        "currency"
    ]

    if clean_text(text) in commands:
        return get_currency()

    return None


# ---------------- ADVANCED CALCULATOR ----------------

def handle_calculator(text):

    prefixes = [
        "hisobla:",
        "hisobla ",
        "calculate:",
        "calc:",
        "matematika:"
    ]

    lowered = text.lower()

    for prefix in prefixes:

        if lowered.startswith(prefix):

            expression = text[len(prefix):].strip()

            if not expression:
                return "Misol yozing. Masalan: hisobla: 250*45"

            try:
                result = calculate(expression)

                if isinstance(result, float):
                    result = round(result, 10)

                return (
                    f"🧮 **Hisoblash natijasi:**\n\n"
                    f"`{expression}` = **{result}**"
                )

            except ZeroDivisionError:
                return "Nolga bo‘lish mumkin emas."

            except Exception:
                return (
                    "Matematik ifodada xatolik bor.\n"
                    "Masalan: hisobla: (25+15)*4"
                )

    return None


# ---------------- EXTRA KNOWLEDGE ----------------

EXTRA_KNOWLEDGE = {

    "yer": """
Yer — Quyosh tizimidagi uchinchi sayyora.
U hayot mavjudligi ma’lum bo‘lgan yagona sayyora.
Yerning tabiiy yo‘ldoshi Oy hisoblanadi.
""",

    "mars": """
Mars Quyoshdan to‘rtinchi sayyora.
U qizg‘ish ko‘rinishi sababli Qizil sayyora
deb ham ataladi.
""",

    "yupiter": """
Yupiter Quyosh tizimidagi eng katta sayyora.
U asosan vodorod va geliydan tashkil topgan.
""",

    "saturn": """
Saturn o‘zining katta halqalari bilan mashhur.
U Quyosh tizimidagi oltinchi sayyora.
""",

    "oy": """
Oy — Yerning tabiiy yo‘ldoshi.
Uning yuzasida kraterlar va tog‘lar mavjud.
""",

    "quyosh": """
Quyosh — Quyosh tizimining markazidagi yulduz.
U Yer uchun asosiy yorug‘lik va issiqlik manbai.
""",

    "kislorod": """
Kislorod kimyoviy element bo‘lib,
uning belgisi O, atom raqami 8.
U ko‘plab tirik organizmlarning
nafas olish jarayonida muhim rol o‘ynaydi.
""",

    "suv": """
Suvning kimyoviy formulasi H2O.
Oddiy atmosfera bosimida u 0°C da muzlaydi
va 100°C da qaynaydi.
""",

    "elektr toki": """
Elektr toki — elektr zaryadlarining
tartibli harakati. U elektr zanjirlarida
energiya uzatish uchun ishlatiladi.
""",

    "kompyuter": """
Kompyuter ma’lumotlarni qayta ishlaydigan
elektron qurilma. U dasturlar yordamida
hisoblash, saqlash va turli vazifalarni bajaradi.
""",

    "algoritm": """
Algoritm — muammoni yechish uchun
ketma-ket bajariladigan aniq ko‘rsatmalar.
Dasturlashda algoritmlar juda muhim.
""",

    "html": """
HTML — veb-sahifalarning tuzilishini
yaratish uchun ishlatiladigan belgilash tili.
U CSS va JavaScript bilan birga ishlatiladi.
""",

    "css": """
CSS veb-sahifaning tashqi ko‘rinishini
boshqaradi. Rang, shrift, joylashuv va
animatsiyalarni sozlashda ishlatiladi.
""",

    "javascript": """
JavaScript veb-sahifalarga interaktivlik
qo‘shadigan dasturlash tilidir.
U brauzerda va serverda ishlashi mumkin.
""",

    "streamlit": """
Streamlit — Python yordamida ma’lumot
ilovalari va interaktiv veb-ilovalar
yaratishga imkon beradigan kutubxona.
""",

    "robototexnika": """
Robototexnika robotlarni loyihalash,
yaratish va boshqarishni o‘rganuvchi soha.
U mexanika, elektronika va dasturlashni
birlashtiradi.
""",

    "geografiya": """
Geografiya Yer yuzasi, tabiat, aholi
va hududlarning xususiyatlarini o‘rganadi.
U tabiiy va ijtimoiy geografiyaga bo‘linadi.
""",

    "atmosfera": """
Atmosfera — Yer atrofini o‘rab turgan
gazlar qatlami. U tirik organizmlarni
himoya qilish va iqlimni shakllantirishda
muhim ahamiyatga ega.
"""
}


def find_extra_knowledge(text):

    question = clean_text(text)

    for key, value in EXTRA_KNOWLEDGE.items():

        if question == key or key in question:
            return value

    return None


# ---------------- RANDOM FACTS ----------------

def get_random_fact():
    return random.choice(FACTS)


def get_random_joke():
    return random.choice(JOKES)


# ---------------- END OF PART 3 ----------------

# ==========================================================
# 4-QISM: SMART CONVERSATION AND GAMES
# ==========================================================

# ---------------- CONVERSATION DATA ----------------

CONVERSATION_RULES = {
    "salom": [
        "Salom! Qalaysan? Nima haqida suhbatlashamiz?",
        "Assalomu alaykum! Qanday yordam bera olaman?",
        "Salom! Bugun qanday yangi bilimlarni o‘rganamiz?"
    ],

    "qalaysan": [
        "Rahmat! Men ishlashga tayyorman. O‘zing qalaysan?",
        "Hammasi joyida! Savollaringni kutaman.",
        "Yaxshi, rahmat! Bugun nimalar qilamiz?"
    ],

    "rahmat": [
        "Arzimaydi! Yana yordam kerak bo‘lsa, yoz.",
        "Marhamat! Yordam bera olganimdan xursandman.",
        "Doimo yordam berishga tayyorman!"
    ],

    "xayr": [
        "Xayr! Kuning yaxshi o‘tsin!",
        "Ko‘rishguncha! Yana suhbatlashamiz.",
        "Xayr! Omad tilayman!"
    ],

    "yaxshi": [
        "Ajoyib! Bugun qanday mavzuni o‘rganamiz?",
        "Zo‘r! Yana qanday yangiliklar bor?",
        "Yaxshi bo‘lsa, juda yaxshi!"
    ],

    "yomon": [
        "Afsus. Xohlasang, nima bo‘lganini aytib berishing mumkin.",
        "Tushunarli. Kayfiyatingni yaxshilash uchun biror qiziqarli mavzu topamizmi?"
    ]
}


# ---------------- NAME MEMORY ----------------

def remember_user_name(text):

    patterns = [
        r"mening ismim\s+(.+)",
        r"ismim\s+(.+)",
        r"meni\s+(.+)\s+deb chaqir",
        r"my name is\s+(.+)",
        r"меня зовут\s+(.+)"
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            flags=re.IGNORECASE
        )

        if match:

            name = match.group(1).strip()

            name = re.sub(
                r"[.!?,]+$",
                "",
                name
            )

            if 1 <= len(name) <= 30:
                st.session_state.user_name = name
                return (
                    f"Yaxshi, {name}! "
                    "Ismingni ushbu suhbat davomida eslab qolaman."
                )

    return None


# ---------------- CONTEXT MEMORY ----------------

def get_recent_context():

    messages = st.session_state.messages[-8:]

    if not messages:
        return "Hozircha suhbat tarixi yo‘q."

    lines = []

    for message in messages:

        role = message.get("role", "")
        content = str(message.get("content", ""))

        if role == "user":
            label = "Foydalanuvchi"
        else:
            label = "SHERZOD AI"

        lines.append(
            f"{label}: {content[:350]}"
        )

    return "\n".join(lines)


def handle_context_question(text):

    question = clean_text(text)

    context_questions = [
        "nima haqida gaplashdik",
        "oldingi savolim nima edi",
        "men nima degandim",
        "oxirgi savolim nima edi",
        "nimani soragandim",
        "nima soradim",
        "what did i ask",
        "что я спрашивал"
    ]

    if contains_any(question, context_questions):

        previous = [
            m["content"]
            for m in st.session_state.messages
            if m.get("role") == "user"
        ]

        if len(previous) <= 1:
            return "Hali yetarli suhbat tarixi yo‘q."

        return (
            "Suhbatimizdagi oldingi savollaring:\n\n"
            + "\n".join(
                f"- {item[:250]}"
                for item in previous[-5:-1]
            )
        )

    if contains_any(question, [
        "davom ettir",
        "davom et",
        "yana tushuntir",
        "batafsilroq",
        "more details",
        "продолжай"
    ]):

        topic = st.session_state.last_topic

        if topic:
            return (
                f"Oldingi mavzumiz: **{topic}**.\n\n"
                "Aniqroq davom ettirish uchun qaysi "
                "qismini batafsil tushuntirishimni yoz."
            )

    return None


# ---------------- PERSONAL RESPONSES ----------------

def personal_response(text):

    question = clean_text(text)

    if contains_any(question, [
        "isming nima",
        "sening isming",
        "who are you",
        "your name",
        "как тебя зовут"
    ]):
        return (
            "Men SHERZOD AI ASSISTANT 1.0. "
            "Fayzullayev Sherzodbek loyihasi."
        )

    if contains_any(question, [
        "meni taniysanmi",
        "men kimman",
        "who am i"
    ]):

        name = st.session_state.user_name

        if name:
            return f"Ushbu suhbatda isming {name} ekanini bilaman."

        return (
            "Hozircha ismingni aytmagansan. "
            "Ismingni yozsang, shu suhbat davomida eslab qolaman."
        )

    if contains_any(question, [
        "nimalarni bilasan",
        "nima qila olasan",
        "yordam bera olasanmi",
        "what can you do"
    ]):
        return """
Men quyidagi ishlarni bajara olaman:

- Savollarga bilimlar bazam asosida javob berish
- Wikipedia orqali ma’lumot qidirish
- O‘zbek, rus va ingliz tillariga tarjima qilish
- Matematik hisob-kitoblar
- Ob-havo ma’lumotlarini olish
- Valyuta kurslarini ko‘rsatish
- Dasturlash bo‘yicha asosiy tushunchalarni tushuntirish
- Topishmoq va viktorina o‘ynash

Men API ulanmagan qoidaviy yordamchiman.
Shuning uchun barcha savollarga mukammal javob bera olmayman.
"""

    if contains_any(question, [
        "rahmat",
        "katta rahmat",
        "thanks"
    ]):
        return random.choice(
            CONVERSATION_RULES["rahmat"]
        )

    if contains_any(question, [
        "qalaysan",
        "qandaysan",
        "how are you"
    ]):
        return random.choice(
            CONVERSATION_RULES["qalaysan"]
        )

    return None


# ---------------- FACTS ----------------

def fact_response():
    return (
        "🧠 **Qiziqarli fakt:**\n\n"
        + get_random_fact()
    )


# ---------------- JOKES ----------------

def joke_response():
    return (
        "😄 **Hazil:**\n\n"
        + get_random_joke()
    )


# ---------------- MOTIVATION ----------------

MOTIVATION = [
    "Har bir katta natija kichik qadamdan boshlanadi.",
    "Bilimga sarflangan vaqt hech qachon bekor ketmaydi.",
    "Xatolar o‘rganish jarayonining bir qismidir.",
    "Bugun o‘rgangan narsang ertaga foyda beradi.",
    "Maqsad sari muntazam harakat qilish muhim.",
    "Dasturlashda sabr va mashq katta ahamiyatga ega.",
    "Yangi narsalarni o‘rganishdan to‘xtama."
]


def motivation_response():
    return (
        "🌟 **Motivatsiya:**\n\n"
        + random.choice(MOTIVATION)
    )


# ---------------- RIDDLES ----------------

RIDDLES = [
    {
        "question": "Qanoti yo‘q, uchadi. Og‘zi yo‘q, gapiradi. Bu nima?",
        "answer": "shamol"
    },
    {
        "question": "O‘zi bitta, ko‘zi mingta. Bu nima?",
        "answer": "elak"
    },
    {
        "question": "Kechasi ko‘rinadi, kunduzi yashirinadi. Bu nima?",
        "answer": "yulduz"
    },
    {
        "question": "Yozda kiyinar, qishda yechinar. Bu nima?",
        "answer": "daraxt"
    },
    {
        "question": "Suvda tug‘iladi, suvdan qo‘rqadi. Bu nima?",
        "answer": "tuz"
    }
]


def start_riddle():

    riddle = random.choice(RIDDLES)

    st.session_state.last_riddle = riddle["answer"]

    return (
        "🧩 **Topishmoq:**\n\n"
        + riddle["question"]
        + "\n\nJavobini yoz!"
    )


def check_riddle(text):

    answer = st.session_state.last_riddle

    if not answer:
        return None

    guess = clean_text(text)

    if guess in ["javobini ayt", "javob", "topolmadim"]:
        st.session_state.last_riddle = None
        return f"Javob: **{answer}**"

    if similarity(guess, answer) >= 0.75:
        st.session_state.last_riddle = None
        return "🎉 To‘g‘ri! Barakalla!"

    return "Bu javob noto‘g‘ri. Yana urinib ko‘r!"


# ---------------- QUIZ ----------------

QUIZZES = [
    {
        "question": "O‘zbekiston mustaqilligi qachon e’lon qilingan?",
        "options": ["1991", "1992", "1990"],
        "answer": "1991"
    },
    {
        "question": "Quyosh tizimidagi eng katta sayyora qaysi?",
        "options": ["Mars", "Yupiter", "Venera"],
        "answer": "Yupiter"
    },
    {
        "question": "Python qaysi turdagi til?",
        "options": ["Dasturlash tili", "Musiqa tili", "Tabiiy til"],
        "answer": "Dasturlash tili"
    },
    {
        "question": "Amir Temur qaysi yilda tug‘ilgan?",
        "options": ["1336", "1405", "1451"],
        "answer": "1336"
    },
    {
        "question": "Yerning tabiiy yo‘ldoshi nima?",
        "options": ["Quyosh", "Oy", "Mars"],
        "answer": "Oy"
    }
]


def start_quiz():

    quiz = random.choice(QUIZZES)

    st.session_state.last_quiz = quiz["answer"]

    return (
        "🎓 **Viktorina:**\n\n"
        + quiz["question"]
        + "\n\n"
        + "\n".join(
            f"{i + 1}. {option}"
            for i, option in enumerate(quiz["options"])
        )
        + "\n\nJavobni yoz!"
    )


def check_quiz(text):

    answer = st.session_state.last_quiz

    if not answer:
        return None

    guess = clean_text(text)

    if guess == clean_text(answer):
        st.session_state.last_quiz = None
        return "🎉 To‘g‘ri javob! Ajoyib!"

    if guess in ["javob", "javobini ayt"]:
        st.session_state.last_quiz = None
        return f"To‘g‘ri javob: **{answer}**"

    return "Noto‘g‘ri javob. Yana urinib ko‘r!"


# ---------------- NUMBER GUESSING GAME ----------------

def start_number_game():

    number = random.randint(1, 20)

    st.session_state.game_number = number

    return (
        "🎮 **Son topish o‘yini!**\n\n"
        "Men 1 dan 20 gacha son o‘yladim. "
        "Uni topishga harakat qil!"
    )


def handle_number_game(text):

    number = st.session_state.game_number

    if number is None:
        return None

    guess_text = clean_text(text)

    if guess_text in ["oyinni toxta", "oyin toxta", "stop"]:
        st.session_state.game_number = None
        return "O‘yin to‘xtatildi."

    try:
        guess = int(guess_text)
    except ValueError:
        return None

    if guess == number:
        st.session_state.game_number = None
        return "🎉 To‘g‘ri topding! Tabriklayman!"

    if guess < number:
        return "Men o‘ylagan son bundan kattaroq."

    return "Men o‘ylagan son bundan kichikroq."


# ---------------- COMMAND HANDLERS ----------------

def handle_games(text):

    question = clean_text(text)

    if question in ["fakt", "qiziqarli fakt"]:
        return fact_response()

    if question in ["hazil", "kuldir"]:
        return joke_response()

    if question in ["motivatsiya", "ruh ber"]:
        return motivation_response()

    if question in ["topishmoq", "topishmoq ber"]:
        return start_riddle()

    if question in ["viktorina", "test boshlash"]:
        return start_quiz()

    if question in ["son top", "son topish oyini"]:
        return start_number_game()

    return None


# ---------------- END OF PART 4 ----------------

# ==========================================================
# 5-QISM: MAIN AI ENGINE AND STREAMLIT CHAT
# ==========================================================

# ---------------- KNOWLEDGE SEARCH ----------------

def find_knowledge(text):

    question = clean_text(text)

    # Asosiy bilimlar bazasi
    for key, value in KNOWLEDGE.items():

        if key in question:
            save_topic(key)
            return value

    # Qo‘shimcha bilimlar bazasi
    result = find_extra_knowledge(text)

    if result:
        save_topic(text)
        return result

    return None


# ---------------- GREETING HANDLER ----------------

def greeting_response(text):

    question = clean_text(text)

    greetings = [
        "salom",
        "assalomu alaykum",
        "assalom",
        "hello",
        "hi",
        "привет",
        "здравствуйте"
    ]

    if question in greetings:
        return random.choice(GREETINGS)

    return None


# ---------------- GENERAL QUESTION HANDLER ----------------

def general_question(text):

    question = clean_text(text)

    if question in ["sana", "bugun sana"]:
        return f"Bugungi sana: {current_date()}"

    if question in ["soat", "soat nechi", "vaqt"]:
        return f"Hozirgi vaqt: {current_time()}"

    if question in ["yordam", "help", "buyruqlar"]:
        return """
### SHERZOD AI 1.0 — Yordam

**Tarjima:**
- `uz-en: Salom`
- `en-uz: Hello`
- `uz-ru: Salom`
- `ru-uz: Привет`

**Wikipedia:**
- `wiki-uz: Amir Temur`
- `wiki-en: Albert Einstein`
- `wiki-ru: История`

**Ob-havo:**
- `ob havo Toshkent`

**Valyuta:**
- `valyuta`

**Hisoblash:**
- `hisobla: 250*45`

**Lug‘at:**
- `word: computer`
- `lugat: привет`

**O‘yinlar:**
- `fakt`
- `hazil`
- `motivatsiya`
- `topishmoq`
- `viktorina`
- `son top`

**Suhbat:**
- `Salom`
- `Isming nima?`
- `Men kimman?`
- `Nimalarni bilasan?`
"""

    return None


# ---------------- SMART RESPONSE ENGINE ----------------

def answer_user(user_text):

    text = str(user_text).strip()

    if not text:
        return "Iltimos, savol yozing."

    question = clean_text(text)

    # 1. Faol topishmoq
    if st.session_state.last_riddle:

        if question in [
            "javobini ayt",
            "javob",
            "topolmadim"
        ]:
            return check_riddle(text)

        if question in ["bekor", "bekor qil", "stop"]:
            st.session_state.last_riddle = None
            return "Topishmoq bekor qilindi."

        if not question.startswith(("wiki", "uz-", "en-", "ru-")):
            return check_riddle(text)

        st.session_state.last_riddle = None

    # 2. Faol viktorina
    if st.session_state.last_quiz:

        if question in ["javob", "javobini ayt"]:
            return check_quiz(text)

        if question in ["bekor", "bekor qil", "stop"]:
            st.session_state.last_quiz = None
            return "Viktorina bekor qilindi."

        # Son topish o‘yini va viktorina aralashmasin
        if question not in ["topishmoq", "fakt", "hazil"]:
            result = check_quiz(text)

            if result:
                return result

    # 3. Faol son topish o‘yini
    if st.session_state.game_number is not None:

        if question.isdigit() or question in [
            "oyinni toxta",
            "oyin toxta",
            "stop"
        ]:
            return handle_number_game(text)

    # 4. Ismni eslab qolish
    result = remember_user_name(text)

    if result:
        return result

    # 5. Tarjima
    result = handle_translation(text)

    if result is not None:
        return result

    # 6. Wikipedia buyruqlari
    result = handle_wikipedia(text)

    if result is not None:
        return result

    # 7. Kalkulyator
    result = handle_calculator(text)

    if result is not None:
        return result

    # 8. Ob-havo
    result = handle_weather(text)

    if result is not None:
        return result

    # 9. Valyuta
    result = handle_currency(text)

    if result is not None:
        return result

    # 10. Lug‘at
    result = handle_dictionary(text)

    if result is not None:
        return result

    # 11. O‘yinlar
    result = handle_games(text)

    if result is not None:
        return result

    # 12. Suhbat tarixi
    result = handle_context_question(text)

    if result is not None:
        return result

    # 13. Shaxsiy savollar
    result = personal_response(text)

    if result is not None:
        return result

    # 14. Oddiy salomlashish
    result = greeting_response(text)

    if result is not None:
        return result

    # 15. Umumiy buyruqlar
    result = general_question(text)

    if result is not None:
        return result

    # 16. Bilimlar bazasidan izlash
    result = find_knowledge(text)

    if result is not None:
        return result

    # 17. O‘xshash bilim nomini izlash
    keys = list(KNOWLEDGE.keys()) + list(EXTRA_KNOWLEDGE.keys())

    words = question.split()

    for key in keys:

        score = similarity(question, key)

        if score >= 0.72 or (
            len(words) >= 2 and
            similarity(" ".join(words[-2:]), key) >= 0.78
        ):
            save_topic(key)
            return (
                "Balki shu mavzuni nazarda tutgandirsan:\n\n"
                f"**{key.title()}**\n\n"
                + KNOWLEDGE.get(
                    key,
                    EXTRA_KNOWLEDGE.get(key, "")
                )
            )

    # 18. Wikipedia avtomatik qidiruvi
    search_words = [
        "kim", "nima", "qachon", "qayerda",
        "kimdir", "tarixi", "haqida",
        "what", "who", "when", "where",
        "кто", "что", "когда", "где"
    ]

    if (
        len(words) >= 2 and
        contains_any(question, search_words)
    ):
        result = wikipedia_search(text, "uz")

        if "natija topilmadi" not in result.lower() and (
            "javob" not in result.lower()
        ):
            save_topic(text)
            return (
                "🔎 **Wikipedia qidiruvi natijasi:**\n\n"
                + result
            )

    # 19. Javob topilmasa
    return random.choice(UNKNOWN)


# ---------------- CHAT HISTORY ----------------

def render_chat():

    for message in st.session_state.messages:

        role = message.get("role", "assistant")
        content = message.get("content", "")

        with st.chat_message(role):

            st.markdown(content)


# ---------------- SIDEBAR ----------------

with st.sidebar:

    st.markdown("## 👑 SHERZOD AI")
    st.caption("ASSISTANT 1.0")

    st.divider()

    st.markdown("### 📌 Asosiy buyruqlar")

    st.markdown("""
    - Salom
    - Yordam
    - Wikipedia
    - Tarjima
    - Ob-havo
    - Valyuta
    - Hisoblash
    - Viktorina
    - Topishmoq
    """)

    st.divider()

    st.markdown("### 👤 Foydalanuvchi")

    if st.session_state.user_name:
        st.write(st.session_state.user_name)
    else:
        st.write("Ismingiz hali kiritilmagan.")

    st.divider()

    st.caption(
        f"Xabarlar soni: {len(st.session_state.messages)}"
    )

    if st.button("🗑️ Suhbatni tozalash", use_container_width=True):

        st.session_state.messages = []
        st.session_state.last_topic = ""
        st.session_state.last_answer = ""
        st.session_state.last_quiz = None
        st.session_state.last_riddle = None
        st.session_state.game_number = None

        st.rerun()


# ---------------- MAIN INTERFACE ----------------

st.markdown(
    '<div class="sherzod-title">👑 SHERZOD AI ASSISTANT</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="sherzod-subtitle">INTELLIGENT DIGITAL ASSISTANT 1.0</div>',
    unsafe_allow_html=True
)

st.divider()

if not st.session_state.messages:

    st.markdown(
        """
        ### Assalomu alaykum!

        Men SHERZOD AI ASSISTANT 1.0.

        Savolingizni yozing. Men yordam berishga tayyorman.
        """
    )

# Oldingi suhbatlarni ko‘rsatish
render_chat()

# ---------------- USER INPUT ----------------

user_text = st.chat_input(
    "SHERZOD AI ga xabar yozing..."
)

if user_text:

    add_message("user", user_text)

    with st.chat_message("user"):
        st.markdown(user_text)

    with st.chat_message("assistant"):

        with st.spinner("SHERZOD AI o‘ylayapti..."):

            try:
                response = answer_user(user_text)

                if not isinstance(response, str):
                    response = str(response)

            except Exception as error:

                response = (
                    "Kutilmagan xatolik yuz berdi. "
                    "Savolingizni boshqacha yozib ko‘ring."
                )

            st.markdown(response)

    add_message("assistant", response)

    save_answer(response)

# ---------------- FOOTER ----------------

st.divider()

st.markdown(
    """
    <div style="text-align:center;color:#777;font-size:12px;">
        SHERZOD AI ASSISTANT 1.0<br>
        Created by Fayzullayev Sherzodbek
    </div>
    """,
    unsafe_allow_html=True
)

# ==========================================================
# END OF SHERZOD AI ASSISTANT 1.0
# ==========================================================
