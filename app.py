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
        } catch (e) {
            recognition.stop();
        }
    };

    recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        status.innerText = "Terkirim: " + transcript;
        btn.style.background = "#dc2626";
        
        const doc = window.parent.document;
        const textarea = doc.querySelector('textarea[data-testid="stChatInputTextArea"]');
        if (textarea) {
            const nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.parent.HTMLTextAreaElement.prototype, "value").set;
            nativeInputValueSetter.call(textarea, transcript);
            textarea.dispatchEvent(new Event('input', { bubbles: true }));

            setTimeout(() => {
                const sendBtn = doc.querySelector('button[data-testid="stChatInputSubmitButton"]');
                if (sendBtn) {
                    sendBtn.disabled = false;
                    sendBtn.click();
                } else {
                    textarea.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', keyCode: 13, bubbles: true }));
                }
            }, 300);
        }
    };

    recognition.onerror = () => {
        status.innerText = "Gagal merekam suara.";
        btn.style.background = "#dc2626";
    };

    recognition.onend = () => {
        btn.style.background = "#dc2626";
    };
} else {
    status.innerText = "Gunakan peramban Chrome untuk fitur suara langsung.";
}
</script>
"""
components.html(voice_component, height=55)

prompt = st.chat_input("Atau ketik pertanyaan kesehatan/poliklinik di sini...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt, "audio": None})
    with st.chat_message("user"):
        st.write(prompt)

    system_instruction = f"""
Anda adalah 'SAE' (Suara, Aksara Edukasi), asisten AI resmi RSUD Kota Bandung.

DATABASE RESMI:
---
{context_data}
---

ATURAN:
1. Pahami sinonim kata kesehatan & poliklinik (contoh: syaraf = saraf = neurologi, obgyn = kandungan, anak = pediatri, poli dalam = penyakit dalam).
2. Jika menanyakan jadwal, tuliskan nama poli, nama dokter, hari, dan jam praktik secara ringkas dan padat.
3. Langsung jawab intinya tanpa pembukaan kalimat yang panjang.
"""

    with st.chat_message("assistant"):
        placeholder_teks = st.empty()
        with st.spinner("SAE sedang memproses tanggapan..."):
            jawaban = None
            daftar_model = ["gemini-2.0-flash", "gemini-1.5-flash"]
            
            for m in daftar_model:
                try:
                    response = client.models.generate_content(
                        model=m,
                        contents=f"{system_instruction}\n\nPertanyaan: {prompt}"
                    )
                    if response.text:
                        jawaban = response.text
                        placeholder_teks.write(jawaban)
                        break
                except Exception:
                    continue
            
            if not jawaban:
                placeholder_teks.warning("Jaringan AI sedang sangat padat. Silakan klik tombol 'Bicara Sekarang' lagi ya.")

            if jawaban:
                audio_stream = None
                try:
                    audio_stream = teks_ke_suara(jawaban)
                    st.audio(audio_stream, format="audio/mp3", autoplay=True)
                except Exception:
                    pass

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": jawaban,
                    "audio": audio_stream
                })
