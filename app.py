import os
import sqlite3
import streamlit as st

# Configuración de la página
st.set_page_config(
    page_title="What We Had Done Before Coming to Class", page_icon="🎓", layout="wide"
)

DB_NAME = "database.db"


def init_db():
  """Inicializa la base de datos SQLite para guardar los aportes."""
  conn = sqlite3.connect(DB_NAME)
  c = conn.cursor()
  c.execute("""
        CREATE TABLE IF NOT EXISTS entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            member_name TEXT NOT NULL,
            entry_num INTEGER NOT NULL,
            sentence TEXT NOT NULL,
            media_path TEXT,
            media_type TEXT
        )
    """)
  c.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY,
            evaluator_name TEXT,
            general_comments TEXT,
            grade TEXT
        )
    """)
  # Insertar el registro inicial con el nombre del profesor por defecto
  c.execute("""
        INSERT OR IGNORE INTO feedback (id, evaluator_name, general_comments, grade)
        VALUES (1, 'Aldemar Cojo Guatame', '', '')
    """)
  conn.commit()
  conn.close()


def get_entries(member_name):
  conn = sqlite3.connect(DB_NAME)
  c = conn.cursor()
  c.execute(
      "SELECT entry_num, sentence, media_path, media_type FROM entries WHERE"
      " member_name = ?",
      (member_name,),
  )
  data = c.fetchall()
  conn.close()
  return data


def save_entry(member_name, entry_num, sentence, media_path, media_type):
  conn = sqlite3.connect(DB_NAME)
  c = conn.cursor()
  c.execute(
      "SELECT id FROM entries WHERE member_name = ? AND entry_num = ?",
      (member_name, entry_num),
  )
  exists = c.fetchone()
  if exists:
    c.execute(
        "UPDATE entries SET sentence = ?, media_path = ?, media_type = ? WHERE"
        " member_name = ? AND entry_num = ?",
        (sentence, media_path, media_type, member_name, entry_num),
    )
  else:
    c.execute(
        "INSERT INTO entries (member_name, entry_num, sentence, media_path,"
        " media_type) VALUES (?, ?, ?, ?, ?)",
        (member_name, entry_num, sentence, media_path, media_type),
    )
  conn.commit()
  conn.close()


def get_feedback():
  conn = sqlite3.connect(DB_NAME)
  c = conn.cursor()
  c.execute("SELECT evaluator_name, general_comments, grade FROM feedback WHERE id = 1")
  data = c.fetchone()
  conn.close()
  return data if data else ("Aldemar Cojo Guatame", "", "")


def save_feedback(evaluator_name, general_comments, grade):
  conn = sqlite3.connect(DB_NAME)
  c = conn.cursor()
  c.execute(
      "UPDATE feedback SET evaluator_name = ?, general_comments = ?, grade = ?"
      " WHERE id = 1",
      (evaluator_name, general_comments, grade),
  )
  conn.commit()
  conn.close()


# Inicializar base de datos
init_db()

# Lista de los 5 integrantes del grupo
TEAM_MEMBERS = [
    "Carlos Castañeda",
    "Juan Suarez",
    "Yirzon Contreras",
    "David Jamaica",
    "Daniel Moreno",
]

# ------------------------------------------------------------------------------
# ENCABEZADO Y EXPLICACIÓN GRAMATICAL
# ------------------------------------------------------------------------------
st.title("🎓 What We Had Done Before Coming to Class")
st.subheader("English Course Presentation — Past Perfect Tense")

st.info("""
💡 **Grammar Focus — Past Perfect:** *Subject + HAD + Past Participle*  
This interactive platform displays two past perfect statements for each member, showing the actions they **had completed** (eating, working, commuting) **before arriving at university/class**.
""")

# ------------------------------------------------------------------------------
# BARRA LATERAL (Formulario de Aporte)
# ------------------------------------------------------------------------------
st.sidebar.header("📝 Submit Your Contribution")
st.sidebar.markdown(
    "Each member must complete 2 entries in English about what they had done"
    " before arriving at university."
)

selected_member = st.sidebar.selectbox("Select Member Name:", TEAM_MEMBERS)
entry_num = st.sidebar.radio("Entry Number:", [1, 2])

sentence = st.sidebar.text_area(
    "Sentence in Past Perfect:",
    placeholder="e.g., Before I arrived at university, I had eaten a quick lunch...",
)

uploaded_file = st.sidebar.file_uploader(
    "Upload Photo or Video (Optional):", type=["png", "jpg", "jpeg", "mp4", "mov"]
)

media_path = None
media_type = None

if uploaded_file is not None:
  os.makedirs("uploads", exist_ok=True)
  media_path = os.path.join("uploads", uploaded_file.name)
  with open(media_path, "wb") as f:
    f.write(uploaded_file.getbuffer())
  if uploaded_file.type.startswith("image"):
    media_type = "image"
  elif uploaded_file.type.startswith("video"):
    media_type = "video"

if st.sidebar.button("💾 Save Entry"):
  if sentence.strip() == "":
    st.sidebar.error("Please write a sentence before saving.")
  else:
    save_entry(selected_member, entry_num, sentence, media_path, media_type)
    st.sidebar.success(f"Entry #{entry_num} for {selected_member} saved successfully!")
    st.rerun()

# ------------------------------------------------------------------------------
# CUERPO PRINCIPAL (Pestañas por Integrante)
# ------------------------------------------------------------------------------
st.markdown("---")
st.header("👥 Group Contributions")

tabs = st.tabs(TEAM_MEMBERS)

for i, member in enumerate(TEAM_MEMBERS):
  with tabs[i]:
    st.subheader(f"📌 Contributions by {member}")
    entries = get_entries(member)

    # Organizar las entradas por número (1 y 2)
    entry_dict = {1: None, 2: None}
    for e_num, sent, m_path, m_type in entries:
      entry_dict[e_num] = (sent, m_path, m_type)

    col1, col2 = st.columns(2)

    with col1:
      st.markdown("### Entry #1")
      if entry_dict[1]:
        sent, m_path, m_type = entry_dict[1]
        st.markdown(f"**Sentence:** *\"{sent}\"*")
        if m_path and os.path.exists(m_path):
          if m_type == "image":
            st.image(m_path, use_container_width=True)
          elif m_type == "video":
            st.video(m_path)
        else:
          st.caption("📷 No image or video attached.")
      else:
        st.warning("⚠️ No entry submitted yet.")

    with col2:
      st.markdown("### Entry #2")
      if entry_dict[2]:
        sent, m_path, m_type = entry_dict[2]
        st.markdown(f"**Sentence:** *\"{sent}\"*")
        if m_path and os.path.exists(m_path):
          if m_type == "image":
            st.image(m_path, use_container_width=True)
          elif m_type == "video":
            st.video(m_path)
        else:
          st.caption("📷 No image or video attached.")
      else:
        st.warning("⚠️ No entry submitted yet.")

# ------------------------------------------------------------------------------
# ZONA DE CALIFICACIÓN Y RETROALIMENTACIÓN DEL PROFESOR
# ------------------------------------------------------------------------------
st.markdown("---")
st.header("💬 Teacher's Feedback & Grading Zone")
st.markdown(
    "This area is designed for the professor to leave comments or evaluate our"
    " grammar structure."
)

evaluator_name, general_comments, grade = get_feedback()

with st.form("feedback_form"):
  teacher_name = st.text_input(
      "Teacher's Name / Evaluator:", value=evaluator_name or "Aldemar Cojo Guatame"
  )
  comments = st.text_area(
      "General Comments & Corrections:",
      value=general_comments,
      placeholder=(
          "Write feedback about past perfect structure, punctuation, etc."
      ),
  )
  grade_input = st.text_input(
      "Grade / Score:", value=grade, placeholder="e.g., 5.0 / A"
  )

  submitted = st.form_submit_button("Submit Feedback")
  if submitted:
    save_feedback(teacher_name, comments, grade_input)
    st.success("Feedback saved successfully!")
    st.rerun()