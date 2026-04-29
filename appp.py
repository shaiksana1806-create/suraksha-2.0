import streamlit as st
import pandas as pd

st.title("Cybercrime Reporting System")

# ---- Form ----
title = st.text_input("Title")
description = st.text_area("Description")
location = st.text_input("Location")
fraud_type = st.selectbox("Fraud Type", ["OTP", "UPI", "Phishing"])

if st.button("Submit Case"):
    new_data = {
        "Title": title,
        "Description": description,
        "Location": location,
        "Fraud Type": fraud_type
    }

    df = pd.DataFrame([new_data])

    # Save to CSV (append mode)
    try:
        existing = pd.read_csv("cases.csv")
        df = pd.concat([existing, df], ignore_index=True)
    except:
        pass

    df.to_csv("cases.csv", index=False)
    st.success("Case submitted successfully!")

# ---- Graph Section ----
st.subheader("Fraud Analytics")

try:
    data = pd.read_csv("cases.csv")
    fraud_counts = data["Fraud Type"].value_counts()

    st.bar_chart(fraud_counts)
except:
    st.info("No data yet. Submit a case to see analytics.")
