import streamlit as st
from google import genai
import PyPDF2
import os

st.set_page_config(page_title="SAE RSUD Kota Bandung", page_icon="🩺", layout="centered")

# Inisialisasi API Client Gemini
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

@st.cache_resource
def load_context_data():
    text = ""
    
    # 1. Baca berkas TXT (jadwal poliklinik & rujukan tertulis langsung)
    txt_files = [f for f in os.listdir(".") if f.endswith(".txt") and f != "requirements.txt"]
    for txt_file in txt_files:
        try:
            with open(txt_file, "r", encoding="utf-8") as file:
                text += file.read() + "\n\n"
        except Exception:
            continue

    # 2. Baca berkas PDF (materi edukasi & promkes)
    pdf_files = [f for f in os.listdir(".") if f.endswith(".pdf")]
    for pdf_file in pdf_files:
        try:
            with open(pdf_file, "rb") as file:
                reader = PyPDF2.PdfReader(file)
                for page in reader.pages[:35]:
                    extracted = page.extract_text()
                    if extracted:
                        text += extracted + "\n"
        except Exception:
            continue
            
    # Batasi muatan teks agar proses ringan dan stabil
   return text[:150000] if text else "Materi promosi kesehatan umum dan informasi poliklinik."

context_data = load_context_data()

st.title("🩺 SAE RSUD Kota Bandung")
st.caption("Suara, Aksara Edukasi — Asisten Edukasi & Informasi Kesehatan Masyarakat berbasis AI")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Halo! Sampurasun! Saya SAE (Suara, Aksara Edukasi), asisten virtual resmi Instalasi Promosi Kesehatan RSUD Kota Bandung. Ada yang ingin Anda tanyakan seputar materi kesehatan atau informasi poliklinik?"}
    ]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

if prompt := st.chat_input("Ketik pertanyaan kesehatan atau info poliklinik di sini..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    system_instruction = f"""
Anda adalah 'SAE' (Suara, Aksara Edukasi), asisten virtual resmi Promosi Kesehatan RSUD Kota Bandung yang ramah, edukatif, empatik, dan mudah dipahami masyarakat.

Gunakan referensi materi promkes dan informasi jadwal berikut sebagai rujukan utama:
{context_data}
Instruksi:
- Jika pengguna hanya menyapa (seperti halo, hai, assalamualaikum, sampurasun), balas dengan ramah, perkenalkan diri singkat sebagai SAE RSUD Kota Bandung, dan tanyakan hal apa yang bisa dibantu tanpa langsung memberikan materi panjang.
- Jika pengguna menanyakan jadwal dokter atau poliklinik, WAJIB sebutkan nama dokter spesialis, hari praktik, serta jam pelayanannya secara rinci sesuai data rujukan jadwal poliklinik di atas. JANGAN hanya memberikan tautan pendaftaran atau jawaban umum jika datanya tertera.
- Jika pengguna menanyakan materi edukasi promkes/kesehatan yang ADA di rujukan materi, prioritaskan rujukan tersebut.
- Jika pengguna menanyakan topik kesehatan umum yang BELUM ADA di referensi materi (seperti DBD, anemia, flu, dll.), jawablah menggunakan pengetahuan medis umum yang sahih, promotif, dan preventif.
- Jawab dengan bahasa yang santun, runtut, dan mudah dipahami warga.
- Di akhir penjelasan atau jika relevan, sertakan anjuran bagi warga untuk berkonsultasi langsung ke RSUD Kota Bandung jika membutuhkan pemeriksaan medis lanjutan.
"""


    with st.chat_message("assistant"):
        with st.spinner("Sedang memproses..."):
            try:
                response = client.models.generate_content(
                    model="gemini-3.8-flash",
                    contents=f"{system_instruction}\n\nPertanyaan: {prompt}"
                )
                jawaban = response.text
                st.write(jawaban)
                st.session_state.messages.append({"role": "assistant", "content": jawaban})
            except Exception as e:
                st.error(f"Terjadi kendala saat memproses: {e}")
