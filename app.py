import streamlit as st
from google import genai
import PyPDF2
import os

st.set_page_config(page_title="SAE RSUD Kota Bandung", page_icon="🩺", layout="centered")

# Inisialisasi API Client Gemini
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

@st.cache_resource
def load_pdf_context():
    text = ""
    pdf_files = [f for f in os.listdir(".") if f.endswith(".pdf")]
    for pdf_file in pdf_files:
        try:
            with open(pdf_file, "rb") as file:
                reader = PyPDF2.PdfReader(file)
                # Ambil 35 halaman pertama per dokumen
                for page in reader.pages[:35]:
                    extracted = page.extract_text()
                    if extracted:
                        text += extracted + "\n"
        except Exception as e:
            continue
    # Batasi muatan teks agar ringan dan stabil
    return text[:80000] if text else "Materi promosi kesehatan umum."

context_data = load_pdf_context()

st.title("🩺 SAE RSUD Kota Bandung")
st.caption("Suara, Aksara Edukasi - Asisten Edukasi & Informasi Kesehatan Masyarakat berbasis AI")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Halo! Saya asisten edukasi kesehatan SAE dari Instalasi Promosi Kesehatan RSUD Kota Bandung. Ada yang ingin Anda tanyakan seputar materi kesehatan atau pencegahan penyakit?"}
    ]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

if prompt := st.chat_input("Ketik pertanyaan kesehatan Anda di sini..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    system_instruction = f"""
Anda adalah 'SAE', asisten virtual resmi Promosi Kesehatan RSUD Kota Bandung yang ramah, edukatif, empatik, dan mudah dipahami masyarakat.

Gunakan referensi materi promkes berikut sebagai rujukan utama:
{context_data}

Instruksi:
- Jika pengguna hanya menyapa (seperti halo, hai, assalamualaikum), balas dengan ramah, perkenalkan diri secara singkat, dan tanyakan apa yang bisa dibantu tanpa langsung memberikan materi panjang.
- Jika pengguna menanyakan topik yang ADA di referensi materi promkes, prioritaskan rujukan tersebut.
- Jika pengguna menanyakan topik kesehatan umum yang BELUM ADA di referensi materi (seperti anemia, DBD, flu, dll.), jawablah menggunakan pengetahuan medis umum yang sahih, promotif, dan preventif.
- Jawab dengan bahasa yang mudah dipahami warga, terstruktur, dan aplikatif.
- Di akhir jawaban atau jika relevan, berikan anjuran kepada warga untuk berkonsultasi langsung ke RSUD Kota Bandung bila memerlukan pemeriksaan medis lebih lanjut.
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
