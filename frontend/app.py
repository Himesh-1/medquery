import streamlit as st
import requests
import os

API_URL = os.getenv("API_URL", "http://backend:8000")

st.set_page_config(page_title="MedQuery AI", page_icon="🏥", layout="centered")

# --- CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #f8f9fa; }

    /* Chat Bubbles */
    .stChatMessage { background: white; border: 1px solid #e5e7eb; border-radius: 12px; padding: 1.5rem; margin-bottom: 1rem; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    div[data-testid="stChatMessage"]:nth-child(odd) { background-color: #f8fafc; }
    div[data-testid="stChatMessage"]:nth-child(even) { background-color: #ffffff; border-left: 4px solid #0ea5e9; }

    /* CARD STYLING */
    .evidence-card {
        background-color: white;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 10px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    }
    .card-title { font-weight: 600; color: #0f172a; font-size: 0.95rem; margin-bottom: 5px; }
    .card-content { font-size: 0.85rem; color: #64748b; margin-bottom: 10px; line-height: 1.4; }
    
    /* LINK STYLING */
    .source-link {
        font-size: 0.8rem;
        color: #0ea5e9;
        font-weight: 600;
        text-decoration: none;
    }
    .source-link:hover { text-decoration: underline; }

    /* BADGES */
    .badge { padding: 2px 6px; border-radius: 4px; font-size: 0.7rem; font-weight: 700; text-transform: uppercase; display: inline-block; margin-bottom: 6px;}
    .badge-pubmed { background: #e0f2fe; color: #0369a1; }
    .badge-fda { background: #fee2e2; color: #b91c1c; }
    .badge-wiki { background: #f3e8ff; color: #7e22ce; }
    .badge-web { background: #f1f5f9; color: #475569; }
</style>
""", unsafe_allow_html=True)

def render_sources(sources):
    if not sources: return
    with st.expander("📚 View Medical Evidence", expanded=True):
        for src in sources:
            # Badge Logic
            s_lower = src['source'].lower()
            if "pubmed" in s_lower: badge, b_class = "PubMed", "badge-pubmed"
            elif "fda" in s_lower: badge, b_class = "FDA", "badge-fda"
            elif "wiki" in s_lower: badge, b_class = "Wikipedia", "badge-wiki"
            else: badge, b_class = "Web", "badge-web"
            
            url = src.get("url", "#")
            
            st.markdown(f"""
            <div class="evidence-card">
                <span class="badge {b_class}">{badge}</span>
                <div class="card-title">{src['title']}</div>
                <div class="card-content">"{src['content']}"</div>
                <a href="{url}" target="_blank" class="source-link">🔗 Read Full Source &rarr;</a>
            </div>
            """, unsafe_allow_html=True)

# --- APP LOGIC ---
if "messages" not in st.session_state: st.session_state.messages = []

with st.sidebar:
    st.title("🩺 MedQuery AI")
    st.caption("Sources: PubMed, FDA, Wikipedia")

st.markdown("<h2 style='text-align: center;'>🏥 MedQuery AI</h2>", unsafe_allow_html=True)

for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar="🧑‍💻" if msg["role"] == "user" else "🩺"):
        st.markdown(msg["content"])
        if "sources" in msg: render_sources(msg["sources"])

if prompt := st.chat_input("Ask a medical question..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="🧑‍💻"): st.markdown(prompt)

    with st.chat_message("assistant", avatar="🩺"):
        placeholder = st.empty()
        placeholder.markdown("🔍 *Analyzing PubMed & Databases...*")
        try:
            response = requests.post(f"{API_URL}/query", json={"question": prompt}, timeout=60)
            if response.status_code == 200:
                data = response.json()
                placeholder.markdown(data["answer"])
                render_sources(data["sources"])
                st.session_state.messages.append({"role": "assistant", "content": data["answer"], "sources": data["sources"]})
            else:
                placeholder.error("Backend Error")
        except Exception as e:
            placeholder.error(f"Connection Error: {e}")