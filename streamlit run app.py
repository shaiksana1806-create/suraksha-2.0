import streamlit as st
import pandas as pd
import sqlite3
import time
from datetime import datetime
import plotly.express as px
from fpdf import FPDF

# ---------------- CONFIG ----------------
st.set_page_config("C3IS MLAT SYSTEM", layout="wide")

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

def generate_mlat(case):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 12)

    pdf.cell(200, 10, "MLAT REPORT", ln=True)
    pdf.ln(5)

    for k, v in case.items():
        pdf.cell(200, 10, f"{k}: {v}", ln=True)

    filename = f"{case['case_id']}.pdf"
    pdf.output(filename)
    return filename

# ---------------- MEMORY ----------------
if "alerts" not in st.session_state:
    st.session_state.alerts = []

# ---------------- START ----------------
init_db()

st.title("🛡 C3IS - Cyber Crime & MLAT Intelligence System")

# ---------------- INPUT ----------------
st.header("📥 Report Case")

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
    cid = generate_case_id()

    jurisdiction = detect_jurisdiction(desc)

    st.info(f"🧠 MLAT RESULT: {jurisdiction}")

    if "INTERNATIONAL" in jurisdiction:
        st.warning("🚨 MLAT ALERT TRIGGERED")

        st.session_state.alerts.append({
            "case_id": cid,
            "location": location
        })

        # AUTO PDF
        report = {
            "case_id": cid,
            "user": user,
            "title": title,
            "description": desc,
            "location": location,
            "fraud": fraud,
            "jurisdiction": jurisdiction
        }

        file = generate_mlat(report)
        st.success(f"📄 MLAT REPORT GENERATED: {file}")

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

    st.success(f"✅ Case Stored with ID: {cid}")

# ---------------- DASHBOARD ----------------
st.header("📊 LIVE DASHBOARD")

data = fetch_cases()

if len(data) == 0:
    st.warning("No data yet")
else:
    df = pd.DataFrame(data, columns=[
        "case_id","user","title","desc",
        "location","fraud","jurisdiction","time"
    ])

    st.metric("Total Cases", len(df))

    st.dataframe(df)

    # ---------------- GRAPHS ----------------
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

    # ---------------- ADVANCED GRAPH ----------------
    st.subheader("📊 Fraud vs Location")

    fig = px.histogram(df, x="location", color="fraud", barmode="group")
    st.plotly_chart(fig)

# ---------------- ALERTS ----------------
st.header("🚨 MLAT Alerts")

if len(st.session_state.alerts) == 0:
    st.info("No Alerts")
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
        st.error("Not Found")
