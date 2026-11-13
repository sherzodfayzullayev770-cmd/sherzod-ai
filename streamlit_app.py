import streamlit as st
import requests
import random
import ast
import operator
from datetime import datetime
from zoneinfo import ZoneInfo

# ==========================================
# SHERZOD AI ASSISTANT 1.0
# Creator: Fayzullayev Sherzodbek
# ==========================================

st.set_page_config(
    page_title="SHERZOD AI ASSISTANT 1.0",
    page_icon="🤖",
    layout="centered"
)

# DESIGN
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg,#080d1b,#172746,#080d1b);
    color: white;
}
.hero {
    text-align:center;
    padding:25px;
    background:#172442;
    border-radius:20px;
    border:1px solid #526baf;
}
.hero h1 {color:white;}
.hero p {color:#c5d3f5;}
[data-testid="stChatMessage"] {
    border-radius:15px;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
<h1>🤖 SHERZOD AI</h1>
<h2>ASSISTANT 1.0</h2>
<p>Fayzullayev Sherzodbek yaratgan</p>
<p>YOUR SMART ASSISTANT</p>
</div>
""", unsafe_allow_html=True)

# INTERNET
S = requests.Session()
S.headers.update({"User-Agent": "SherzodAI/1.0"})
TIMEOUT = 12

# ==========================================
# MA'LUMOTLAR BAZASI
# ==========================================

FACTS = [
    "Ahtapotning uchta yuragi bor.",
    "Quyosh nuri Yerga taxminan 8 daqiqada yetadi.",
    "Venerada bir kun uning yilidan uzunroq.",
    "Asalarilar raqs orqali ma'lumot uzatadi.",
    "Inson tanasidagi eng katta a'zo teridir.",
    "Delfinlar bir-birini tovush orqali taniydi.",
    "Kosmosda tovush odatdagidek tarqalmaydi.",
    "Yer yuzining katta qismi suv bilan qoplangan.",
    "Bambukning ayrim turlari juda tez o'sadi.",
    "Oyning o'zidan yorug'lik chiqmaydi, u Quyosh nurini qaytaradi."
]

JOKES = [
    "Kompyuter nega sovqotdi? Windows ochiq qolibdi! 😂",
    "Dasturchi choy ichib, kodiga yana bug qo'shibdi.",
    "Robotning sevimli musiqasi? Algo-ritm! 🤖",
    "Matematika kitobi nega xafa? Unda muammolar ko'p!"
]

MOTIVATION = [
    "Har kuni ozgina o'rganish katta natija beradi! 💪",
    "Xatolar — o'rganishning bir qismi.",
    "Maqsading sari har kuni bir qadam tashla!",
    "Taslim bo'lma, muvaffaqiyat mehnat bilan keladi!"
]

RU = {
    "привет":"salom",
    "здравствуйте":"assalomu alaykum",
    "пока":"xayr",
    "до свидания":"xayr",
    "спасибо":"rahmat",
    "пожалуйста":"iltimos / arzimaydi",
    "да":"ha",
    "нет":"yo'q",
    "хорошо":"yaxshi",
    "плохо":"yomon",
    "как дела":"ishlar qalay",
    "что":"nima",
    "кто":"kim",
    "где":"qayerda",
    "когда":"qachon",
    "почему":"nega",
    "я":"men",
    "ты":"sen",
    "вы":"siz",
    "мы":"biz",
    "они":"ular",
    "друг":"do'st",
    "мама":"ona",
    "папа":"ota",
    "дом":"uy",
    "школа":"maktab",
    "книга":"kitob",
    "вода":"suv",
    "солнце":"quyosh",
    "любовь":"sevgi",
    "красивый":"chiroyli",
    "добрый":"mehribon",
    "злой":"jahldor",
    "хватит":"bas",
    "ладно":"mayli",
    "потом":"keyin",
    "сейчас":"hozir",
    "ещё":"yana",
    "пойдём":"ketdik",
    "не знаю":"bilmayman",
    "я не буду":"men qilmayman",
    "мне нравится":"menga yoqadi",
    "ты мне нравишься":"sen menga yoqasan",
    "сладких снов":"shirin tushlar",
    "го":"yur"
}

EN = {
    "hello":"salom",
    "hi":"salom",
    "goodbye":"xayr",
    "bye":"xayr",
    "thank you":"rahmat",
    "thanks":"rahmat",
    "please":"iltimos",
    "yes":"ha",
    "no":"yo'q",
    "good":"yaxshi",
    "bad":"yomon",
    "beautiful":"chiroyli",
    "friend":"do'st",
    "school":"maktab",
    "book":"kitob",
    "water":"suv",
    "sun":"quyosh",
    "moon":"oy",
    "computer":"kompyuter",
    "phone":"telefon",
    "how are you":"qalaysan",
    "what is your name":"isming nima",
    "my name is":"mening ismim",
    "i am fine":"men yaxshiman",
    "see you":"ko'rishguncha",
    "good morning":"xayrli tong",
    "good night":"xayrli tun",
    "sit":"o'tir",
    "look behind":"orqaga qara",
    "look back":"orqaga qara",
    "love":"sevgi",
    "happy":"baxtli",
    "learn":"o'rganmoq"
}

# ==========================================
# MATEMATIKA
# ==========================================

OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow
}

def calculate(expression):
    expression = expression.replace("^", "**")
    tree = ast.parse(expression, mode="eval")

    def solve(node):
        if isinstance(node, ast.Expression):
            return solve(node.body)

        if isinstance(node, ast.Constant):
            if type(node.value) in (int, float):
                return node.value

        if isinstance(node, ast.BinOp):
            if type(node.op) in OPS:
                a = solve(node.left)
                b = solve(node.right)
                if isinstance(node.op, ast.Pow) and abs(b) > 10:
                    raise ValueError()
                return OPS[type(node.op)](a, b)

        if isinstance(node, ast.UnaryOp):
            if isinstance(node.op, ast.USub):
                return -solve(node.operand)
            if isinstance(node.op, ast.UAdd):
                return solve(node.operand)

        raise ValueError()

    return solve(tree)

# ==========================================
# OB-HAVO
# ==========================================

def weather(city):
    aliases = {
        "mangit": "Mangit, Uzbekistan",
        "mang'it": "Mangit, Uzbekistan",
        "mang‘it": "Mangit, Uzbekistan",
        "toshkent": "Tashkent, Uzbekistan"
    }

    city = aliases.get(city.lower().strip(), city)

    r = S.get(
        "https://geocoding-api.open-meteo.com/v1/search",
        params={"name": city, "count": 1},
        timeout=TIMEOUT
    )
    r.raise_for_status()

    places = r.json().get("results", [])

    if not places:
        return "Shahar topilmadi. Nomini tekshiring."

    p = places[0]

    r = S.get(
        "https://api.open-meteo.com/v1/forecast",
        params={
            "latitude": p["latitude"],
            "longitude": p["longitude"],
            "current": "temperature_2m,relative_humidity_2m,apparent_temperature,wind_speed_10m,weather_code",
            "timezone": "auto"
        },
        timeout=TIMEOUT
    )
    r.raise_for_status()

    c = r.json()["current"]

    descriptions = {
        0: "Ochiq osmon",
        1: "Asosan ochiq",
        2: "Qisman bulutli",
        3: "Bulutli",
        45: "Tuman",
        51: "Yengil yomg'ir",
        61: "Yomg'ir",
        63: "Yomg'ir",
        65: "Kuchli yomg'ir",
        71: "Qor",
        73: "Qor",
        75: "Kuchli qor",
        95: "Momaqaldiroq"
    }

    status = descriptions.get(c["weather_code"], "Ob-havo ma'lumoti")

    return f"""
🌤️ **{p['name']}**

Holat: {status}

🌡️ Harorat: {c['temperature_2m']} °C

🤔 His qilinishi: {c['apparent_temperature']} °C

💧 Namlik: {c['relative_humidity_2m']}%

💨 Shamol: {c['wind_speed_10m']} km/soat

Manba: Open-Meteo
"""

# ==========================================
# TARJIMA
# ==========================================

def translate(text, target="uz"):
    r = S.get(
        "https://api.mymemory.translated.net/get",
        params={
            "q": text[:450],
            "langpair": "auto|" + target
        },
        timeout=TIMEOUT
    )
    r.raise_for_status()
    data = r.json()

    result = data.get("responseData", {}).get("translatedText")

    if not result:
        return "Tarjima topilmadi."

    return result

# ==========================================
# WIKIPEDIA
# ==========================================

def wiki(query, lang="uz"):
    r = S.get(
        f"https://{lang}.wikipedia.org/w/api.php",
        params={
            "action": "query",
            "generator": "search",
            "gsrsearch": query,
            "gsrlimit": 1,
            "prop": "extracts",
            "exintro": 1,
            "explaintext": 1,
            "format": "json"
        },
        timeout=TIMEOUT
    )
    r.raise_for_status()

    pages = r.json().get("query", {}).get("pages", {})

    if not pages:
        return "Wikipedia'da ma'lumot topilmadi."

    page = next(iter(pages.values()))
    result = page.get("extract", "")

    return f"📚 **{page['title']}**\n\n{result[:1800]}"

# ==========================================
# SHERZOD AI JAVOB TIZIMI
# ==========================================

def sherzod_ai(question):
    q = question.strip()
    low = q.lower()

    if not q:
        return "Savolingizni yozing."

    # SALOMLASHISH
    if any(x in low for x in [
        "salom", "assalomu alaykum",
        "привет", "здравствуйте", "hello", "hi"
    ]):
        return "Salom! 😊 Men Sherzod AI Assistant 1.0man. Qanday yordam beray?"

    # YARATUVCHI
    if any(x in low for x in [
        "seni kim yarat", "kim yaratgan",
        "who made you", "creator"
    ]):
        return "Meni Fayzullayev Sherzodbek yaratgan! 🤖"

    # ISM
    if any(x in low for x in [
        "isming nima", "what is your name",
        "как тебя зовут"
    ]):
        return "Mening ismim Sherzod AI Assistant 1.0."

    # YORDAM
    if any(x in low for x in ["yordam", "help", "nima qila olasan"]):
        return """
Men quyidagilarni bajara olaman:

1. Tarjima
2. Matematika
3. Ob-havo
4. Vaqt va sana
5. Wikipedia qidiruvi
6. Qiziqarli faktlar
7. Hazillar
8. Motivatsiya
9. Inglizcha lug'at
10. Ruscha lug'at

Buyruqlar:
`ob-havo Toshkent`
`tarjima: hello`
`hisobla: 25*4`
`wiki: Amir Temur`
"""

    # VAQT
    if any(x in low for x in ["soat", "vaqt", "time", "время"]):
        now = datetime.now(ZoneInfo("Asia/Tashkent"))
        return "🕒 Toshkent vaqti: " + now.strftime("%H:%M:%S")

    # SANA
    if any(x in low for x in ["sana", "date", "число"]):
        now = datetime.now(ZoneInfo("Asia/Tashkent"))
        return "📅 Sana: " + now.strftime("%d.%m.%Y")

    # OB-HAVO
    if any(x in low for x in ["ob-havo", "ob havo", "weather", "погода"]):
        city = q

        for word in [
            "ob-havo", "ob havo", "weather in",
            "weather", "погода в", "погода"
        ]:
            city = city.replace(word, "").strip(" :,-")

        if not city:
            city = "Toshkent"

        try:
            return weather(city)
        except Exception:
            return "Ob-havo xizmati ishlamayapti. Internetni tekshiring."

    # MATEMATIKA
    if low.startswith(("hisobla:", "calculate:", "вычисли:")):
        expression = q.split(":", 1)[1].strip()

        try:
            return "🧮 Javob: " + str(calculate(expression))
        except ZeroDivisionError:
            return "Nolga bo'lish mumkin emas."
        except Exception:
            return "Misolni tekshiring. Masalan: hisobla: 25*4"

    # ODDIY MATEMATIK MISOL
    candidate = q.replace(" ", "")

    if candidate and any(x in candidate for x in "+*/%^"):
        if all(x.isdigit() or x in ".+-*/%^()" for x in candidate):
            try:
                return "🧮 Javob: " + str(calculate(candidate))
            except Exception:
                return "Matematik misolni tushunmadim."

    # TARJIMA
    if low.startswith(("tarjima:", "translate:", "перевод:")):
        phrase = q.split(":", 1)[1].strip()

        if phrase.lower() in RU:
            return "🇷🇺 " + phrase + " = " + RU[phrase.lower()]

        if phrase.lower() in EN:
            return "🇬🇧 " + phrase + " = " + EN[phrase.lower()]

        try:
            return "🌐 Tarjima: " + translate(phrase)
        except Exception:
            return "Tarjima xizmati hozir ishlamayapti."

    # LUG'AT
    if low in RU:
        return "🇷🇺 " + q + " = " + RU[low]

    if low in EN:
        return "🇬🇧 " + q + " = " + EN[low]

    # WIKIPEDIA
    if low.startswith(("wiki:", "wikipedia:")):
        topic = q.split(":", 1)[1].strip()

        if not topic:
            return "Mavzuni yozing."

        lang = "ru" if any("\u0400" <= x <= "\u04ff" for x in topic) else "uz"

        try:
            return wiki(topic, lang)
        except Exception:
            return "Wikipedia bilan aloqa yo'q."

    # FAKTLAR
    if any(x in low for x in [
        "fakt", "qiziqarli ma'lumot", "interesting fact", "факт"
    ]):
        return "💡 " + random.choice(FACTS)

    # HAZIL
    if any(x in low for x in ["hazil", "joke", "шутка", "kuld"]):
        return "😂 " + random.choice(JOKES)

    # MOTIVATSIYA
    if any(x in low for x in ["motivatsiya", "ruh ber", "motivation"]):
        return "🌟 " + random.choice(MOTIVATION)

    # SUHBAT
    if any(x in low for x in ["rahmat", "спасибо", "thanks"]):
        return "Arzimaydi! 😊"

    if any(x in low for x in ["qalaysan", "как дела", "how are you"]):
        return "Yaxshi, rahmat! Sizchi? 😊"

    if any(x in low for x in ["xayr", "пока", "goodbye", "bye"]):
        return "Xayr! Yaxshi kun tilayman! 👋"

    if "python" in low:
        return "Python — dasturlash tili. U bilan sayt, dastur va botlar yaratish mumkin."

    if any(x in low for x in ["blockpost", "fc mobile", "fifa", "minecraft"]):
        return "🎮 O'yin haqida yordam beraman. Savolingizni batafsil yozing."

    return """
Savolingizni tushundim, ammo hozircha aniq javob topolmadim.

Quyidagilarni sinab ko'ring:

- `ob-havo Mangit`
- `tarjima: hello`
- `hisobla: 125*8`
- `wiki: Amir Temur`
- `qiziqarli fakt`
- `hazil ayt`
- `motivatsiya`
"""

# ==========================================
# SIDEBAR
# ==========================================

with st.sidebar:
    st.title("⚙️ SHERZOD AI")

    st.write("Assistant 1.0")

    if st.button("🗑️ Suhbatni tozalash"):
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")
    st.write("**Buyruqlar:**")

    st.code("""
ob-havo Toshkent
soat nechchi?
tarjima: hello
hisobla: 25*4
wiki: Amir Temur
qiziqarli fakt
hazil ayt
motivatsiya
""")

# ==========================================
# CHAT OYNASI
# ==========================================

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Assalomu alaykum! 🤖 Men Sherzod AI Assistant 1.0man. Savolingizni yozing!"
        }
    ]

st.subheader("💬 Sherzod AI bilan suhbat")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.chat_input("Savolingizni yozing...")

if prompt:
    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Sherzod AI o'ylayapti..."):
            response = sherzod_ai(prompt)

        st.markdown(response)

    st.session_state.messages.append({
        "role": "assistant",
        "content": response
    })

st.markdown("---")
st.caption("SHERZOD AI ASSISTANT 1.0 | Fayzullayev Sherzodbek")
