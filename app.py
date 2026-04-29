import streamlit as st
import pandas as pd
from datetime import datetime

from db import init_db, insert_case, fetch_cases, get_case
from auth import login, register
from ml_engine import detect_jurisdiction
from alert import trigger_alert, alerts
from blockchain import add_block
from mlat import generate
from utils import generate_case_id

st.set_page_config("C3IS MLAT SYSTEM", layout="wide")

init_db()

if "user" not in st.session_state:
    st.session_state.user = None


# ---------------- AUTH ----------------
def auth():
    st.title("🛡 MLAT CYBER SYSTEM")

    mode = st.radio("Mode", ["LOGIN", "REGISTER"])

    u = st.text_input("Username")
    p = st.text_input("Password", type="password")

    if mode == "REGISTER":
        if st.button("Register"):
            if register(u, p):
                st.success("Registered")
            else:
                st.error("User exists")

    if mode == "LOGIN":
        if st.button("Login"):
            if login(u, p):
                st.session_state.user = u
                st.rerun()
            else:
                st.error("Invalid login")


# ---------------- USER ----------------
def user():
    st.header("📥 Submit Cybercrime Case")

    title = st.text_input("Title")
    desc = st.text_area("Description")
    location = st.text_input("Location")
    fraud = st.selectbox("Fraud Type", ["OTP", "Bank", "Crypto"])

    if st.button("Submit Case"):
        cid = generate_case_id()

        jurisdiction = detect_jurisdiction(desc)

        # 🔥 SHOW MLAT OUTPUT (FIXED)
        st.info(f"🧠 MLAT RESULT: {jurisdiction}")

        if "INTERNATIONAL" in jurisdiction:
            trigger_alert(cid, location)
            st.warning("🚨 MLAT ALERT TRIGGERED")

            # 🔥 AUTO REPORT
            report = {
                "case_id": cid,
                "user": st.session_state.user,
                "title": title,
                "description": desc,
                "location": location,
                "fraud": fraud,
                "jurisdiction": jurisdiction
            }

            file = generate(report)
            st.success(f"📄 MLAT REPORT GENERATED: {file}")

        data = (
            cid,
            st.session_state.user,
            title,
            desc,
            location,
            fraud,
            jurisdiction,
            str(datetime.now())
        )

        insert_case(data)
        add_block(data)

        st.success(f"Case Created: {cid}")


# ---------------- ADMIN ----------------
def admin():
    st.header("📊 CYBER INTELLIGENCE DASHBOARD")

    st.autorefresh(interval=3000)

    data = fetch_cases()

    if len(data) == 0:
        st.warning("No cases found")
        return

    df = pd.DataFrame(data, columns=[
        "case_id","user","title","desc","location",
        "fraud","jurisdiction","time"
    ])

    st.metric("Total Cases", len(df))

    st.dataframe(df)

    # 📊 GRAPHS (FIXED)
    st.subheader("Fraud Analysis")
    st.bar_chart(df["fraud"].value_counts())

    st.subheader("Location Analysis")
    st.bar_chart(df["location"].value_counts())

    st.subheader("Jurisdiction Analysis")
    st.bar_chart(df["jurisdiction"].value_counts())

    # 🚨 ALERTS
    st.subheader("Active MLAT Alerts")
    st.write(alerts)

    # 🔎 SEARCH
    st.subheader("Search Case")
    cid = st.text_input("Case ID")

    if st.button("Search"):
        st.write(get_case(cid))


# ---------------- ROUTER ----------------
if st.session_state.user is None:
    auth()
else:
    if st.sidebar.button("Logout"):
        st.session_state.user = None
        st.rerun()

    user() if st.session_state.user != "admin" else admin()
