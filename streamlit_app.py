
import streamlit as st
import requests
import random
import ast
import operator
import string
from datetime import datetime
from zoneinfo import ZoneInfo
from urllib.parse import quote

# ==========================================
# SHERZOD AI ASSISTANT
# Creator: Fayzullayev Sherzodbek
# ==========================================

st.set_page_config(
    page_title="Sherzod AI Assistant",
    page_icon="🤖",
    layout="wide"
)

# ---------- DIZAYN ----------

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg,#07111f,#101e38);
    color: white;
}
h1,h2,h3,p,label {
    color: white !important;
}
.stChatMessage {
    background: #172943;
    border-radius: 15px;
}
.stButton button {
    background: #183b66;
    color: white;
    border-radius: 12px;
    border: 1px solid #3974ad;
}
.stButton button:hover {
    background: #28609a;
    color: white;
}
</style>
""", unsafe_allow_html=True)

# ---------- SOZLAMALAR ----------

FACTS = [
    "Ahtapotning uchta yuragi bor.",
    "Yorug'lik Quyoshdan Yerga taxminan 8 daqiqada yetadi.",
    "Venerada bir kun uning yilidan uzunroq.",
    "Asalarilar raqs orqali ma'lumot uzatadi.",
    "Kitlar tovushlar yordamida aloqa qiladi.",
    "Inson tanasidagi eng katta organ teridir.",
    "Pingvinlar ucha olmaydigan qushlardir.",
    "Saturnning zichligi suvnikidan kichik.",
    "Oy Yerning tabiiy yo'ldoshidir.",
    "Suvning kimyoviy formulasi H2O."
]

JOKES = [
    "Kompyuter nega sovqotmaydi? Chunki Windows oynalari bor! 😄",
    "Dasturchi choy ichsa nima deydi? Java kerak!",
    "Telefon nega uxlamaydi? Chunki doim zaryad kutadi!",
    "Kitob nega xafa? Chunki uni hech kim varaqlamayapti."
]

MOTIVATION = [
    "Har bir katta natija kichik qadamdan boshlanadi!",
    "Xatolar o'rganishning bir qismidir.",
    "Bugungi harakating ertangi natijangni yaratadi.",
    "Bilim olishdan hech qachon to'xtama!",
    "Maqsading sari sabr bilan harakat qil."
]

WORDS = {
    "hello": "Salom",
    "hi": "Salom",
    "good morning": "Xayrli tong",
    "good night": "Xayrli tun",
    "thank you": "Rahmat",
    "please": "Iltimos",
    "friend": "Do'st",
    "beautiful": "Chiroyli",
    "school": "Maktab",
    "book": "Kitob",
    "water": "Suv",
    "apple": "Olma",
    "привет": "Salom",
    "здравствуйте": "Assalomu alaykum",
    "спасибо": "Rahmat",
    "пожалуйста": "Iltimos",
    "друг": "Do'st",
    "красивый": "Chiroyli",
    "школа": "Maktab",
    "книга": "Kitob",
    "вода": "Suv",
    "пока": "Xayr",
    "ладно": "Mayli",
    "хватит": "Yetar",
    "добрый": "Mehribon",
    "злой": "Jahldor"
}

# ---------- KALKULYATOR ----------

OPERATIONS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos
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

            if isinstance(node, ast.BinOp):
                operation = OPERATIONS.get(type(node.op))
                if operation is None:
                    raise ValueError()

                left = solve(node.left)
                right = solve(node.right)

                if isinstance(node.op, ast.Pow) and abs(right) > 100:
                    raise ValueError()

                result = operation(left, right)

                if abs(result) > 10**100:
                    raise ValueError()

                return result

            if isinstance(node, ast.UnaryOp):
                operation = OPERATIONS.get(type(node.op))
                if operation is None:
                    raise ValueError()
                return operation(solve(node.operand))

            raise ValueError()

        return solve(tree)

    except ZeroDivisionError:
        return "Nolga bo'lish mumkin emas."
    except Exception:
        return "Misol xato. Masalan: 25+15*2"

# ---------- VAQT VA SANA ----------

def get_time():
    return datetime.now(
        ZoneInfo("Asia/Tashkent")
    ).strftime("%H:%M:%S")

def get_date():
    return datetime.now(
        ZoneInfo("Asia/Tashkent")
    ).strftime("%d.%m.%Y")

# ---------- OB-HAVO ----------

def weather(city):
    try:
        url = (
            "https://geocoding-api.open-meteo.com/v1/search"
            f"?name={quote(city)}&count=1&language=uz"
        )
        response = requests.get(url, timeout=12)
        response.raise_for_status()

        places = response.json().get("results", [])

        if not places:
            return "Shahar topilmadi."

        place = places[0]

        url = (
            "https://api.open-meteo.com/v1/forecast"
            f"?latitude={place['latitude']}"
            f"&longitude={place['longitude']}"
            "&current=temperature_2m,relative_humidity_2m,"
            "apparent_temperature,wind_speed_10m"
        )

        response = requests.get(url, timeout=12)
        response.raise_for_status()

        data = response.json()["current"]

        return (
            f"🌍 Shahar: {place['name']}\n"
            f"🌡 Harorat: {data['temperature_2m']} °C\n"
            f"🤗 His qilinadigan harorat: "
            f"{data['apparent_temperature']} °C\n"
            f"💧 Namlik: {data['relative_humidity_2m']}%\n"
            f"💨 Shamol: {data['wind_speed_10m']} km/soat"
        )

    except requests.RequestException:
        return "Ob-havo xizmatiga ulanib bo'lmadi."
    except Exception:
        return "Ob-havo ma'lumotida xatolik."

# ---------- TARJIMON ----------

def translate(text, language):
    try:
        url = "https://api.mymemory.translated.net/get"
        params = {
            "q": text,
            "langpair": language
        }

        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()

        data = response.json()

        if data.get("responseStatus") == 200:
            return data["responseData"]["translatedText"]

        return "Tarjima topilmadi."

    except Exception:
        return "Tarjima xizmatiga ulanib bo'lmadi."

# ---------- WIKIPEDIA ----------

def wiki(query, language="uz"):
    try:
        url = (
            f"https://{language}.wikipedia.org/w/api.php"
            "?action=query&generator=search&gsrsearch="
            f"{quote(query)}&gsrlimit=1&prop=extracts"
            "&exintro=1&explaintext=1&format=json"
        )

        response = requests.get(
            url,
            headers={"User-Agent": "SherzodAI/1.0"},
            timeout=15
        )
        response.raise_for_status()

        pages = response.json().get("query", {}).get("pages", {})

        if not pages:
            return None

        page = next(iter(pages.values()))
        return page.get("extract", "")[:2000] or None

    except Exception:
        return None

# ---------- VALYUTA ----------

def currency():
    try:
        url = "https://open.er-api.com/v6/latest/USD"
        response = requests.get(url, timeout=12)
        response.raise_for_status()

        data = response.json()

        if data.get("result") != "success":
            return "Valyuta xizmati ishlamadi."

        rates = data["rates"]

        return (
            "💱 Valyuta ma'lumoti:\n"
            f"1 USD = {rates['UZS']} UZS\n"
            f"1 USD = {rates['EUR']} EUR\n"
            f"1 USD = {rates['RUB']} RUB\n"
            f"1 USD = {rates['GBP']} GBP\n\n"
            "Kurslar o'zgarib turadi."
        )

    except Exception:
        return "Valyuta ma'lumotini olish imkoni bo'lmadi."

# ---------- TASODIFIY PAROL ----------

def make_password():
    alphabet = string.ascii_letters + string.digits + "!@#$%&*"
    return "".join(random.SystemRandom().choice(alphabet) for _ in range(16))

# ---------- O'YIN ----------

def start_game():
    st.session_state.secret_number = random.randint(1, 100)
    st.session_state.game_active = True
    return "🎮 1 dan 100 gacha son o'yladim. Uni toping!"

def guess_number(text):
    try:
        number = int(text)

        if not st.session_state.get("game_active", False):
            return "Avval `son top` deb yozing."

        secret = st.session_state.secret_number

        if number == secret:
            st.session_state.game_active = False
            return "🎉 To'g'ri! Siz sonni topdingiz!"

        if number < secret:
            return "Kattaroq son ayting! ⬆️"

        return "Kichikroq son ayting! ⬇️"

    except ValueError:
        return "Iltimos, butun son kiriting."

# ---------- TEST ----------

def quiz():
    questions = [
        ("O'zbekiston poytaxti?", ["Toshkent", "Samarqand", "Buxoro"], 0),
        ("Yerning tabiiy yo'ldoshi?", ["Mars", "Oy", "Quyosh"], 1),
        ("5*5 nechchi?", ["20", "25", "30"], 1),
        ("Suv formulasi?", ["CO2", "H2O", "O2"], 1),
        ("Python nima?", ["Dasturlash tili", "Hayvon", "Shahar"], 0)
    ]

    question, options, answer = random.choice(questions)

    return (
        f"🧠 Savol: {question}\n"
        f"A) {options[0]}\n"
        f"B) {options[1]}\n"
        f"C) {options[2]}\n"
        f"Javobni A, B yoki C ko'rinishida yozing."
    )

# ---------- MATN YORDAMCHISI ----------

def write_text(topic):
    return (
        f"📝 {topic} mavzusida matn yozish uchun reja:\n"
        "1. Kirish va mavzuni tanishtirish.\n"
        "2. Asosiy fikrlar va misollar.\n"
        "3. Mavzuning ahamiyati.\n"
        "4. Xulosa.\n\n"
        "Mavzu haqida qo'shimcha ma'lumot bersangiz, "
        "matnni batafsilroq tuzaman."
    )

# ---------- KUNLIK REJA ----------

def daily_plan():
    return (
        "📅 KUNLIK REJA\n\n"
        "08:00 — Uyg'onish va nonushta\n"
        "09:00 — Dars va bilim olish\n"
        "11:00 — Tanaffus\n"
        "12:00 — Muhim vazifalar\n"
        "14:00 — Tushlik\n"
        "15:00 — Yangi ko'nikma o'rganish\n"
        "17:00 — Dam olish\n"
        "19:00 — Uy vazifalari\n"
        "21:00 — Ertangi kunga tayyorgarlik"
    )

# ---------- ASOSIY SHERZOD AI ----------

def sherzod_ai(question):
    q = question.strip()
    low = q.lower()

    if not q:
        return "Savolingizni yozing."

    # Salomlashish
    greetings = [
        "salom", "assalomu alaykum", "assalom",
        "привет", "здравствуйте", "hello", "hi"
    ]

    if low in greetings or low.startswith("salom "):
        return (
            "Assalomu alaykum! 😊\n\n"
            "Men Sherzod AI Assistantman. Siz bilan "
            "suhbatlashishga tayyorman!\n"
            "Bugun qanday yangiliklar bor? Nima haqida "
            "gaplashamiz: texnologiya, bilim, o'yin yoki boshqa mavzumi?"
        )

    if any(x in low for x in ["qalaysan", "yaxshimisan", "как дела", "how are you"]):
        return "Rahmat! Men ishlashga tayyorman. 😊 Sizning ishlaringiz qalay?"

    if any(x in low for x in ["xayr", "до свидания", "goodbye", "bye"]):
        return "Xayr! Kuningiz yaxshi o'tsin! 👋"

    if any(x in low for x in ["rahmat", "спасибо", "thank you"]):
        return "Arzimaydi! 😊 Yana yordam kerak bo'lsa yozing."

    if any(x in low for x in ["kimsan", "isming nima", "who are you", "кто ты"]):
        return (
            "Men Sherzod AI Assistant 1.0man. 🤖\n"
            "Mening yaratuvchim: Fayzullayev Sherzodbek."
        )

    if any(x in low for x in ["kim yaratgan", "yaratuvching", "creator"]):
        return "Meni Fayzullayev Sherzodbek loyihasi sifatida yaratgan."

    if low in ["yordam", "help", "помощь"]:
        return (
            "🤖 SHERZOD AI BUYRUQLARI\n\n"
            "salom — suhbat\n"
            "soat — vaqt\n"
            "sana — sana\n"
            "ob-havo Toshkent — ob-havo\n"
            "tarjima: — tarjima yo'nalishlari\n"
            "uz-en: Salom — inglizchaga tarjima\n"
            "uz-ru: Salom — ruschaga tarjima\n"
            "en-uz: Hello — o'zbekchaga tarjima\n"
            "ru-uz: Привет — o'zbekchaga tarjima\n"
            "wiki: O'zbekiston — ma'lumot\n"
            "valyuta — valyuta kurslari\n"
            "hisobla: 25+25 — hisoblash\n"
            "fakt — qiziqarli fakt\n"
            "hazil — hazil\n"
            "motivatsiya — motivatsiya\n"
            "topishmoq — topishmoq\n"
            "son top — o'yin\n"
            "test — bilim testi\n"
            "parol — tasodifiy parol\n"
            "reja — kunlik reja\n"
            "matn: mavzu — matn rejasi\n"
            "soz: hello — lug'at\n"
            "kod — Python haqida"
        )

    if "soat" in low or "vaqt" in low or "time" in low:
        return f"🕒 Toshkent vaqti: {get_time()}"

    if "sana" in low or "date" in low:
        return f"📅 Sana: {get_date()}"

    if any(x in low for x in ["ob-havo", "ob havo", "weather", "погода"]):
        city = "Toshkent"

        for name in [
            "mangit", "mang'it", "samarqand", "buxoro",
            "andijon", "namangan", "fargona", "qarshi",
            "nukus", "urganch"
        ]:
            if name in low:
                city = name
                break

        return weather(city)

    if low.startswith("uz-en:"):
        return translate(q[6:].strip(), "uz|en")

    if low.startswith("uz-ru:"):
        return translate(q[6:].strip(), "uz|ru")

    if low.startswith("en-uz:"):
        return translate(q[6:].strip(), "en|uz")

    if low.startswith("ru-uz:"):
        return translate(q[6:].strip(), "ru|uz")

    if low.startswith("tarjima:"):
        return (
            "Tarjima buyruqlari:\n"
            "uz-en: Salom\n"
            "uz-ru: Salom\n"
            "en-uz: Hello\n"
            "ru-uz: Привет"
        )

    if low.startswith("wiki:") or low.startswith("qidir:"):
        search_query = q.split(":", 1)[1].strip()

        if not search_query:
            return "Qidiruv so'zini ham yozing."

        result = wiki(search_query, "uz")

        if not result:
            result = wiki(search_query, "ru")

        return result or "Wikipedia'da ma'lumot topilmadi."

    if low == "valyuta":
        return currency()

    if low.startswith("hisobla:"):
        return f"🧮 Natija: {calculate(q.split(':', 1)[1].strip())}"

    if low.startswith("soz:") or low.startswith("so'z:"):
        word = q.split(":", 1)[1].strip().lower()
        return WORDS.get(word, "Bu so'z lug'atimda hozircha yo'q.")

    if low in WORDS:
        return WORDS[low]

    if low == "fakt" or "qiziqarli fakt" in low:
        return "💡 " + random.choice(FACTS)

    if low == "hazil" or "hazil ayt" in low:
        return "😂 " + random.choice(JOKES)

    if low == "motivatsiya":
        return "⭐ " + random.choice(MOTIVATION)

    if low == "topishmoq":
        return (
            "🧩 Topishmoq:\n"
            "O'zi yurmaydi, lekin odamlarni olib yuradi. Bu nima?\n"
            "Javobini topishga harakat qiling!"
        )

    if low == "parol":
        return "🔐 Tasodifiy parol namunasi:\n" + make_password()

    if low == "son top":
        return start_game()

    if st.session_state.get("game_active", False) and low.isdigit():
        return guess_number(low)

    if low == "test":
        return quiz()

    if low.startswith("matn:"):
        topic = q.split(":", 1)[1].strip()
        return write_text(topic) if topic else "Matn mavzusini yozing."

    if low == "reja":
        return daily_plan()

    if low == "kod":
        return (
            "💻 Python — o'rganish uchun qulay dasturlash tili.\n"
            "Misol:\n"
            "print('Salom, Sherzod AI!')\n\n"
            "Bu kod ekranga salom chiqaradi."
        )

    if "python" in low:
        return (
            "Python — dasturlash tili. U sun'iy intellekt, "
            "saytlar, avtomatlashtirish va ma'lumotlar "
            "bilan ishlashda qo'llanadi."
        )

    if "internet" in low:
        return (
            "Internet — dunyo bo'ylab qurilmalarni "
            "bog'laydigan global tarmoq."
        )

    if "sevgi" in low:
        return "Sevgi — hurmat, ishonch va mehrga asoslangan tuyg'u."

    if "zerik" in low:
        return "Keling, fakt, hazil yoki topishmoq bilan kayfiyatni ko'taramiz!"

    # Oddiy hisoblash
    allowed = set("0123456789+-*/().% ")
    if any(ch.isdigit() for ch in q) and all(ch in allowed for ch in q):
        return f"🧮 Natija: {calculate(q)}"

    # Wikipedia orqali umumiy qidiruv
    result = wiki(q, "uz")

    if result:
        return "📚 Topilgan ma'lumot:\n\n" + result

    return (
        "Savolingizni tushunishga harakat qilyapman. 🤖\n\n"
        "Iltimos, savolni biroz boshqacharoq yozing "
        "yoki `yordam` buyrug'ini yuboring."
    )

# ==========================================
# CHAT INTERFEYSI
# ==========================================

st.title("🤖 SHERZOD AI")
st.subheader("Assistant 1.0")
st.caption("Yaratuvchi: Fayzullayev Sherzodbek")

st.markdown(
    "Salom! Men Sherzod AI. Savollaringizga yordam berishga tayyorman."
)

if "messages" not in st.session_state:
    st.session_state.messages = []

if "game_active" not in st.session_state:
    st.session_state.game_active = False

with st.sidebar:
    st.title("⚙️ Boshqaruv")

    st.write("Sherzod AI Assistant 1.0")

    st.divider()

    if st.button("🗑 Suhbatni tozalash"):
        st.session_state.messages = []
        st.session_state.game_active = False
        st.rerun()

    st.subheader("📌 Buyruqlar")
    st.code(
        "yordam\n"
        "salom\n"
        "soat\n"
        "sana\n"
        "ob-havo Toshkent\n"
        "valyuta\n"
        "uz-en: Salom\n"
        "uz-ru: Salom\n"
        "en-uz: Hello\n"
        "ru-uz: Привет\n"
        "wiki: O'zbekiston\n"
        "hisobla: 25+15*2\n"
        "fakt\n"
        "hazil\n"
        "motivatsiya\n"
        "topishmoq\n"
        "son top\n"
        "test\n"
        "parol\n"
        "reja\n"
        "matn: Texnologiya\n"
        "soz: hello\n"
        "kod"
    )

    st.divider()
    st.caption("© Sherzod AI Assistant")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.chat_input("Sherzod AI ga savol yozing...")

if prompt:
    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            with st.spinner("Sherzod AI o'ylayapti..."):
                response = sherzod_ai(prompt)
        except Exception:
            response = (
                "Kutilmagan xatolik yuz berdi. "
                "Iltimos, qayta urinib ko'ring."
            )

        st.markdown(response)

    st.session_state.messages.append({
        "role": "assistant",
        "content": response
    })
