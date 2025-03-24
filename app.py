import streamlit as st
import requests
import openai
from xml.etree import ElementTree as ET
from io import BytesIO

# --- PAGE CONFIG ---
st.set_page_config(page_title="DyeMind - Fluorescent Probe Explorer", layout="wide")
st.title("🧠 DyeMind – Unified Fluorescent Probe & Fluorophore Explorer")

st.markdown("""
### 📘 About This App

**DyeMind – AI-Powered Fluorescent Probe Explorer**

**Created by Dr. Joy Karmakar (March 2025)**  
DyeMind is the *first AI-native platform* dedicated to fluorescent dyes and probes. It unifies chemical structures, spectral data, literature discovery, intelligent summarization, and natural language Q&A — powered by real-time data from **PubMed**, **PubChem**, **Wikipedia**, **ChEMBL**, **FPbase**, and more.

---
#### 🔬 Explore Probes for:
- Calcium, pH, ROS, Mitochondria, Membranes, Lysosomes, and more
- Compare probe families by emission, photostability, or application
""")

query = st.text_input("🔍 Ask about any fluorescent probe, dye, or application")

openai.api_key = st.secrets["openai_key"]

def gpt35_summarize(prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=2000
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"⚠️ GPT error: {e}"

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

def search_pubmed(query, max_results=10):
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

def parse_pubmed_xml(xml_data):
    articles = []
    root = ET.fromstring(xml_data)
    for article in root.findall(".//PubmedArticle"):
        title = article.findtext(".//ArticleTitle", default="No title")
        abstract = article.findtext(".//AbstractText") or "No abstract available."
        journal = article.findtext(".//Journal/Title", default="Unknown Journal")
        authors = [a.findtext(".//LastName") + " " + a.findtext(".//ForeName") for a in article.findall(".//Author") if a.findtext(".//LastName")]
        doi = article.findtext(".//ArticleId[@IdType='doi']")
        articles.append({
            "title": title,
            "abstract": abstract,
            "journal": journal,
            "authors": ", ".join(authors[:4]),
            "doi": doi
        })
    return articles

if query:
    with st.spinner("🔬 Synthesizing insights from multiple sources..."):
        parsed_query = gpt35_summarize(f"Interpret this scientific query for probe/dye analysis: {query}")

        intro, wiki_link = get_wikipedia_intro(parsed_query)
        img_url, cid, smiles = get_pubchem_structure(parsed_query)
        xml = search_pubmed(parsed_query)

        pubmed_summaries = ""
        article_refs = []
        if xml:
            articles = parse_pubmed_xml(xml)
            for art in articles:
                pubmed_summaries += f"{art['title']}: {art['abstract']}\n"
                ref = f"• *{art['title']}* ({art['journal']}, {art['authors']})"
                if art['doi']:
                    ref += f" – [DOI](https://doi.org/{art['doi']})"
                article_refs.append(ref)

        fusion_prompt = f"""
Using these inputs, write an expert-level review of the fluorescent probe:

Topic: {parsed_query}
Wikipedia Info: {intro}
Structure (SMILES): {smiles}
Literature Insights:
{pubmed_summaries}

Include:
- Molecular structure and key functional features
- Spectral properties and emission/excitation characteristics
- Applications (e.g., organelle targeting, sensing)
- Detection performance: limit of detection (LOD), linear range, sensitivity (if available)
- Summary of best-performing examples or use cases
- Mention DOI if source contains key LOD findings
- Use bold or bullets for clear metrics if found
"""
        final_summary = gpt35_summarize(fusion_prompt)

    st.markdown("## 🧠 Fluorescent Probe Summary")
    st.markdown(final_summary)

    st.download_button("📄 Download Summary", final_summary.encode(), file_name="dyemind_summary.txt")

    with st.expander("📚 Show Underlying Sources"):
        if wiki_link:
            st.markdown(f"**Wikipedia:** [Read more]({wiki_link})")
        if img_url:
            st.image(img_url, caption=f"PubChem CID: {cid}")
            st.code(smiles, language="none")
        if article_refs:
            st.markdown("**PubMed Literature:**")
            for ref in article_refs:
                st.markdown(ref)

st.markdown("---")
st.caption("DyeMind by Dr. Joy Karmakar · Unified AI via ChatGPT, PubMed, PubChem, Wikipedia, ChEMBL, FPbase")

