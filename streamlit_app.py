
import streamlit as st
import requests
import json
import ast
import operator
import re
import random
import base64
import io
import hashlib
import html
from datetime import datetime
import streamlit.components.v1 as components

# =====================================================
# SWER.AI 1.0 PREMIUM
# Creator: Fayzullayev Sherzodbek
# =====================================================

st.set_page_config(
    page_title="SWER.AI PREMIUM",
    page_icon="👑",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------- DESIGN ----------------

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background:
    radial-gradient(circle at 15% 5%, #242424 0%, transparent 35%),
    linear-gradient(135deg, #050505, #111111 55%, #080808);
    color: #eeeeee;
}

header {visibility: hidden;}
footer {visibility: hidden;}

.block-container {
    max-width: 1150px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #101010, #050505);
    border-right: 1px solid #303030;
}

[data-testid="stChatMessage"] {
    background: linear-gradient(145deg, #191919, #101010);
    border: 1px solid #333333;
    border-radius: 18px;
    padding: 16px;
    margin-bottom: 12px;
}

.stTextInput input {
    background: #151515 !important;
    color: white !important;
    border: 1px solid #555 !important;
    border-radius: 12px !important;
}

.stButton button {
    background: linear-gradient(135deg, #eeeeee, #888888);
    color: #080808;
    font-weight: 800;
    border: none;
    border-radius: 12px;
    min-height: 42px;
}

.stButton button:hover {
    background: white;
    color: black;
    border: 1px solid white;
}

.premium-title {
    font-size: 55px;
    font-weight: 800;
    letter-spacing: 5px;
    background: linear-gradient(90deg, #ffffff, #888888, #ffffff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-align: center;
}

.premium-sub {
    text-align: center;
    color: #999;
    letter-spacing: 4px;
    font-size: 11px;
}

.panel {
    background: linear-gradient(145deg, #1c1c1c, #0d0d0d);
    border: 1px solid #353535;
    border-radius: 18px;
    padding: 20px;
}

.small-muted {
    color: #999999;
    font-size: 12px;
}
</style>
""", unsafe_allow_html=True)

# ---------------- SESSION ----------------

if "messages" not in st.session_state:
    st.session_state.messages = []

if "uploaded_hash" not in st.session_state:
    st.session_state.uploaded_hash = ""

if "last_voice_hash" not in st.session_state:
    st.session_state.last_voice_hash = ""

if "language" not in st.session_state:
    st.session_state.language = "O‘zbekcha"

# ---------------- KNOWLEDGE BASE ----------------

KNOWLEDGE = {
    "quyosh": """Quyosh — Quyosh sistemasining markazidagi yulduz.
U asosan vodorod va geliydan tashkil topgan.
Quyosh energiyasi uning yadrosidagi termoyadro reaksiyalari orqali hosil bo‘ladi.
U Yerga yorug‘lik va issiqlik beradi.""",

    "yer": """Yer — Quyosh sistemasidagi uchinchi sayyora.
Uning tabiiy yo‘ldoshi Oy hisoblanadi.
Yer o‘z o‘qi atrofida taxminan 24 soatda aylanadi,
Quyosh atrofida esa taxminan 365,25 kunda bir marta aylanadi.""",

    "osmon": """Osmonning ko‘k ko‘rinishi atmosferadagi yorug‘lik sochilishi bilan bog‘liq.
Havodagi molekulalar qisqa to‘lqinli ko‘k yorug‘likni
uzun to‘lqinli qizil yorug‘likka qaraganda kuchliroq sochadi.
Quyosh botishida yorug‘lik atmosferada uzunroq yo‘l bosadi,
shu sabab qizil va to‘q sariq ranglar ko‘proq ko‘rinadi.""",

    "oy": """Oy — Yerning tabiiy yo‘ldoshi.
U o‘zidan yorug‘lik chiqarmaydi, Quyosh nurini qaytaradi.
Oyning ko‘rinadigan shakli uning fazalariga bog‘liq.""",

    "suv": """Suv — H₂O kimyoviy formulali modda.
U ikki vodorod va bir kislorod atomidan tashkil topgan.
Oddiy atmosfera bosimida 0°C da muzlaydi,
100°C da qaynaydi.""",

    "fotosintez": """Fotosintez — o‘simliklar yorug‘lik energiyasidan foydalanib
suv va karbonat angidriddan organik moddalar hosil qiladigan jarayon.
Bu jarayonda kislorod ham ajralib chiqadi.""",

    "atom": """Atom — kimyoviy elementning xossalarini saqlaydigan eng kichik zarracha.
U proton, neytron va elektronlardan tashkil topadi.
Proton va neytron yadroda, elektronlar esa uning atrofida joylashadi.""",

    "internet": """Internet — butun dunyo bo‘ylab kompyuter va qurilmalarni
o‘zaro bog‘laydigan global tarmoq.
U orqali ma’lumot almashish, aloqa qilish va xizmatlardan foydalanish mumkin.""",

    "python": """Python — sodda sintaksisga ega, keng qo‘llaniladigan dasturlash tili.
U sun’iy intellekt, veb-dasturlash, avtomatlashtirish,
ma’lumotlar tahlili va boshqa sohalarda ishlatiladi.""",

    "ai": """Sun’iy intellekt — kompyuter tizimlarining
o‘rganish, ma’lumotni tahlil qilish va ayrim vazifalarni
inson aqliga o‘xshash tarzda bajarish imkoniyatidir.
Uning imkoniyatlari ishlatilayotgan model va ma’lumotlarga bog‘liq.""",

    "tarix": """Tarix — insoniyatning o‘tmishini o‘rganuvchi fan.
U davlatlar, jamiyatlar, urushlar, madaniyatlar va
insonlarning tarixiy rivojlanishini o‘rganadi.""",

    "alisher navoiy": """Alisher Navoiy — buyuk o‘zbek shoiri,
mutafakkiri va davlat arbobi.
U 1441-yilda Hirotda tug‘ilgan.
Turkiy tildagi adabiyot rivojiga katta hissa qo‘shgan.""",

    "amir temur": """Amir Temur — XIV asrda yashagan yirik davlat arbobi
va sarkarda. U 1336-yilda Kesh yaqinida tug‘ilgan.
Samarqandni davlatining markaziga aylantirgan.""",

    "mars": """Mars — Quyosh sistemasidagi to‘rtinchi sayyora.
U qizg‘ish ko‘rinishi sababli Qizil sayyora deb ataladi.
Marsda Olympus Mons deb nomlangan ulkan vulqon bor.""",

    "kislorod": """Kislorod — O belgisi bilan ifodalanadigan kimyoviy element.
U tirik organizmlarning nafas olishi uchun muhim.
Atmosferada molekulyar kislorod O₂ shaklida mavjud.""",

    "kompyuter": """Kompyuter — ma’lumotlarni qabul qilish,
qayta ishlash, saqlash va uzatish uchun mo‘ljallangan elektron qurilma.
Uning asosiy qismlariga protsessor, tezkor xotira,
saqlash qurilmasi va boshqa komponentlar kiradi."""
}

# ---------------- SAFE CALCULATOR ----------------

OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.FloorDiv: operator.floordiv,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos
}

def safe_calc(expression):
    expression = expression.replace(",", ".")
    tree = ast.parse(expression, mode="eval")

    def evaluate(node):
        if isinstance(node, ast.Expression):
            return evaluate(node.body)

        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)):
                return node.value

        if isinstance(node, ast.BinOp):
            if type(node.op) in OPS:
                left = evaluate(node.left)
                right = evaluate(node.right)

                if isinstance(node.op, ast.Pow) and abs(right) > 100:
                    raise ValueError("Daraja juda katta")

                result = OPS[type(node.op)](left, right)

                if abs(result) > 10**100:
                    raise ValueError("Natija juda katta")

                return result

        if isinstance(node, ast.UnaryOp):
            if type(node.op) in OPS:
                return OPS[type(node.op)](evaluate(node.operand))

        raise ValueError("Noto‘g‘ri matematik ifoda")

    return evaluate(tree)

# ---------------- WIKIPEDIA SEARCH ----------------

def wikipedia_search(query, language="uz"):
    languages = {
        "O‘zbekcha": "uz",
        "Русский": "ru",
        "English": "en"
    }

    lang = languages.get(language, "uz")

    url = f"https://{lang}.wikipedia.org/w/api.php"

    try:
        response = requests.get(
            url,
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
            timeout=12,
            headers={"User-Agent": "SWERAI/1.0"}
        )

        data = response.json()
        pages = data.get("query", {}).get("pages", {})

        if not pages:
            return None

        page = next(iter(pages.values()))
        extract = page.get("extract", "")

        if extract:
            return extract[:3500]

    except Exception:
        return None

    return None

# ---------------- TRANSLATION ----------------

def translate_text(text, source, target):
    try:
        url = "https://api.mymemory.translated.net/get"

        response = requests.get(
            url,
            params={
                "q": text[:450],
                "langpair": f"{source}|{target}"
            },
            timeout=12
        )

        data = response.json()
        return data.get("responseData", {}).get("translatedText")

    except Exception:
        return None

# ---------------- SMART ANSWER ENGINE ----------------

def smart_answer(question, language="O‘zbekcha"):
    q = question.lower().strip()

    if not q:
        return "Savolingizni yozing."

    greetings = [
        "salom", "assalomu alaykum", "hello",
        "hi", "привет", "здравствуйте"
    ]

    if q in greetings:
        answers = {
            "O‘zbekcha": "Salom! Men SWER.AI. Sizga qanday yordam bera olaman?",
            "Русский": "Здравствуйте! Я SWER.AI. Чем могу помочь?",
            "English": "Hello! I am SWER.AI. How can I help you?"
        }
        return answers.get(language, answers["O‘zbekcha"])

    if any(x in q for x in ["isming", "sening isming", "who are you", "кто ты"]):
        return "Men SWER.AI 1.0 PREMIUM sun’iy intellekt yordamchisiman."

    if any(x in q for x in ["soat", "vaqt", "time now"]):
        return "Hozirgi sana va vaqt: " + datetime.now().strftime("%d.%m.%Y %H:%M")

    # Calculator
    math_match = re.search(
        r"(?:hisobla|yech|calculate|what is)\s*([0-9+\-*/().,% ]+)",
        q
    )

    if math_match:
        try:
            return "Hisoblash natijasi: " + str(
                safe_calc(math_match.group(1))
            )
        except Exception:
            pass

    # Specific question intents before general keywords
    if "osmon" in q and any(x in q for x in ["nega", "nima uchun", "why", "почему"]):
        return KNOWLEDGE["osmon"]

    if "quyosh" in q and any(x in q for x in ["nima", "qanday", "haqida", "what", "расскажи"]):
        return KNOWLEDGE["quyosh"]

    # Knowledge matching
    for key, answer in KNOWLEDGE.items():
        if key in q:
            return answer

    # Translation
    if any(x in q for x in ["tarjima qil", "translate", "переведи"]):
        return (
            "Tarjima qilish uchun matn va qaysi tilga tarjima "
            "qilishni yozing. Masalan: translate hello to Uzbek."
        )

    # Wikipedia fallback
    if len(q.split()) >= 2:
        result = wikipedia_search(question, language)

        if result:
            return (
                "Wikipedia ma’lumotiga ko‘ra:\n\n"
                + result
                + "\n\nManba: Wikipedia. Ma’lumotni mustaqil tekshirib ko‘ring."
            )

    fallbacks = {
        "O‘zbekcha": (
            "Bu savolga hozir aniq javob topa olmadim. "
            "Savolni boshqacha yoki batafsilroq yozib ko‘ring. "
            "Men bilmagan narsamni to‘qib aytmayman."
        ),
        "Русский": (
            "Я пока не смог найти точный ответ. "
            "Попробуйте задать вопрос подробнее."
        ),
        "English": (
            "I could not find a reliable answer yet. "
            "Please try asking in more detail."
        )
    }

    return fallbacks.get(language, fallbacks["O‘zbekcha"])

# ---------------- TEXT TO SPEECH ----------------

def speak_text(text, language):
    lang_codes = {
        "O‘zbekcha": "uz-UZ",
        "Русский": "ru-RU",
        "English": "en-US"
    }

    safe_text = json.dumps(text[:2500], ensure_ascii=False)
    lang = lang_codes.get(language, "uz-UZ")

    components.html(
        f"""
        <script>
        const text = {safe_text};
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = "{lang}";
        utterance.rate = 1;
        speechSynthesis.cancel();
        speechSynthesis.speak(utterance);
        </script>
        """,
        height=0
    )

# ---------------- HEADER ----------------

st.markdown(
    '<div class="premium-title">SWER.AI</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="premium-sub">PREMIUM INTELLIGENCE SYSTEM · VERSION 1.0</div>',
    unsafe_allow_html=True
)

st.write("")

# ---------------- SIDEBAR ----------------

with st.sidebar:
    st.markdown("## 👑 SWER.AI")
    st.caption("PREMIUM CONTROL PANEL")

    st.divider()

    st.markdown("### 🌐 Til")
    st.session_state.language = st.selectbox(
        "Tilni tanlang",
        ["O‘zbekcha", "Русский", "English"],
        index=["O‘zbekcha", "Русский", "English"].index(
            st.session_state.language
        )
    )

    st.divider()

    st.markdown("### ⚙️ Boshqaruv")

    if st.button("🗑️ Yangi suhbat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.markdown("### 💾 Suhbatni saqlash")

    export_data = {
        "app": "SWER.AI 1.0 PREMIUM",
        "created": datetime.now().isoformat(),
        "messages": [
            {
                "role": m["role"],
                "content": m["content"]
            }
            for m in st.session_state.messages
        ]
    }

    st.download_button(
        "⬇️ Suhbatni yuklab olish",
        data=json.dumps(
            export_data,
            ensure_ascii=False,
            indent=2
        ),
        file_name="swer_ai_chat.json",
        mime="application/json",
        use_container_width=True
    )

    st.caption(
        "Suhbatni JSON fayl qilib qurilmangizga saqlang."
    )

    st.divider()

    st.markdown("### 📊 Tizim")
    st.write("🟢 SWER.AI: Ishlayapti")
    st.write("🧠 AI rejimi: API'siz")
    st.write("🌍 Wikipedia: Internet orqali")
    st.write("🎙️ Ovoz: Brauzer imkoniyatiga bog‘liq")

    st.divider()
    st.caption("Created by Fayzullayev Sherzodbek")

# ---------------- IMAGE UPLOAD ----------------

st.markdown("### 🖼️ Rasm yuklash")

uploaded_image = st.file_uploader(
    "Rasmni tanlang",
    type=["png", "jpg", "jpeg", "webp"],
    key="image_upload"
)

image_bytes = None

if uploaded_image:
    image_bytes = uploaded_image.getvalue()
    st.image(
        image_bytes,
        caption="Yuklangan rasm",
        use_container_width=True
    )

    st.info(
        "Rasm chatga biriktiriladi. Hozirgi API'siz versiya "
        "rasm ichidagi narsalarni avtomatik tahlil qila olmaydi."
    )

# ---------------- CHAT DISPLAY ----------------

st.markdown("### 💬 SWER.AI bilan suhbat")

if not st.session_state.messages:
    st.markdown("""
    <div class="panel">
        <h3>Assalomu alaykum!</h3>
        <p>Men SWER.AI PREMIUM yordamchisiman.</p>
        <p>Istalgan savolingizni yozing yoki ovozli javobni tinglang.</p>
        <p class="small-muted">Bilimlarimni bosqichma-bosqich kengaytirib boramiz.</p>
    </div>
    """, unsafe_allow_html=True)

for i, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

        if message.get("image"):
            try:
                st.image(
                    base64.b64decode(message["image"]),
                    use_container_width=True
                )
            except Exception:
                st.caption("Rasmni ko‘rsatib bo‘lmadi.")

        if message["role"] == "assistant":
            if st.button(
                "🔊 Ovoz chiqarish",
                key=f"speak_{i}"
            ):
                speak_text(
                    message["content"],
                    st.session_state.language
                )

# ---------------- VOICE INPUT ----------------

st.markdown("### 🎙️ Ovozli savol")

try:
    audio_value = st.audio_input("Ovozingizni yozib oling")

    if audio_value:
        st.audio(audio_value)

        audio_hash = hashlib.sha256(
            audio_value.getvalue()
        ).hexdigest()

        if st.button("🎧 Ovozni matnga aylantirish"):
            if audio_hash == st.session_state.last_voice_hash:
                st.warning("Bu ovoz avval yuborilgan.")
            else:
                try:
                    import speech_recognition as sr

                    recognizer = sr.Recognizer()

                    with sr.AudioFile(
                        io.BytesIO(audio_value.getvalue())
                    ) as source:
                        audio_data = recognizer.record(source)

                    lang_codes = {
                        "O‘zbekcha": "uz-UZ",
                        "Русский": "ru-RU",
                        "English": "en-US"
                    }

                    recognized = recognizer.recognize_google(
                        audio_data,
                        language=lang_codes.get(
                            st.session_state.language,
                            "uz-UZ"
                        )
                    )

                    st.session_state.last_voice_hash = audio_hash
                    st.success("Tushunilgan matn: " + recognized)

                    st.session_state.messages.append({
                        "role": "user",
                        "content": recognized
                    })

                    answer = smart_answer(
                        recognized,
                        st.session_state.language
                    )

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer
                    })

                    st.rerun()

                except Exception as e:
                    st.error(
                        "Ovozni aniqlash amalga oshmadi. "
                        "Internetni tekshiring yoki savolni yozing."
                    )

except Exception:
    st.info(
        "Ovoz yozish funksiyasi uchun Streamlitning yangi "
        "versiyasi kerak bo‘lishi mumkin."
    )

# ---------------- CHAT INPUT ----------------

prompt = st.chat_input("SWER.AI ga savolingizni yozing...")

if prompt:
    user_message = {
        "role": "user",
        "content": prompt
    }

    if image_bytes:
        user_message["image"] = base64.b64encode(
            image_bytes
        ).decode("utf-8")

    st.session_state.messages.append(user_message)

    with st.spinner("SWER.AI javob tayyorlamoqda..."):
        answer = smart_answer(
            prompt,
            st.session_state.language
        )

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer
    })

    st.rerun()

# ---------------- FOOTER ----------------

st.divider()

st.markdown(
    """
    <div style="text-align:center;color:#777;padding:15px">
        <b style="color:#ddd;letter-spacing:3px">SWER.AI</b>
        <br>
        PREMIUM AI ASSISTANT · 1.0
        <br>
        <span style="font-size:11px">
        Created by Fayzullayev Sherzodbek
        </span>
    </div>
    """,
    unsafe_allow_html=True
    )
    
