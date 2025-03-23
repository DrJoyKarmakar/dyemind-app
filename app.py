import streamlit as st
import requests
import pandas as pd

# Existing Bimane data display (keep this part)
st.set_page_config(page_title="DyeMind - Bimane Explorer", layout="wide")
st.title("🧠 DyeMind – Bimane Fluorophore Explorer")
st.markdown("Explore and compare key properties of known Bimane fluorophores.")

# Fluorophore data
data = {
    "Name": [
        "Monobromobimane (mBBr)",
        "Dibromobimane (dBBr)",
        "Azido-Bimane",
        "Amino-Bimane",
        "Glutathione-Bimane Adduct"
    ],
    "Excitation λ (nm)": [394, 396, 405, 410, 395],
    "Emission λ (nm)": [480, 482, 510, 520, 478],
    "Stokes Shift (nm)": [86, 86, 105, 110, 83],
    "Quantum Yield": [0.96, 0.88, 0.71, 0.69, 0.85],
    "Application": [
        "Thiol detection in proteins",
        "Environmental ROS sensing",
        "Click chemistry labeling",
        "Bio-conjugation and probes",
        "Detection of GSH in cells"
    ],
    "DOI / Source": [
        "10.1021/bi00219a008",
        "10.1039/b204601n",
        "10.1002/chem.202000322",
        "10.1021/jacs.9b13294",
        "10.1016/j.ab.2004.09.007"
    ]
}

df = pd.DataFrame(data)
st.dataframe(df, use_container_width=True)

# -----------------------------------------------
# ✅ AI Summarizer Section (Hugging Face)
# -----------------------------------------------
st.markdown("---")
st.subheader("🧠 AI-Powered Paper Summarizer (Free with Hugging Face)")

API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
headers = {"Authorization": f"Bearer {st.secrets['huggingface_token']}"}

def summarize_text(text):
    response = requests.post(API_URL, headers=headers, json={"inputs": text})
    if response.status_code == 200:
        return response.json()[0]["summary_text"]
    else:
        return "⚠️ Error from AI model. Please check your token or try again."

# Input
user_input = st.text_area("📋 Paste the abstract or paper text here:")

if st.button("Summarize"):
    with st.spinner("Summarizing..."):
        summary = summarize_text(user_input)
        st.success("📘 Summary:")
        st.write(summary)
