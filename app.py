import streamlit as st
from google import genai
import PyPDF2
import os

st.set_page_config(page_title="DekatSehat", page_icon="🩺", layout="centered")

# Inisialisasi API Client Gemini versi baru
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

@st.cache_resource
def load_pdf_context():
    text = ""
    pdf_files = [f for f in os.listdir(".") if f.endswith(".pdf")]
    for pdf_file in pdf_files:
        try:
            with open(pdf_file, "rb") as file:
                reader = PyPDF2.PdfReader(file)
                # Ambil 35 halaman pertama per dokumen (bagian substansi utama)
                for page in reader.pages[:35]:
                    extracted = page.extract_text()
                    if extracted:
                        text += extracted + "\n"
        except Exception as e:
            continue
    # Batasi muatan maksimal teks yang dikirim ke AI
    return text[:80000] if text else "Materi promosi kesehatan umum."

context_data = load_pdf_context()

st.title("🩺 DekatSehat")
st.caption("Asisten Edukasi & Informasi Kesehatan Masyarakat berbasis AI")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Halo! Saya asisten edukasi kesehatan DekatSehat. Ada yang ingin Anda tanyakan seputar materi kesehatan atau pencegahan penyakit?"}
    ]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

if prompt := st.chat_input("Ketik pertanyaan kesehatan Anda di sini..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    system_instruction = f"""
    Anda adalah 'DekatSehat', asisten virtual promosi kesehatan masyarakat yang ramah, informatif, dan mudah dipahami.
    Gunakan referensi materi promkes berikut untuk memperkaya jawaban Anda:
    {context_data}

    Instruksi:
    - Jawab secara edukatif, empatik, dan terstruktur.
    - Sertakan pesan pencegahan yang aplikatif untuk masyarakat.
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
