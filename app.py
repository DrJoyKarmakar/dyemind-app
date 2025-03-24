import streamlit as st
import openai

# Load OpenAI API key from Streamlit secrets
openai.api_key = st.secrets["openai"]["api_key"]

st.title("🧠 DyeMind: Fluorophore Discovery")

# Input query
query = st.text_input("Search fluorophores (e.g., 'Bimane derivatives')")

if st.button("Search") and query:
    with st.spinner("Fetching and summarizing..."):
        # Dummy result (to be replaced with real API integrations)
        results = [{
            "title": "Example Fluorophore Study on Bimanes",
            "authors": "Doe J, Smith A",
            "abstract": "This is a mock abstract for a Bimane-based fluorophore study involving photophysical properties."
        }]

        # Concatenate abstracts to summarize
        abstracts = "\n".join([r["abstract"] for r in results])

        try:
            # Send to OpenAI for summarization
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a helpful scientific research assistant."},
                    {"role": "user", "content": f"""Summarize the following text:\n{abstracts}"""}
                ]
            )
            summary = response['choices'][0]['message']['content']
        except Exception as e:
            summary = f"Error during summarization: {str(e)}"

        # Display summary
        st.subheader("🧠 AI Summary")
        st.write(summary)

        # Display dummy results
        st.subheader("📄 Results")
        for res in results:
            st.markdown(f"**{res['title']}**")
            st.markdown(f"*{res['authors']}*")
            st.write(res['abstract'])
