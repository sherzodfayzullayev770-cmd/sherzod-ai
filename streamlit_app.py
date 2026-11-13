
import streamlit as st
import requests
import re
import ast
import operator
import random
from datetime import datetime
from zoneinfo import ZoneInfo
from urllib.parse import quote

# =========================================
# SHERZOD AI ASSISTANT 1.0
# Fayzullayev Sherzodbek yaratgan
# =========================================

st.set_page_config(
    page_title="SHERZOD AI ASSISTANT 1.0",
    page_icon="🤖",
    layout="centered"
)

S = requests.Session()
S.headers.update({"User-Agent": "SherzodAI/1.0"})

# QORAMTIR DIZAYN
st.markdown("""
<style>
.stApp {
    background: #070a12;
    color: #f1f3fa;
}
h1, h2, h3 {
    color: #e5eaff !important;
}
p, label, .stMarkdown {
    color: #d5dcef;
}
.stChatMessage {
    background: #111827;
    border: 1px solid #26334d;
    border-radius: 14px;
}
input {
    background: #111827 !important;
}
footer {
    visibility: hidden;
}
#MainMenu {
    visibility: hidden;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div style="text-align:center;padding:20px;">
<h1>🤖 SHERZOD AI</h1>
<h3>ASSISTANT 1.0</h3>
<p>Fayzullayev Sherzodbek yaratgan</p>
<p>YOUR SMART ASSISTANT</p>
</div>
""", unsafe_allow_html=True)

# 1. SANA VA VAQT

def get_time():
    now = datetime.now(ZoneInfo("Asia/Tashkent"))
    return (
        f"📅 Sana: {now.strftime('%d.%m.%Y')}\n\n"
        f"🕒 Toshkent vaqti: {now.strftime('%H:%M:%S')}"
    )


# 2. OB-HAVO

WEATHER_CODES = {
    0: "Ochiq osmon",
    1: "Asosan ochiq",
    2: "Qisman bulutli",
    3: "Bulutli",
    45: "Tuman",
    48: "Qirovli tuman",
    51: "Yengil shivalama yomg'ir",
    53: "O'rtacha shivalama yomg'ir",
    55: "Kuchli shivalama yomg'ir",
    61: "Yengil yomg'ir",
    63: "O'rtacha yomg'ir",
    65: "Kuchli yomg'ir",
    71: "Yengil qor",
    73: "O'rtacha qor",
    75: "Kuchli qor",
    80: "Yomg'ir ehtimoli",
    81: "Kuchli yomg'ir",
    82: "Juda kuchli yomg'ir",
    95: "Momaqaldiroq",
    96: "Do'lli momaqaldiroq",
    99: "Kuchli do'lli momaqaldiroq"
}

CITY_ALIASES = {
    "mangit": ["Mangit", "Manghit", "Mangyt"],
    "mang'it": ["Mangit", "Manghit", "Mangyt"],
    "mang‘it": ["Mangit", "Manghit", "Mangyt"]
}

def find_city(city):
    variants = CITY_ALIASES.get(city.lower(), [city])

    for name in variants:
        try:
            r = S.get(
                "https://geocoding-api.open-meteo.com/v1/search",
                params={
                    "name": name,
                    "count": 10,
                    "language": "en",
                    "format": "json"
                },
                timeout=15
            )
            r.raise_for_status()
            places = r.json().get("results", [])

            uz = [
                p for p in places
                if p.get("country_code") == "UZ"
            ]

            if uz:
                return uz[0]

            if places and len(variants) == 1:
                return places[0]

        except Exception:
            pass

    return None


def get_weather(city):
    try:
        place = find_city(city)

        if not place:
            return f"❌ {city} topilmadi. Shahar nomini tekshiring."

        r = S.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": place["latitude"],
                "longitude": place["longitude"],
                "current": (
                    "temperature_2m,relative_humidity_2m,"
                    "apparent_temperature,precipitation,"
                    "weather_code,wind_speed_10m"
                ),
                "daily": (
                    "weather_code,temperature_2m_max,"
                    "temperature_2m_min,precipitation_probability_max"
                ),
                "forecast_days": 7,
                "timezone": "auto"
            },
            timeout=20
        )
        r.raise_for_status()

        data = r.json()
        c = data["current"]
        d = data["daily"]

        result = (
            f"🌍 {place['name']}, {place.get('country', '')}\n\n"
            f"🌤 HOZIRGI OB-HAVO\n"
            f"Holat: {WEATHER_CODES.get(c['weather_code'], 'Noma’lum')}\n"
            f"🌡 Harorat: {c['temperature_2m']} °C\n"
            f"🤔 His qilinishi: {c['apparent_temperature']} °C\n"
            f"💧 Namlik: {c['relative_humidity_2m']}%\n"
            f"🌧 Yog'ingarchilik: {c['precipitation']} mm\n"
            f"💨 Shamol: {c['wind_speed_10m']} km/soat\n\n"
            "📆 7 KUNLIK PROGNOZ\n"
        )

        for i, day in enumerate(d["time"]):
            result += (
                f"\n📅 {day}: "
                f"{WEATHER_CODES.get(d['weather_code'][i], 'Noma’lum')}\n"
                f"🌡 {d['temperature_2m_min'][i]}°C - "
                f"{d['temperature_2m_max'][i]}°C\n"
                f"🌧 Yomg'ir ehtimoli: "
                f"{d['precipitation_probability_max'][i]}%\n"
            )

        return result + "\n📡 Manba: Open-Meteo"

    except Exception:
        return "Ob-havo xizmatiga ulanib bo'lmadi. Keyinroq urinib ko'ring."


# 3. TIL ANIQLASH VA TARJIMA

EN_WORDS = set("""
hello hi hey goodbye bye good morning good evening good night
how are you what why when where who which thank thanks please
beautiful friend friends school computer phone house home
love happy sad today tomorrow yesterday water book work learn
world language english russian uzbek family mother father
brother sister sister brother name age time day week month year
yes no okay fine cool great amazing wonderful welcome sorry
help understand speak write read listen look come go want need
like know think believe make create play game music movie
weather sun moon star earth space science history future
technology artificial intelligence assistant question answer
because maybe always never sometimes important interesting
computer programming python website internet browser application
football basketball player team goal win lose fast slow good bad
""".split())

RU_WORDS = set("""
привет здравствуйте пока до свидания спасибо пожалуйста
доброе утро добрый день добрый вечер спокойной ночи
как дела хорошо плохо отлично нормально
да нет ладно конечно почему зачем когда где кто что
сколько какой какая какие можно нельзя хочу нужно
люблю нравится не нравится понимаю не понимаю
говорить писать читать слушать смотреть играть
мама папа брат сестра друг подруга семья школа
дом работа компьютер телефон интернет сайт программа
красивый красивая хороший хорошая плохой плохая
сегодня завтра вчера сейчас потом уже ещё
время дата погода дождь снег солнце ветер
вода книга машина город страна человек мир
учёба урок учитель ученик вопрос ответ
помоги помогите перевод переведи значение слово
молодец умный интересный смешной шутка
""".split())


def detect_source(text):
    low = text.lower()

    if re.search(r"[а-яё]", low):
        return "ru"

    words = set(re.findall(r"[a-z']+", low))

    if words.intersection(EN_WORDS):
        return "en"

    return "uz"


# KENGAYTIRILGAN LUG'AT
RU_DICTIONARY = {
    "привет": "salom",
    "пока": "xayr",
    "спасибо": "rahmat",
    "пожалуйста": "iltimos / arzimaydi",
    "да": "ha",
    "нет": "yo'q",
    "хорошо": "yaxshi",
    "плохо": "yomon",
    "красивый": "chiroyli",
    "красивая": "chiroyli",
    "друг": "do'st",
    "подруга": "dugona",
    "мама": "ona",
    "папа": "ota",
    "брат": "aka / uka",
    "сестра": "opa / singil",
    "любовь": "sevgi",
    "люблю": "sevaman",
    "нравится": "yoqadi",
    "скучаю": "sog'indim",
    "почему": "nima uchun",
    "зачем": "nima maqsadda",
    "когда": "qachon",
    "где": "qayerda",
    "кто": "kim",
    "что": "nima",
    "сегодня": "bugun",
    "завтра": "ertaga",
    "вчера": "kecha",
    "сейчас": "hozir",
    "потом": "keyin",
    "дом": "uy",
    "школа": "maktab",
    "книга": "kitob",
    "вода": "suv",
    "солнце": "quyosh",
    "луна": "oy",
    "время": "vaqt",
    "день": "kun",
    "ночь": "tun",
    "утро": "ertalab",
    "вечер": "kechqurun",
    "работа": "ish",
    "учёба": "o'qish",
    "девушка": "qiz",
    "мальчик": "o'g'il bola",
    "девочка": "qiz bola",
    "умный": "aqlli",
    "смешной": "kulgili",
    "классно": "zo'r",
    "ладно": "mayli",
    "хватит": "yetar",
    "пойдём": "ketdik / boramiz",
    "помоги": "yordam ber",
    "понимаю": "tushunyapman",
    "не понимаю": "tushunmayapman"
}

EN_DICTIONARY = {
    "hello": "salom",
    "goodbye": "xayr",
    "thanks": "rahmat",
    "thank you": "rahmat",
    "please": "iltimos",
    "yes": "ha",
    "no": "yo'q",
    "good": "yaxshi",
    "bad": "yomon",
    "beautiful": "chiroyli",
    "friend": "do'st",
    "family": "oila",
    "mother": "ona",
    "father": "ota",
    "brother": "aka / uka",
    "sister": "opa / singil",
    "love": "sevgi",
    "happy": "xursand",
    "sad": "xafa",
    "today": "bugun",
    "tomorrow": "ertaga",
    "yesterday": "kecha",
    "now": "hozir",
    "later": "keyin",
    "house": "uy",
    "school": "maktab",
    "book": "kitob",
    "water": "suv",
    "sun": "quyosh",
    "moon": "oy",
    "time": "vaqt",
    "day": "kun",
    "night": "tun",
    "morning": "ertalab",
    "evening": "kechqurun",
    "computer": "kompyuter",
    "phone": "telefon",
    "work": "ish",
    "learn": "o'rganmoq",
    "beautiful": "chiroyli",
    "smart": "aqlli",
    "funny": "kulgili",
    "interesting": "qiziqarli",
    "weather": "ob-havo",
    "question": "savol",
    "answer": "javob",
    "help": "yordam",
    "understand": "tushunmoq",
    "friendship": "do'stlik",
    "future": "kelajak",
    "world": "dunyo",
    "dream": "orzu",
    "success": "muvaffaqiyat"
}


def translate_text(text, target):
    if len(text.encode("utf-8")) > 500:
        return "Matn juda uzun. Uni qisqaroq qismlarga bo'ling."

    source = detect_source(text)
    low = text.lower().strip()

    if source == target:
        return "Matn allaqachon shu tilda yozilgan bo'lishi mumkin."

    if target == "uz":
        dictionary = RU_DICTIONARY if source == "ru" else EN_DICTIONARY
        if low in dictionary:
            return dictionary[low]

    # MyMemory
    try:
        r = S.get(
            "https://api.mymemory.translated.net/get",
            params={
                "q": text,
                "langpair": f"{source}|{target}",
                "mt": "1"
            },
            timeout=20
        )
        r.raise_for_status()
        data = r.json()

        translated = data.get("responseData", {}).get(
            "translatedText", ""
        )

        if data.get("responseStatus") == 200 and translated:
            if translated.lower() != low:
                return translated

    except Exception:
        pass

    # Google tarjima xizmati
    try:
        r = S.get(
            "https://translate.googleapis.com/translate_a/single",
            params={
                "client": "gtx",
                "sl": source,
                "tl": target,
                "dt": "t",
                "q": text
            },
            timeout=20
        )
        r.raise_for_status()
        data = r.json()

        translated = "".join(
            part[0] for part in data[0] if part[0]
        )

        if translated:
            return translated

    except Exception:
        pass

    return "Tarjima xizmati hozir ishlamadi. Keyinroq urinib ko'ring."


# 4. MATEMATIKA

OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.USub: operator.neg
}


def calculate(expression):
    try:
        tree = ast.parse(expression, mode="eval")

        def solve(node):
            if isinstance(node, ast.Expression):
                return solve(node.body)

            if isinstance(node, ast.Constant):
                if type(node.value) in (int, float):
                    return node.value
                raise ValueError()

            if isinstance(node, ast.BinOp) and type(node.op) in OPS:
                a = solve(node.left)
                b = solve(node.right)

                if abs(a) > 10**50 or abs(b) > 10**50:
                    raise ValueError()

                return OPS[type(node.op)](a, b)

            if isinstance(node, ast.UnaryOp) and type(node.op) in OPS:
                return OPS[type(node.op)](solve(node.operand))

            raise ValueError()

        result = solve(tree)

        if abs(result) > 10**100:
            return None

        return result

    except Exception:
        return None


# 5. QIZIQARLI FAKTLAR

FACTS = [
    "Quyosh nuri Yerga taxminan 8 daqiqada yetib keladi.",
    "Ahtapotning uchta yuragi bor.",
    "Mars Qizil sayyora deb ataladi.",
    "Yupiter Quyosh tizimidagi eng katta sayyoradir.",
    "Saturn halqalari bilan mashhur.",
    "Delfinlar tovushlar orqali muloqot qiladi.",
    "Pingvinlar ucha olmaydi, lekin yaxshi suzadi.",
    "Inson tanasidagi eng katta a'zo teridir.",
    "Yer taxminan 4,5 milliard yoshda.",
    "Antarktida Yer yuzidagi eng sovuq materikdir.",
    "Python dasturlash tili 1991-yilda ommaga taqdim etilgan.",
    "Kompyuterlar ma'lumotlarni ikkilik tizimda qayta ishlaydi.",
    "Kapalaklar ta'mni oyoqlari orqali sezishi mumkin.",
    "Yulduzlar juda katta gaz sharlari hisoblanadi.",
    "Kitlar sutemizuvchi hayvonlardir.",
    "Yerning tabiiy yo'ldoshi Oy deb ataladi.",
    "O'simliklar fotosintez jarayonida yorug'likdan foydalanadi.",
    "Kamalak yorug'lik va suv tomchilari bilan hosil bo'ladi.",
    "Internet butun dunyo kompyuter tarmoqlarini bog'laydi.",
    "Suv odatdagi bosimda 100°C da qaynaydi."
]


# 6. AVTOJAVOBLAR

AUTO_REPLIES = {
    "qalaysan": [
        "Zo'r! Men ishlashga tayyorman. Sizchi? 😎",
        "Sherzod AI doim yordam berishga tayyor! 🤖",
        "Hammasi yaxshi! Bugun qanday savolingiz bor?"
    ],
    "zerikdim": [
        "Unda sizga qiziqarli fakt aytaymi? 💡",
        "Keling, yangi bilimlarni o'rganamiz!",
        "Hazil yoki qiziqarli fakt eshitishni xohlaysizmi?"
    ],
    "rahmat": [
        "Arzimaydi! Yana yordam kerak bo'lsa, yozing! 😊",
        "Sizga yordam bera olganimdan xursandman!",
        "Har doim yordam berishga tayyorman!"
    ],
    "hazil": [
        "Kompyuter nega sovqotmaydi? Chunki uning Windows oynalari bor! 😂",
        "Dasturchi choy ichayotganda ham kod haqida o'ylaydi! ☕",
        "Kompyuterning sevimli musiqasi? Disko! 😄"
    ],
    "motivatsiya": [
        "Har bir katta loyiha kichik qadamdan boshlanadi! 🚀",
        "Xatolar — o'rganishning bir qismi. Taslim bo'lmang!",
        "Bugungi mehnat ertangi natijaga aylanadi!",
        "Bilim — eng kuchli vositalardan biri!"
    ]
}


# 7. WIKIPEDIA BILIM QIDIRISH

def search_knowledge(question):
    for lang in ["uz", "en", "ru"]:
        try:
            r = S.get(
                f"https://{lang}.wikipedia.org/w/api.php",
                params={
                    "action": "query",
                    "list": "search",
                    "srsearch": question,
                    "format": "json",
                    "srlimit": 3
                },
                timeout=15
            )
            r.raise_for_status()

            results = r.json()["query"]["search"]

            if not results:
                continue

            title = results[0]["title"]

            page = S.get(
                f"https://{lang}.wikipedia.org/api/rest_v1/page/summary/"
                + quote(title.replace(" ", "_")),
                timeout=15
            )

            if page.status_code == 200:
                answer = page.json().get("extract", "")

                if answer:
                    return (
                        f"📚 {title}\n\n{answer}\n\n"
                        f"📡 Manba: {lang}.wikipedia.org"
                    )

        except Exception:
            continue

    return None


# 8. SHERZOD AI ASOSIY MIYASI

def sherzod_ai(message, history):
    text = message.strip()
    low = text.lower()

    if not text:
        return "Savolingizni yozing!"

    # Salomlashish
    if low in [
        "salom", "assalomu alaykum", "hello",
        "hi", "привет", "здравствуйте",
        "добрый день", "доброе утро"
    ]:
        return (
            "Va alaykum assalom! 😊\n\n"
            "Men SHERZOD AI ASSISTANT 1.0 man.\n"
            "Sizga qanday yordam beray?"
        )

    # Muallif
    if any(x in low for x in [
        "seni kim yaratgan", "kim yaratdi",
        "muallifing kim", "кто тебя создал",
        "who created you"
    ]):
        return "Meni Fayzullayev Sherzodbek yaratgan! 🤖"

    # Sana va vaqt
    if any(x in low for x in [
        "soat nechchi", "soat nechi",
        "sana nechchi", "bugun nechanchi",
        "hozirgi vaqt", "vaqtni ko'rsat",
        "what time", "который час"
    ]):
        return get_time()

    # Ob-havo
    if low in ["ob havo", "ob-havo", "weather", "погода"]:
        return get_weather("Mangit")

    weather_match = re.search(
        r"(.+?)\s+(?:ob[\s-]?havo|weather|погода)$|"
        r"(?:ob[\s-]?havo|weather|погода)\s+(.+)$",
        text,
        re.IGNORECASE
    )

    if weather_match:
        city = (
            weather_match.group(1) or
            weather_match.group(2)
        ).strip(" ?.!,")

        if city.lower() in ["bugun", "hozir", "qanday"]:
            city = "Mangit"

        return get_weather(city)

    # Tarjima
    match = re.match(
        r"^(?:ruscha|rus tiliga|russcha|переведи на русский)"
        r"\s*[:\-]?\s*(.+)$",
        text,
        re.IGNORECASE
    )
    if match:
        return "🇷🇺 RUSCHA TARJIMA:\n\n" + translate_text(
            match.group(1), "ru"
        )

    match = re.match(
        r"^(?:inglizcha|ingliz tiliga|english|translate to english)"
        r"\s*[:\-]?\s*(.+)$",
        text,
        re.IGNORECASE
    )
    if match:
        return "🇬🇧 ENGLISH TRANSLATION:\n\n" + translate_text(
            match.group(1), "en"
        )

    match = re.match(
        r"^(?:o'zbekcha|uzbekcha|o'zbek tiliga)"
        r"\s*[:\-]?\s*(.+)$",
        text,
        re.IGNORECASE
    )
    if match:
        return "🇺🇿 O'ZBEKCHA TARJIMA:\n\n" + translate_text(
            match.group(1), "uz"
        )

    # So'z ma'nosi
    match = re.match(
        r"^(?:ma'nosi|manosi|meaning|значение)"
        r"\s*[:\-]?\s*(.+)$",
        text,
        re.IGNORECASE
    )
    if match:
        return "📖 SO'Z MA'NOSI:\n\n" + translate_text(
            match.group(1), "uz"
        )

    # Lug'atdagi so'z
    if low in RU_DICTIONARY:
        return f"🇷🇺 {low} — 🇺🇿 {RU_DICTIONARY[low]}"

    if low in EN_DICTIONARY:
        return f"🇬🇧 {low} — 🇺🇿 {EN_DICTIONARY[low]}"

    # Matematika
    expression = low.replace("×", "*").replace("÷", "/")

    if re.fullmatch(r"[\d\s+\-*/().%^]+", expression):
        result = calculate(expression.replace("^", "**"))

        if result is not None:
            return f"🧮 Hisob natijasi: {result}"

    # Faktlar
    if any(x in low for x in [
        "fakt ayt", "qiziqarli fakt",
        "qiziq ma'lumot", "bir fakt"
    ]):
        return "💡 QIZIQARLI FAKT:\n\n" + random.choice(FACTS)

    # Hazil
    if "hazil" in low or "kuldir" in low or "шутка" in low:
        return random.choice(AUTO_REPLIES["hazil"])

    # Motivatsiya
    if any(x in low for x in [
        "motivatsiya", "ruh ber", "мотивируй",
        "motivation"
    ]):
        return random.choice(AUTO_REPLIES["motivatsiya"])

    # Salomlashishga yaqin ruscha iboralar
    if any(x in low for x in ["как дела", "как ты"]):
        return "У меня всё хорошо! 😊 А у вас как дела?"

    if any(x in low for x in ["спасибо", "благодарю"]):
        return "Пожалуйста! 😊 Har doim yordam beraman."

    if "i love" in low:
        return "Bu juda yaxshi fikr! ❤️"

    if "how are you" in low:
        return "I'm doing well, thank you! 😊"

    if "what is your name" in low:
        return "My name is Sherzod AI Assistant 1.0. 🤖"

    # Avtojavoblar
        for key, replies in AUTO_REPLIES.items():
            if key in low:
                return random.choice(replies)

        return "Kechirasiz, bu savolga hozircha javob topolmadim. Boshqacha so‘rab ko‘ring."
