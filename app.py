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

# Inisialisasi Google GenAI client
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

# 3. Riwayat Percakapan
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant", 
            "content": "Halo! Saya asisten edukasi kesehatan DekatSehat. Ada yang ingin Anda tanyakan seputar materi kesehatan atau pencegahan penyakit?"
        }
    ]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 4. Input dan Respon Chatbot
if user_prompt := st.chat_input("Ketik pertanyaan kesehatan Anda di sini..."):
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.markdown(user_prompt)

    # Instruksi sistem untuk asisten promosi kesehatan
    system_instruction = f"""
    Anda adalah asisten promosi kesehatan (Promkes) bernama DekatSehat.
    Tugas utama Anda: Memberikan informasi dan edukasi kesehatan dengan bahasa ramah, santun, jelas, dan mudah dipahami oleh masyarakat umum.

    Rujukan materi resmi:
    \"\"\"{context_text}\"\"\"

    Aturan ketat:
    1. Utamakan menjawab berdasarkan fakta yang tercantum pada rujukan materi resmi di atas.
    2. Jelaskan konsep medis dengan bahasa awam dan analogi sederhana.
    3. Jika pengguna menanyakan hal medis di luar materi rujukan atau memerlukan tindakan medis/obat khusus, ingatkan dengan ramah untuk berkonsultasi langsung ke dokter atau fasilitas kesehatan terdekat (Puskesmas/Rumah Sakit).
    4. Anda BUKAN pengganti dokter. Jangan memberikan diagnosis pasti atau meresepkan dosis obat klinis.
    """

    with st.chat_message("assistant"):
        with st.spinner("Sedang mencari materi edukasi..."):
            try:
                contents = []
                for m in st.session_state.messages:
                    role = "user" if m["role"] == "user" else "model"
                    contents.append(f"{role}: {m['content']}")
                
                full_prompt = f"{system_instruction}\n\nPercakapan sejauh ini:\n" + "\n".join(contents)

                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=full_prompt,
                )
                answer = response.text
                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
            except Exception as err:
                st.error(f"Terjadi kendala saat memproses: {err}")
