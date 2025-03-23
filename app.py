import streamlit as st
import requests
from xml.etree import ElementTree as ET

# --- PAGE CONFIG ---

st.set\_page\_config(page\_title="DyeMind - Fluorophore Explorer", layout="wide")
st.title("🧠 DyeMind – Unified Fluorophore Search Panel")

st.markdown("""

### 📘 About This App

**🧠 DyeMind – AI-Powered Fluorophore Explorer**

**Created by Dr. Joy Karmakar (March 2025)**\
DyeMind is the *first AI-native platform* dedicated to fluorophores. It unifies chemical structures, literature discovery, intelligent summarization, and natural language Q&A — powered by real-time data. """)





st.markdown("Search any fluorophore name, DOI, or topic to explore structure, summaries, and literature.")

query = st.text\_input("🔍 Enter fluorophore, DOI, or topic")

# --- WIKIPEDIA INTRO ---

def get\_wikipedia\_intro(query):
url = f"[https://en.wikipedia.org/api/rest\_v1/page/summary/{query.replace(](https://en.wikipedia.org/api/rest_v1/page/summary/{query.replace\()' ', '\_')}"
try:
response = requests.get(url)
if response.status\_code == 200:
data = response.json()
return data.get("extract", ""), data.get("content\_urls", {}).get("desktop", {}).get("page", "")
except:
return None, None
return None, None

# --- AI SUMMARIZATION VIA HUGGING FACE ---

def summarize\_text(text):
try:
API\_URL = "[https://api-inference.huggingface.co/models/facebook/bart-large-cnn](https://api-inference.huggingface.co/models/facebook/bart-large-cnn)"
headers = {"Authorization": f"Bearer {st.secrets['huggingface\_token']}"}
response = requests.post(API\_URL, headers=headers, json={"inputs": text})
if response.status\_code == 200:
return response.json()[0]['summary\_text']
except:
return "Summary unavailable (AI offline or token missing)."
return "Summary unavailable."

# --- GPT-STYLE Q&A VIA HUGGING FACE ---

def ask\_dyemind\_ai(question):
api\_url = "[https://api-inference.huggingface.co/models/google/flan-t5-xl](https://api-inference.huggingface.co/models/google/flan-t5-xl)"
headers = {"Authorization": f"Bearer {st.secrets['huggingface\_token']}"}
payload = {"inputs": question}
try:
response = requests.post(api\_url, headers=headers, json=payload)
if response.status\_code == 200:
return response.json()[0]['generated\_text']
except:
return "❌ Unable to generate a response. Please try again later."
return "❌ AI not responding."

# --- PUBCHEM STRUCTURE ---

def get\_pubchem\_structure(name):
try:
cid\_url = f"[https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{name}/cids/TXT](https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{name}/cids/TXT)"
cid\_resp = requests.get(cid\_url)
if cid\_resp.status\_code == 200:
cid = cid\_resp.text.strip().split("\n")[0]
img\_url = f"[https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/PNG](https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/PNG)"
smiles\_url = f"[https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/property/CanonicalSMILES/JSON](https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/property/CanonicalSMILES/JSON)"
smiles\_resp = requests.get(smiles\_url)
smiles = smiles\_resp.json()['PropertyTable']['Properties'][0]['CanonicalSMILES']
return img\_url, cid, smiles
except:
return None, None, None
return None, None, None

# --- PUBMED SEARCH ---

def search\_pubmed(query, max\_results=3):
try:
term = f"{query} AND hasabstract[text]"
esearch = f"[https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&retmode=json&term={term}&sort=relevance&retmax={max\_results}](https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed\&retmode=json\&term={term}\&sort=relevance\&retmax={max_results})"
esearch\_resp = requests.get(esearch).json()
ids = esearch\_resp.get("esearchresult", {}).get("idlist", [])
if not ids:
return None
efetch = f"[https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id={','.join(ids)}&retmode=xml](https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed\&id={','.join\(ids\)}\&retmode=xml)"
fetch\_resp = requests.get(efetch)
return fetch\_resp.text
except:
return None

# --- PARSE PUBMED RESULTS ---

def parse\_pubmed\_xml(xml\_data):
articles = []
root = ET.fromstring(xml\_data)
for article in root.findall(".//PubmedArticle"):
title = article.findtext(".//ArticleTitle", default="No title")
abstract = article.findtext(".//AbstractText") or "No abstract available."
journal = article.findtext(".//Journal/Title", default="Unknown Journal")
authors = [a.findtext(".//LastName") + " " + a.findtext(".//ForeName") for a in article.findall(".//Author") if a.findtext(".//LastName")]
doi = article.findtext(".//ArticleId[@IdType='doi']")
summary = summarize\_text(abstract)
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

```
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
```

# --- GPT STYLE Q&A ---

st.markdown("---")
st.subheader("💬 Ask DyeMind Anything")
user\_question = st.text\_area("Ask a question about fluorophores, structure, use cases, or scientific insights:")
if st.button("Ask AI"):
with st.spinner("🤖 Thinking..."):
ai\_response = ask\_dyemind\_ai(user\_question)
st.markdown(ai\_response)

# Footer

st.markdown("---")
st.caption("DyeMind by Dr. Joy Karmakar · Powered by PubMed, PubChem, Wikipedia, and Hugging Face APIs")



