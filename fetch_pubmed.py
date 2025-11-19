import requests
import xml.etree.ElementTree as ET
import json
import time
import sys
import argparse

# NCBI E-utilities Configuration
BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
DB = "pubmed"

def search_pubmed(query, max_results=100):
    """Search PubMed and return a list of PMIDs."""
    print(f"🔍 Searching PubMed for: '{query}' (Max: {max_results})...")
    
    params = {
        "db": DB,
        "term": query,
        "retmode": "json",
        "retmax": max_results,
        "sort": "relevance"
    }
    
    response = requests.get(f"{BASE_URL}/esearch.fcgi", params=params)
    response.raise_for_status()
    data = response.json()
    
    id_list = data.get("esearchresult", {}).get("idlist", [])
    print(f"✅ Found {len(id_list)} articles.")
    return id_list

def fetch_details(id_list):
    """Fetch article details (Title, Abstract) for a list of PMIDs."""
    if not id_list:
        return []
    
    print(f"📥 Fetching abstracts for {len(id_list)} articles...")
    
    # PubMed allows fetching multiple IDs via POST (better for large lists)
    ids_str = ",".join(id_list)
    params = {
        "db": DB,
        "retmode": "xml",
        "id": ids_str
    }
    
    # Use POST to avoid URL length limits
    response = requests.post(f"{BASE_URL}/efetch.fcgi", data=params)
    response.raise_for_status()
    
    return response.content

def parse_xml_to_json(xml_data):
    """Parse NCBI XML response into the JSON format MedQuery expects."""
    root = ET.fromstring(xml_data)
    articles = []

    for article in root.findall(".//PubmedArticle"):
        pmid = article.find(".//PMID").text
        
        # Extract Title
        article_title = article.find(".//ArticleTitle")
        title = article_title.text if article_title is not None else "No Title"
        
        # Extract Abstract (can be multipart)
        abstract_texts = article.findall(".//AbstractText")
        abstract = " ".join([t.text for t in abstract_texts if t.text])
        
        if not abstract:
            continue  # Skip articles without abstracts

        articles.append({
            "pmid": pmid,
            "title": title,
            "abstract": abstract
        })
    
    return articles

def main():
    parser = argparse.ArgumentParser(description="Fetch PubMed abstracts for MedQuery.")
    parser.add_argument("query", type=str, help="Search query (e.g., 'diabetes', 'COVID-19')")
    parser.add_argument("--count", type=int, default=50, help="Number of articles to fetch")
    parser.add_argument("--output", type=str, default="pubmed_data.json", help="Output JSON filename")
    
    args = parser.parse_args()
    
    # 1. Search
    pmids = search_pubmed(args.query, args.count)
    
    if not pmids:
        print("No results found.")
        return

    # 2. Fetch (Batching to respect API limits if count is high)
    batch_size = 200
    all_articles = []
    
    for i in range(0, len(pmids), batch_size):
        batch_ids = pmids[i:i+batch_size]
        xml_data = fetch_details(batch_ids)
        batch_articles = parse_xml_to_json(xml_data)
        all_articles.extend(batch_articles)
        time.sleep(0.5)  # Be polite to NCBI servers
    
    # 3. Save
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(all_articles, f, indent=2)
    
    print(f"🎉 Success! Saved {len(all_articles)} abstracts to '{args.output}'.")
    print("🚀 Next Step: Upload this file via the MedQuery Admin Panel.")

if __name__ == "__main__":
    main()