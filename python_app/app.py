import streamlit as st
import requests

st.set_page_config(page_title="MedQuery RAG", page_icon="⚕️", layout="centered")

st.title("⚕️ MedQuery RAG")
st.markdown("Verify medical questions with sources from **PubMed**, **ClinicalTrials.gov**, and **CDC/NIH**.")

query = st.text_input("Ask a medical question...", placeholder="e.g., benefits of vitamin D")

import os

# ... imports ...

# Dynamic Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

if st.button("Search") and query:
    with st.spinner("Analyzing scientific literature..."):
        try:
            # Connect to python backend
            res = requests.post(f"{BACKEND_URL}/api/query", json={"query": query})
            
            if res.status_code == 200:
                data = res.json()
                answer = data.get('answer', "No answer found.")
                sources = data.get('sources', [])
                
                st.success("Analysis Complete")
                
                st.subheader("AI Answer")
                st.markdown(answer) # Streamlit renders Markdown natively
                
                st.divider()
                st.caption("Trusted Sources")
                
                if not sources:
                     st.warning("No specific sources were found.")
                
                for i, s in enumerate(sources):
                    with st.expander(f"[{i+1}] {s['title']}"):
                        st.markdown(f"**Source:** {s['source']} ({s['year']})")
                        st.markdown(f"**Tier:** {s.get('tier', 'N/A')}")
                        st.markdown(f"_{s['snippet']}_")
                        st.markdown(f"[Read Full Article]({s['url']})")
                        
            else:
                st.error("Backend Error: " + str(res.status_code))
                
        except Exception as e:
            st.error(f"Connection Error: {e}")
            st.info("Make sure the backend is running: `python python_app/server.py`")
