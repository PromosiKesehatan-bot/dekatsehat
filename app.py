import streamlit as st
from google import genai
import PyPDF2
import os

st.set_page_config(page_title="SAE RSUD Kota Bandung", page_icon="🩺", layout="centered")

# Inisialisasi API Client Gemini
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

@st.cache_resource
def load_context_data():
    txt_data = ""
    pdf_data = ""
    
    # 1. BACA FILE TXT TERLEBIH DAHULU (Prioritas Utama Jadwal)
    for f in os.listdir("."):
        if f.endswith(".txt") and f != "requirements.txt":
            try:
                with open(f, "r", encoding="utf-8") as file:
                    txt_data += file.read() + "\n\n"
            except Exception:
                continue

    # 2. BACA FILE PDF
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

# Tampilkan status context di sidebar
st.sidebar.title("Informasi Sistem")
st.sidebar.info(f"Total Karakter Terbaca: {len(context_data)}")

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

    prompt_instruksi = f"""
Anda adalah 'SAE' (Suara, Aksara Edukasi), asisten AI resmi RSUD Kota Bandung.

Berikut adalah DATABASE RESMI JADWAL & MATERI KESEHATAN RSUD KOTA BANDUNG:
---
{context_data}
---

ATURAN MENJAWAB:
1. Pahami sinonim kata poliklinik, misalnya: "poli syaraf" = "klinik saraf" = "neurologi", "poli kandungan" = "obgyn", "poli anak" = "pediatri", "poli jiwa" = "psikiatri".
2. JIKA pengguna menanyakan jadwal poli atau dokter, CARI di DATABASE RESMI di atas. Jika poli/dokter tersebut ada di database, WAJIB sebutkan secara langsung dan lengkap:
   - Nama poliklinik
   - Nama lengkap dokter spesialis
   - Hari praktik dan jam praktiknya
   JANGAN mengarahkan ke web/WA jika jadwalnya sudah tertulis di database.
3. JIKA jadwal yang ditanyakan benar-benar tidak ditemukan di database di atas, baru arahkan untuk konfirmasi melalui kontak/pendaftaran resmi RSUD Kota Bandung.
4. Gunakan gaya bahasa yang ramah, santun, dan jelas.

Pertanyaan Pengguna: {prompt}
Jawaban Anda:
"""

    with st.chat_message("assistant"):
        with st.spinner("Sedang mencari informasi..."):
            try:
                response = client.models.generate_content(
                    model="gemini-3.8-flash",
                    contents=prompt_instruksi
                )
                jawaban = response.text
                st.write(jawaban)
                st.session_state.messages.append({"role": "assistant", "content": jawaban})
            except Exception as e:
                st.error(f"Terjadi kendala: {e}")
