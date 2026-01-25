import requests
import logging
import re
from typing import List, Any
from langchain.schema import Document
from langchain.schema.retriever import BaseRetriever
from langchain.chains import RetrievalQA
from langchain_community.retrievers import PubMedRetriever, WikipediaRetriever
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper
from langchain.retrievers import MergerRetriever
from app.services.gemini import gemini_service
from app.services.ingestion import ingestion_pipeline 
from app.core.prompts import PROMPT

# Set logging to see exactly what URLs are generated
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def clean_text(text: str) -> str:
    return re.sub(r'\s+', ' ', text).strip()

# --- 1. OPENFDA RETRIEVER ---
class OpenFDARetriever(BaseRetriever):
    def _get_relevant_documents(self, query: str, *, run_manager: Any = None) -> List[Document]:
        search_term = query.split(" ")[-1] if len(query.split(" ")) > 1 else query
        url = "https://api.fda.gov/drug/label.json"
        params = {
            "search": f'openfda.brand_name:"{search_term}"+OR+openfda.generic_name:"{search_term}"',
            "limit": 1
        }
        try:
            response = requests.get(url, params=params, timeout=5)
            data = response.json()
            if "error" in data or not data.get("results"): return []

            result = data["results"][0]
            brand = result.get("openfda", {}).get("brand_name", ["Unknown"])[0]
            warnings = " ".join(result.get("warnings", [])[:1])
            
            # Construct a SEARCH link for FDA
            fda_link = f"https://www.accessdata.fda.gov/scripts/cder/daf/index.cfm?event=BasicSearch.process&SearchTerm={brand}"

            content = f"FDA LABEL: {brand}. WARNINGS: {warnings[:400]}..."
            
            return [Document(
                page_content=content, 
                metadata={"source": "OpenFDA", "title": f"FDA Label: {brand}", "url": fda_link}
            )]
        except Exception:
            return []

# --- 2. DUCKDUCKGO RETRIEVER (Strict English) ---
class DuckDuckGoRetriever(BaseRetriever):
    def _get_relevant_documents(self, query: str, *, run_manager: Any = None) -> List[Document]:
        try:
            # FORCE region="us-en" to prevent Mandarin results
            wrapper = DuckDuckGoSearchAPIWrapper(max_results=3, region="us-en", time="y")
            search_results = wrapper.results(query, max_results=3)
            docs = []
            for res in search_results:
                docs.append(Document(
                    page_content=res['snippet'], 
                    metadata={"source": "DuckDuckGo", "title": res['title'], "url": res['link']}
                ))
            return docs
        except Exception:
            return []

# --- 3. MAIN RAG SERVICE ---
class RAGService:
    def __init__(self):
        self.llm = gemini_service.get_llm()
        
        # 1. Local Vector Store (Primary)
        self.vector_store_retriever = None
        vs = ingestion_pipeline.get_vector_store()
        if vs:
            # High k to ensure we get enough local context
            self.vector_store_retriever = vs.as_retriever(search_kwargs={"k": 5})

        # 2. Live Tools (Backups)
        self.pubmed = PubMedRetriever(top_k_results=3)
        self.wiki = WikipediaRetriever(top_k_results=1, doc_content_chars_max=1000)
        self.web = DuckDuckGoRetriever()
        self.fda = OpenFDARetriever()
        
    def _get_combined_retriever(self):
        """Dynamic retriever assembly based on what's available."""
        retrievers = []
        
        # Check if vector store has been updated/loaded
        vs = ingestion_pipeline.get_vector_store()
        if vs:
             retrievers.append(vs.as_retriever(search_kwargs={"k": 5}))
        
        # Add fallbacks
        # retrievers.extend([self.pubmed, self.wiki, self.web, self.fda])
        
        return MergerRetriever(retrievers=retrievers)

    def get_answer(self, question: str):
        # Dynamically build retriever to catch updates
        print("--- Building Combined Retriever ---")
        combined_retriever = self._get_combined_retriever()
        
        print("--- Initializing QA Chain ---")
        qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=combined_retriever,
            return_source_documents=True,
            chain_type_kwargs={"prompt": PROMPT}
        )

        print(f"--- Invoking QA Chain for question: {question} ---")
        result = qa_chain.invoke({"query": question})
        print("--- QA Chain Invocation Complete ---")
        
        source_docs = []
        seen_urls = set()

        for doc in result["source_documents"]:
            meta = doc.metadata
            
            # --- STRICT PUBMED ID EXTRACTION ---
            # PubMedRetriever sometimes uses 'uid' or 'UID'
            pmid = meta.get("uid") or meta.get("UID") or meta.get("pmid")
            
            if pmid and pmid != "Unknown ID":
                label = "PubMed"
                # THE EXACT LEGITIMATE SOURCE LINK
                url = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
            elif "openfda" in str(meta).lower():
                label = "OpenFDA"
                url = meta.get("url", "https://open.fda.gov")
            elif "source" in meta and "http" in meta["source"]:
                 # Wikipedia / Web often put link in 'source'
                label = "Wikipedia" if "wiki" in meta["source"] else "Web"
                url = meta["source"]
            elif "url" in meta:
                label = "DuckDuckGo"
                url = meta["url"]
            else:
                label = "Local Knowledge"
                url = "#"
            
            # De-duplication
            if url in seen_urls and url != "#":
                continue
            seen_urls.add(url)

            source_docs.append({
                "title": clean_text(meta.get("Title") or meta.get("title") or "Medical Source")[:80],
                "source": label,
                "content": clean_text(doc.page_content)[:200] + "...",
                "url": url 
            })

        return {"answer": result["result"], "sources": source_docs}

rag_service = RAGService()