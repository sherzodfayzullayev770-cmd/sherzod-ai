import streamlit as st
import requests
import random
import ast
import operator
import re
import difflib
from datetime import datetime
from urllib.parse import quote

# =====================================================
# SHERZOD AI ASSISTANT 1.0
# Creator: Fayzullayev Sherzodbek
# =====================================================

st.set_page_config(
    page_title="SHERZOD AI ASSISTANT",
    page_icon="👑",
    layout="wide"
)

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg,#050505,#151515,#050505);
    color: #eeeeee;
}
section[data-testid="stSidebar"] {
    background: #101010;
    border-right: 1px solid #555;
}
h1,h2,h3 {
    color: #eeeeee !important;
}
p, label, span {
    color: #eeeeee;
}
.stButton button {
    background: linear-gradient(135deg,#222,#777,#333);
    color: white;
    border: 1px solid #999;
    border-radius: 12px;
    font-weight: bold;
}
.stButton button:hover {
    background: #888;
    color: black;
}
[data-testid="stChatMessage"] {
    background: rgba(255,255,255,0.035);
    border: 1px solid #454545;
    border-radius: 15px;
}
[data-testid="stChatInput"] {
    border: 1px solid #888;
    border-radius: 12px;
}
hr {
    border-color: #555;
}
</style>
""", unsafe_allow_html=True)

HEADERS = {"User-Agent": "SherzodAI/1.0"}

if "messages" not in st.session_state:
    st.session_state.messages = []

if "last_topic" not in st.session_state:
    st.session_state.last_topic = ""

if "last_quiz" not in st.session_state:
    st.session_state.last_quiz = None

if "game_number" not in st.session_state:
    st.session_state.game_number = None


def get_time():
    try:
        from zoneinfo import ZoneInfo
        now = datetime.now(ZoneInfo("Asia/Tashkent"))
    except Exception:
        now = datetime.utcnow()

    return now.strftime("%H:%M:%S"), now.strftime("%d.%m.%Y")


# =====================================================
# KNOWLEDGE DATABASE
# =====================================================

KNOWLEDGE = {
    "amir temur": """
Amir Temur 1336-yil 9-aprelda Kesh vohasida tug‘ilgan.
U buyuk davlat arbobi va sarkarda bo‘lgan.
1370-yilda Movarounnahrda hokimiyatni qo‘lga kiritgan.
Samarqandni o‘z davlatining poytaxtiga aylantirgan.
Temuriylar davrida ilm-fan, me'morchilik va savdo rivojlangan.
Amir Temur 1405-yilda O‘tror shahrida vafot etgan.
""",

    "napoleon bonapart": """
Napoleon Bonapart 1769-yil 15-avgustda Korsika orolida tug‘ilgan.
U Fransiya harbiy va siyosiy arbobi bo‘lgan.
1804-yilda Fransiya imperatori deb e'lon qilingan.
Napoleon Yevropa tarixiga katta ta'sir ko‘rsatgan.
1815-yilda Vaterloo jangidagi mag‘lubiyatidan keyin hokimiyatdan ketgan.
U 1821-yilda Muqaddas Yelena orolida vafot etgan.
""",

    "shayboniyxon": """
Muhammad Shayboniyxon 1451-yilda tug‘ilgan.
U Shayboniylar sulolasining asoschisi hisoblanadi.
1500-yildan boshlab Movarounnahrda hokimiyatni egallashga kirishgan.
Uning davrida Buxoro va Samarqand muhim markazlar bo‘lgan.
1510-yilda Marv yaqinidagi jangda halok bo‘lgan.
""",

    "zahiriddin muhammad bobur": """
Zahiriddin Muhammad Bobur 1483-yil 14-fevralda Andijonda tug‘ilgan.
U davlat arbobi, sarkarda va shoir bo‘lgan.
Bobur Hindistonda Boburiylar davlatiga asos solgan.
Uning mashhur asari Boburnoma hisoblanadi.
1530-yilda vafot etgan.
""",

    "alisher navoiy": """
Alisher Navoiy 1441-yil 9-fevralda Hirotda tug‘ilgan.
U buyuk shoir, mutafakkir va davlat arbobi bo‘lgan.
Uning mashhur asarlaridan biri Xamsadir.
""",

    "jaloliddin manguberdi": """
Jaloliddin Manguberdi Xorazmshohlar davlatining so‘nggi hukmdori bo‘lgan.
U mo‘g‘ullar bosqiniga qarshi kurashgan.
1231-yilda vafot etgan.
""",

    "al-xorazmiy": """
Muhammad al-Xorazmiy IX asrda yashagan buyuk matematik va olim.
U algebra fanining rivojlanishiga katta hissa qo‘shgan.
Algoritm atamasi uning nomi bilan bog‘liq.
""",

    "ikkinchi jahon urushi": """
Ikkinchi jahon urushi 1939-yil 1-sentabrda boshlangan.
Urush 1945-yil sentabrda yakunlangan.
1945-yil may oyida Germaniya taslim bo‘lgan.
1945-yil sentabrda Yaponiya taslim bo‘lgan.
""",

    "birinchi jahon urushi": """
Birinchi jahon urushi 1914–1918-yillarda bo‘lib o‘tgan.
1918-yil 11-noyabrda sulh bitimi imzolangan.
""",

    "o‘zbekiston mustaqilligi": """
O‘zbekiston 1991-yil 31-avgustda davlat mustaqilligini e'lon qilgan.
1-sentabr Mustaqillik kuni sifatida nishonlanadi.
1992-yil 2-martda O‘zbekiston BMTga a'zo bo‘lgan.
""",

    "qadimgi misr": """
Qadimgi Misr Nil daryosi bo‘yida rivojlangan sivilizatsiya edi.
U piramidalari, fir'avnlari va ieroglif yozuvi bilan mashhur.
""",

    "rim imperiyasi": """
Rim imperiyasi qadimgi dunyoning eng yirik davlatlaridan biri bo‘lgan.
G‘arbiy Rim imperiyasi 476-yilda qulagan.
""",

    "quyosh tizimi": """
Quyosh tizimi markazida Quyosh joylashgan.
Uning atrofida sakkizta sayyora aylanadi:
Merkuriy, Venera, Yer, Mars, Yupiter, Saturn, Uran va Neptun.
""",

    "python": """
Python — sodda va keng imkoniyatli dasturlash tili.
U veb-dasturlash, ma'lumotlar tahlili va sun'iy intellektda ishlatiladi.
print("Salom dunyo!")
""",

    "suniy intellekt": """
Sun'iy intellekt kompyuter tizimlarining ma'lumotlarni
tahlil qilish va vazifalarni bajarish imkoniyatlarini o‘rganuvchi soha.
""",

    "internet": """
Internet — butun dunyodagi kompyuter tarmoqlarini
birlashtiruvchi global tizim.
""",

    "fotosintez": """
Fotosintez — yashil o‘simliklarning yorug‘lik yordamida
suv va karbonat angidriddan organik moddalar hosil qilish jarayoni.
""",

    "gravitatsiya": """
Gravitatsiya — jismlarning bir-birini tortish hodisasi.
""",

    "futbol": """
Futbol ikki jamoa o‘rtasida o‘ynaladigan sport turi.
Har bir jamoada maydonda 11 nafar futbolchi bo‘ladi.
""",

    "geografiya": """
Geografiya Yer yuzasi, tabiat, aholi va hududlarni o‘rganadi.
"""
}
# =====================================================
# LANGUAGE DETECTION
# =====================================================

def detect_language(text):
    if re.search(r"[а-яёА-ЯЁ]", text):
        return "ru"

    english_words = [
        "what", "who", "where", "when", "why", "how",
        "hello", "history", "science", "world", "tell me"
    ]

    low = text.lower()

    if any(word in low for word in english_words):
        return "en"

    return "uz"


# =====================================================
# QUESTION CLEANER
# =====================================================

def clean_question(question):
    text = question.lower().strip()

    remove_words = [
        "kim", "nima", "qachon", "qayerda", "haqida",
        "malumot", "ma'lumot", "aytib ber", "tushuntir",
        "kim edi", "nima edi", "расскажи", "кто такой",
        "что такое", "when", "who is", "what is",
        "tell me about", "explain"
    ]

    for word in remove_words:
        text = text.replace(word, " ")

    text = re.sub(r"[?!.,:;]", " ", text)
    text = re.sub(r"\s+", " ", text)

    return text.strip()


# =====================================================
# WIKIPEDIA SEARCH
# =====================================================

def wikipedia_search(query, language=None):
    if not language:
        language = detect_language(query)

    languages = [language]

    for lang in ["uz", "ru", "en"]:
        if lang not in languages:
            languages.append(lang)

    clean = clean_question(query)

    if len(clean) < 2:
        clean = query.strip()

    for lang in languages:
        try:
            url = f"https://{lang}.wikipedia.org/w/api.php"

            params = {
                "action": "query",
                "list": "search",
                "srsearch": clean,
                "format": "json",
                "srlimit": 6
            }

            response = requests.get(
                url,
                params=params,
                headers=HEADERS,
                timeout=12
            )

            response.raise_for_status()

            results = response.json().get(
                "query", {}
            ).get("search", [])

            if not results:
                continue

            best = None
            best_score = 0

            query_words = set(clean.lower().split())

            for item in results:
                title = item["title"]
                title_low = title.lower()

                title_words = set(title_low.split())

                overlap = len(query_words & title_words)

                ratio = difflib.SequenceMatcher(
                    None,
                    clean.lower(),
                    title_low
                ).ratio()

                score = overlap * 2 + ratio

                if clean.lower() in title_low:
                    score += 3

                if score > best_score:
                    best_score = score
                    best = item

            if not best or best_score < 1.2:
                continue

            title = best["title"]

            summary_url = (
                f"https://{lang}.wikipedia.org/api/rest_v1/page/summary/"
                + quote(title.replace(" ", "_"))
            )

            summary = requests.get(
                summary_url,
                headers=HEADERS,
                timeout=12
            )

            if summary.status_code != 200:
                continue

            data = summary.json()
            extract = data.get("extract", "")

            if not extract:
                continue

            return (
                f"📚 **{title}**\n\n"
                f"{extract}\n\n"
                f"Manba: {lang}.wikipedia.org"
            )

        except Exception:
            continue

    return None


# =====================================================
# TRANSLATOR
# =====================================================

def translate_text(text, source, target):
    try:
        url = "https://api.mymemory.translated.net/get"

        response = requests.get(
            url,
            params={
                "q": text,
                "langpair": f"{source}|{target}"
            },
            timeout=15
        )

        response.raise_for_status()
        data = response.json()

        if data.get("responseStatus") == 200:
            return data["responseData"]["translatedText"]

    except Exception:
        pass

    return "Tarjima amalga oshmadi. Internetni tekshiring."
    # =====================================================
# WEATHER
# =====================================================

def weather(city):
    try:
        geo = requests.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={
                "name": city,
                "count": 1,
                "language": "en",
                "format": "json"
            },
            timeout=12
        ).json()

        if not geo.get("results"):
            return "Shahar topilmadi. Boshqa nom bilan urinib ko‘ring."

        place = geo["results"][0]

        data = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": place["latitude"],
                "longitude": place["longitude"],
                "current": (
                    "temperature_2m,relative_humidity_2m,"
                    "wind_speed_10m"
                ),
                "timezone": "Asia/Tashkent"
            },
            timeout=12
        ).json()

        current = data["current"]

        return (
            f"🌤 **{place['name']} ob-havosi**\n\n"
            f"🌡 Harorat: {current['temperature_2m']} °C\n\n"
            f"💧 Namlik: {current['relative_humidity_2m']}%\n\n"
            f"💨 Shamol: {current['wind_speed_10m']} km/soat"
        )

    except Exception:
        return "Ob-havo ma'lumotini olishda xatolik."


# =====================================================
# CURRENCY
# =====================================================

def currency():
    try:
        data = requests.get(
            "https://open.er-api.com/v6/latest/USD",
            timeout=12
        ).json()

        if data.get("result") != "success":
            return "Valyuta kursi olinmadi."

        rates = data["rates"]

        return (
            "💰 **Valyuta kurslari**\n\n"
            f"1 USD ≈ {rates.get('UZS')} UZS\n\n"
            f"1 USD ≈ {rates.get('EUR')} EUR\n\n"
            f"1 USD ≈ {rates.get('RUB')} RUB\n\n"
            "Kurslar o‘zgarib turadi."
        )

    except Exception:
        return "Valyuta ma'lumotini olishda xatolik."


# =====================================================
# SAFE CALCULATOR
# =====================================================

OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.UAdd: operator.pos,
    ast.USub: operator.neg
}


def safe_calculate(expression):
    try:
        tree = ast.parse(expression, mode="eval")

        def calc(node):
            if isinstance(node, ast.Expression):
                return calc(node.body)

            if isinstance(node, ast.Constant):
                if isinstance(node.value, (int, float)):
                    return node.value
                raise ValueError()

            if isinstance(node, ast.BinOp):
                op = type(node.op)

                if op not in OPERATORS:
                    raise ValueError()

                left = calc(node.left)
                right = calc(node.right)

                if isinstance(node.op, ast.Pow) and abs(right) > 10:
                    raise ValueError()

                result = OPERATORS[op](left, right)

                if abs(result) > 10**100:
                    raise ValueError()

                return result

            if isinstance(node, ast.UnaryOp):
                op = type(node.op)

                if op not in OPERATORS:
                    raise ValueError()

                return OPERATORS[op](calc(node.operand))

            raise ValueError()

        return calc(tree)

    except ZeroDivisionError:
        return "Nolga bo‘lish mumkin emas."
    except Exception:
        return "Hisoblash xatosi. Masalan: hisobla: 25*4"


# =====================================================
# DICTIONARY
# =====================================================

WORDS = {
    "hello": "Salom",
    "good morning": "Xayrli tong",
    "good night": "Xayrli tun",
    "thank you": "Rahmat",
    "please": "Iltimos",
    "friend": "Do‘st",
    "school": "Maktab",
    "book": "Kitob",
    "water": "Suv",
    "computer": "Kompyuter",
    "beautiful": "Chiroyli",
    "knowledge": "Bilim",
    "family": "Oila",
    "time": "Vaqt",
    "world": "Dunyo",
    "history": "Tarix",
    "science": "Fan",
    "дом": "Uy",
    "привет": "Salom",
    "спасибо": "Rahmat",
    "пожалуйста": "Iltimos",
    "друг": "Do‘st",
    "школа": "Maktab",
    "книга": "Kitob",
    "вода": "Suv",
    "красивый": "Chiroyli",
    "любовь": "Sevgi",
    "семья": "Oila",
    "время": "Vaqt",
    "мир": "Dunyo",
    "история": "Tarix",
    "наука": "Fan"
}
# =====================================================
# RANDOM CONTENT
# =====================================================

FACTS = [
    "Yorug‘lik Quyoshdan Yerga taxminan 8 daqiqada yetib keladi.",
    "Yupiter Quyosh tizimidagi eng katta sayyora.",
    "Ahtapotning uchta yuragi bor.",
    "Tinch okeani Yer yuzidagi eng katta okean.",
    "Asalarilar raqs orqali ma'lumot uzatadi.",
    "Saturn halqalari asosan muz va changdan iborat.",
    "Yer Quyosh atrofida taxminan 365,25 kunda aylanadi.",
    "Antarktida Yer yuzidagi eng sovuq materik."
]

JOKES = [
    "Kompyuter nega sovuq qotmaydi? Chunki uning Windows'i bor! 😄",
    "Dasturchi choy ichsa ham bug qidiradi. 😂",
    "Matematika kitobi nega xafa? Unda muammolar ko‘p!",
    "Kompyuter uxlayaptimi? Balki Sleep rejimidadir!"
]

MOTIVATION = [
    "Har bir katta natija kichik qadamdan boshlanadi.",
    "Bugungi mehnating ertangi muvaffaqiyatingdir.",
    "Xatolar — o‘rganishning bir qismi.",
    "Bilim olishdan hech qachon to‘xtama.",
    "Maqsading sari sabr bilan harakat qil!"
]

RIDDLES = [
    ("Qanoti yo‘q, uchadi. Og‘zi yo‘q, gapiradi.", "Shamol"),
    ("Qancha ko‘p olsang, shuncha kattalashadi.", "Chuqur"),
    ("Kechasi ko‘rinadi, kunduzi yo‘qoladi.", "Yulduz")
]

QUIZ = [
    {
        "q": "O‘zbekiston mustaqilligi qachon e'lon qilingan?",
        "a": ["1991-yil", "1995-yil", "1989-yil"],
        "correct": 0
    },
    {
        "q": "Quyosh tizimidagi eng katta sayyora qaysi?",
        "a": ["Mars", "Yupiter", "Merkuriy"],
        "correct": 1
    },
    {
        "q": "Python nima?",
        "a": ["Dasturlash tili", "Sayyora", "Sport turi"],
        "correct": 0
    },
    {
        "q": "Amir Temur qaysi yilda tug‘ilgan?",
        "a": ["1336", "1405", "1500"],
        "correct": 0
    }
]


# =====================================================
# HELP
# =====================================================

def help_text():
    return """
# 👑 SHERZOD AI — YORDAM

### 💬 Oddiy suhbat
Istalgan savolingizni yozing.

### 📚 Ma'lumot qidirish
- `wiki-uz: Amir Temur`
- `wiki-ru: история Узбекистана`
- `wiki-en: Solar System`

### 🌍 Tarjima
- `uz-en: Salom`
- `uz-ru: Salom`
- `en-uz: Hello`
- `ru-uz: Привет`

### 🌤 Ob-havo
- `ob havo Toshkent`
- `ob havo Mangit`

### 🧮 Kalkulyator
- `hisobla: 25*4`

### 💰 Valyuta
- `valyuta`

### 🎮 O‘yinlar
- `son top`
- `viktorina`
- `topishmoq`

### 🎲 Boshqa
- `fakt`
- `hazil`
- `motivatsiya`
- `parol yarat`
- `sana`
- `soat nechi`
"""


# =====================================================
# SMART ANSWER ENGINE
# =====================================================

def answer_user(message):
    original = message.strip()
    text = original.lower().strip()

    if not text:
        return "Savolingizni yozing."

    if text in ["salom", "assalomu alaykum", "hello", "привет"]:
        return random.choice([
            "Salom! Men SHERZOD AI. Sizga qanday yordam beray?",
            "Assalomu alaykum! Bugun nimalarni o‘rganamiz?",
            "Salom! Savolingizni kutaman."
        ])

    if text in ["yordam", "help", "komandalar"]:
        return help_text()

    if text.startswith("wiki-uz:"):
        result = wikipedia_search(original.split(":", 1)[1], "uz")
        return result or "O‘zbekcha Wikipedia ma'lumoti topilmadi."

    if text.startswith("wiki-ru:"):
        result = wikipedia_search(original.split(":", 1)[1], "ru")
        return result or "Ruscha Wikipedia ma'lumoti topilmadi."

    if text.startswith("wiki-en:"):
        result = wikipedia_search(original.split(":", 1)[1], "en")
        return result or "Inglizcha Wikipedia ma'lumoti topilmadi."

    if text.startswith("wiki:"):
        result = wikipedia_search(original.split(":", 1)[1])
        return result or "Ma'lumot topilmadi."

    translations = {
        "uz-en:": ("uz", "en"),
        "uz-ru:": ("uz", "ru"),
        "en-uz:": ("en", "uz"),
        "ru-uz:": ("ru", "uz")
    }

    for prefix, langs in translations.items():
        if text.startswith(prefix):
            sentence = original.split(":", 1)[1].strip()
            if not sentence:
                return "Tarjima qilinadigan matnni yozing."
            return translate_text(sentence, langs[0], langs[1])

    if text.startswith("ob havo "):
        return weather(original[8:].strip())

    if text == "valyuta":
        return currency()

    if text.startswith("hisobla:"):
        expression = original.split(":", 1)[1].strip()
        return f"Natija: **{safe_calculate(expression)}**"

    if text == "fakt":
        return random.choice(FACTS)

    if text == "hazil":
        return random.choice(JOKES)

    if text == "motivatsiya":
        return random.choice(MOTIVATION)

    if text == "topishmoq":
        riddle, answer = random.choice(RIDDLES)
        st.session_state.last_riddle = answer
        return riddle + "\n\nJavobini bilsangiz yozing: javobi"

    if text == "javobi":
        answer = st.session_state.get("last_riddle")
        return answer or "Avval topishmoq so‘rang."

    if text == "son top":
        number = random.randint(1, 20)
        st.session_state.game_number = number
        return "Men 1 dan 20 gacha son o‘yladim. Topib ko‘ring!"

    if st.session_state.game_number is not None and text.isdigit():
        guess = int(text)
        target = st.session_state.game_number

        if guess == target:
            st.session_state.game_number = None
            return "🎉 To‘g‘ri! Siz topdingiz!"
        if guess < target:
            return "Kattaroq son ayting."
        return "Kichikroq son ayting."

    if text == "viktorina":
        quiz = random.choice(QUIZ)
        st.session_state.last_quiz = quiz
        options = "\n".join(
            f"{i + 1}. {option}"
            for i, option in enumerate(quiz["a"])
        )
        return (
            f"🧠 **{quiz['q']}**\n\n"
            f"{options}\n\n"
            "Javobni 1, 2 yoki 3 shaklida yozing."
        )

    quiz = st.session_state.last_quiz

    if quiz and text in ["1", "2", "3"]:
        choice = int(text) - 1
        st.session_state.last_quiz = None

        if choice == quiz["correct"]:
            return "🎉 To‘g‘ri javob! Barakalla!"

        return (
            "Bu safar noto‘g‘ri.\n"
            f"To‘g‘ri javob: {quiz['a'][quiz['correct']]}"
        )

    if text == "parol yarat":
        password = "".join(
            random.choices(
                "abcdefghijkmnopqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789!@#",
                k=12
            )
        )
        return f"🔐 Tasodifiy parol: `{password}`"

    if text == "sana":
        return get_time()[1]

    if text == "soat nechi":
        return get_time()[0]

    for key, value in WORDS.items():
        if text == key:
            return f"📖 {key} — {value}"

    for key, value in KNOWLEDGE.items():
        if key in text:
            return value

    if any(word in text for word in ["rahmat", "спасибо", "thanks"]):
        return "Arzimaydi! Yana savolingiz bo‘lsa, yozing."

    if any(word in text for word in ["xayr", "пока", "goodbye"]):
        return "Xayr! Yana ko‘rishguncha!"

    if any(word in text for word in ["qalaysan", "qandaysan", "how are you"]):
        return "Yaxshi, rahmat! Sizga qanday yordam bera olaman?"

    if any(word in text for word in ["isming nima", "who are you"]):
        return "Men SHERZOD AI ASSISTANT 1.0 dasturiman."

    result = wikipedia_search(original)

    if result:
        st.session_state.last_topic = original
        return result

    return (
        "Bu savolga hozircha aniq javob topa olmadim. "
        "Savolni boshqacha yozib ko‘ring yoki `yordam` deb yozing."
    )


# =====================================================
# MAIN INTERFACE
# =====================================================

st.title("👑 SHERZOD AI ASSISTANT")
st.caption("Creator: Fayzullayev Sherzodbek")
st.markdown("---")

with st.sidebar:
    st.title("👑 SHERZOD AI")
    st.write("Sun'iy intellekt yordamchisi")
    st.markdown("---")

    if st.button("🗑 Suhbatni tozalash"):
        st.session_state.messages = []
        st.session_state.last_quiz = None
        st.session_state.game_number = None
        st.rerun()

    st.markdown("### Imkoniyatlar")
    st.write("📚 Wikipedia qidiruvi")
    st.write("🌍 Tarjima")
    st.write("🌤 Ob-havo")
    st.write("💰 Valyuta")
    st.write("🧮 Kalkulyator")
    st.write("🎮 O‘yinlar")
    st.write("🧠 Bilimlar bazasi")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

user_input = st.chat_input("SHERZOD AI ga savol yozing...")

if user_input:
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("SHERZOD AI o‘ylayapti..."):
            response = answer_user(user_input)
        st.markdown(response)

    st.session_state.messages.append({
        "role": "assistant",
        "content": response
    })

st.markdown("---")
st.caption("SHERZOD AI ASSISTANT 1.0 | Fayzullayev Sherzodbek")
