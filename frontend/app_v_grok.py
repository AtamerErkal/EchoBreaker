import streamlit as st
import requests
import json
from datetime import datetime

# ──────────────────────────────────────────────
# PAGE CONFIG + CUSTOM THEME (Inter font + dark pro)
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="EchoBreaker | Breaking Algorithmic Echo Chambers",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * { font-family: 'Inter', sans-serif; }
    
    .stApp { background: #0a0e1a; color: #e2e8f0; }
    
    [data-testid="stSidebar"] {
        background: #111827;
        border-right: 1px solid #1f2937;
    }
    
    [data-testid="stSidebar"] h1, h2, h3 { color: #10b981; }
    
    /* Mission Box */
    .mission-box {
        background: linear-gradient(135deg, #1e293b, #0f172a);
        border: 1px solid #334155;
        border-left: 4px solid #10b981;
        padding: 2rem;
        border-radius: 0.75rem;
        margin: 2rem 0;
    }
    
    .mission-title { color: #10b981; font-size: 1.5rem; font-weight: 700; margin-bottom: 1rem; }
    .mission-text { color: #cbd5e1; line-height: 1.8; font-size: 1.05rem; }
    
    /* Video Summary */
    .video-summary-card {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 0.75rem;
        padding: 2rem;
        margin: 2rem 0;
        border-left: 4px solid #3b82f6;
    }
    
    .video-title-display { color: #f1f5f9; font-size: 1.4rem; font-weight: 700; margin-bottom: 1rem; }
    
    /* Counter Argument Box */
    .counter-container {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 0.75rem;
        padding: 2rem;
        margin-bottom: 2rem;
        border-left: 4px solid #fbbf24;
    }
    
    .counter-type {
        background: #10b981;
        color: #0a0e1a;
        padding: 0.6rem 1.5rem;
        border-radius: 0.5rem;
        font-weight: 700;
        text-transform: uppercase;
    }
    
    .contrast-score {
        background: #fbbf24;
        color: #0a0e1a;
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
        font-weight: 600;
    }
    
    /* Academic & Video Cards */
    .academic-section {
        background: #0f172a;
        border: 1px solid #1e293b;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin: 1.5rem 0;
        border-left: 3px solid #3b82f6;
    }
    
    .video-card {
        background: #0f172a;
        border: 1px solid #1e293b;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        transition: all 0.3s;
    }
    
    .video-card:hover {
        border-color: #10b981;
        transform: translateY(-3px);
        box-shadow: 0 8px 24px rgba(16,185,129,0.15);
    }
    
    .video-thumbnail { width: 100%; height: 180px; object-fit: cover; }
    
    .relevance-badge {
        padding: 0.35rem 0.8rem;
        border-radius: 0.5rem;
        font-weight: 700;
        font-size: 0.75rem;
    }
    .relevance-high  { background: #10b981; color: white; }
    .relevance-medium { background: #fbbf24; color: #0a0e1a; }
    .relevance-low   { background: #64748b; color: white; }
    
    .section-header {
        color: #10b981;
        font-size: 1.6rem;
        font-weight: 700;
        margin: 3rem 0 1.5rem;
        border-bottom: 2px solid #1e293b;
        padding-bottom: 0.75rem;
    }
    
    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #10b981, #059669);
        color: white;
        font-weight: 700;
        border: none;
        padding: 1rem;
        border-radius: 0.5rem;
        transition: all 0.3s;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(16,185,129,0.4);
    }
    
    .stTextInput > div > div > input {
        background: #1e293b;
        border: 1px solid #334155;
        color: #f1f5f9;
        border-radius: 0.5rem;
        padding: 1rem;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #10b981;
        box-shadow: 0 0 0 3px rgba(16,185,129,0.2);
    }
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────
# SIDEBAR
# ──────────────────────────────────────────────
with st.sidebar:
    st.title("🛡️ EchoBreaker")
    st.subheader("Breaking Algorithmic Echo Chambers")
    
    st.markdown("---")
    
    st.markdown("### 🎯 Our Mission")
    st.markdown("""
    Modern recommendation systems create echo chambers by showing you more of what you already agree with.  
    EchoBreaker surfaces the **strongest counter-perspectives** the algorithm hides — not to argue, but to help you see the full picture.
    """)
    
    st.markdown("---")
    
    st.markdown("### ⚙️ System Status")
    try:
        r = requests.get("http://localhost:8000/", timeout=2)
        st.success("API Online") if r.status_code == 200 else st.error("API Issues")
    except:
        st.error("API Offline")
    
    st.markdown("---")
    
    st.markdown("### 📖 How It Works")
    st.markdown("1. Download audio\n2. Transcribe with Whisper\n3. Extract claims\n4. Generate counters (Ethical/Empirical/Logical)\n5. Find verified opposing videos\n**100% local • 100% private**")

# ──────────────────────────────────────────────
# MAIN AREA
# ──────────────────────────────────────────────

st.markdown("""
<div class="mission-box">
    <div class="mission-title">Why EchoBreaker?</div>
    <div class="mission-text">
        Recommendation algorithms optimize for engagement → filter bubbles → polarization.  
        We complement YouTube by showing what it doesn't: strong, high-quality opposing views.  
        Goal: Informed opinions through perspective diversity — without judgment.
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

st.subheader("🔍 Analyze a Video")
video_url = st.text_input("", placeholder="https://www.youtube.com/watch?v=...", label_visibility="collapsed")
analyze = st.button("🔍 Analyze Now", use_container_width=True)

if analyze and video_url:
    with st.spinner("Analyzing locally (1–5 min depending on length)..."):
        try:
            resp = requests.post("http://localhost:8000/analyze", json={"video_url": video_url}, timeout=900)
            if resp.status_code == 200:
                data = resp.json()
                st.success("Analysis Complete")

                # Video Summary
                meta = data.get("video_metadata", {})
                st.markdown(f"""
                <div class="video-summary-card">
                    <div class="video-title-display">{meta.get('title', 'Unknown')}</div>
                    <p>{meta.get('channel_name')} • {meta.get('duration', 'N/A')} • {meta.get('view_count', 0)} views</p>
                    <p><strong>Topic:</strong> {data.get('topic', '—')}</p>
                </div>
                """, unsafe_allow_html=True)

                # Counter Perspectives
                st.markdown('<div class="section-header">Counter-Perspectives</div>', unsafe_allow_html=True)
                for ca in data.get("counter_arguments", []):
                    st.markdown(f"""
                    <div class="counter-container">
                        <div style="display:flex; gap:1rem; align-items:center;">
                            <span class="counter-type">{ca.get('type','Unknown')}</span>
                            <span class="contrast-score">Opposition: {ca.get('semantic_contrast_score',0)*100:.0f}%</span>
                        </div>
                        <h3>{ca.get('title','')}</h3>
                        <p>{ca.get('content','')}</p>
                    """, unsafe_allow_html=True)

                    if ca.get("academic_insight"):
                        st.markdown(f"""
                        <div class="academic-section">
                            <strong>Academic Context</strong><br>
                            {ca['academic_insight']}
                        </div>
                        """, unsafe_allow_html=True)

                    st.markdown("</div>", unsafe_allow_html=True)

                # JSON Export
                st.download_button(
                    "Download Full JSON Report",
                    json.dumps(data, indent=2),
                    file_name=f"echobreaker_{datetime.now():%Y%m%d_%H%M}.json"
                )
            else:
                st.error(f"API Error: {resp.status_code}")
        except Exception as e:
            st.error(f"Error: {str(e)}")

st.markdown("---")
st.caption("EchoBreaker • 100% Local • Privacy First • 2026")