import streamlit as st
import pandas as pd
import uuid
import os

st.set_page_config(page_title="C3IS System", layout="wide")

st.title("🛡 C3IS - Cyber Crime & MLAT Intelligence System")

# -------------------- CASE FORM --------------------
st.subheader("📥 Report Case")

user_name = st.text_input("User Name")
title = st.text_input("Case Title")
location = st.text_input("Location")
fraud_type = st.selectbox("Fraud Type", ["OTP", "UPI", "Phishing", "Investment Scam"])
description = st.text_area("Description")

if st.button("Submit Case"):
    if user_name and title and location and description:
        case_id = str(uuid.uuid4())[:8]

        new_data = {
            "Case ID": case_id,
            "User Name": user_name,
            "Title": title,
            "Location": location,
            "Fraud Type": fraud_type,
            "Description": description
        }

        df_new = pd.DataFrame([new_data])

        if os.path.exists("cases.csv"):
            df_old = pd.read_csv("cases.csv")
            df = pd.concat([df_old, df_new], ignore_index=True)
        else:
            df = df_new

        df.to_csv("cases.csv", index=False)

        st.success(f"✅ Case submitted! Your Case ID: {case_id}")
    else:
        st.error("⚠ Please fill all fields")

st.divider()

# -------------------- DASHBOARD --------------------
st.subheader("📊 LIVE DASHBOARD")

if os.path.exists("cases.csv"):
    data = pd.read_csv("cases.csv")

    if not data.empty:
        fraud_counts = data["Fraud Type"].value_counts()
        st.bar_chart(fraud_counts)

        st.write("📄 Recent Cases")
        st.dataframe(data.tail(5))
    else:
        st.info("No data yet")
else:
    st.info("No data yet")

st.divider()

# -------------------- MLAT ALERTS --------------------
st.subheader("🚨 MLAT Alerts")

alerts = []

if os.path.exists("cases.csv"):
    data = pd.read_csv("cases.csv")

    for _, row in data.iterrows():
        desc = str(row["Description"]).lower()

        score = 0

        if "+44" in desc or "+1" in desc or "+971" in desc:
            score += 2
        if "international" in desc or "foreign" in desc or "overseas" in desc:
            score += 1
        if "crypto" in desc or "bitcoin" in desc:
            score += 2

        if score >= 3:
            alerts.append(row)

if alerts:
    for alert in alerts:
        st.error(f"🚨 MLAT Alert: {alert['Title']} ({alert['Location']})")
else:
    st.info("No Alerts")

st.divider()

# -------------------- SEARCH --------------------
st.subheader("🔎 Search Case")

search_id = st.text_input("Enter Case ID")

if st.button("Search"):
    if os.path.exists("cases.csv"):
        data = pd.read_csv("cases.csv")
        result = data[data["Case ID"] == search_id]

        if not result.empty:
            st.success("✅ Case Found")
            st.dataframe(result)
        else:
            st.error("❌ Not Found")
    else:
        st.error("No records available")
