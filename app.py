import streamlit as st
import pandas as pd

# Page setup
st.set_page_config(page_title="DyeMind - Bimane Explorer", layout="wide")
st.title("🧠 DyeMind – Bimane Fluorophore Explorer")
st.markdown("Explore and compare key properties of known Bimane fluorophores.")

# Sample data
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

# Create dataframe
df = pd.DataFrame(data)

# Show the table
st.dataframe(df, use_container_width=True)

# Optional footer
st.markdown("📌 *More features coming soon — structure search, AI summaries, and compound visualization.*")
