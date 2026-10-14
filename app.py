import streamlit as st
import streamlit.components.v1 as components
from google import genai
from gtts import gTTS
import PyPDF2
import os
import io

st.set_page_config(page_title="SAE RSUD Kota Bandung", page_icon="🩺", layout="centered")

# Desain Gradien Biru Elegan & Kartu Glassmorphism
custom_css = """
<style>
.stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
    background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%) !important;
}
header {visibility: hidden !important;}
div[data-testid="stChatMessage"] {
    background: rgba(255, 255, 255, 0.08) !important;
    border: 1px solid rgba(255, 255, 255, 0.15) !important;
    border-radius: 16px !important;
    backdrop-filter: blur(8px) !important;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25) !important;
    margin-bottom: 12px !important;
}
div[data-testid="stChatInput"] {
    background: rgba(255, 255, 255, 0.05) !important;
    border-radius: 14px !important;
}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

@st.cache_resource
def load_context_data():
    txt_data = ""
    pdf_data = ""
    
    for f in os.listdir("."):
        if f.endswith(".txt") and f != "requirements.txt":
            try:
                with open(f, "r", encoding="utf-8") as file:
                    txt_data += file.read() + "\n\n"
            except Exception:
                continue

    for f in os.listdir("."):
        if f.endswith(".pdf"):
            try:
                with open(f, "rb") as file:
                    reader = PyPDF2.PdfReader(file)
                    for page in reader.pages[:20]:
                        extracted = page.extract_text()
                        if extracted:
                            pdf_data += extracted + "\n"
            except Exception:
                continue
            
    gabungan = f"DATA RESMI JADWAL POLIKLINIK RSUD KOTA BANDUNG:\n{txt_data}\n\nMATERI EDUKASI KESEHATAN:\n{pdf_data}"
    return gabungan[:100000] if txt_data or pdf_data else "Materi promosi kesehatan dan informasi poliklinik."

context_data = load_context_data()

st.sidebar.title("Informasi Sistem")
st.sidebar.info(f"Total Karakter Terbaca: {len(context_data)}")

st.title("🩺 SAE RSUD Kota Bandung")
st.caption("Suara, Aksara Edukasi — Asisten Edukasi & Informasi Kesehatan Masyarakat berbasis AI")

def teks_ke_suara(teks):
    teks_bersih = teks.replace("*", "").replace("#", "").replace("-", " ")
    # Batasi intisari suara ke 180 karakter agar file audio tercipta dalam 1 detik
    teks_audio = teks_bersih[:180]
    tts = gTTS(text=teks_audio, lang="id")
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    fp.seek(0)
    return fp

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Halo! Sampurasun! Saya SAE (Suara, Aksara Edukasi), asisten virtual resmi Promosi Kesehatan RSUD Kota Bandung. Ada yang ingin Anda tanyakan seputar materi kesehatan atau informasi poliklinik?",
            "audio": None
        }
    ]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if msg.get("audio"):
            st.audio(msg["audio"], format="audio/mp3")

# Tombol Suara Web Speech API
voice_component = """
<div style="display:flex; align-items:center; gap:10px; margin-bottom:12px;">
    <button id="micBtn" style="background:#dc2626; color:white; border:none; border-radius:50px; padding:10px 18px; font-size:14px; cursor:pointer; font-weight:bold; display:flex; align-items:center; gap:6px; box-shadow: 0 4px 10px rgba(220,38,38,0.4);">
        🎤 Bicara Sekarang
    </button>
    <span id="micStatus" style="color:#aaa; font-size:13px;">Ketuk tombol untuk bicara</span>
</div>

<script>
const btn = document.getElementById('micBtn');
const status = document.getElementById('micStatus');
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

if (SpeechRecognition) {
    const recognition = new SpeechRecognition();
    recognition.lang = 'id-ID';
    recognition.interimResults = false;

    btn.onclick = () => {
        try {
            recognition.start();
            status.innerText = "Mendengarkan...";
            btn.style.background = "#16a34a";
