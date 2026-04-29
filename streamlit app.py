import streamlit as st
import pandas as pd
import sqlite3
import time
from datetime import datetime
import plotly.express as px
from fpdf import FPDF
import os

# ---------------- CONFIG ----------------
st.set_page_config("MLAT SYSTEM", layout="wide")

DB = "cases.db"

# ---------------- DATABASE ----------------
def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS cases (
        case_id TEXT PRIMARY KEY,
        user TEXT,
        title TEXT,
        description TEXT,
        location TEXT,
        fraud TEXT,
        jurisdiction TEXT,
        time TEXT
    )
    """)

    conn.commit()
    conn.close()

def insert_case(data):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("INSERT INTO cases VALUES (?,?,?,?,?,?,?,?)", data)
    conn.commit()
    conn.close()

def fetch_cases():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT * FROM cases")
    rows = c.fetchall()
    conn.close()
    return rows

def get_case(cid):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT * FROM cases WHERE case_id=?", (cid,))
    row = c.fetchone()
    conn.close()
    return row

# ---------------- UTILS ----------------
def generate_case_id():
    return f"CASE-{int(time.time()*1000)}"

def detect_jurisdiction(text):
    text = text.lower()
    keywords = ["paypal", "bitcoin", "server", "gmail", "binance"]

    for k in keywords:
        if k in text:
            return "INTERNATIONAL (MLAT REQUIRED)"
    return "LOCAL (INDIA)"

def generate_mlat_pdf(case):
    filename = f"{case['case_id']}.pdf"

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 12)

    pdf.cell(200, 10, "MLAT CYBERCRIME REPORT", ln=True, align="C")
    pdf.ln(10)

    for k, v in case.items():
        pdf.cell(200, 10, f"{k}: {v}", ln=True)

    pdf.output(filename)

    return filename

# ---------------- MEMORY ----------------
if "alerts" not in st.session_state:
    st.session_state.alerts = []

# ---------------- INIT ----------------
init_db()

st.title("🛡 C3IS - MLAT Intelligence System")

# ---------------- INPUT ----------------
st.header("📥 Submit Cybercrime Case")

col1, col2 = st.columns(2)

with col1:
    user = st.text_input("User Name")
    title = st.text_input("Case Title")
    location = st.text_input("Location")

with col2:
    fraud = st.selectbox("Fraud Type", ["OTP", "Bank", "Crypto"])
    desc = st.text_area("Description")

# ---------------- SUBMIT ----------------
if st.button("Submit Case"):
    if user and title and desc and location:
        cid = generate_case_id()
        jurisdiction = detect_jurisdiction(desc)

        st.info(f"🧠 MLAT RESULT: {jurisdiction}")

        pdf_file = None

        if "INTERNATIONAL" in jurisdiction:
            st.warning("🚨 MLAT ALERT TRIGGERED")

            # Create alert
            st.session_state.alerts.append({
                "case_id": cid,
                "location": location
            })

            # Generate PDF
            report = {
                "case_id": cid,
                "user": user,
                "title": title,
                "description": desc,
                "location": location,
                "fraud": fraud,
                "jurisdiction": jurisdiction,
                "time": str(datetime.now())
            }

            pdf_file = generate_mlat_pdf(report)

            st.success("📄 MLAT REPORT GENERATED")

            # Download button
            with open(pdf_file, "rb") as f:
                st.download_button(
                    label="⬇ Download MLAT Report",
                    data=f,
                    file_name=pdf_file,
                    mime="application/pdf"
                )

        # Store case
        data = (
            cid,
            user,
            title,
            desc,
            location,
            fraud,
            jurisdiction,
            str(datetime.now())
        )

        insert_case(data)

        st.success(f"✅ Case Stored: {cid}")

    else:
        st.error("Please fill all fields")

# ---------------- DASHBOARD ----------------
st.header("📊 LIVE DASHBOARD")

data = fetch_cases()

if len(data) > 0:
    df = pd.DataFrame(data, columns=[
        "case_id","user","title","desc",
        "location","fraud","jurisdiction","time"
    ])

    st.metric("Total Cases", len(df))
    st.dataframe(df)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("Fraud Types")
        st.bar_chart(df["fraud"].value_counts())

    with col2:
        st.subheader("Locations")
        st.bar_chart(df["location"].value_counts())

    with col3:
        st.subheader("Jurisdiction")
        st.bar_chart(df["jurisdiction"].value_counts())

    st.subheader("📊 Fraud vs Location")
    fig = px.histogram(df, x="location", color="fraud", barmode="group")
    st.plotly_chart(fig)

else:
    st.warning("No cases yet")

# ---------------- ALERTS ----------------
st.header("🚨 MLAT Alerts")

if len(st.session_state.alerts) == 0:
    st.info("No active alerts")
else:
    for a in st.session_state.alerts:
        st.error(f"ALERT → Case: {a['case_id']} | Location: {a['location']}")

# ---------------- SEARCH ----------------
st.header("🔎 Search Case")

search_id = st.text_input("Enter Case ID")

if st.button("Search"):
    result = get_case(search_id)

    if result:
        st.success("Case Found")
        st.write(result)
    else:
        st.error("Case Not Found")
