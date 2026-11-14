
import streamlit as st
import requests
import ast
import operator
import random
import re
import difflib
from datetime import datetime
from urllib.parse import quote

# =========================================================
# SWER.AI 1.0
# Creator: Fayzullayev Sherzodbek
# Free edition - No paid AI API required
# =========================================================

st.set_page_config(
    page_title="SWER.AI",
    page_icon="👑",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------- DESIGN --------------------

st.markdown("""
<style>
.stApp {
    background: #080808;
    color: #eeeeee;
}
[data-testid="stSidebar"] {
    background: #111111;
    border-right: 1px solid #333333;
}
h1, h2, h3 {
    color: #e5e5e5 !important;
}
p, label, span {
    color: #eeeeee;
}
.stChatMessage {
    background: #151515;
    border: 1px solid #303030;
    border-radius: 15px;
}
.stButton > button {
    background: #222222;
    color: white;
    border: 1px solid #777777;
    border-radius: 10px;
}
.stButton > button:hover {
    background: #444444;
    border-color: white;
}
textarea, input {
    background: #151515 !important;
    color: white !important;
}
hr {
    border-color: #333333;
}
</style>
""", unsafe_allow_html=True)

# -------------------- SETTINGS --------------------

APP_NAME = "SWER.AI"
VERSION = "1.0"

LANGUAGES = {
    "O‘zbekcha": "uz",
    "Русский": "ru",
    "English": "en"
}

DEFAULTS = {
    "messages": [],
    "language": "uz",
    "user_name": "",
    "last_topic": "",
    "last_answer": "",
    "chat_count": 0
}

for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value

# -------------------- KNOWLEDGE BASE --------------------

KNOWLEDGE = {
    "sun": {
        "keywords": ["quyosh", "sun", "солнце"],
        "answer": (
            "Quyosh — Quyosh sistemasining markazidagi yulduz. "
            "U Yerga yorug‘lik va issiqlik beradi. "
            "Quyosh asosan vodorod va geliydan tashkil topgan."
        )
    },
    "earth": {
        "keywords": ["yer", "earth", "земля"],
        "answer": (
            "Yer — Quyosh sistemasidagi uchinchi sayyora. "
            "Uning tabiiy yo‘ldoshi Oy. Yerda hayot mavjud."
        )
    },
    "moon": {
        "keywords": ["oy", "moon", "луна"],
        "answer": (
            "Oy — Yerning tabiiy yo‘ldoshi. "
            "U o‘zidan yorug‘lik chiqarmaydi, Quyosh nurini qaytaradi."
        )
    },
    "water": {
        "keywords": ["suv", "water", "вода"],
        "answer": (
            "Suvning kimyoviy formulasi H2O. "
            "U ikki vodorod va bir kislorod atomidan tashkil topgan."
        )
    },
    "python": {
        "keywords": ["python", "питон"],
        "answer": (
            "Python — sodda va kuchli dasturlash tili. "
            "U sun’iy intellekt, veb-dasturlash, avtomatlashtirish "
            "va ma’lumotlar tahlilida ishlatiladi."
        )
    },
    "ai": {
        "keywords": [
            "suniy intellekt",
            "sun'iy intellekt",
            "artificial intelligence",
            "искусственный интеллект"
        ],
        "answer": (
            "Sun’iy intellekt — kompyuter tizimlarining "
            "ma’lumotlarni tahlil qilish, o‘rganish va vazifalarni "
            "bajarish imkoniyatidir."
        )
    },
    "uzbekistan": {
        "keywords": ["o'zbekiston", "uzbekiston", "узбекистан"],
        "answer": (
            "O‘zbekiston — Markaziy Osiyoda joylashgan davlat. "
            "Poytaxti Toshkent. Davlat tili — o‘zbek tili."
        )
    },
    "computer": {
        "keywords": ["kompyuter", "computer", "компьютер"],
        "answer": (
            "Kompyuter — ma’lumotlarni qabul qilish, qayta ishlash "
            "va saqlash uchun mo‘ljallangan elektron qurilma."
        )
    },
    "internet": {
        "keywords": ["internet", "интернет"],
        "answer": (
            "Internet — dunyo bo‘ylab kompyuter va qurilmalarni "
            "bog‘laydigan global tarmoq."
        )
    },
    "history": {
        "keywords": ["tarix", "history", "история"],
        "answer": (
            "Tarix — insoniyatning o‘tmishi, davlatlar, xalqlar, "
            "madaniyatlar va muhim voqealarni o‘rganuvchi fan."
        )
    },
    "geography": {
        "keywords": ["geografiya", "geography", "география"],
        "answer": (
            "Geografiya — Yer yuzasi, tabiat, aholi, davlatlar "
            "va iqtisodiy hududlarni o‘rganuvchi fan."
        )
    },
    "biology": {
        "keywords": ["biologiya", "biology", "биология"],
        "answer": (
            "Biologiya — tirik organizmlar, ularning tuzilishi, "
            "rivojlanishi va yashash jarayonlarini o‘rganuvchi fan."
        )
    },
    "physics": {
        "keywords": ["fizika", "physics", "физика"],
        "answer": (
            "Fizika — tabiatdagi hodisalar, energiya, harakat, "
            "kuch, yorug‘lik va moddalarni o‘rganuvchi fan."
        )
    },
    "chemistry": {
        "keywords": ["kimyo", "chemistry", "химия"],
        "answer": (
            "Kimyo — moddalarning tarkibi, tuzilishi, xususiyatlari "
            "va o‘zgarishlarini o‘rganuvchi fan."
        )
    },
    "space": {
        "keywords": ["koinot", "space", "космос"],
        "answer": (
            "Koinot — sayyoralar, yulduzlar, galaktikalar, "
            "gaz va boshqa kosmik jismlarni o‘z ichiga olgan ulkan makon."
        )
    },
    "mars": {
        "keywords": ["mars", "марс"],
        "answer": (
            "Mars — Quyosh sistemasidagi to‘rtinchi sayyora. "
            "U Qizil sayyora deb ham ataladi."
        )
    },
    "football": {
        "keywords": ["futbol", "football", "футбол"],
        "answer": (
            "Futbol — ikki jamoa o‘rtasida o‘ynaladigan sport turi. "
            "Har bir jamoada maydonda 11 nafargacha futbolchi bo‘ladi."
        )
    },
    "chess": {
        "keywords": ["shaxmat", "chess", "шахматы"],
        "answer": (
            "Shaxmat — ikki kishi o‘ynaydigan strategik stol o‘yini. "
            "Maqsad raqib qiroliga mot qo‘yish."
        )
    },
    "book": {
        "keywords": ["kitob", "book", "книга"],
        "answer": (
            "Kitob — bilim, hikoya va ma’lumotlarni yozma shaklda "
            "saqlash va tarqatish vositasi."
        )
    }
}

EXTRA_KNOWLEDGE = {
    "gravity": "Gravitatsiya — jismlarning bir-birini tortish hodisasi.",
    "atom": "Atom — kimyoviy elementning xususiyatlarini saqlovchi eng kichik zarracha.",
    "molecule": "Molekula — ikki yoki undan ortiq atomdan tashkil topgan zarracha.",
    "galaxy": "Galaktika — yulduzlar, gaz, chang va boshqa jismlardan tashkil topgan ulkan tizim.",
    "algorithm": "Algoritm — vazifani bajarish uchun ketma-ket ko‘rsatmalar majmuasi.",
    "database": "Ma’lumotlar bazasi — tartiblangan ma’lumotlar to‘plami.",
    "html": "HTML — veb-sahifalarning tuzilishini yaratish uchun ishlatiladigan belgilash tili.",
    "css": "CSS — veb-sahifalarning ko‘rinishini bezash uchun ishlatiladi.",
    "javascript": "JavaScript — veb-sahifalarga interaktivlik qo‘shuvchi dasturlash tili.",
    "cpu": "CPU — kompyuterning markaziy protsessori.",
    "ram": "RAM — kompyuter ishlayotgan paytda ma’lumotlarni vaqtincha saqlaydigan xotira.",
    "gpu": "GPU — grafik hisoblash va tasvirlarni qayta ishlash uchun protsessor."
}

# -------------------- UTILITIES --------------------

def clean_text(text):
    text = str(text).lower().strip()
    text = re.sub(r"\s+", " ", text)
    return text


def current_time():
    return datetime.now().strftime("%H:%M")


def current_date():
    return datetime.now().strftime("%d.%m.%Y")


def contains_any(text, words):
    return any(word in text for word in words)


def save_topic(topic):
    st.session_state.last_topic = topic


def save_answer(answer):
    st.session_state.last_answer = answer
    return answer


# -------------------- SAFE CALCULATOR --------------------

OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos
}


def safe_calculate(expression):
    expression = expression.replace(",", ".")
    tree = ast.parse(expression, mode="eval")

    def evaluate(node):
        if isinstance(node, ast.Expression):
            return evaluate(node.body)

        if isinstance(node, ast.Constant):
            if type(node.value) in (int, float):
                return node.value
            raise ValueError("Faqat sonlardan foydalaning.")

        if isinstance(node, ast.BinOp):
            op_type = type(node.op)
            if op_type not in OPERATORS:
                raise ValueError("Bu amal qo‘llab-quvvatlanmaydi.")

            left = evaluate(node.left)
            right = evaluate(node.right)

            if op_type is ast.Pow and abs(right) > 10:
                raise ValueError("Daraja juda katta.")

            result = OPERATORS[op_type](left, right)

            if isinstance(result, complex):
                raise ValueError("Kompleks sonlar qo‘llanmaydi.")

            if abs(result) > 10**100:
                raise ValueError("Natija juda katta.")

            return result

        if isinstance(node, ast.UnaryOp):
            op_type = type(node.op)
            if op_type not in OPERATORS:
                raise ValueError("Bu amal qo‘llab-quvvatlanmaydi.")
            return OPERATORS[op_type](evaluate(node.operand))

        raise ValueError("Ifoda noto‘g‘ri.")

    return evaluate(tree)


def calculator_answer(text):
    match = re.search(
        r"(?:hisobla|calculate|сколько|hisoblab ber)\s*[:\-]?\s*(.+)",
        text,
        re.IGNORECASE
    )

    expression = match.group(1) if match else text

    expression = expression.replace("×", "*")
    expression = expression.replace("÷", "/")

    if not re.fullmatch(r"[0-9+\-*/().,%\s]+", expression):
        return None

    try:
        result = safe_calculate(expression)
        return f"🧮 Hisob natijasi: **{result}**"
    except ZeroDivisionError:
        return "Nolga bo‘lish mumkin emas."
    except Exception:
        return None


# -------------------- WIKIPEDIA SEARCH --------------------

def wikipedia_search(query, language="uz"):
    endpoints = {
        "uz": "https://uz.wikipedia.org/w/api.php",
        "ru": "https://ru.wikipedia.org/w/api.php",
        "en": "https://en.wikipedia.org/w/api.php"
    }

    url = endpoints.get(language, endpoints["uz"])

    params = {
        "action": "query",
        "format": "json",
        "generator": "search",
        "gsrsearch": query,
        "gsrlimit": 1,
        "prop": "extracts",
        "exintro": 1,
        "explaintext": 1
    }

    try:
        response = requests.get(
            url,
            params=params,
            timeout=8,
            headers={"User-Agent": "SWERAI/1.0"}
        )
        response.raise_for_status()
        data = response.json()

        pages = data.get("query", {}).get("pages", {})
        if not pages:
            return None

        page = next(iter(pages.values()))
        answer = page.get("extract", "")

        if answer:
            return answer[:1800]

    except Exception:
        return None

    return None


# -------------------- TRANSLATION --------------------

def translate_text(text, source, target):
    if source == target:
        return text

    url = "https://api.mymemory.translated.net/get"

    try:
        response = requests.get(
            url,
            params={
                "q": text[:450],
                "langpair": f"{source}|{target}"
            },
            timeout=8
        )
        response.raise_for_status()

        data = response.json()
        return data.get("responseData", {}).get("translatedText")

    except Exception:
        return None


# -------------------- GREETINGS --------------------

GREETINGS = {
    "uz": [
        "Salom! Men SWER.AI. Sizga qanday yordam beray?",
        "Assalomu alaykum! Savolingizni bemalol yozing.",
        "Salom! Bugun nimani o‘rganamiz?"
    ],
    "ru": [
        "Привет! Я SWER.AI. Чем могу помочь?",
        "Здравствуйте! Задайте свой вопрос.",
        "Привет! Что будем изучать сегодня?"
    ],
    "en": [
        "Hello! I am SWER.AI. How can I help you?",
        "Hi! Ask me anything.",
        "Hello! What would you like to learn today?"
    ]
}


# -------------------- RESPONSE ENGINE --------------------

def knowledge_answer(text):
    text = clean_text(text)

    for item in KNOWLEDGE.values():
        for keyword in item["keywords"]:
            if keyword in text:
                return item["answer"]

    for keyword, answer in EXTRA_KNOWLEDGE.items():
        if keyword in text:
            return answer

    return None


def language_response(text):
    if contains_any(text, ["salom", "assalomu alaykum", "hello", "hi", "привет", "здравствуйте"]):
        lang = st.session_state.language
        return random.choice(GREETINGS.get(lang, GREETINGS["uz"]))

    if contains_any(text, ["rahmat", "thanks", "thank you", "спасибо"]):
        return "Arzimaydi! Yana qanday yordam bera olaman? 😊"

    if contains_any(text, ["xayr", "goodbye", "bye", "пока"]):
        return "Xayr! Yana uchrashguncha!"

    if contains_any(text, ["isming nima", "what is your name", "как тебя зовут"]):
        return "Mening ismim SWER.AI. Men sizning virtual yordamchingizman."

    if contains_any(text, ["kim yaratgan", "who created you", "кто тебя создал"]):
        return "Meni Fayzullayev Sherzodbek SWER.AI loyihasi sifatida yaratmoqda."

    if contains_any(text, ["soat", "time", "время"]):
        return f"Hozirgi qurilma vaqti: {current_time()}"

    if contains_any(text, ["sana", "bugun qaysi kun", "date", "дата"]):
        return f"Sana: {current_date()}"

    return None


def math_word_problem(text):
    text = clean_text(text)

    patterns = [
        (r"(\d+)\s*\+\s*(\d+)", "+"),
        (r"(\d+)\s*-\s*(\d+)", "-"),
        (r"(\d+)\s*(?:\*|x|×)\s*(\d+)", "*"),
        (r"(\d+)\s*(?:/|÷)\s*(\d+)", "/")
    ]

    for pattern, symbol in patterns:
        match = re.search(pattern, text)
        if match:
            a, b = map(float, match.groups())
            try:
                result = safe_calculate(f"{a}{symbol}{b}")
                return f"Javob: {result}"
            except Exception:
                pass

    return None


def get_wiki_query(text):
    prefixes = [
        "kim bu", "kim edi", "haqida ayt", "haqida ma'lumot",
        "haqida malumot", "ma'lumot ber", "malumot ber",
        "what is", "who is", "tell me about",
        "что такое", "кто такой", "расскажи о"
    ]

    query = clean_text(text)

    for prefix in prefixes:
        if query.startswith(prefix):
            query = query[len(prefix):].strip()
            break

    return query.strip(" ?!.,") 


def answer_user(user_text):
    text = clean_text(user_text)

    if not text:
        return "Iltimos, savolingizni yozing."

    # 1. Greetings and simple conversation
    response = language_response(text)
    if response:
        return save_answer(response)

    # 2. Calculator
    response = calculator_answer(text)
    if response:
        return save_answer(response)

    response = math_word_problem(text)
    if response:
        return save_answer(response)

    # 3. Translation
    if contains_any(text, ["tarjima qil", "translate", "переведи"]):
        original = re.sub(
            r"^(tarjima qil|translate|переведи)\s*",
            "",
            user_text,
            flags=re.IGNORECASE
        )

        result = translate_text(original, "uz", "en")
        if result:
            return save_answer(f"Tarjima: {result}")

        return "Tarjima xizmati hozir ishlamayapti. Keyinroq urinib ko‘ring."

    # 4. Local knowledge
    response = knowledge_answer(text)
    if response:
        save_topic(text)
        return save_answer(response)

    # 5. Previous topic
    if contains_any(text, ["yana", "davom et", "more", "ещё"]):
        if st.session_state.last_answer:
            return (
                "Oldingi mavzuimiz: "
                + st.session_state.last_topic
                + "\n\n"
                + st.session_state.last_answer
                + "\n\nAniqroq qaysi qismini tushuntiray?"
            )

    # 6. Wikipedia
    wiki_query = get_wiki_query(user_text)

    if len(wiki_query) >= 3:
        language = st.session_state.language
        result = wikipedia_search(wiki_query, language)

        if result:
            save_topic(wiki_query)
            return save_answer(
                "📚 **Topilgan ma’lumot:**\n\n" + result
                + "\n\n*Manba: Wikipedia.*"
            )

    # 7. Similar knowledge
    all_keywords = []

    for item in KNOWLEDGE.values():
        all_keywords.extend(item["keywords"])

    matches = difflib.get_close_matches(
        text,
        all_keywords,
        n=1,
        cutoff=0.72
    )

    if matches:
        response = knowledge_answer(matches[0])
        if response:
            return save_answer(response)

    # 8. Safe fallback
    return (
        "Bu savolga hozir aniq javob topa olmadim. "
        "Internet orqali Wikipedia ma’lumotini ham qidirib ko‘rdim.\n\n"
        "Savolingizni boshqacha yoki batafsilroq yozib ko‘ring. "
        "Men SWER.AI 1.0 sifatida imkoniyatlarimni kengaytirib boraman."
    )


# -------------------- CHAT FUNCTIONS --------------------

def add_message(role, content):
    st.session_state.messages.append({
        "role": role,
        "content": content,
        "time": current_time()
    })

    if len(st.session_state.messages) > 100:
        st.session_state.messages = st.session_state.messages[-100:]


def render_chat():
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            st.caption(message["time"])


def process_message(user_text):
    add_message("user", user_text)
    answer = answer_user(user_text)
    add_message("assistant", answer)
    st.session_state.chat_count += 1


# -------------------- SIDEBAR --------------------

with st.sidebar:
    st.markdown("# 👑 SWER.AI")
    st.caption("Artificial Intelligence Assistant")
    st.divider()

    st.markdown("### 🌐 Til / Language")

    language_name = st.selectbox(
        "Tilni tanlang",
        list(LANGUAGES.keys()),
        index=list(LANGUAGES.values()).index(
            st.session_state.language
        )
    )

    st.session_state.language = LANGUAGES[language_name]

    st.divider()

    st.markdown("### 👤 Foydalanuvchi")

    name = st.text_input(
        "Ismingiz",
        value=st.session_state.user_name
    )

    st.session_state.user_name = name

    st.divider()

    st.metric("Suhbatlar", st.session_state.chat_count)
    st.metric("Xabarlar", len(st.session_state.messages))

    if st.button("🗑️ Yangi suhbat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.last_topic = ""
        st.session_state.last_answer = ""
        st.rerun()

    st.divider()

    st.caption("SWER.AI 1.0")
    st.caption("Creator: Fayzullayev Sherzodbek")
    st.caption("Free edition")


# -------------------- MAIN INTERFACE --------------------

st.markdown(
    "<h1 style='text-align:center;'>👑 SWER.AI</h1>",
    unsafe_allow_html=True
)

st.markdown(
    "<p style='text-align:center;color:#aaaaaa;'>"
    "Your intelligent digital assistant"
    "</p>",
    unsafe_allow_html=True
)

st.divider()

if not st.session_state.messages:
    st.markdown("### Assalomu alaykum!")

    if st.session_state.user_name:
        st.markdown(
            f"**{st.session_state.user_name}**, SWER.AI ga xush kelibsiz!"
        )
    else:
        st.markdown("SWER.AI ga xush kelibsiz!")

    st.write("Men sizga quyidagi yo‘nalishlarda yordam bera olaman:")

    col1, col2 = st.columns(2)

    with col1:
        st.info("📚 Tarix, geografiya va fan")
        st.info("🌍 O‘zbek, rus va ingliz tili")
        st.info("🧮 Matematika va hisob-kitob")

    with col2:
        st.info("💻 Dasturlash va texnologiya")
        st.info("🚀 Koinot va tabiat")
        st.info("🔎 Wikipedia qidiruvi")

    st.caption("Savolingizni quyidagi oynaga yozing.")

render_chat()

# -------------------- INPUT --------------------

user_input = st.chat_input("SWER.AI ga xabar yozing...")

if user_input:
    process_message(user_input)
    st.rerun()

# -------------------- FOOTER --------------------

st.divider()

st.markdown(
    "<p style='text-align:center;color:#777777;'>"
    "SWER.AI 1.0 | Built with Python and Streamlit"
    "</p>",
    unsafe_allow_html=True
)
