import streamlit as st
from dotenv import load_dotenv
import os
import re
import time
import json
try:
    import fitz  # PyMuPDF
    HAVE_PYMUPDF = True
except Exception:
    fitz = None
    HAVE_PYMUPDF = False

# Load environment variables
load_dotenv()

# Running without LangChain: use built-in rule-based handler for responses

# Global storage for application info
application_info = {"name": None, "email": None, "skills": None}

# Extract info from plain text (chat or resume)
def extract_application_info(text: str) -> str:
    name_match = re.search(r"(?:my name is|i am)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)", text, re.IGNORECASE)
    email_match = re.search(r"\b[\w\.-]+@[\w\.-]+\.\w+\b", text)
    skills_match = re.search(r"(?:skills are|i know|i can use)\s+(.+)", text, re.IGNORECASE)

    if name_match:
        application_info["name"] = name_match.group(1).title()
    if email_match:
        application_info["email"] = email_match.group(0)
    if skills_match:
        application_info["skills"] = skills_match.group(1).strip()

    return "Got it. Let me check what else I need."

# Extract info from uploaded CV
def extract_text_from_pdf(uploaded_file):
    # If PyMuPDF is available, use it to extract text from PDF.
    if HAVE_PYMUPDF and fitz is not None:
        doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return text
    # Fallback: try to read as plain bytes and decode
    try:
        raw = uploaded_file.read()
        return raw.decode(errors="ignore")
    except Exception:
        return ""

def extract_info_from_cv(text: str):
    extracted_info = {"name": None, "email": None, "skills": None}
    name_match = re.search(r"(?:Full Name:|Name:)\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)", text)
    email_match = re.search(r"\b[\w\.-]+@[\w\.-]+\.\w+\b", text)
    skills_match = re.search(r"Skills\s*-+\s*(.*?)\n(?:Projects|Certifications|$)", text, re.DOTALL)

    if name_match:
        extracted_info["name"] = name_match.group(1).strip()
    if email_match:
        extracted_info["email"] = email_match.group(0).strip()
    if skills_match:
        skills = skills_match.group(1).replace("\n", ", ").replace("\u2022", "").replace("-", "")
        extracted_info["skills"] = re.sub(r"\s+", " ", skills.strip())

    return extracted_info

# Goal checker
def check_application_goal(_: str) -> str:
    if all(application_info.values()):
        return f"✅ You're ready! Name: {application_info['name']}, Email: {application_info['email']}, Skills: {application_info['skills']}."
    else:
        missing = [k for k, v in application_info.items() if not v]
        return f"⏳ Still need: {', '.join(missing)}"

# Streamlit UI (no LangChain agent)
st.set_page_config(page_title="🎯 Job Application Assistant", layout="centered")
st.title("🧠 Goal-Based Agent: Job Application Assistant")
st.markdown("Tell me your **name**, **email**, and **skills** to complete your application!")

# Session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "goal_complete" not in st.session_state:
    st.session_state.goal_complete = False
if "download_ready" not in st.session_state:
    st.session_state.download_ready = False
if "application_summary" not in st.session_state:
    st.session_state.application_summary = ""

# Upload resume
st.sidebar.header("📤 Upload Resume (Optional)")
resume = st.sidebar.file_uploader("Upload your resume", type=["pdf", "txt"])

if resume:
    st.sidebar.success("Resume uploaded!")
    if resume.type == "application/pdf" and not HAVE_PYMUPDF:
        st.sidebar.warning("PyMuPDF not installed — PDF parsing may be limited. Consider installing PyMuPDF for better extraction.")
    text = extract_text_from_pdf(resume)
    extracted = extract_info_from_cv(text)
    for key in application_info:
        if extracted.get(key):
            application_info[key] = extracted[key]
    st.sidebar.info("🔍 Extracted info from resume:")
    for key, value in extracted.items():
        st.sidebar.markdown(f"**{key.capitalize()}:** {value}")

# Allow user to edit extracted info
st.sidebar.header("✏️ Edit extracted info")
application_info["name"] = st.sidebar.text_input("Full name", value=application_info.get("name") or "")
application_info["email"] = st.sidebar.text_input("Email", value=application_info.get("email") or "")
application_info["skills"] = st.sidebar.text_area("Skills (comma separated)", value=application_info.get("skills") or "")

# Email validation
def is_valid_email(email: str) -> bool:
    return bool(re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email))

# Progress
filled = sum(1 for v in application_info.values() if v and v.strip())
progress = int(filled / 3 * 100)
st.sidebar.progress(progress)
st.sidebar.markdown(f"**Progress:** {filled}/3 fields")

# Finalize and download
if st.sidebar.button("✅ Finalize & Prepare Download"):
    if not is_valid_email(application_info.get("email", "")):
        st.sidebar.error("Please enter a valid email before finalizing.")
    else:
        summary = (
            f"Name: {application_info['name']}\n"
            f"Email: {application_info['email']}\n"
            f"Skills: {application_info['skills']}\n"
        )
        st.session_state.application_summary = summary
        st.session_state.download_ready = True
        st.success("Application summary prepared — use the Download button to save it.")

# Reset chat
if st.sidebar.button("🔄 Reset Chat"):
    st.session_state.chat_history.clear()
    st.session_state.goal_complete = False
    st.session_state.download_ready = False
    st.session_state.application_summary = ""
    for key in application_info:
        application_info[key] = None
    if hasattr(st, "experimental_rerun"):
        st.experimental_rerun()
    else:
        # Older/newer Streamlit may not have experimental_rerun; force a rerun
        try:
            st.experimental_set_query_params(_reset=str(time.time()))
        except Exception:
            pass

# Chat input
user_input = st.chat_input("Type here...")

if user_input:
    st.session_state.chat_history.append(("user", user_input))
    # Extract info and respond using local extractor
    bot_reply = extract_application_info(user_input)
    st.session_state.chat_history.append(("bot", bot_reply))
    goal_status = check_application_goal("check")
    st.session_state.chat_history.append(("status", goal_status))

    if "you're ready" in goal_status.lower():
        st.session_state.goal_complete = True
        summary = (
            f"✅ Name: {application_info['name']}\n"
            f"📧 Email: {application_info['email']}\n"
            f"🛠️ Skills: {application_info['skills']}\n"
        )
        st.session_state.application_summary = summary
        st.session_state.download_ready = True

# Chat UI with avatars
for sender, message in st.session_state.chat_history:
    if sender == "user":
        with st.chat_message("🧑"):
            st.markdown(message)
    elif sender == "bot":
        with st.chat_message("🤖"):
            st.markdown(message)
    elif sender == "status":
        with st.chat_message("📊"):
            st.info(message)

# Final message
if st.session_state.goal_complete:
    st.success("🎉 All information collected! You're ready to apply!")

# Download summary
if st.session_state.download_ready:
    st.download_button(
        label="📥 Download Application Summary",
        data=st.session_state.application_summary,
        file_name="application_summary.txt",
        mime="text/plain"
    )
