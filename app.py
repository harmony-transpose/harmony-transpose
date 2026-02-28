import streamlit as st
import io
import os

# ───────────────────────────────────────────────
# ייבוא הלוגיקה שלך
# ───────────────────────────────────────────────
from logic import process_text  # ← שנה ל־import שלך


# ───────────────────────────────────────────────
# פונקציות קריאה/כתיבה לכל סוג קובץ
# ───────────────────────────────────────────────

def read_file(uploaded_file) -> str:
    ext = os.path.splitext(uploaded_file.name)[1].lower()

    if ext == ".txt":
        return uploaded_file.read().decode("utf-8")

    elif ext == ".pdf":
        import fitz  # pip install pymupdf
        data = uploaded_file.read()
        doc = fitz.open(stream=data, filetype="pdf")
        return "\n".join(page.get_text() for page in doc)

    elif ext == ".docx":
        from docx import Document  # pip install python-docx
        doc = Document(uploaded_file)
        return "\n".join(para.text for para in doc.paragraphs)

    else:
        raise ValueError(f"סוג קובץ לא נתמך: {ext}")


def write_file(text: str, original_filename: str) -> tuple[bytes, str]:
    """מחזיר (bytes של הקובץ, mime type)"""
    ext = os.path.splitext(original_filename)[1].lower()

    if ext == ".txt":
        return text.encode("utf-8"), "text/plain"

    elif ext == ".pdf":
        import fitz
        doc = fitz.open()
        page = doc.new_page()
        page.insert_text((50, 50), text, fontsize=11)
        pdf_bytes = doc.tobytes()
        return pdf_bytes, "application/pdf"

    elif ext == ".docx":
        from docx import Document
        doc = Document()
        for line in text.split("\n"):
            doc.add_paragraph(line)
        buf = io.BytesIO()
        doc.save(buf)
        return buf.getvalue(), "application/vnd.openxmlformats-officedocument.wordprocessingml.document"

    else:
        raise ValueError(f"סוג קובץ לא נתמך: {ext}")


# ───────────────────────────────────────────────
# ממשק המשתמש
# ───────────────────────────────────────────────

st.set_page_config(page_title="Harmonic Modulation", page_icon="🎵")
st.title("🎵 Harmonic Modulation")
st.write("Upload a file with harmony and get it modulated")

uploaded_file = st.file_uploader(
    "Choose a file",
    type=["txt", "pdf", "docx"]
)

if uploaded_file:
    try:
        # Read
        original_text = read_file(uploaded_file)

        # Show original
        with st.expander("Original text"):
            st.text(original_text)

        # Process
        with st.spinner("Processing..."):
            result_text = process_text(original_text)  # ← your logic

        # Show result
        with st.expander("Modulated text", expanded=True):
            st.text(result_text)

        # Write and create download button
        output_bytes, mime = write_file(result_text, uploaded_file.name)
        output_filename = "modulated_" + uploaded_file.name

        st.download_button(
            label="⬇️ Download modulated file",
            data=output_bytes,
            file_name=output_filename,
            mime=mime
        )

    except Exception as e:
        st.error(f"Error: {e}")
