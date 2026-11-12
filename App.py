

%pip -q install -U gradio requests

import gradio as gr
import requests
import re
import ast
import operator
import random
from datetime import datetime
from zoneinfo import ZoneInfo
from urllib.parse import quote

S = requests.Session()
S.headers.update({"User-Agent": "SherzodAI/1.0"})

# =========================================
# SHERZOD AI ASSISTANT 1.0
# Fayzullayev Sherzodbek yaratgan
# =========================================

# 1. SANA VA VAQT

def get_time():
    now = datetime.now(ZoneInfo("Asia/Tashkent"))
    return (
        f"📅 Sana: {now.strftime('%d.%m.%Y')}\n"
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
            return (
                f"❌ {city} topilmadi.\n"
                "Shahar nomini boshqacha yozib ko'ring."
            )

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

# 3. TARJIMA TIZIMI

EN_WORDS = {
    "hello", "good", "morning", "evening", "night",
    "how", "are", "you", "thank", "thanks", "please",
    "beautiful", "friend", "school", "computer",
    "love", "happy", "today", "tomorrow", "yesterday",
    "water", "book", "house", "work", "learn"
}

def detect_source(text):
    if re.search(r"[а-яё]", text.lower()):
        return "ru"

    words = set(re.findall(r"[a-z]+", text.lower()))

    if words.intersection(EN_WORDS):
        return "en"

    return "uz"

def translate_text(text, target):
    if len(text.encode("utf-8")) > 500:
        return "Matn juda uzun. Iltimos, uni qisqaroq qismlarga bo'ling."

    source = detect_source(text)

    if source == target:
        return "Matn allaqachon shu tilda yozilgan bo'lishi mumkin."

    # Birinchi usul: MyMemory
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
            if translated.lower() != text.lower():
                return translated

    except Exception:
        pass

    # Ikkinchi usul: Google tarjima xizmati
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

    return (
        "Tarjima xizmatlari hozir ishlamadi.\n"
        "Internetni tekshirib, keyinroq urinib ko'ring."
    )

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
    "Asalarilar gullarni changlatishda muhim rol o'ynaydi.",
    "Yorug'lik vakuumda sekundiga taxminan 300 ming km yuradi.",
    "Yer Quyosh atrofida aylanadi.",
    "Oy Yerning tabiiy yo'ldoshidir.",
    "Mars Qizil sayyora deb ataladi.",
    "Yupiter Quyosh tizimidagi eng katta sayyoradir.",
    "Saturn halqalari bilan mashhur.",
    "Delfinlar tovushlar orqali muloqot qiladi.",
    "Pingvinlar ucha olmaydi, lekin yaxshi suzadi.",
    "Bambukning ayrim turlari juda tez o'sadi.",
    "Inson tanasidagi eng katta a'zo teridir.",
    "Suv odatdagi atmosfera bosimida 100°C da qaynaydi.",
    "O'simliklar fotosintez jarayonida yorug'likdan foydalanadi.",
    "Yer taxminan 4,5 milliard yoshda.",
    "Antarktida Yer yuzidagi eng sovuq materikdir.",
    "Nil dunyodagi eng uzun daryolardan biri hisoblanadi.",
    "Kompyuterlar ma'lumotlarni ikkilik tizimda qayta ishlaydi.",
    "Python dasturlash tili 1991-yilda ommaga taqdim etilgan.",
    "Internet butun dunyo kompyuter tarmoqlarini bog'laydi.",
    "Kapalaklar ta'mni oyoqlari orqali sezishi mumkin.",
    "Koalalar asosan evkalipt barglari bilan oziqlanadi.",
    "Yulduzlar juda katta gaz sharlari hisoblanadi.",
    "Kamalak yorug'likning suv tomchilarida sinishi va qaytishi bilan hosil bo'ladi.",
    "Dunyo okeanlari Yer yuzasining katta qismini egallaydi.",
    "Kitlar sutemizuvchi hayvonlardir.",
    "Asalarilar raqsga o'xshash harakatlar bilan oziq manzilini bildiradi.",
    "Inson miyasi juda ko'p nerv hujayralaridan tashkil topgan.",
    "Yerning tabiiy yo'ldoshi Oy deb ataladi."
]

# 6. QIZIQARLI AVTOJAVOBLAR

AUTO_REPLIES = {
    "qalaysan": [
        "Zo'r! Men ishlashga tayyorman. Sizchi? 😎",
        "Sherzod AI doim yordam berishga tayyor! 🤖"
    ],
    "zerikdim": [
        "Unda sizga qiziqarli fakt aytaymi? 💡",
        "Keling, kichik bilim sinovini boshlaymiz! 🧠"
    ],
    "rahmat": [
        "Arzimaydi! Yana yordam kerak bo'lsa, yozing! 😊",
        "Sizga yordam berish men uchun muhim!"
    ],
    "kimman": [
        "Siz Sherzod AI bilan suhbatlashayotgan foydalanuvchisiz! 😄"
    ],
    "hazil": [
        "Kompyuter nega sovqotmaydi? Chunki uning Windows oynalari bor! 😂",
        "Dasturchi choy ichayotganda ham kod haqida o'ylaydi! ☕"
    ],
    "motivatsiya": [
        "Har bir katta loyiha kichik qadamdan boshlanadi! 🚀",
        "Bugun o'rgangan narsangiz ertangi muvaffaqiyatingizga yordam beradi! 💡",
        "Xatolar — o'rganishning bir qismi. Taslim bo'lmang!"
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

# 8. ASOSIY SUHBAT

def sherzod_ai(message, history):
    text = message.strip()
    low = text.lower()

    if not text:
        return "Savolingizni yozing!"

    # Salomlashish
    if low in [
        "salom", "assalomu alaykum", "hello",
        "hi", "привет", "здравствуйте"
    ]:
        return (
            "Va alaykum assalom! 😊\n\n"
            "Men SHERZOD AI ASSISTANT 1.0 man.\n"
            "Sizga qanday yordam beray?"
        )

    # Muallif
    if any(x in low for x in [
        "seni kim yaratgan", "kim yaratdi",
        "muallifing kim"
    ]):
        return "Meni Fayzullayev Sherzodbek yaratgan! 🤖"

    # Sana va vaqt
    if any(x in low for x in [
        "soat nechchi", "soat nechi",
        "sana nechchi", "bugun nechanchi",
        "hozirgi vaqt", "vaqtni ko'rsat"
    ]):
        return get_time()

    # Ob-havo
    if low in ["ob havo", "ob-havo", "weather"]:
        return get_weather("Mangit")

    weather_match = re.search(
        r"(.+?)\s+(?:ob[\s-]?havo|weather)$|"
        r"(?:ob[\s-]?havo|weather)\s+(.+)$",
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
        r"^(?:ruscha|rus tiliga|russcha|"
        r"переведи на русский)\s*[:\-]?\s*(.+)$",
        text,
        re.IGNORECASE
    )
    if match:
        return (
            "🇷🇺 RUSCHA TARJIMA:\n\n" +
            translate_text(match.group(1), "ru")
        )

    match = re.match(
        r"^(?:inglizcha|ingliz tiliga|english|"
        r"translate to english)\s*[:\-]?\s*(.+)$",
        text,
        re.IGNORECASE
    )
    if match:
        return (
            "🇬🇧 ENGLISH TRANSLATION:\n\n" +
            translate_text(match.group(1), "en")
        )

    match = re.match(
        r"^(?:o'zbekcha|uzbekcha|o'zbek tiliga)\s*[:\-]?\s*(.+)$",
        text,
        re.IGNORECASE
    )
    if match:
        return (
            "🇺🇿 O'ZBEKCHA TARJIMA:\n\n" +
            translate_text(match.group(1), "uz")
        )

    # So'z ma'nosi
    match = re.match(
        r"^(?:ma'nosi|manosi|meaning|значение)\s*[:\-]?\s*(.+)$",
        text,
        re.IGNORECASE
    )
    if match:
        return (
            "📖 SO'Z MA'NOSI:\n\n" +
            translate_text(match.group(1), "uz")
        )

    # Matematika
    expression = low.replace("×", "*").replace("÷", "/")

    if re.fullmatch(r"[\d\s+\-*/().%^]+", expression):
        result = calculate(expression.replace("^", "**"))

        if result is not None:
            return f"🧮 Hisob natijasi: {result}"

    # Qiziqarli fakt
    if any(x in low for x in [
        "fakt ayt", "qiziqarli fakt",
        "qiziq ma'lumot", "bir fakt"
    ]):
        return "💡 QIZIQARLI FAKT:\n\n" + random.choice(FACTS)

    # Hazil
    if "hazil" in low or "kuldir" in low:
        return random.choice(AUTO_REPLIES["hazil"])

    # Motivatsiya
    if "motivatsiya" in low or "ruh ber" in low:
        return random.choice(AUTO_REPLIES["motivatsiya"])

    # Avtojavoblar
    for key, replies in AUTO_REPLIES.items():
        if key in low:
            return random.choice(replies)

    # Imkoniyatlar
    if "nima qila olasan" in low:
        return (
            "🤖 MENING IMKONIYATLARIM:\n\n"
            "🌤 Ob-havo va prognoz\n"
            "🇷🇺 Ruscha tarjima\n"
            "🇬🇧 Inglizcha tarjima\n"
            "🇺🇿 O'zbekcha tarjima\n"
            "📖 So'z ma'nosi\n"
            "🧮 Matematika\n"
            "🕒 Sana va vaqt\n"
            "💡 Qiziqarli faktlar\n"
            "😂 Hazillar\n"
            "🚀 Motivatsiya\n"
            "🌍 Wikipedia bilim qidiruvi"
        )

    # Suhbat tarixidan oddiy kontekst
    if "oldingi savolim" in low or "nima degandim" in low:
        if history:
            previous = history[-1]
            if isinstance(previous, dict):
                previous = previous.get("content", "")
            return f"Oldingi xabaringiz: {previous}"
        return "Hozircha oldingi xabar topilmadi."

    # Internetdan ma'lumot
    answer = search_knowledge(text)

    if answer:
        return answer

    return (
        "Kechirasiz, bu savolga hozir javob topa olmadim.\n\n"
        "Boshqacha qilib so'rab ko'ring. "
        "Agar xatolik bo'lsa, adminimiz Feruzaga murojaat qiling."
    )

# 9. QORAMTIR DIZAYN

css = """
.gradio-container {
    background: #070a12 !important;
    color: #f1f3fa !important;
}
#main-title {
    text-align: center;
    padding: 22px 5px;
}
#main-title h1 {
    color: #e5eaff;
    font-size: 36px;
    letter-spacing: 2px;
}
#main-title p {
    color: #9ba8c5;
}
footer {
    color: #8792aa !important;
}
"""

with gr.Blocks(
    theme=gr.themes.Base(
        primary_hue="indigo",
        neutral_hue="slate"
    ),
    css=css,
    title="SHERZOD AI ASSISTANT 1.0"
) as app:

    gr.HTML("""
    <div id="main-title">
        <h1>🤖 SHERZOD AI</h1>
        <h3>ASSISTANT 1.0</h3>
        <p>Fayzullayev Sherzodbek yaratgan</p>
        <p>YOUR SMART ASSISTANT</p>
    </div>
    """)

    gr.ChatInterface(
        fn=sherzod_ai,
        chatbot=gr.Chatbot(height=520),
        textbox=gr.Textbox(
            placeholder="Sherzod AI ga savolingizni yozing...",
            container=False
        )
    )

    gr.Markdown(
        "<center>SHERZOD AI • ASSISTANT 1.0 • 2026</center>"
    )

app.launch(share=True)
