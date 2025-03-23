import streamlit as st
import requests
from xml.etree import ElementTree as ET

# --- PAGE CONFIG ---
st.set_page_config(page_title="DyeMind - Fluorophore Explorer", layout="wide")
st.title("🧠 DyeMind – Unified Fluorophore Search Panel")

st.markdown("""
**Created by Dr. Joy Karmakar (March 2025)**  
DyeMind is the **first AI-powered unified search platform** for fluorescent molecules. It brings together real-time data from PubChem, PubMed, CrossRef, Wikipedia, and Hugging Face AI models.

🔬 Instantly retrieve chemical structures and SMILES  
📚 Access and summarize the latest literature  
🧠 Ask natural-language questions about fluorophores  
🌐 Learn through integrated Wikipedia context

DyeMind is a novel tool built at the intersection of chemistry, artificial intelligence, and open science — a step toward democratizing fluorescence knowledge for the world.
""")

st.markdown("""
**Created by Dr. Joy Karmakar (March 2025)**  
DyeMind is the **first AI-powered unified search platform** for fluorescent molecules, combining PubChem, PubMed, CrossRef, Wikipedia, and Hugging Face AI into one tool.  
It offers a **novel integration of chemical structure, literature summarization, and intelligent Q&A**, designed to accelerate discovery and understanding of fluorophores in scientific research.
""")

st.markdown("Search any fluorophore name, DOI, or topic to explore structure, summaries, and literature.")

query = st.text_input("🔍 Enter fluorophore, DOI, or topic")

# --- WIKIPEDIA INTRO ---
def get_wikipedia_intro(query):
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{query.replace(' ', '_')}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return data.get("extract", ""), data.get("content_urls", {}).get("desktop", {}).get("page", "")
    except:
        return None, None
    return None, None

# --- AI SUMMARIZATION VIA HUGGING FACE ---
def summarize_text(text):
    try:
        API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
        headers = {"Authorization": f"Bearer {st.secrets['huggingface_token']}"}
        response = requests.post(API_URL, headers=headers, json={"inputs": text})
        if response.status_code == 200:
            return response.json()[0]['summary_text']
    except:
        return "Summary unavailable (AI offline or token missing)."
    return "Summary unavailable."

# --- GPT-STYLE Q&A VIA HUGGING FACE ---
def ask_dyemind_ai(question):
    api_url = "https://api-inference.huggingface.co/models/google/flan-t5-xl"
    headers = {"Authorization": f"Bearer {st.secrets['huggingface_token']}"}
    payload = {"inputs": question}
    try:
        response = requests.post(api_url, headers=headers, json=payload)
        if response.status_code == 200:
            return response.json()[0]['generated_text']
    except:
        return "❌ Unable to generate a response. Please try again later."
    return "❌ AI not responding."

# --- PUBCHEM STRUCTURE ---
def get_pubchem_structure(name):
    try:
        cid_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{name}/cids/TXT"
        cid_resp = requests.get(cid_url)
        if cid_resp.status_code == 200:
            cid = cid_resp.text.strip().split("\n")[0]
            img_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/PNG"
            smiles_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/property/CanonicalSMILES/JSON"
            smiles_resp = requests.get(smiles_url)
            smiles = smiles_resp.json()['PropertyTable']['Properties'][0]['CanonicalSMILES']
            return img_url, cid, smiles
    except:
        return None, None, None
    return None, None, None

# --- PUBMED SEARCH ---
def search_pubmed(query, max_results=3):
    try:
        term = f"{query} AND hasabstract[text]"
        esearch = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&retmode=json&term={term}&sort=relevance&retmax={max_results}"
        esearch_resp = requests.get(esearch).json()
        ids = esearch_resp.get("esearchresult", {}).get("idlist", [])
        if not ids:
            return None
        efetch = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id={','.join(ids)}&retmode=xml"
        fetch_resp = requests.get(efetch)
        return fetch_resp.text
    except:
        return None

# --- PARSE PUBMED RESULTS ---
def parse_pubmed_xml(xml_data):
    articles = []
    root = ET.fromstring(xml_data)
    for article in root.findall(".//PubmedArticle"):
        title = article.findtext(".//ArticleTitle", default="No title")
        abstract = article.findtext(".//AbstractText") or "No abstract available."
        journal = article.findtext(".//Journal/Title", default="Unknown Journal")
        authors = [a.findtext(".//LastName") + " " + a.findtext(".//ForeName") for a in article.findall(".//Author") if a.findtext(".//LastName")]
        doi = article.findtext(".//ArticleId[@IdType='doi']")
        summary = summarize_text(abstract)
        articles.append({
            "title": title,
            "abstract": abstract,
            "summary": summary,
            "journal": journal,
            "authors": ", ".join(authors[:4]),
            "doi": doi
        })
    return articles

# --- DISPLAY RESULTS ---
if query:
    with st.spinner("🔬 Fetching insights..."):

        # Wikipedia intro
        intro, link = get_wikipedia_intro(query)
        if intro:
            st.subheader("🧬 Introduction from Wikipedia")
            st.markdown(f"{intro} [Read more]({link})")

        # PubChem structure
        img_url, cid, smiles = get_pubchem_structure(query)
        if img_url:
            st.subheader("🧪 Chemical Structure")
            st.image(img_url, caption=f"PubChem CID: {cid}")
            st.code(smiles, language="none")

        # PubMed articles
        xml = search_pubmed(query)
        if xml:
            articles = parse_pubmed_xml(xml)
            st.subheader("📚 Literature Insights")
            for i, art in enumerate(articles):
                with st.expander(f"{i+1}. {art['title']}"):
                    if art['doi']:
                        st.markdown(f"**DOI:** [{art['doi']}](https://doi.org/{art['doi']})")
                    st.markdown(f"**Journal:** *{art['journal']}*")
                    st.markdown(f"**Authors:** {art['authors']}")
                    st.markdown(f"**Summary:** _{art['summary']}_")
                    st.markdown("---")
                    st.markdown(art['abstract'])
        else:
            st.warning("No PubMed articles found or failed to fetch.")

# --- GPT STYLE Q&A ---
st.markdown("---")
st.subheader("💬 Ask DyeMind Anything")
user_question = st.text_area("Ask a question about fluorophores, structure, use cases, or scientific insights:")
if st.button("Ask AI"):
    with st.spinner("🤖 Thinking..."):
        ai_response = ask_dyemind_ai(user_question)
        st.markdown(ai_response)

# Footer
st.markdown("---")
st.caption("DyeMind by Dr. Joy Karmakar · Powered by PubMed, PubChem, Wikipedia, and Hugging Face APIs")

st.markdown("""
---

### 📘 About This App
**🧠 DyeMind – AI-Powered Fluorophore Explorer**

**Created by Dr. Joy Karmakar (March 2025)**  
DyeMind is the *first AI-native platform* dedicated to fluorophores. It unifies chemical structures, literature discovery, intelligent summarization, and natural language Q&A — powered by real-time data and Hugging Face AI.

- 🔬 PubChem integration for molecular structure and SMILES
- 📚 PubMed + CrossRef for recent fluorophore literature
- 🧠 AI summaries from state-of-the-art NLP models
- 💬 GPT-style Q&A built on Hugging Face
- 🌐 Wikipedia context for quick understanding

This app pioneers a new direction in chemical research tools — combining science and AI to accelerate fluorescence discovery.
""")

