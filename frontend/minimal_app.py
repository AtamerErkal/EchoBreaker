import streamlit as st
import requests
import json
from datetime import datetime
from typing import Optional

# =============================================================================
# PAGE CONFIGURATION
# =============================================================================
st.set_page_config(
    page_title="EchoBreaker | Breaking Algorithmic Echo Chambers",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================================================
# MINIMAL PROFESSIONAL CSS
# =============================================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', -apple-system, sans-serif;
    }
    
    .main {
        background-color: #0a0e1a;
        color: #e2e8f0;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: #111827;
        border-right: 1px solid #1f2937;
    }
    
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #10b981;
    }
    
    /* Mission Statement Box */
    .mission-box {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid #334155;
        border-left: 4px solid #10b981;
        padding: 2rem;
        border-radius: 0.75rem;
        margin: 2rem 0;
    }
    
    .mission-title {
        color: #10b981;
        font-size: 1.5rem;
        font-weight: 700;
        margin-bottom: 1rem;
    }
    
    .mission-text {
        color: #cbd5e1;
        line-height: 1.8;
        font-size: 1.05rem;
    }

    /* Summary Card */
    .summary-card {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 0.75rem;
        padding: 1.5rem;
        margin-bottom: 1rem;
    }
    
    /* Counter Argument Cards */
    .counter-card {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 0.75rem;
        padding: 2rem;
        margin-bottom: 2rem;
        border-left: 4px solid #fbbf24;
    }
    
    .counter-header {
        display: flex;
        align-items: center;
        gap: 1rem;
        margin-bottom: 1.5rem;
        flex-wrap: wrap;
    }
    
    .counter-type {
        background: #10b981;
        color: #0a0e1a;
        padding: 0.5rem 1.25rem;
        border-radius: 0.5rem;
        font-weight: 700;
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .contrast-score {
        background: #fbbf24;
        color: #0a0e1a;
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
        font-weight: 600;
        font-size: 0.85rem;
    }
    
    .counter-title {
        color: #f1f5f9;
        font-size: 1.4rem;
        font-weight: 700;
        flex: 1;
    }
    
    .counter-content {
        color: #cbd5e1;
        line-height: 1.9;
        font-size: 1.05rem;
        margin-bottom: 1.5rem;
    }
    
    .academic-insight {
        background: #0f172a;
        border: 1px solid #1e293b;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-bottom: 1.5rem;
        border-left: 3px solid #3b82f6;
    }
    
    .academic-text {
        color: #94a3b8;
        font-style: italic;
        line-height: 1.8;
        font-size: 1rem;
    }
    
    .academic-label {
        color: #3b82f6;
        font-weight: 600;
        font-size: 0.85rem;
        margin-bottom: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    /* Video Cards */
    .video-card {
        background: #111827;
        border: 1px solid #334155;
        border-radius: 0.75rem;
        overflow: hidden;
        transition: all 0.3s ease;
        margin-bottom: 1.5rem;
        height: 100%;
        display: flex;
        flex-direction: column;
    }
    
    .video-card:hover {
        border-color: #10b981;
        transform: translateY(-2px);
    }
    
    .video-content {
        padding: 1.25rem;
        flex-grow: 1;
        display: flex;
        flex-direction: column;
    }
    
    .video-title {
        color: #f1f5f9;
        font-weight: 600;
        font-size: 0.95rem;
        margin-bottom: 0.75rem;
        line-height: 1.4;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow: hidden;
    }
    
    .video-meta {
        color: #64748b;
        font-size: 0.8rem;
        margin-bottom: 1rem;
    }
    
    .relevance-badge {
        display: inline-block;
        padding: 0.3rem 0.6rem;
        border-radius: 0.4rem;
        font-weight: 700;
        font-size: 0.7rem;
        margin-bottom: 1rem;
    }
    
    .relevance-high { background: #059669; color: white; }
    .relevance-medium { background: #b45309; color: white; }
    
    .video-link {
        display: block;
        background: #10b981;
        color: #0a0e1a;
        padding: 0.6rem;
        border-radius: 0.4rem;
        text-decoration: none;
        font-weight: 700;
        font-size: 0.85rem;
        text-align: center;
        margin-top: auto;
    }

    .video-link:hover {
        background: #34d399;
    }
    
    /* Section Headers */
    .section-header {
        color: #10b981;
        font-size: 1.6rem;
        font-weight: 700;
        margin: 3rem 0 1.5rem 0;
        padding-bottom: 0.75rem;
        border-bottom: 2px solid #1e293b;
    }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# SIDEBAR
# =============================================================================
with st.sidebar:
    st.markdown("# 🛡️ EchoBreaker")
    st.markdown("### Breaking Filter Bubbles")
    st.markdown("---")
    
    st.markdown("### ⚙️ System Status")
    try:
        health = requests.get("http://localhost:8000/", timeout=2)
        if health.status_code == 200:
            st.success("✅ API Online")
        else:
            st.error("⚠️ API Issues")
    except:
        st.error("❌ API Offline - Ensure backend is running.")
    
    st.markdown("---")
    st.markdown("""
    ### 🎯 Our Mission
    Algorithms show you what you *want* to see. We show you what you *need* to consider.
    """)
    st.caption("v2.2.0 • Llama 3 • Whisper Local")

# =============================================================================
# MAIN CONTENT
# =============================================================================

st.markdown("""
<div class="mission-box">
    <div class="mission-title">🎯 Why EchoBreaker?</div>
    <div class="mission-text">
        Recommendation algorithms optimize for engagement, creating <strong>filter bubbles</strong>. 
        EchoBreaker analyzes the video's claims and surfaces <strong>verified counter-perspectives</strong> 
        to help you form a balanced, well-informed opinion.
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("## 🔍 Analyze Video")
col1, col2 = st.columns([4, 1])
with col1:
    video_url = st.text_input("YouTube URL", placeholder="Paste a link here...", label_visibility="collapsed")
with col2:
    analyze_button = st.button("🚀 Analyze", use_container_width=True)

if analyze_button:
    if not video_url:
        st.warning("Please provide a YouTube URL.")
    else:
        status_placeholder = st.empty()
        status_placeholder.info("🧠 Initializing AI Pipeline... (This involves downloading and transcribing, please wait)")
        
        try:
            response = requests.post(
                "http://localhost:8000/analyze",
                json={"video_url": video_url},
                timeout=600 
            )
            
            status_placeholder.empty()
            
            if response.status_code == 200:
                data = response.json()
                st.success("✅ Analysis Complete!")
                
                # --- 1. Video Metadata ---
                meta = data.get('video_metadata')
                if meta:
                    with st.expander("📺 Source Video Metadata"):
                        m_col1, m_col2 = st.columns([1, 2])
                        with m_col1:
                            if meta.get('thumbnail'):
                                st.image(meta.get('thumbnail'))
                        with m_col2:
                            st.write(f"**Title:** {meta.get('video_title')}")
                            st.write(f"**Channel:** {meta.get('channel_name')}")
                            st.write(f"**Views:** {meta.get('view_count')}")
                            st.write(f"**Duration:** {meta.get('duration')}")
                
                # --- 2. Summary & Sentiment ---
                st.markdown('<div class="section-header">📝 Intelligence Report</div>', unsafe_allow_html=True)
                
                sum_col1, sum_col2 = st.columns([2, 1])
                with sum_col1:
                    st.markdown(f"**Topic:** {data.get('topic', 'Topic detection failed.')}")
                    st.markdown(f"**Primary Claim:** {data.get('primary_claim', 'No clear claim identified.')}")
                with sum_col2:
                    sentiment = data.get('overall_sentiment', 'Neutral').upper()
                    st.metric("Detected Tone", sentiment)

                # --- 3. Counter Arguments ---
                st.markdown('<div class="section-header">🔓 Counter-Perspectives</div>', unsafe_allow_html=True)
                
                counters = data.get('counter_arguments', [])
                if not counters:
                    st.info("The AI determined this video doesn't contain controversial claims requiring counter-arguments.")
                else:
                    for arg in counters:
                        st.markdown(f"""
                        <div class="counter-card">
                            <div class="counter-header">
                                <span class="counter-type">{arg.get('type')}</span>
                                <span class="contrast-score">⚡ Opposition Level: {int(arg.get('semantic_contrast_score', 0.8)*100)}%</span>
                            </div>
                            <h3 class="counter-title">{arg.get('title')}</h3>
                            <p class="counter-content">{arg.get('content')}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Academic Insight
                        if arg.get('academic_insight'):
                            st.markdown(f"""
                            <div class="academic-insight">
                                <div class="academic-label">🏛️ Academic Context</div>
                                <div class="academic-text">"{arg.get('academic_insight')}"</div>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        # Suggested Videos for this Argument
                        suggestions = arg.get('suggest_videos', arg.get('suggested_videos', []))
                        if suggestions:
                            st.write("**📺 Suggested Exploration:**")
                            v_cols = st.columns(len(suggestions))
                            for idx, vid in enumerate(suggestions):
                                with v_cols[idx]:
                                    rel_score = vid.get('relevance_score', 0.5)
                                    badge_class = "relevance-high" if rel_score >= 0.7 else "relevance-medium"
                                    
                                    st.markdown(f"""
                                    <div class="video-card">
                                        <div class="video-content">
                                            <div class="video-title" title="{vid.get('title')}">{vid.get('title')}</div>
                                            <div class="video-meta">👤 {vid.get('channel_name')}</div>
                                            <span class="relevance-badge {badge_class}">SCORE: {int(rel_score*100)}%</span>
                                            <a href="{vid.get('url')}" target="_blank" class="video-link">Watch Perspective</a>
                                        </div>
                                    </div>
                                    """, unsafe_allow_html=True)
                        st.markdown("<br>", unsafe_allow_html=True)

                # --- 4. Export ---
                st.markdown("---")
                st.download_button(
                    label="📥 Download Full Analysis (JSON)",
                    data=json.dumps(data, indent=2),
                    file_name=f"echobreaker_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )

            else:
                st.error(f"❌ Backend Error ({response.status_code}): {response.text}")
        except Exception as e:
            st.error(f"🔌 Connection Error: Is the API running? Error: {e}")

st.markdown("""
<div style="text-align: center; color: #64748b; padding: 2rem;">
    <p><strong>EchoBreaker</strong> • Privacy First • Local Processing</p>
</div>
""", unsafe_allow_html=True)