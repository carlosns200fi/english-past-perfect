import os
import sqlite3
import streamlit as st

# ---------------------------------------------------------
# 1. CONFIGURACIÓN DE LA PÁGINA Y BASE DE DATOS
# ---------------------------------------------------------
st.set_page_config(
    page_title="Past Perfect Timeline - Before University",
    page_icon="🎓",
    layout="wide",
)

DB_NAME = "group_activities.db"
UPLOAD_DIR = "uploaded_media"

# Crear directorio para guardar imágenes y videos cargados
os.makedirs(UPLOAD_DIR, exist_ok=True)


def init_db():
    """Inicializa la base de datos SQLite para guardar los aportes."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            member_name TEXT NOT NULL,
            entry_num INTEGER NOT NULL,
            sentence TEXT NOT NULL,
            media_path TEXT,
            media_type TEXT
        )
    """
    )
    conn.commit()
    conn.close()


init_db()

# Lista de los 5 integrantes del grupo
TEAM_MEMBERS = ["Carlos Castañeda", "Juan Suarez", "Yirzon Contreras", "David Jamaica", "Daniel Moreno"]

# ---------------------------------------------------------
# 2. ENCABEZADO Y EXPLICACIÓN GRAMATICAL (Para el Profesor)
# ---------------------------------------------------------
st.title("🎓 Our Lives Before University")
st.subheader("Interactive Past Perfect Showcase")

st.info(
    "💡 **Grammar Focus — Past Perfect:** "
    "`Subject + had + past participle...`\n\n"
    "This interactive platform displays 2 personal activities per group member describing "
    "what they **had done** or **had experienced** before entering university."
)

st.divider()

# ---------------------------------------------------------
# 3. BARRA LATERAL: FORMULARIO PARA REGISTRAR / EDITAR
# ---------------------------------------------------------
st.sidebar.header("📝 Submit Your Contribution")
st.sidebar.write("Each member must complete **2 entries** in English.")

selected_member = st.sidebar.selectbox("Select Member Name:", TEAM_MEMBERS)
entry_number = st.sidebar.radio("Entry Number:", [1, 2], horizontal=True)

sentence_input = st.sidebar.text_area(
    "Sentence in Past Perfect:",
    placeholder="e.g., Before I entered university, I had worked as a cargo driver for three years.",
    help="Remember to use HAD + Past Participle!",
)

uploaded_file = st.sidebar.file_uploader(
    "Upload Photo or Video (Optional):",
    type=["png", "jpg", "jpeg", "mp4", "mov"],
)

if st.sidebar.button("💾 Save Entry", type="primary"):
    if not sentence_input.strip():
        st.sidebar.error("Please write a valid Past Perfect sentence.")
    else:
        file_path = None
        file_type = None

        if uploaded_file is not None:
            file_type = uploaded_file.type.split("/")[0]  # 'image' or 'video'
            file_path = os.path.join(
                UPLOAD_DIR, f"{selected_member}_entry{entry_number}_{uploaded_file.name}"
            )
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()

        c.execute(
            "SELECT id FROM entries WHERE member_name = ? AND entry_num = ?",
            (selected_member, entry_number),
        )
        existing = c.fetchone()

        if existing:
            c.execute(
                """
                UPDATE entries 
                SET sentence = ?, media_path = ?, media_type = ?
                WHERE member_name = ? AND entry_num = ?
            """,
                (
                    sentence_input,
                    file_path,
                    file_type,
                    selected_member,
                    entry_number,
                ),
            )
        else:
            c.execute(
                """
                INSERT INTO entries (member_name, entry_num, sentence, media_path, media_type)
                VALUES (?, ?, ?, ?, ?)
            """,
                (
                    selected_member,
                    entry_number,
                    sentence_input,
                    file_path,
                    file_type,
                ),
            )

        conn.commit()
        conn.close()
        st.sidebar.success(
            f"Entry {entry_number} for {selected_member} saved successfully!"
        )
        st.rerun()

# ---------------------------------------------------------
# 4. MOSTRAR LOS APORTES DE LOS 5 INTEGRANTES
# ---------------------------------------------------------
st.header("👥 Group Contributions")

conn = sqlite3.connect(DB_NAME)
c = conn.cursor()
c.execute(
    "SELECT member_name, entry_num, sentence, media_path, media_type FROM entries"
)
records = c.fetchall()
conn.close()

data_by_member = {member: {} for member in TEAM_MEMBERS}
for row in records:
    m_name, e_num, sentence, m_path, m_type = row
    data_by_member[m_name][e_num] = {
        "sentence": sentence,
        "media_path": m_path,
        "media_type": m_type,
    }

tabs = st.tabs(TEAM_MEMBERS)

for i, member in enumerate(TEAM_MEMBERS):
    with tabs[i]:
        st.subheader(f"📌 Contributions by {member}")
        col1, col2 = st.columns(2)

        for e_num, col in zip([1, 2], [col1, col2]):
            with col:
                st.markdown(f"#### Entry #{e_num}")
                entry_data = data_by_member[member].get(e_num)

                if entry_data:
                    st.write(f"**Sentence:** *\"{entry_data['sentence']}\"*")
                    m_path = entry_data["media_path"]
                    m_type = entry_data["media_type"]

                    if m_path and os.path.exists(m_path):
                        if m_type == "image":
                            st.image(m_path, use_container_width=True)
                        elif m_type == "video":
                            st.video(m_path)
                    else:
                        st.caption("📷 No image or video attached.")
                else:
                    st.warning("⚠️ No entry submitted yet.")

st.divider()

# ---------------------------------------------------------
# 5. SECCIÓN INTERACTIVA PARA EL PROFESOR (FEEDBACK)
# ---------------------------------------------------------
st.header("💬 Teacher's Feedback & Grading Zone")
st.write(
    "This area is designed for the professor to leave comments or evaluate our grammar structure."
)

teacher_name = st.text_input("Teacher's Name / Evaluator:", value="Prof. Johnson")
feedback_text = st.text_area(
    "Teacher's Comments / Feedback:",
    placeholder="Great use of Past Perfect structures!",
)
grade = st.slider("Score / Grade:", 0.0, 5.0, 5.0, 0.1)

if st.button("Submit Teacher Evaluation"):
    st.balloons()
    st.success(
        f"Thank you, {teacher_name}! Evaluation recorded with grade: {grade}/5.0"
    )