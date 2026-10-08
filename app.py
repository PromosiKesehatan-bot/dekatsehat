import streamlit as st
from pypdf import PdfReader
from google import genai

st.set_page_config(page_title="DekatSehat - Tanya Promkes", page_icon="🩺", layout="centered")

st.title("🩺 DekatSehat")
st.caption("Asisten Edukasi & Informasi Kesehatan Masyarakat")

# 1. Ambil API Key dari Streamlit Secrets
api_key = st.secrets.get("GEMINI_API_KEY")

if not api_key:
    st.error("API Key belum dikonfigurasi di Settings Streamlit!")
    st.stop()

# Inisialisasi Google GenAI client (mendukung key format AQ...)
client = genai.Client(api_key=api_key)

# 2. Ekstraksi teks dari file materi leaflet
@st.cache_resource
def load_health_context():
    try:
        reader = PdfReader("materi_promkes.pdf")
        text = ""
        for page in reader.pages:
            content = page.extract_text()
            if content:
                text += content + "\n"
        return text
    except Exception as e:
        return ""

context_text = load_health_context()

welcome_message = (
    "Halo! Saya asisten edukasi kesehatan DekatSehat. "
    "Ada yang ingin Anda tanyakan seputar materi kesehatan atau pencegahan penyakit?"
)

# 3. Inisialisasi riwayat chat
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": welcome_message}]

# Tampilkan riwayat chat
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 4. Input pertanyaan pengguna
if user_prompt := st.chat_input("Ketik pertanyaan kesehatan Anda di sini..."):
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.markdown(user_prompt)

    system_instruction = f"""
    Anda adalah asisten edukasi promosi kesehatan (Promkes) bernama DekatSehat.
    Gunakan konteks materi resmi berikut sebagai referensi utama:
    ---
    {context_text}
    ---
    Jawab dengan bahasa Indonesia yang ramah, sopan, mudah dipahami masyarakat awam, dan edukatif.
    Jika topik medis bersifat darurat atau butuh diagnosis langsung, selalu sarankan konsultasi langsung dengan dokter/tenaga medis di RSUD.
    """

    prompt_with_context = f"{system_instruction}\n\nPertanyaan masyarakat: {user_prompt}"

    with st.chat_message("assistant"):
        with st.spinner("Sedang mencari materi edukasi..."):
            try:
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt_with_context,
                )
                bot_reply = response.text
                st.markdown(bot_reply)
                st.session_state.messages.append({"role": "assistant", "content": bot_reply})
            except Exception as e:
                st.error(f"Terjadi kendala saat memproses: {e}")
