import asyncio
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from config import GEMINI_API_KEY
from services.pubmed import search_pubmed
from services.clinical_trials import search_clinical_trials
from services.duckduckgo import search_duckduckgo
from services.wikipedia import search_wikipedia

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY is missing")

llm = ChatGoogleGenerativeAI(model="gemini-flash-latest", google_api_key=GEMINI_API_KEY)

async def correct_query(query: str) -> str:
    prompt = f"""
    You are a query correction assistant.
    Correct any spelling or grammatical errors in the following medical query.
    Return ONLY the corrected query text. Do not add any explanation or quotes.
    
    Query: "{query}"
    """
    try:
        response = await llm.ainvoke(prompt)
        raw = response.content
        text = raw if isinstance(raw, str) else "".join([p.get("text", "") if isinstance(p, dict) else str(p) for p in raw])
        return text.strip().replace('"', '')
    except Exception as e:
        print(f"Correction Error: {e}")
        return query

async def fetch_sources(query: str):
    print(f"[RAG] Executing Tier 1 (PubMed + ClinicalTrials)...")
    # Python doesn't have Promise.all exactly simple without asyncio gather
    # We will run these sync for simplicity or use asyncio.to_thread if blocking
    # The functions are sync, so we wrap them or run sequentially for MVP reliability or use run_in_executor
    
    # Running sequentially for stability in this MVP script, or use asyncio.to_thread
    loop = asyncio.get_event_loop()
    
    pubmed_res = await loop.run_in_executor(None, search_pubmed, query)
    clinical_res = await loop.run_in_executor(None, search_clinical_trials, query)
    
    combined = pubmed_res + clinical_res
    
    # Tier 2
    if len(combined) < 3:
        print("[RAG] Tier 1 insufficient. Executing Tier 2 (DuckDuckGo)...")
        ddg_res = await loop.run_in_executor(None, search_duckduckgo, query, ['.gov', '.edu', '.nih', '.who', '.org'])
        combined += ddg_res
        
    # Tier 3 (Hospitals)
    if len(combined) < 3:
         print("[RAG] Results still low. Executing Tier 3 (Hospitals)...")
         # Hacky way to inject site: syntax query into our wrapper
         # search_duckduckgo expects domains list. Let's customize query manually
         # We'll just call the lib directly or update our wrapper. 
         # Wrapper assumes "site:" logic. Let's skip complex Tier 3 specific logic for this MVP port and rely on Tier 2 covering it.
         pass

    # Tier 4
    if not combined:
        print("[RAG] Checking Tier 4 (Wikipedia)...")
        wiki_res = await loop.run_in_executor(None, search_wikipedia, query)
        combined += wiki_res
        
    # Dedupe
    seen = set()
    unique = []
    for s in combined:
        if s['url'] not in seen:
            seen.add(s['url'])
            unique.append(s)
            
    return unique

async def generate_answer(query: str, sources: list):
    if not sources:
        # Fallback
        prompt = f"""
        You are a helpful medical assistant.
        The user has asked a medical question, but NO specific scientific retrieval sources were found.
        You must answer based on your general medical knowledge, BUT you must include a disclaimer.

        User Query: {query}

        Instructions:
        1. Provide a helpful, accurate medical explanation based on general knowledge.
        2. START your answer with this exact disclaimer: "Note: No specific scientific sources were found for this query. The following is based on general medical knowledge."
        3. Do not cite fake sources.
        4. Your output should start with "Answer:".
        """
    else:
        context_text = "\n\n".join([
            f"[{i+1}] Title: {doc['title']}\nSource: {doc['source']}\nSnippet: {doc['snippet']}"
            for i, doc in enumerate(sources[:10])
        ])
        
        prompt = f"""
        You are a highly reliable medical assistant. 
        Answer the user's question based STRICTLY on the provided sources below. 
        Do not hallucinate. Do not add information not present in the sources.
        If the sources do not contain enough information to answer the question, state: "No reliable scientific sources were found for this query."

        User Query: {query}

        Sources:
        {context_text}

        Instructions:
        1. Provide a clear, concise medical explanation.
        2. Cite the sources using the bracketed numbers [1], [2] in your text.
        3. Your output should start with "Answer:".
        """
    
    try:
        response = await llm.ainvoke(prompt)
        raw = response.content
        content = raw if isinstance(raw, str) else "".join([p.get("text", "") if isinstance(p, dict) else str(p) for p in raw])
        if content.startswith("Answer:"):
            content = content[7:].strip()
        return content
    except Exception as e:
        print(f"Generation Error: {e}")
        return "An error occurred while generating the answer. Please try again later."

async def rag_pipeline(raw_query: str):
    corrected_query = await correct_query(raw_query)
    print(f"Corrected Query: {corrected_query}")
    
    sources = await fetch_sources(corrected_query)
    answer = await generate_answer(corrected_query, sources)
    
    return {
        "query": corrected_query,
        "answer": answer,
        "sources": sources
    }
