import streamlit as st
import requests
import plotly.graph_objects as go
import plotly.express as px
from typing import Optional

# =============================================================================
# PAGE CONFIGURATION
# =============================================================================
st.set_page_config(
    page_title="EchoBreaker | Intellectual Diversity Engine",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================================================
# CUSTOM CSS STYLING WITH GOOGLE FONTS
# =============================================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    /* Root Variables */
    :root {
        --slate-900: #0f172a;
        --slate-800: #1e293b;
        --slate-700: #334155;
        --slate-600: #475569;
        --emerald: #10b981;
        --emerald-dark: #059669;
        --gold: #fbbf24;
        --text-primary: #f1f5f9;
        --text-secondary: #94a3b8;
    }
    
    /* Global Font */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Main Container */
    .main {
        background-color: var(--slate-900);
        color: var(--text-primary);
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: var(--slate-800);
        border-right: 1px solid var(--slate-700);
    }
    
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: var(--emerald);
    }
    
    /* Metric Cards */
    .metric-card {
        background: linear-gradient(135deg, var(--slate-800) 0%, var(--slate-700) 100%);
        padding: 1.5rem;
        border-radius: 0.75rem;
        border: 1px solid var(--slate-600);
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        border-color: var(--emerald);
        transform: translateY(-2px);
        box-shadow: 0 10px 25px rgba(16, 185, 129, 0.2);
    }
    
    .metric-label {
        color: var(--text-secondary);
        font-size: 0.85rem;
        font-weight: 500;
        margin-bottom: 0.5rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .metric-value {
        color: var(--text-primary);
        font-size: 2rem;
        font-weight: 700;
    }
    
    /* Video Cards */
    .video-card {
        background: var(--slate-800);
        border: 1px solid var(--slate-700);
        border-radius: 0.75rem;
        overflow: hidden;
        transition: all 0.3s ease;
        height: 100%;
    }
    
    .video-card:hover {
        border-color: var(--emerald);
        transform: translateY(-4px);
        box-shadow: 0 12px 30px rgba(16, 185, 129, 0.25);
    }
    
    .video-thumbnail {
        width: 100%;
        height: 180px;
        object-fit: cover;
        border-bottom: 1px solid var(--slate-700);
    }
    
    .video-content {
        padding: 1rem;
    }
    
    .video-title {
        color: var(--text-primary);
        font-weight: 600;
        font-size: 0.95rem;
        margin-bottom: 0.75rem;
        line-height: 1.4;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow: hidden;
    }
    
    .video-link {
        display: inline-block;
        background: var(--emerald);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
        text-decoration: none;
        font-weight: 600;
        font-size: 0.85rem;
        transition: all 0.2s ease;
    }
    
    .video-link:hover {
        background: var(--emerald-dark);
        transform: translateX(2px);
    }
    
    /* Counter Argument Cards */
    .counter-card {
        background: linear-gradient(135deg, var(--slate-800) 0%, var(--slate-900) 100%);
        border: 1px solid var(--slate-700);
        border-radius: 0.75rem;
        padding: 2rem;
        margin-bottom: 2rem;
        border-left: 4px solid var(--gold);
    }
    
    .counter-header {
        display: flex;
        align-items: center;
        gap: 1rem;
        margin-bottom: 1.5rem;
    }
    
    .counter-type {
        background: var(--emerald);
        color: var(--slate-900);
        padding: 0.5rem 1.25rem;
        border-radius: 0.5rem;
        font-weight: 700;
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .counter-title {
        color: var(--text-primary);
        font-size: 1.5rem;
        font-weight: 700;
        flex: 1;
    }
    
    .counter-content {
        color: var(--text-secondary);
        line-height: 1.8;
        font-size: 1rem;
        margin-bottom: 1.5rem;
    }
    
    .counter-reference {
        color: var(--gold);
        font-size: 0.85rem;
        font-style: italic;
    }
    
    /* Section Headers */
    .section-header {
        color: var(--emerald);
        font-size: 1.25rem;
        font-weight: 700;
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid var(--slate-700);
    }
    
    /* Sentiment Badges */
    .badge {
        display: inline-block;
        padding: 0.35rem 0.85rem;
        border-radius: 0.5rem;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .badge-positive { background: #065f46; color: #10b981; }
    .badge-negative { background: #7f1d1d; color: #ef4444; }
    .badge-neutral { background: #374151; color: #9ca3af; }
    .badge-mixed { background: #713f12; color: #fbbf24; }
    
    /* Buttons */
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, var(--emerald) 0%, var(--emerald-dark) 100%);
        color: white;
        font-weight: 700;
        border: none;
        padding: 0.875rem 2rem;
        border-radius: 0.5rem;
        font-size: 1rem;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 25px rgba(16, 185, 129, 0.4);
    }
    
    /* Input Fields */
    .stTextInput>div>div>input {
        background-color: var(--slate-800);
        border: 1px solid var(--slate-700);
        color: var(--text-primary);
        border-radius: 0.5rem;
        padding: 0.875rem;
        font-size: 1rem;
    }
    
    .stTextInput>div>div>input:focus {
        border-color: var(--emerald);
        box-shadow: 0 0 0 2px rgba(16, 185, 129, 0.2);
    }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# SIDEBAR - MISSION & FRAMEWORK
# =============================================================================
with st.sidebar:
    st.markdown("# 🔍 EchoBreaker")
    st.markdown("### Breaking Echo Chambers")
    
    st.markdown("---")
    
    st.markdown("### 📖 Our Mission")
    st.markdown("""
    In an age where algorithms reinforce existing beliefs, **EchoBreaker** provides 
    objective counter-perspectives across three dimensions:
    
    - ⚖️ **Ethical**: Moral implications
    - 📈 **Empirical**: Data-driven evidence  
    - 🧠 **Logical**: Reasoning consistency
    
    We combat algorithmic bias by surfacing **intellectual diversity**.
    """)
    
    st.markdown("---")
    
    st.markdown("### 🎯 How It Works")
    st.markdown("""
    1. **Extract** audio from YouTube
    2. **Transcribe** using Whisper AI
    3. **Analyze** claims with Llama 3
    4. **Generate** counter-arguments
    5. **Discover** diverse perspectives
    """)
    
    st.markdown("---")
    st.markdown("_Powered by Local AI_")
    st.caption("Whisper + Llama 3 via Ollama")

# =============================================================================
# MAIN CONTENT
# =============================================================================
st.markdown("# 🎯 Analyze Video Content")
st.markdown("Enter a YouTube URL to discover alternative perspectives and counter-arguments.")

# Input Section
col1, col2 = st.columns([4, 1])
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
        # Multi-stage spinner messages
        progress_messages = [
            "🎬 Downloading audio...",
            "🎤 Transcribing with Whisper...",
            "🧠 Analyzing claims with Llama 3...",
            "🔍 Searching for diverse perspectives...",
        ]
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            for i, msg in enumerate(progress_messages):
                status_text.info(msg)
                progress_bar.progress((i + 1) / len(progress_messages))
                
                if i == 0:
                    # Start the actual request
                    response = requests.post(
                        "http://localhost:8000/analyze",
                        json={"video_url": video_url},
                        timeout=600
                    )
            
            progress_bar.empty()
            status_text.empty()
            
            if response.status_code == 200:
                data = response.json()
                st.success("✅ Analysis Complete!")
                
                # =============================================================================
                # QUICK INSIGHTS - METRICS & VISUALIZATIONS
                # =============================================================================
                st.markdown('<div class="section-header">📊 Quick Insights</div>', unsafe_allow_html=True)
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-label">Overall Sentiment</div>
                        <div class="metric-value">{data.get('overall_sentiment', 'N/A').upper()}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-label">Claims Extracted</div>
                        <div class="metric-value">{len(data.get('claims', []))}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-label">Counter-Arguments</div>
                        <div class="metric-value">{len(data.get('counter_arguments', []))}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col4:
                    total_videos = sum(len(c.get('suggested_videos', [])) for c in data.get('counter_arguments', []))
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-label">Videos Found</div>
                        <div class="metric-value">{total_videos}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Sentiment Distribution Chart
                claims = data.get('claims', [])
                if claims:
                    st.markdown("#### Sentiment Distribution")
                    sentiment_counts = {}
                    for claim in claims:
                        sent = claim.get('sentiment', 'neutral')
                        sentiment_counts[sent] = sentiment_counts.get(sent, 0) + 1
                    
                    fig = go.Figure(data=[go.Pie(
                        labels=list(sentiment_counts.keys()),
                        values=list(sentiment_counts.values()),
                        hole=0.4,
                        marker=dict(colors=['#10b981', '#ef4444', '#9ca3af']),
                        textfont=dict(color='#f1f5f9', size=14)
                    )])
                    fig.update_layout(
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        font=dict(color='#f1f5f9'),
                        height=300,
                        showlegend=True
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                # =============================================================================
                # TOPIC SUMMARY
                # =============================================================================
                st.markdown('<div class="section-header">📝 Topic Summary</div>', unsafe_allow_html=True)
                st.info(data.get('topic_summary', 'No summary available.'))
                
                # =============================================================================
                # EXTRACTED CLAIMS
                # =============================================================================
                st.markdown('<div class="section-header">💬 Extracted Claims</div>', unsafe_allow_html=True)
                
                if claims:
                    with st.expander(f"View {len(claims)} Claims", expanded=False):
                        for i, claim in enumerate(claims[:15], 1):
                            sentiment = claim.get('sentiment', 'neutral')
                            badge_class = f"badge-{sentiment}"
                            confidence = claim.get('confidence_score', 0) * 100
                            
                            st.markdown(f"""
                            <div style="background: var(--slate-800); padding: 1rem; border-radius: 0.5rem; margin-bottom: 1rem; border-left: 3px solid var(--emerald);">
                                <span class="badge {badge_class}">{sentiment.upper()}</span>
                                <span style="color: var(--gold); font-size: 0.85rem; margin-left: 0.5rem;">
                                    {confidence:.0f}% Confidence
                                </span>
                                <p style="color: var(--text-primary); margin-top: 0.75rem; line-height: 1.6;">
                                    {claim.get('text', '')}
                                </p>
                            </div>
                            """, unsafe_allow_html=True)
                
                # =============================================================================
                # COUNTER-ARGUMENTS & VIDEO SUGGESTIONS
                # =============================================================================
                st.markdown('<div class="section-header">🔓 Alternative Perspectives</div>', unsafe_allow_html=True)
                
                counter_arguments = data.get('counter_arguments', [])
                
                if counter_arguments:
                    for counter in counter_arguments:
                        # Counter Argument Header
                        st.markdown(f"""
                        <div class="counter-card">
                            <div class="counter-header">
                                <span class="counter-type">{counter.get('type', 'Unknown')}</span>
                                <h3 class="counter-title">{counter.get('title', 'Untitled')}</h3>
                            </div>
                            <p class="counter-content">{counter.get('content', '')}</p>
                            <p class="counter-reference">📚 {counter.get('source_reference', 'General reference')}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Video Suggestions Grid
                        suggested_videos = counter.get('suggested_videos', [])
                        
                        if suggested_videos:
                            st.markdown("#### 🎥 Recommended Videos")
                            
                            cols = st.columns(min(len(suggested_videos), 3))
                            for idx, video in enumerate(suggested_videos):
                                with cols[idx % 3]:
                                    thumbnail_url = video.get('thumbnail', '')
                                    
                                    if thumbnail_url:
                                        st.image(thumbnail_url, use_container_width=True)
                                    
                                    st.markdown(f"""
                                    <div style="background: var(--slate-800); padding: 1rem; border-radius: 0 0 0.75rem 0.75rem; border: 1px solid var(--slate-700); border-top: none;">
                                        <div class="video-title">{video.get('title', 'Untitled Video')}</div>
                                        <a href="{video.get('url', '#')}" target="_blank" class="video-link">
                                            ▶️ Watch Now
                                        </a>
                                    </div>
                                    """, unsafe_allow_html=True)
                        else:
                            st.caption("_No video suggestions available_")
                        
                        st.markdown("<br>", unsafe_allow_html=True)
                
                else:
                    st.warning("No counter-arguments generated.")
            
            else:
                st.error(f"❌ Error: {response.status_code} - {response.text}")
        
        except requests.exceptions.Timeout:
            st.error("⏱️ Request timed out. Try a shorter video.")
        except requests.exceptions.ConnectionError:
            st.error("🔌 Cannot connect to backend. Ensure the API is running at http://localhost:8000")
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: var(--text-secondary); padding: 1rem;">
    <p><strong>EchoBreaker</strong> | Intellectual Diversity Engine</p>
    <p style="font-size: 0.85rem;">Built with Responsible AI Principles</p>
</div>
""", unsafe_allow_html=True)
