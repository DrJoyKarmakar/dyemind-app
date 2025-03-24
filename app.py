import streamlit as st
from openai import OpenAI
import time

# Set up OpenAI client using Streamlit secrets
client = OpenAI(api_key=st.secrets["openai"]["api_key"])

st.set_page_config(page_title="DyeMind Fluorophore Assistant", layout="wide")
st.title("🧠 DyeMind – AI Fluorophore Discovery")

query = st.text_input("🔍 Enter your fluorophore-related query", placeholder="e.g., Rhodamine derivatives for pH sensing")

if st.button("Search") and query:
    with st.spinner("🧠 Analyzing your query with ChatGPT..."):
        try:
            intent_response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert in fluorescence chemistry. Help interpret and optimize user queries for scientific data mining."},
                    {"role": "user", "content": f"Refine and extract keywords from this query for PubMed, PubChem, and CrossRef search: {query}"}
                ]
            )
            refined_query = intent_response.choices[0].message.content.strip()
        except Exception as e:
            st.error(f"Failed to analyze query: {e}")
            st.stop()

    st.success("✅ Query refined successfully!")
    st.markdown(f"**Refined keywords:** {refined_query}")

    # Simulated results for now (replace with real API calls later)
    with st.spinner("🔬 Searching PubMed, PubChem, CrossRef..."):
        time.sleep(2)  # Simulated delay
        papers = [
            {
                "title": "Rhodamine-based pH sensors in live-cell imaging",
                "authors": "Lee J, Wang T, Gupta N",
                "abstract": "This study explores rhodamine dyes as pH-sensitive probes for cellular imaging...",
                "doi": "10.1021/acsomega.0c00000"
            },
            {
                "title": "Fluorescence properties of cyanine dyes in aqueous solution",
                "authors": "Singh R, O'Neill K",
                "abstract": "We report the emission shift and quenching patterns of Cy5 derivatives under physiological pH...",
                "doi": "10.1039/D2RA00555K"
            }
        ]

        compounds = [
            {
                "name": "Rhodamine B",
                "cid": "6689",
                "image": "https://pubchem.ncbi.nlm.nih.gov/image/imgsrv.fcgi?cid=6689&t=l"
            },
            {
                "name": "Cy5",
                "cid": "136570280",
                "image": "https://pubchem.ncbi.nlm.nih.gov/image/imgsrv.fcgi?cid=136570280&t=l"
            }
        ]

    with st.spinner("📚 Summarizing findings with ChatGPT..."):
        paper_text = "\n\n".join([f"Title: {p['title']}\nAbstract: {p['abstract']}" for p in papers])
        try:
            final_summary = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a chemistry research assistant. Summarize fluorophore research and include references."},
                    {"role": "user", "content": f"Summarize the following papers and compounds:\n\n{paper_text}"}
                ]
            )
            summary = final_summary.choices[0].message.content
        except Exception as e:
            summary = f"❌ Error during summarization: {str(e)}"

    st.subheader("🧠 Final Summary")
    st.write(summary)

    st.subheader("📄 References")
    for p in papers:
        st.markdown(f"""**{p['title']}**  
*pby {p['authors']}*  
[DOI: {p['doi']}](https://doi.org/{p['doi']})""")

    st.subheader("🧪 Fluorophore Structures")
    for c in compounds:
        st.markdown(f"**{c['name']}** (PubChem CID: {c['cid']})")
        st.image(c["image"], width=150)
