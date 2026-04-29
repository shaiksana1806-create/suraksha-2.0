import streamlit as st
import pandas as pd

data = {
    "Fraud Type": ["OTP", "UPI", "Phishing"],
    "Cases": [10, 5, 3]
}

df = pd.DataFrame(data)
st.bar_chart(df.set_index("Fraud Type"))
