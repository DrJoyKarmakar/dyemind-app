import streamlit as st
import openai
from openai import OpenAI

# Set up OpenAI client using Streamlit secrets
client = OpenAI(api_key=st.secrets["openai"]["api_key"])

st.title("🧠 DyeMind: Fluorophore Discovery")

# Input
query = st.text_input("Search fluorophores (e.g., 'Bimane derivatives')")

if st.button("Search") and query:
    with st.spinner("Fetching and summarizing..."):
        # Dummy search result
        results = [{
            "title": "Example Fluorophore Study on Bimanes",
            "authors": "Doe J, Smith A",
            "abstract": "This is a mock abstract for a Bimane-based fluorophore study involving photophysical properties."
        }]

        abstracts = "\n".join([r["abstract"] for r in results])

        try:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a helpful scientific research assistant."},
                    {"role": "user", "content": f"""Summarize the following text:\n{abstracts}"""}
                ]
            )
            summary = response.choices[0].message.content
        except Exception as e:
            summary = f"❌ Error: {str(e)}"

        # Output
        st.subheader("🧠 AI Summary")
        st.write(summary)

        st.subheader("📄 Results")
        for res in results:
            st.markdown(f"**{res['title']}**")
            st.markdown(f"*{res['authors']}*")
            st.write(res['abstract'])
