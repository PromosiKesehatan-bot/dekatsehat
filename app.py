import streamlit as st
from google import genai
from audio_recorder_streamlit import audio_recorder
from gtts import gTTS
import PyPDF2
import os
import io

st.set_page_config(page_title="SAE RSUD Kota Bandung", page_icon="🩺", layout="centered")

client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

@st.cache_resource
def load_context_data():
    txt_data = ""
    pdf_data = ""
    
    # 1. BACA FILE TXT (Prioritas Utama Jadwal)
    for f in os.listdir("."):
        if f.endswith(".txt") and f != "requirements.txt":
            try:
                with open(f, "r", encoding="utf-8") as file:
                    txt_data += file.read() + "\n\n"
            except Exception:
                continue

    # 2. BACA FILE PDF (Materi Promkes)
    for f in os.listdir("."):
        if f.endswith(".pdf"):
            try:
                with open(f, "rb") as file:
                    reader = PyPDF2.PdfReader(file)
                    for page in reader.pages[:15]:
                        extracted = page.extract_text()
                        if extracted:
                            pdf_data += extracted + "\n"
            except Exception:
                continue
            
    gabungan = f"DATA RESMI JADWAL POLIKLINIK RSUD KOTA BANDUNG:\n{txt_data}\n\nMATERI EDUKASI KESEHATAN:\n{pdf_data}"
    return gabungan[:150000] if txt_data or pdf_data else "Materi promosi kesehatan dan informasi poliklinik."

context_data = load_context_data()

st.sidebar.title("Informasi Sistem")
st.sidebar.info(f"Total Karakter Terbaca: {len(context_data)}")

st.title("🩺 SAE RSUD Kota Bandung")
st.caption("Suara, Aksara Edukasi — Asisten Edukasi & Informasi Kesehatan Masyarakat berbasis AI")

def teks_ke_suara(teks):
    teks_bersih = teks.replace("*", "").replace("#", "").replace("-", " ")
    tts = gTTS(text=teks_bersih, lang="id")
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    fp.seek(0)
    return fp

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Halo! Sampurasun! Saya SAE (Suara, Aksara Edukasi), asisten virtual resmi Instalasi Promosi Kesehatan RSUD Kota Bandung. Ada yang ingin Anda tanyakan seputar materi kesehatan atau informasi poliklinik?",
            "audio": None
        }
    ]

# Tampilkan riwayat percakapan
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if msg.get("audio"):
            st.audio(msg["audio"], format="audio/mp3")

# Area input mikrofon
st.markdown("---")
col_audio, col_label = st.columns([1, 5])
with col_audio:
    audio_bytes = audio_recorder(
        text="",
        recording_color="#e02424",
        neutral_color="#1f2937",
        icon_name="microphone",
        icon_size="2x"
    )
with col_label:
    st.caption("🎙️ Ketuk mikrofon untuk bicara, lalu ketuk lagi untuk berhenti & mengirim.")

text_input = st.chat_input("Atau ketik pertanyaan kesehatan/poliklinik di sini...")

prompt_final = None
audio_payload = None

if audio_bytes:
    if "last_recorded_audio" not in st.session_state or st.session_state.last_recorded_audio != audio_bytes:
        st.session_state.last_recorded_audio = audio_bytes
        audio_payload = audio_bytes
elif text_input:
    prompt_final = text_input

if prompt_final or audio_payload:
    user_display = prompt_final if prompt_final else "🎤 [Pertanyaan Suara]"
    st.session_state.messages.append({"role": "user", "content": user_display, "audio": audio_payload})
    with st.chat_message("user"):
        st.write(user_display)
        if audio_payload:
            st.audio(audio_payload, format="audio/wav")

    system_instruction = f"""
Anda adalah 'SAE' (Suara, Aksara Edukasi), asisten AI resmi RSUD Kota Bandung.

Berikut DATABASE RESMI JADWAL & MATERI KESEHATAN RSUD KOTA BANDUNG:
---
{context_data}
---

ATURAN MENJAWAB:
1. Pahami sinonim kata (contoh: syaraf = saraf = neurologi, obgyn = kandungan, anak = pediatri).
2. Jika menanyakan jadwal, WAJIB sebutkan nama klinik, nama lengkap dokter, hari, dan jam praktik secara rinci sesuai database.
3. Buat kalimat yang jelas, ramah, dan ringkas agar nyaman didengar saat dibacakan suara audio.
"""

    with st.chat_message("assistant"):
        with st.spinner("SAE sedang memproses tanggapan..."):
            try:
                if audio_payload:
                    contents_input = [
                        system_instruction,
                        "Dengarkan rekaman audio ini, pahami pertanyaannya, lalu jawab sesuai panduan database RSUD Kota Bandung:",
                        {"mime_type": "audio/wav", "data": audio_payload}
                    ]
                else:
                    contents_input = f"{system_instruction}\n\nPertanyaan: {prompt_final}"

                response = client.models.generate_content(
                    model="gemini-3.8-flash",
                    contents=contents_input
                )
                jawaban = response.text
                st.write(jawaban)

                audio_stream = teks_ke_suara(jawaban)
                st.audio(audio_stream, format="audio/mp3", autoplay=True)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": jawaban,
                    "audio": audio_stream
                })
            except Exception as e:
                st.error(f"Terjadi kendala saat memproses: {e}")
