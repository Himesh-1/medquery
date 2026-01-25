import requests
import xml.etree.ElementTree as ET
from urllib.parse import quote

BASE_URL = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils'

def search_pubmed(query: str, max_results: int = 5):
    try:
        # 1. Search for IDs
        search_url = f"{BASE_URL}/esearch.fcgi?db=pubmed&retmode=json&term={quote(query)}&retmax={max_results}&sort=relevance"
        response = requests.get(search_url)
        data = response.json()
        
        id_list = data.get('esearchresult', {}).get('idlist', [])
        if not id_list:
            return []
            
        # 2. Fetch Details
        ids_str = ",".join(id_list)
        fetch_url = f"{BASE_URL}/efetch.fcgi?db=pubmed&retmode=xml&id={ids_str}"
        fetch_res = requests.get(fetch_url)
        
        root = ET.fromstring(fetch_res.content)
        articles = []
        
        for article in root.findall('.//PubmedArticle'):
            title_node = article.find('.//ArticleTitle')
            title = title_node.text if title_node is not None else "No Title"
            
            abstract_texts = article.findall('.//AbstractText')
            snippet = " ".join([t.text for t in abstract_texts if t.text])
            if not snippet:
                snippet = "No abstract available."
                
            pmid_node = article.find('.//PMID')
            pmid = pmid_node.text if pmid_node is not None else ""
            
            pub_date_node = article.find('.//PubDate/Year')
            year = pub_date_node.text if pub_date_node is not None else "N/A"
            
            if pmid:
                articles.append({
                    "title": title,
                    "snippet": snippet,
                    "source": "PubMed",
                    "year": year,
                    "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                    "tier": "Tier 1: Scientific"
                })
                
        return articles

    except Exception as e:
        print(f"PubMed Error: {e}")
        return []
