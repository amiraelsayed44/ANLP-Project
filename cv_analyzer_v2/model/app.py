import streamlit as st
import pdfplumber
import io
from pathlib import Path
from nlp_analyzer import analyze_cv

st.set_page_config(
    page_title="CV Analyzer",
    page_icon="📄",
    layout="wide"
)

st.title("📄 CV Analyzer")
st.markdown("Upload your CV or paste the text below to get instant feedback.")

with st.sidebar:
    st.header("Settings")
    use_ai = st.toggle("AI Suggestions (Gemini)", value=False)
    # if use_ai:
    #     st.info("Make sure GOOGLE_API_KEY is set in your .env file.")
    st.divider()
    st.caption("Powered by spaCy NER + Gemini AI")

tab1, tab2 = st.tabs(["📋 Paste Text", "📁 Upload File"])

cv_text = ""

with tab1:
    cv_text_input = st.text_area(
        "Paste your CV here",
        height=300,
        placeholder="Paste your CV content here..."
    )
    if cv_text_input:
        cv_text = cv_text_input

with tab2:
    uploaded = st.file_uploader("Upload a .txt or .pdf file", type=["txt", "pdf"])
    if uploaded:
        if uploaded.name.endswith(".pdf"):
            with pdfplumber.open(io.BytesIO(uploaded.read())) as pdf:
                pages = [page.extract_text() or "" for page in pdf.pages]
            cv_text = "\n".join(pages).strip()
        else:
            cv_text = uploaded.read().decode("utf-8", errors="ignore")

        st.success(f"File loaded: {uploaded.name}")
        with st.expander("Preview"):
            st.text(cv_text[:500] + ("..." if len(cv_text) > 500 else ""))

if st.button("Analyze CV", type="primary", disabled=not cv_text):
    with st.spinner("Analyzing..."):
        result = analyze_cv(cv_text, use_ai=use_ai)

    if "error" in result:
        st.error(result["error"])
        st.stop()

    st.divider()

    col1, col2, col3 = st.columns(3)
    col1.metric("Word Count",        result["word_count"])
    col2.metric("Sections Found",    len(result["sections_found"]))
    col3.metric("Entities Detected", len(result["named_entities"]))

    st.divider()

    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("✅ Sections Detected")
        if result["sections_found"]:
            for sec in result["sections_found"]:
                st.success(sec.replace("_", " ").title())
        else:
            st.warning("No sections detected.")

        st.subheader("🛠 Skills")
        if result["skills"]:
            st.write(", ".join(result["skills"]))
        else:
            st.warning("No skills detected.")

        st.subheader("📬 Contact Info")
        if result["contact_info"]:
            for key, val in result["contact_info"].items():
                st.write(f"**{key.title()}:** {val}")
        else:
            st.warning("No contact info found.")

    with col_right:
        st.subheader("💡 Suggestions")
        for tip in result["suggestions"]:
            st.warning(tip)

        st.subheader("🏷 Named Entities")
        if result["named_entities"]:
            color_map = {
                "NAME":               "🟣",
                "SKILLS":             "🟢",
                "DESIGNATION":        "🔵",
                "COMPANIES_WORKED_AT":"🟡",
                "COLLEGE_NAME":       "🟠",
                "DEGREE":             "🔴",
                "LOCATION":           "⚪",
                "EMAIL_ADDRESS":      "📧",
                "GRADUATION_YEAR":    "📅",
            }
            for ent in result["named_entities"]:
                icon = color_map.get(ent["label"], "⚫")
                st.write(f"{icon} **{ent['label']}** — {ent['text']}")
        else:
            st.info("No entities detected.")