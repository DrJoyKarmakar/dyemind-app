
import streamlit as st
import requests
import pandas as pd
from xml.etree import ElementTree as ET

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="DyeMind - AI Fluorophore Explorer", layout="wide")
st.title("🧠 DyeMind – Unified Fluorophore Search Panel")

# --- SEARCH PANEL ---
st.markdown("Search any fluorophore name, DOI, or topic to explore literature, structure, and summaries.")
query = st.text_input("🔍 Enter fluorophore, DOI, or topic")

# --- FUNCTION: Wikipedia Introduction ---
def get_wikipedia_intro(query):
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{query.replace(' ', '_')}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return data.get("extract", ""), data.get("content_urls", {}).get("desktop", {}).get("page", "")
    except:
        pass
    return None, None

# --- FUNCTION: Summarize Abstract via Hugging Face ---
@st.cache_data
def summarize_text(text):
    API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
    headers = {"Authorization": f"Bearer {st.secrets['huggingface_token']}"}
    try:
        response = requests.post(API_URL, headers=headers, json={"inputs": text})
        if response.status_code == 200:
            return response.json()[0]['summary_text']
    except:
        return "Summary unavailable."
    return "Summary unavailable."

# --- FUNCTION: Get PubChem Structure ---
def get_pubchem_structure(compound_name):
    try:
        cid_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{compound_name}/cids/TXT"
        cid_resp = requests.get(cid_url)
        if cid_resp.status_code == 200:
            cid = cid_resp.text.strip().split("\n")[0]
            img_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/PNG"
            smiles_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/property/CanonicalSMILES/JSON"
            smiles_resp = requests.get(smiles_url)
            smiles = smiles_resp.json()['PropertyTable']['Properties'][0]['CanonicalSMILES']
            return img_url, cid, smiles
    except:
        pass
    return None, None, None

# --- FUNCTION: Search PubMed for Articles ---
def search_pubmed(query, max_results=3):
    try:
        esearch = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&retmode=json&term={query}+AND+hasabstract[text]&sort=relevance&retmax={max_results}"
        esearch_resp = requests.get(esearch).json()
        ids = esearch_resp['esearchresult']['idlist']
        efetch = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id={','.join(ids)}&retmode=xml"
        fetch_resp = requests.get(efetch)
        return fetch_resp.text
    except:
        return None

# --- FUNCTION: Parse PubMed XML ---
def parse_pubmed_xml(xml_data):
    articles = []
    root = ET.fromstring(xml_data)
    for article in root.findall(".//PubmedArticle"):
        title = article.findtext(".//ArticleTitle")
        abstract = article.findtext(".//AbstractText") or "No abstract available."
        journal = article.findtext(".//Journal/Title")
        authors = [a.findtext(".//LastName") + " " + a.findtext(".//ForeName") for a in article.findall(".//Author") if a.findtext(".//LastName")]
        doi = article.findtext(".//ArticleId[@IdType='doi']")
        articles.append({
            "title": title,
            "abstract": abstract,
            "summary": summarize_text(abstract),
            "journal": journal,
            "authors": ", ".join(authors[:4]),
            "doi": doi
        })
    return articles

# --- DISPLAY RESULTS ---
if query:
    with st.spinner("🔬 Fetching data and generating insights..."):

        # Wikipedia Introduction
        intro, wiki_link = get_wikipedia_intro(query)
        if intro:
            st.subheader("🧬 Introduction from Wikipedia")
            st.markdown(f"{intro} [Read more]({wiki_link})")

        # Show PubChem Structure (if applicable)
        img_url, cid, smiles = get_pubchem_structure(query)
        if img_url:
            st.subheader("🧪 Chemical Information")
            st.image(img_url, caption=f"PubChem CID: {cid}")
            st.code(smiles, language='none')

        # PubMed Results
        xml_results = search_pubmed(query)
        if xml_results:
            articles = parse_pubmed_xml(xml_results)
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
            st.warning("No articles found or unable to retrieve PubMed data.")

# Footer
st.markdown("---")
st.caption("DyeMind by Dr. Joy Karmakar · All data retrieved from PubMed, PubChem, CrossRef, Wikipedia, and Hugging Face APIs")
