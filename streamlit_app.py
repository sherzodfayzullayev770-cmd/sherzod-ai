
import streamlit as st
import requests
import random
import ast
import operator
import re
from datetime import datetime
from urllib.parse import quote

# ==========================================
# SHERZOD AI ASSISTANT 1.0
# Creator: Fayzullayev Sherzodbek
# ==========================================

st.set_page_config(
    page_title="SHERZOD AI ASSISTANT",
    page_icon="👑",
    layout="wide"
)

# ==========================================
# DESIGN
# ==========================================

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg,#050505,#171717,#080808);
    color: #eeeeee;
}
section[data-testid="stSidebar"] {
    background: #101010;
    border-right: 1px solid #555;
}
h1, h2, h3 {
    color: #dedede !important;
}
p, label, span {
    color: #eeeeee;
}
.stButton button {
    background: linear-gradient(135deg,#333,#999,#333);
    color: white;
    border: 1px solid #aaa;
    border-radius: 12px;
    font-weight: bold;
}
.stButton button:hover {
    background: #777;
    color: white;
}
[data-testid="stChatMessage"] {
    background: rgba(255,255,255,0.04);
    border: 1px solid #444;
    border-radius: 14px;
}
input, textarea {
    background: #151515 !important;
    color: white !important;
}
hr {
    border-color: #555;
}
</style>
""", unsafe_allow_html=True)

# ==========================================
# SESSION
# ==========================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "username" not in st.session_state:
    st.session_state.username = "Foydalanuvchi"

# ==========================================
# CONSTANTS
# ==========================================

HEADERS = {
    "User-Agent": "SherzodAI/1.0"
}

FACTS = [
    "Asalarilar bir-biri bilan raqs orqali aloqa qiladi.",
    "Yorug‘lik Quyoshdan Yerga taxminan 8 daqiqada yetib keladi.",
    "Ahtapotning uchta yuragi bor.",
    "Yupiter Quyosh tizimidagi eng katta sayyora.",
    "Inson miyasi juda ko‘p ma'lumotni qayta ishlay oladi.",
    "Dunyodagi eng katta okean Tinch okeanidir.",
    "Pingvinlar ucha olmaydi, lekin juda yaxshi suzadi.",
    "Saturnning halqalari asosan muz va changdan iborat.",
    "O‘simliklar fotosintez orqali oziqa hosil qiladi.",
    "Yer Quyosh atrofida aylanadi."
]

JOKES = [
    "Kompyuter nega sovuq qotmaydi? Chunki uning Windows'i bor! 😄",
    "Dasturchi choy ichsa ham bug qidiradi. 😂",
    "Matematika kitobi nega xafa? Chunki unda muammolar juda ko‘p!",
    "Kompyuter uxlayaptimi? Balki Sleep rejimidadir!"
]

MOTIVATION = [
    "Har bir katta natija kichik qadamdan boshlanadi.",
    "Bugungi mehnating ertangi muvaffaqiyatingdir.",
    "Xatolar — o‘rganishning bir qismi.",
    "Maqsading sari sabr bilan harakat qil!",
    "O‘zingga ishon va bilim olishdan to‘xtama."
]

RIDDLES = [
    ("Qanoti yo‘q, uchadi. Og‘zi yo‘q, gapiradi. Bu nima?", "Shamol"),
    ("Qancha ko‘p olsang, shuncha kattalashadi. Bu nima?", "Chuqur"),
    ("Kechasi ko‘rinadi, kunduzi yo‘qoladi. Bu nima?", "Yulduz")
]

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
    "love": "Sevgi",
    "family": "Oila",
    "work": "Ish",
    "time": "Vaqt",
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
    "добрый вечер": "Xayrli kech"
}

# ==========================================
# TIME
# ==========================================

def get_time():
    try:
        from zoneinfo import ZoneInfo
        now = datetime.now(ZoneInfo("Asia/Tashkent"))
    except Exception:
        now = datetime.utcnow()

    return now.strftime("%H:%M:%S"), now.strftime("%d.%m.%Y")


# ==========================================
# WIKIPEDIA SEARCH
# ==========================================

def wikipedia_search(query, language="uz"):
    languages = [language]

    if language == "uz":
        languages += ["ru", "en"]
    elif language == "ru":
        languages += ["uz", "en"]
    else:
        languages += ["uz", "ru"]

    for lang in languages:
        try:
            url = f"https://{lang}.wikipedia.org/w/api.php"

            params = {
                "action": "query",
                "list": "search",
                "srsearch": query,
                "format": "json",
                "srlimit": 3
            }

            response = requests.get(
                url,
                params=params,
                headers=HEADERS,
                timeout=12
            )
            response.raise_for_status()

            results = response.json()["query"]["search"]

            if not results:
                continue

            page_title = results[0]["title"]

            summary_url = (
                f"https://{lang}.wikipedia.org/api/rest_v1/"
                f"page/summary/{quote(page_title.replace(' ', '_'))}"
            )

            summary = requests.get(
                summary_url,
                headers=HEADERS,
                timeout=12
            )

            if summary.status_code == 200:
                data = summary.json()
                extract = data.get("extract", "")

                if extract:
                    return (
                        f"📚 **{page_title}**\n\n"
                        f"{extract}\n\n"
                        f"Manba: {lang}.wikipedia.org"
                    )

        except Exception:
            continue

    return None


# ==========================================
# TRANSLATOR
# ==========================================

def translate_text(text, source, target):
    try:
        url = "https://api.mymemory.translated.net/get"

        params = {
            "q": text,
            "langpair": f"{source}|{target}"
        }

        response = requests.get(
            url,
            params=params,
            timeout=15
        )
        response.raise_for_status()

        result = response.json()
        translated = result["responseData"]["translatedText"]

        if result["responseStatus"] == 200:
            return translated

    except Exception:
        pass

    return "Tarjima amalga oshmadi. Internetni tekshiring."


# ==========================================
# WEATHER
# ==========================================

def weather(city):
    try:
        geo_url = "https://geocoding-api.open-meteo.com/v1/search"

        geo = requests.get(
            geo_url,
            params={
                "name": city,
                "count": 1,
                "language": "uz",
                "format": "json"
            },
            timeout=12
        ).json()

        if not geo.get("results"):
            return "Shahar topilmadi. Nomini tekshiring."

        place = geo["results"][0]
        lat = place["latitude"]
        lon = place["longitude"]

        weather_url = "https://api.open-meteo.com/v1/forecast"

        data = requests.get(
            weather_url,
            params={
                "latitude": lat,
                "longitude": lon,
                "current": "temperature_2m,relative_humidity_2m,wind_speed_10m",
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
        return "Ob-havo ma'lumotini olishda xatolik. Internetni tekshiring."


# ==========================================
# CURRENCY
# ==========================================

def currency():
    try:
        url = "https://open.er-api.com/v6/latest/USD"
        data = requests.get(url, timeout=12).json()

        if data.get("result") != "success":
            return "Valyuta ma'lumoti hozircha olinmadi."

        rates = data["rates"]

        usd = rates.get("UZS")
        eur = rates.get("EUR")
        rub = rates.get("RUB")

        return (
            "💰 **Valyuta kurslari**\n\n"
            f"1 USD ≈ {usd} UZS\n\n"
            f"1 USD ≈ {eur} EUR\n\n"
            f"1 USD ≈ {rub} RUB\n\n"
            "Kurslar o‘zgarib turadi."
        )

    except Exception:
        return "Valyuta ma'lumoti olinmadi."


# ==========================================
# SAFE CALCULATOR
# ==========================================

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

        def calculate(node):
            if isinstance(node, ast.Expression):
                return calculate(node.body)

            if isinstance(node, ast.Constant):
                if isinstance(node.value, (int, float)):
                    return node.value
                raise ValueError()

            if isinstance(node, ast.BinOp):
                op = type(node.op)

                if op not in OPERATORS:
                    raise ValueError()

                left = calculate(node.left)
                right = calculate(node.right)

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

                return OPERATORS[op](calculate(node.operand))

            raise ValueError()

        return calculate(tree)

    except ZeroDivisionError:
        return "Nolga bo‘lish mumkin emas."
    except Exception:
        return "Hisoblash xatosi. Masalan: hisobla: 25*4"


# ==========================================
# KNOWLEDGE
# ==========================================

KNOWLEDGE = {
    "amir temur": (
        "Amir Temur 1336-yilda Kesh yaqinida tug‘ilgan. "
        "U buyuk davlat arbobi va sarkarda bo‘lgan. "
        "1370-yilda Movarounnahrda hokimiyatni qo‘lga kiritgan. "
        "Samarqandni davlatining poytaxtiga aylantirgan."
    ),

    "shayboniyxon": (
        "Muhammad Shayboniyxon 1451-yilda tug‘ilgan. "
        "U Shayboniylar davlatiga asos solgan. "
        "1500-yilda Movarounnahrda hokimiyatni egallashni boshlagan. "
        "Uning faoliyati O‘zbekiston tarixida muhim o‘rin tutadi."
    ),

    "ikkinchi jahon urushi": (
        "Ikkinchi jahon urushi 1939-yil 1-sentabrda boshlangan "
        "va 1945-yilda tugagan. Urush ko‘plab davlatlarni qamrab olgan. "
        "1945-yil sentabrda Yaponiya taslim bo‘lishi bilan yakunlangan."
    ),

    "birinchi jahon urushi": (
        "Birinchi jahon urushi 1914–1918-yillarda bo‘lib o‘tgan. "
        "U Yevropa va boshqa hududlardagi ko‘plab davlatlarni qamrab olgan."
    ),

    "misr": (
        "Qadimgi Misr Nil daryosi bo‘yida rivojlangan. "
        "U piramidalari, fir'avnlari va yozuv tizimi bilan mashhur."
    ),

    "rim imperiyasi": (
        "Rim imperiyasi qadimgi dunyoning eng yirik davlatlaridan biri "
        "bo‘lgan. Uning huquq, me'morchilik va madaniyatga ta'siri katta."
    ),

    "mustaqillik": (
        "O‘zbekiston 1991-yil 31-avgustda davlat mustaqilligini e'lon qilgan. "
        "1-sentabr Mustaqillik kuni sifatida nishonlanadi."
    ),

    "quyosh": (
        "Quyosh Yerga eng yaqin yulduzdir. U yorug‘lik va issiqlik "
        "manbai bo‘lib, Quyosh tizimining markazida joylashgan."
    ),

    "yer": (
        "Yer Quyosh tizimidagi uchinchi sayyora. "
        "Unda hayot mavjudligi ma'lum bo‘lgan yagona sayyoradir."
    ),

    "python": (
        "Python — o‘rganish oson bo‘lgan dasturlash tili. "
        "U sun'iy intellekt, veb-saytlar, avtomatlashtirish va "
        "ma'lumotlar tahlilida ishlatiladi."
    ),

    "suniy intellekt": (
        "Sun'iy intellekt kompyuterlarning ma'lumotlarni tahlil qilish, "
        "naqshlarni aniqlash va ayrim vazifalarni bajarish imkoniyatidir."
    )
}


# ==========================================
# QUIZ
# ==========================================

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


# ==========================================
# MAIN ASSISTANT
# ==========================================

def answer_user(message):
    original = message.strip()
    text = original.lower().strip()

    if not text:
        return "Savolingizni yozing."

    # SALOMLASHISH

    greetings = [
        "salom", "assalomu alaykum", "assalom",
        "hello", "hi", "привет", "здравствуйте"
    ]

    if text in greetings:
        return random.choice([
            "Salom! 👋 Men SHERZOD AI ASSISTANT 1.0 man. Sizga qanday yordam beray?",
            "Assalomu alaykum! Bugun qanday savolingiz bor?",
            "Salom! Men tayyorman. Suhbatlashamizmi?"
        ])

    if "qalaysan" in text or "qandaysan" in text:
        return "Rahmat, yaxshi! Sizga qanday yordam bera olaman?"

    if "rahmat" in text or "спасибо" in text or "thank you" in text:
        return "Arzimaydi! Yana yordam kerak bo‘lsa, bemalol so‘rang. 😊"

    if "isming" in text or "kimsan" in text:
        return "Men SHERZOD AI ASSISTANT 1.0 man. Muallifim: Fayzullayev Sherzodbek."

    if "kim yaratgan" in text or "muallif" in text:
        return "Meni Fayzullayev Sherzodbek yaratgan."

    if "nima qila olasan" in text or text == "yordam":
        return help_text()

    # TIME

    if "soat" in text and (
        "nechi" in text or "vaqt" in text
    ):
        clock, date = get_time()
        return f"🕒 Toshkent vaqti: {clock}\n📅 Sana: {date}"

    if "bugun sana" in text or text == "sana":
        clock, date = get_time()
        return f"Bugungi sana: {date}"

    # WEATHER

    if text.startswith("ob havo:") or text.startswith("ob-havo:"):
        city = original.split(":", 1)[1].strip()
        return weather(city) if city else "Shahar nomini yozing."

    if text.startswith("ob havo ") or text.startswith("ob-havo "):
        city = original.split(" ", 2)[2].strip()
        return weather(city)

    # TRANSLATION

    translation_commands = [
        ("uz-en:", "uz", "en"),
        ("uz-ru:", "uz", "ru"),
        ("en-uz:", "en", "uz"),
        ("ru-uz:", "ru", "uz"),
        ("uz-en ", "uz", "en"),
        ("uz-ru ", "uz", "ru"),
        ("en-uz ", "en", "uz"),
        ("ru-uz ", "ru", "uz")
    ]

    for prefix, source, target in translation_commands:
        if text.startswith(prefix):
            content = original[len(prefix):].strip()

            if not content:
                return "Tarjima qilinadigan matnni yozing."

            return translate_text(content, source, target)

    # DICTIONARY

    dictionary_query = text.replace("tarjima:", "").strip()

    if dictionary_query in WORDS:
        return f"📖 {original} — {WORDS[dictionary_query]}"

    # CURRENCY

    if "valyuta" in text or "dollar kurs" in text:
        return currency()

    # CALCULATOR

    if text.startswith("hisobla:") or text.startswith("calc:"):
        expression = original.split(":", 1)[1].strip()
        return f"🧮 Natija: {safe_calculate(expression)}"

    # RANDOM CONTENT

    if "qiziqarli fakt" in text or text == "fakt":
        return "💡 " + random.choice(FACTS)

    if "hazil" in text or "kulgili" in text:
        return "😂 " + random.choice(JOKES)

    if "motivatsiya" in text:
        return "⭐ " + random.choice(MOTIVATION)

    if "topishmoq" in text:
        question, solution = random.choice(RIDDLES)
        return f"🧩 {question}\n\nJavobini topishga harakat qiling!"

    if text == "javobi":
        return "Topishmoq javobini bilish uchun qaytadan 'topishmoq' deb yozing."

    # KNOWLEDGE

    for key, value in KNOWLEDGE.items():
        if key in text:
            return "📚 " + value

    # QUIZ

    if text == "viktorina":
        question = random.choice(QUIZ)

        st.session_state.last_quiz = question

        return (
            "🎓 **Viktorina**\n\n"
            + question["q"] + "\n\n"
            + "\n".join(
                f"{i+1}. {a}"
                for i, a in enumerate(question["a"])
            )
            + "\n\nJavobingizni 1, 2 yoki 3 ko‘rinishida yozing."
        )

    if hasattr(st.session_state, "last_quiz") and text in ["1", "2", "3"]:
        question = st.session_state.last_quiz

        if int(text) - 1 == question["correct"]:
            del st.session_state.last_quiz
            return "🎉 To‘g‘ri javob! Barakalla!"

        del st.session_state.last_quiz
        return "Bu safar xato. Yana bir marta viktorina o‘ynab ko‘ring!"

    # GAME

    if text == "son top":
        number = random.randint(1, 10)
        st.session_state.game_number = number

        return "🎮 Men 1 dan 10 gacha son o‘yladim. Topishga harakat qiling!"

    if hasattr(st.session_state, "game_number"):
        if text.isdigit():
            guess = int(text)

            if guess == st.session_state.game_number:
                del st.session_state.game_number
                return "🏆 Barakalla! To‘g‘ri topdingiz!"

            if guess < st.session_state.game_number:
                return "Kattaroq son ayting!"

            return "Kichikroq son ayting!"

    # PASSWORD GENERATOR

    if "parol yarat" in text:
        alphabet = "abcdefghijkmnopqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789!@#"
        password = "".join(
            random.choice(alphabet) for _ in range(16)
        )
        return f"🔐 Yangi parol: `{password}`"

    # PYTHON

    if "python" in text and (
        "nima" in text or "o‘rgan" in text or "organ" in text
    ):
        return (
            "🐍 Python — dasturlash tili.\n\n"
            "U orqali sayt, dastur, o‘yin va sun'iy intellekt "
            "loyihalarini yaratish mumkin.\n\n"
            "Oddiy misol:\n\n"
            "```python\nprint('Salom dunyo!')\n```"
        )

    # WIKIPEDIA LANGUAGE COMMANDS

    for prefix, lang in [
        ("wiki-uz:", "uz"),
        ("wiki-ru:", "ru"),
        ("wiki-en:", "en"),
        ("wiki:", "uz")
    ]:
        if text.startswith(prefix):
            query = original[len(prefix):].strip()

            if not query:
                return "Qidiruv uchun mavzuni yozing."

            result = wikipedia_search(query, lang)

            return result or "Bu mavzu bo‘yicha ma'lumot topilmadi."

    # GENERAL WIKIPEDIA SEARCH

    if len(text.split()) >= 2:
        result = wikipedia_search(original, "uz")

        if result:
            return result

    # CONTEXT FOLLOW-UP

    if len(st.session_state.messages) >= 2:
        previous = st.session_state.messages[-1]["content"]

        if text in ["nega?", "nima uchun?", "batafsil", "davom et", "yana"]:
            return (
                "Albatta! Oldingi mavzuimizni davom ettiramiz.\n\n"
                f"Oldingi javobimiz: {previous[:700]}\n\n"
                "Qaysi qismini batafsil tushuntirishimni yozing."
            )

    return (
        "Savolingizni tushunishga harakat qildim, lekin aniq javob "
        "topa olmadim. Boshqacharoq qilib yozing yoki quyidagilardan "
        "foydalaning:\n\n"
        "- `wiki-uz: Amir Temur`\n"
        "- `wiki-ru: история Узбекистана`\n"
        "- `wiki-en: Solar System`\n"
        "- `uz-en: Salom`\n"
        "- `ob havo Toshkent`\n"
        "- `hisobla: 25*4`"
    )


# ==========================================
# HELP
# ==========================================

def help_text():
    return """
# 👑 SHERZOD AI — YORDAM

### 💬 Suhbat
Oddiy savollar yozing va suhbatlashing.

### 🌍 Tarjima
- `uz-en: Salom`
- `uz-ru: Salom`
- `en-uz: Hello`
- `ru-uz: Привет`

### 📚 Wikipedia
- `wiki-uz: Amir Temur`
- `wiki-ru: история`
- `wiki-en: science`

### 🌤 Ob-havo
- `ob havo Toshkent`
- `ob havo Mangit`

### 🧮 Kalkulyator
- `hisobla: 25*4`
- `hisobla: 100/5`

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


# ==========================================
# HEADER
# ==========================================

st.markdown(
    "<h1 style='text-align:center;'>👑 SHERZOD AI</h1>",
    unsafe_allow_html=True
)

st.markdown(
    "<p style='text-align:center;color:#aaa;'>"
    "SMART ASSISTANT • VERSION 1.0"
    "</p>",
    unsafe_allow_html=True
)

st.divider()

# ==========================================
# SIDEBAR
# ==========================================

with st.sidebar:
    st.markdown("## 👑 SHERZOD AI")
    st.caption("Fayzullayev Sherzodbek")

    st.divider()

    clock, date = get_time()

    st.write("🕒", clock)
    st.write("📅", date)

    st.divider()

    st.markdown("### 📌 Buyruqlar")

    if st.button("💡 Yordam", use_container_width=True):
        st.session_state.messages.append({
            "role": "assistant",
            "content": help_text()
        })

    if st.button("🎲 Qiziqarli fakt", use_container_width=True):
        st.session_state.messages.append({
            "role": "assistant",
            "content": random.choice(FACTS)
        })

    if st.button("😂 Hazil", use_container_width=True):
        st.session_state.messages.append({
            "role": "assistant",
            "content": random.choice(JOKES)
        })

    if st.button("⭐ Motivatsiya", use_container_width=True):
        st.session_state.messages.append({
            "role": "assistant",
            "content": random.choice(MOTIVATION)
        })

    if st.button("🧩 Topishmoq", use_container_width=True):
        question, solution = random.choice(RIDDLES)
        st.session_state.messages.append({
            "role": "assistant",
            "content": question
        })

    st.divider()

    if st.button("🗑 Suhbatni tozalash", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.caption("SHERZOD AI ASSISTANT 1.0")


# ==========================================
# CHAT DISPLAY
# ==========================================

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# ==========================================
# CHAT INPUT
# ==========================================

user_input = st.chat_input(
    "SHERZOD AI ga savolingizni yozing..."
)

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


# ==========================================
# FOOTER
# ==========================================

st.divider()

st.markdown(
    "<p style='text-align:center;color:#888;'>"
    "© SHERZOD AI ASSISTANT 1.0 | "
    "Created by Fayzullayev Sherzodbek"
    "</p>",
    unsafe_allow_html=True
)
