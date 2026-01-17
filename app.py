import streamlit as st
import requests
import time
from typing import Optional

# =============================================================================
# PAGE CONFIGURATION
# =============================================================================
st.set_page_config(
    page_title="EchoBreaker | Intellectual Diversity Engine",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =============================================================================
# CUSTOM CSS STYLING
# =============================================================================
st.markdown("""
<style>
    /* Root Variables */
    :root {
        --slate: #1e293b;
        --slate-light: #334155;
        --emerald: #10b981;
        --gold: #fbbf24;
        --text-primary: #f1f5f9;
        --text-secondary: #94a3b8;
    }
    
    /* Main Container */
    .main {
        background-color: #0f172a;
        color: var(--text-primary);
    }
    
    /* Hero Section */
    .hero-container {
        background: linear-gradient(135deg, var(--slate) 0%, #0f172a 100%);
        padding: 3rem 2rem;
        border-radius: 1rem;
        border-left: 4px solid var(--emerald);
        margin-bottom: 2rem;
    }
    
    .hero-title {
        font-size: 3rem;
        font-weight: 700;
        background: linear-gradient(135deg, var(--emerald) 0%, var(--gold) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1rem;
    }
    
    .hero-subtitle {
        font-size: 1.25rem;
        color: var(--text-secondary);
        line-height: 1.8;
    }
    
    /* Framework Pills */
    .framework-container {
        display: flex;
        gap: 1rem;
        margin: 2rem 0;
        flex-wrap: wrap;
    }
    
    .framework-pill {
        background: var(--slate-light);
        padding: 1rem 1.5rem;
        border-radius: 0.75rem;
        border: 1px solid #475569;
        flex: 1;
        min-width: 200px;
    }
    
    .framework-pill h4 {
        color: var(--emerald);
        margin-bottom: 0.5rem;
        font-size: 1.1rem;
    }
    
    .framework-pill p {
        color: var(--text-secondary);
        font-size: 0.9rem;
        line-height: 1.6;
    }
    
    /* Sentiment Badges */
    .badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 0.5rem;
        font-size: 0.85rem;
        font-weight: 600;
        margin-right: 0.5rem;
    }
    
    .badge-positive { background: #065f46; color: #10b981; }
    .badge-negative { background: #7f1d1d; color: #ef4444; }
    .badge-neutral { background: #374151; color: #9ca3af; }
    
    /* Counter Argument Card */
    .counter-card {
        background: var(--slate);
        border: 1px solid #475569;
        border-radius: 0.75rem;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        border-left: 4px solid var(--gold);
    }
    
    .counter-card-header {
        display: flex;
        align-items: center;
        gap: 1rem;
        margin-bottom: 1rem;
    }
    
    .counter-type {
        background: var(--emerald);
        color: #0f172a;
        padding: 0.35rem 1rem;
        border-radius: 0.5rem;
        font-weight: 700;
        font-size: 0.85rem;
    }
    
    .counter-title {
        color: var(--text-primary);
        font-size: 1.3rem;
        font-weight: 600;
    }
    
    .counter-content {
        color: var(--text-secondary);
        line-height: 1.8;
        margin-bottom: 1.5rem;
    }
    
    /* Video Suggestion Cards */
    .video-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 1rem;
        margin-top: 1rem;
    }
    
    .video-card {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 0.5rem;
        padding: 1rem;
        transition: all 0.3s ease;
    }
    
    .video-card:hover {
        border-color: var(--emerald);
        transform: translateY(-2px);
    }
    
    .video-title {
        color: var(--text-primary);
        font-weight: 500;
        margin-bottom: 0.5rem;
        font-size: 0.95rem;
    }
    
    .video-link {
        color: var(--emerald);
        text-decoration: none;
        font-size: 0.85rem;
    }
    
    /* Metrics */
    .metric-container {
        background: var(--slate);
        border-radius: 0.75rem;
        padding: 1.5rem;
        border: 1px solid #475569;
    }
    
    .metric-label {
        color: var(--text-secondary);
        font-size: 0.9rem;
        margin-bottom: 0.5rem;
    }
    
    .metric-value {
        color: var(--text-primary);
        font-size: 1.8rem;
        font-weight: 700;
    }
    
    /* Streamlit Overrides */
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, var(--emerald) 0%, #059669 100%);
        color: white;
        font-weight: 700;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 0.5rem;
        font-size: 1.1rem;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        background: linear-gradient(135deg, #059669 0%, var(--emerald) 100%);
        transform: translateY(-2px);
        box-shadow: 0 10px 25px rgba(16, 185, 129, 0.3);
    }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# HERO SECTION
# =============================================================================
st.markdown("""
<div class="hero-container">
    <h1 class="hero-title">🔍 EchoBreaker</h1>
    <p class="hero-subtitle">
        <strong>Breaking the Echo Chamber, One Perspective at a Time.</strong><br><br>
        In an age where algorithms reinforce our existing beliefs, EchoBreaker serves as your intellectual 
        compass. We analyze video content and surface <em>complementary and opposing viewpoints</em> across 
        three critical dimensions: Ethical reasoning, Empirical evidence, and Logical consistency.<br><br>
        <strong>Why?</strong> Because intellectual diversity is not just healthy—it's essential for a 
        functioning democracy and personal growth. Welcome to the antidote to algorithmic bias.
    </p>
</div>
""", unsafe_allow_html=True)

# =============================================================================
# ANALYSIS FRAMEWORK
# =============================================================================
st.markdown("### 📊 Our Analysis Framework")
st.markdown("""
<div class="framework-container">
    <div class="framework-pill">
        <h4>⚖️ Ethical</h4>
        <p>Examining moral implications, societal impact, and value-based considerations.</p>
    </div>
    <div class="framework-pill">
        <h4>📈 Empirical</h4>
        <p>Confronting claims with data, research, and real-world evidence.</p>
    </div>
    <div class="framework-pill">
        <h4>🧠 Logical</h4>
        <p>Identifying reasoning gaps, fallacies, and alternative logical frameworks.</p>
    </div>
</div>
""", unsafe_allow_html=True)

# =============================================================================
# INPUT SECTION
# =============================================================================
st.markdown("---")
st.markdown("### 🎯 Analyze a Video")

col1, col2 = st.columns([3, 1])
with col1:
    video_url = st.text_input(
        "YouTube URL",
        placeholder="https://www.youtube.com/watch?v=...",
        label_visibility="collapsed"
    )
with col2:
    analyze_button = st.button("🔍 Analyze", use_container_width=True)

# =============================================================================
# ANALYSIS LOGIC
# =============================================================================
if analyze_button:
    if not video_url:
        st.error("⚠️ Please enter a valid YouTube URL.")
    else:
        with st.spinner("🧠 Analyzing video... This may take a few minutes."):
            try:
                response = requests.post(
                    "http://localhost:8000/analyze",
                    json={"video_url": video_url},
                    timeout=600
                )
                
                if response.status_code == 200:
                    data = response.json()
                    st.success("✅ Analysis complete!")
                    
                    # =============================================================================
                    # RESULTS DASHBOARD
                    # =============================================================================
                    st.markdown("---")
                    st.markdown("## 📋 Analysis Results")
                    
                    # Summary Metrics
                    metric_col1, metric_col2, metric_col3 = st.columns(3)
                    
                    with metric_col1:
                        st.markdown(f"""
                        <div class="metric-container">
                            <div class="metric-label">Overall Sentiment</div>
                            <div class="metric-value">{data.get('overall_sentiment', 'N/A').upper()}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with metric_col2:
                        st.markdown(f"""
                        <div class="metric-container">
                            <div class="metric-label">Claims Extracted</div>
                            <div class="metric-value">{len(data.get('claims', []))}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with metric_col3:
                        st.markdown(f"""
                        <div class="metric-container">
                            <div class="metric-label">Counter-Arguments</div>
                            <div class="metric-value">{len(data.get('counter_arguments', []))}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Topic Summary
                    st.markdown("### 📝 Topic Summary")
                    st.info(data.get('topic_summary', 'No summary available.'))
                    
                    # Claims Mining
                    st.markdown("### 💬 Extracted Claims")
                    claims = data.get('claims', [])
                    
                    if claims:
                        with st.expander(f"View {len(claims)} Claims", expanded=True):
                            for i, claim in enumerate(claims[:10], 1):  # Limit to 10 for readability
                                sentiment = claim.get('sentiment', 'neutral')
                                badge_class = f"badge-{sentiment}"
                                st.markdown(f"""
                                <div style="margin-bottom: 1rem; padding: 1rem; background: var(--slate); border-radius: 0.5rem;">
                                    <span class="badge {badge_class}">{sentiment.upper()}</span>
                                    <p style="color: var(--text-primary); margin-top: 0.5rem;">{claim.get('text', '')}</p>
                                </div>
                                """, unsafe_allow_html=True)
                    else:
                        st.warning("No claims extracted.")
                    
                    # =============================================================================
                    # ECHO BREAKER SECTION - THE STAR OF THE SHOW
                    # =============================================================================
                    st.markdown("---")
                    st.markdown("## 🔓 EchoBreaker: Alternative Perspectives")
                    
                    counter_arguments = data.get('counter_arguments', [])
                    
                    if counter_arguments:
                        for counter in counter_arguments:
                            # Counter Argument Card
                            st.markdown(f"""
                            <div class="counter-card">
                                <div class="counter-card-header">
                                    <span class="counter-type">{counter.get('type', 'Unknown').upper()}</span>
                                    <h3 class="counter-title">{counter.get('title', 'Untitled')}</h3>
                                </div>
                                <p class="counter-content">{counter.get('content', '')}</p>
                                <p style="color: var(--text-secondary); font-size: 0.85rem; font-style: italic;">
                                    📚 {counter.get('source_reference', 'General reference')}
                                </p>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Recommended Videos Section
                            suggested_videos = counter.get('suggested_videos', [])
                            
                            if suggested_videos:
                                st.markdown("#### 🎥 Recommended Perspectives")
                                
                                # Video grid
                                cols = st.columns(min(len(suggested_videos), 3))
                                for idx, video in enumerate(suggested_videos):
                                    with cols[idx % 3]:
                                        st.markdown(f"""
                                        <div class="video-card">
                                            <div class="video-title">{video.get('title', 'Untitled Video')}</div>
                                            <a href="{video.get('url', '#')}" target="_blank" class="video-link">
                                                🔗 Watch on YouTube
                                            </a>
                                        </div>
                                        """, unsafe_allow_html=True)
                            else:
                                st.caption("_No video suggestions available for this argument._")
                            
                            st.markdown("<br>", unsafe_allow_html=True)
                    
                    else:
                        st.warning("No counter-arguments generated.")
                
                else:
                    st.error(f"❌ Error: {response.status_code} - {response.text}")
            
            except requests.exceptions.Timeout:
                st.error("⏱️ Request timed out. The video might be too long or the server is busy.")
            except requests.exceptions.ConnectionError:
                st.error("🔌 Cannot connect to the backend. Make sure the API is running at http://localhost:8000")
            except Exception as e:
                st.error(f"❌ An unexpected error occurred: {str(e)}")

# =============================================================================
# FOOTER
# =============================================================================
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: var(--text-secondary); padding: 2rem 0;">
    <p><strong>EchoBreaker</strong> | Built with responsibility for intellectual diversity.</p>
    <p style="font-size: 0.85rem;">Powered by Local AI (Whisper + Llama 3 via Ollama)</p>
</div>
""", unsafe_allow_html=True)
