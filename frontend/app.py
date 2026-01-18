import streamlit as st
import requests
import plotly.graph_objects as go
import plotly.express as px
from typing import Optional
import json
from datetime import datetime

# =============================================================================
# PAGE CONFIGURATION
# =============================================================================
st.set_page_config(
    page_title="EchoBreaker V2.0 | Intelligence Dashboard",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================================================
# CUSTOM CSS STYLING WITH GOOGLE FONTS
# =============================================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Lexend:wght@400;500;600;700&display=swap');
    
    /* Root Variables */
    :root {
        --slate-950: #020617;
        --slate-900: #0f172a;
        --slate-800: #1e293b;
        --slate-700: #334155;
        --slate-600: #475569;
        --emerald: #10b981;
        --emerald-dark: #059669;
        --emerald-light: #34d399;
        --gold: #fbbf24;
        --gold-dark: #f59e0b;
        --red: #ef4444;
        --blue: #3b82f6;
        --text-primary: #f1f5f9;
        --text-secondary: #94a3b8;
        --text-tertiary: #64748b;
    }
    
    /* Global Font */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    h1, h2, h3, .section-header {
        font-family: 'Lexend', sans-serif;
    }
    
    /* Main Container */
    .main {
        background-color: var(--slate-950);
        color: var(--text-primary);
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, var(--slate-900) 0%, var(--slate-800) 100%);
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
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    
    .metric-card:hover {
        border-color: var(--emerald);
        transform: translateY(-4px);
        box-shadow: 0 12px 28px rgba(16, 185, 129, 0.25);
    }
    
    .metric-label {
        color: var(--text-secondary);
        font-size: 0.85rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
    }
    
    .metric-value {
        color: var(--text-primary);
        font-size: 2.25rem;
        font-weight: 800;
        font-family: 'Lexend', sans-serif;
    }
    
    .metric-subtitle {
        color: var(--text-tertiary);
        font-size: 0.75rem;
        margin-top: 0.5rem;
    }
    
    /* Video Cards */
    .video-card {
        background: var(--slate-800);
        border: 1px solid var(--slate-700);
        border-radius: 0.75rem;
        overflow: hidden;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        height: 100%;
        position: relative;
    }
    
    .video-card:hover {
        border-color: var(--emerald);
        transform: translateY(-6px) scale(1.02);
        box-shadow: 0 16px 36px rgba(16, 185, 129, 0.3);
    }
    
    .video-thumbnail-container {
        position: relative;
        overflow: hidden;
    }
    
    .video-thumbnail {
        width: 100%;
        height: 180px;
        object-fit: cover;
        border-bottom: 1px solid var(--slate-700);
        transition: transform 0.3s ease;
    }
    
    .video-card:hover .video-thumbnail {
        transform: scale(1.05);
    }
    
    .video-metadata-overlay {
        position: absolute;
        bottom: 0;
        left: 0;
        right: 0;
        background: linear-gradient(to top, rgba(0,0,0,0.9), transparent);
        padding: 1rem 0.75rem 0.5rem;
        display: flex;
        justify-content: space-between;
        font-size: 0.7rem;
        color: var(--text-primary);
    }
    
    .relevance-badge {
        position: absolute;
        top: 0.5rem;
        right: 0.5rem;
        padding: 0.35rem 0.75rem;
        border-radius: 0.5rem;
        font-weight: 700;
        font-size: 0.7rem;
        backdrop-filter: blur(10px);
        display: flex;
        align-items: center;
        gap: 0.25rem;
    }
    
    .relevance-high {
        background: rgba(16, 185, 129, 0.9);
        color: white;
    }
    
    .relevance-medium {
        background: rgba(251, 191, 36, 0.9);
        color: var(--slate-900);
    }
    
    .relevance-low {
        background: rgba(239, 68, 68, 0.9);
        color: white;
    }
    
    .video-content {
        padding: 1.25rem;
    }
    
    .video-title {
        color: var(--text-primary);
        font-weight: 600;
        font-size: 0.95rem;
        margin-bottom: 0.75rem;
        line-height: 1.5;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow: hidden;
        min-height: 2.85rem;
    }
    
    .video-channel {
        color: var(--text-secondary);
        font-size: 0.8rem;
        margin-bottom: 0.5rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .video-stats {
        color: var(--text-tertiary);
        font-size: 0.75rem;
        margin-bottom: 1rem;
    }
    
    .video-link {
        display: inline-block;
        background: linear-gradient(135deg, var(--emerald) 0%, var(--emerald-dark) 100%);
        color: white;
        padding: 0.65rem 1.25rem;
        border-radius: 0.5rem;
        text-decoration: none;
        font-weight: 700;
        font-size: 0.85rem;
        transition: all 0.3s ease;
        text-align: center;
        width: 100%;
    }
    
    .video-link:hover {
        background: linear-gradient(135deg, var(--emerald-dark) 0%, var(--emerald) 100%);
        transform: translateX(2px);
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.4);
    }
    
    /* Counter Argument Cards */
    .counter-card {
        background: linear-gradient(135deg, var(--slate-800) 0%, var(--slate-900) 100%);
        border: 1px solid var(--slate-700);
        border-radius: 0.75rem;
        padding: 2rem;
        margin-bottom: 2.5rem;
        border-left: 4px solid var(--gold);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
    }
    
    .counter-header {
        display: flex;
        align-items: center;
        gap: 1rem;
        margin-bottom: 1.5rem;
        flex-wrap: wrap;
    }
    
    .counter-type {
        background: var(--emerald);
        color: var(--slate-900);
        padding: 0.5rem 1.25rem;
        border-radius: 0.5rem;
        font-weight: 800;
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
    }
    
    .contrast-badge {
        background: var(--gold);
        color: var(--slate-900);
        padding: 0.4rem 0.9rem;
        border-radius: 0.5rem;
        font-weight: 700;
        font-size: 0.7rem;
    }
    
    .counter-title {
        color: var(--text-primary);
        font-size: 1.5rem;
        font-weight: 700;
        flex: 1;
        min-width: 200px;
    }
    
    .counter-content {
        color: var(--text-secondary);
        line-height: 1.9;
        font-size: 1.05rem;
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
        font-size: 1.5rem;
        font-weight: 700;
        margin: 2.5rem 0 1.5rem 0;
        padding-bottom: 0.75rem;
        border-bottom: 2px solid var(--slate-700);
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }
    
    /* Sentiment Badges */
    .badge {
        display: inline-block;
        padding: 0.4rem 1rem;
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
        padding: 0.95rem 2rem;
        border-radius: 0.5rem;
        font-size: 1rem;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 28px rgba(16, 185, 129, 0.5);
    }
    
    /* Input Fields */
    .stTextInput>div>div>input {
        background-color: var(--slate-800);
        border: 1px solid var(--slate-700);
        color: var(--text-primary);
        border-radius: 0.5rem;
        padding: 0.95rem;
        font-size: 1rem;
    }
    
    .stTextInput>div>div>input:focus {
        border-color: var(--emerald);
        box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.2);
    }
    
    /* Skeleton Loader Animation */
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    .skeleton-loader {
        animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
    }
    
    /* Filter Panel */
    .filter-panel {
        background: var(--slate-800);
        border: 1px solid var(--slate-700);
        border-radius: 0.75rem;
        padding: 1.5rem;
        margin-bottom: 2rem;
    }
    
    /* Expander Styling */
    .streamlit-expanderHeader {
        background: var(--slate-800);
        border-radius: 0.5rem;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# SIDEBAR - MISSION & STATUS
# =============================================================================
with st.sidebar:
    st.markdown("# 🔍 EchoBreaker V2.0")
    st.markdown("### Intelligence Dashboard")
    
    st.markdown("---")
    
    # Mission in collapsible section
    with st.expander("📖 Our Mission", expanded=False):
        st.markdown("""
        In an age where algorithms reinforce existing beliefs, **EchoBreaker V2.0** provides 
        objective counter-perspectives across three dimensions:
        
        - ⚖️ **Ethical**: Moral implications and value trade-offs
        - 📈 **Empirical**: Data-driven evidence and research  
        - 🧠 **Logical**: Reasoning consistency and fallacy detection
        
        We combat algorithmic bias by surfacing **intellectual diversity** through:
        - **Semantic Contrast Enforcement**: Counter-arguments are diametrically opposed
        - **Dual-Pass Verification**: AI-verified relevance scoring
        - **Source Authority**: Prioritizing news, research, and educational content
        """)
    
    st.markdown("---")
    
    # System Status
    st.markdown("### ⚙️ System Status")
    try:
        health = requests.get("http://localhost:8000/", timeout=2)
        if health.status_code == 200:
            st.success("✅ API Online")
        else:
            st.error("⚠️ API Issues")
    except:
        st.error("❌ API Offline")
    
    st.markdown("---")
    
    st.markdown("### 🎯 How It Works")
    st.markdown("""
    1. **Extract** audio from YouTube (yt-dlp)
    2. **Transcribe** using Whisper AI
    3. **Analyze** with semantic contrast enforcement
    4. **Verify** video relevance (dual-pass)
    5. **Discover** authoritative diverse perspectives
    """)
    
    st.markdown("---")
    st.markdown("_Powered by Local AI_")
    st.caption("Whisper + Llama 3 via Ollama")

# =============================================================================
# MAIN CONTENT
# =============================================================================
st.markdown("# 🎯 Analyze Video Content")
st.markdown("Enter a YouTube URL to discover **diametrically opposed** perspectives with AI-verified relevance.")

# Input Section with examples
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
        # Enhanced multi-stage skeleton loaders
        stages = [
            ("🎬 Extracting audio stream...", "Downloading content"),
            ("🎤 Transcribing with Whisper AI...", "Speech-to-text processing"),
            ("🧠 Analyzing rhetorical patterns...", "Claim extraction and sentiment analysis"),
            ("🔍 Generating counter-arguments...", "Semantic contrast enforcement"),
            ("🌐 Cross-referencing global perspectives...", "Searching verified sources"),
            ("✅ Verifying source authority...", "Dual-pass relevance checking"),
        ]
        
        progress_container = st.container()
        status_placeholder = st.empty()
        
        with progress_container:
            progress_bar = st.progress(0)
            stage_cols = st.columns(len(stages))
            
            for i, (stage_icon, stage_desc) in enumerate(stages):
                with stage_cols[i]:
                    st.markdown(f"<div style='text-align: center; font-size: 0.7rem; color: var(--text-tertiary);'>{stage_icon}</div>", unsafe_allow_html=True)
        
        try:
            for i, (msg, desc) in enumerate(stages):
                status_placeholder.info(f"{msg}\n\n_{desc}_")
                progress_bar.progress((i + 1) / len(stages))
                
                if i == 0:
                    # Start the actual request
                    response = requests.post(
                        "http://localhost:8000/analyze",
                        json={"video_url": video_url},
                        timeout=1200  # 20 minutes for dual-pass verification
                    )
            
            progress_bar.empty()
            status_placeholder.empty()
            
            if response.status_code == 200:
                data = response.json()
                st.success("✅ Analysis Complete! Intelligence report generated.")
                
                # =============================================================================
                # QUICK INSIGHTS - METRICS & VISUALIZATIONS
                # =============================================================================
                st.markdown('<div class="section-header">📊 Intelligence Overview</div>', unsafe_allow_html=True)
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    sentiment = data.get('overall_sentiment', 'N/A').upper()
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-label">Overall Sentiment</div>
                        <div class="metric-value">{sentiment}</div>
                        <div class="metric-subtitle">Primary tone detected</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    claims_count = len(data.get('claims', []))
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-label">Claims Extracted</div>
                        <div class="metric-value">{claims_count}</div>
                        <div class="metric-subtitle">Statements analyzed</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    counter_count = len(data.get('counter_arguments', []))
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-label">Counter-Arguments</div>
                        <div class="metric-value">{counter_count}</div>
                        <div class="metric-subtitle">Opposing perspectives</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col4:
                    total_videos = sum(len(c.get('suggested_videos', [])) for c in data.get('counter_arguments', []))
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-label">Verified Videos</div>
                        <div class="metric-value">{total_videos}</div>
                        <div class="metric-subtitle">AI-verified sources</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Visualizations
                st.markdown("### 📈 Data Visualizations")
                
                viz_col1, viz_col2 = st.columns(2)
                
                claims = data.get('claims', [])
                counter_arguments = data.get('counter_arguments', [])
                
                # Sentiment Distribution Pie Chart
                with viz_col1:
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
                            marker=dict(colors=['#10b981', '#ef4444', '#9ca3af', '#fbbf24']),
                            textfont=dict(color='#f1f5f9', size=14, family='Inter')
                        )])
                        fig.update_layout(
                            paper_bgcolor='rgba(0,0,0,0)',
                            plot_bgcolor='rgba(0,0,0,0)',
                            font=dict(color='#f1f5f9', family='Inter'),
                            height=300,
                            showlegend=True,
                            margin=dict(l=20, r=20, t=20, b=20)
                        )
                        st.plotly_chart(fig, use_container_width=True)
                
                # Average Confidence Gauge
                with viz_col2:
                    if claims:
                        st.markdown("#### Average Confidence")
                        avg_confidence = sum(c.get('confidence_score', 0) for c in claims) / len(claims)
                        
                        fig = go.Figure(go.Indicator(
                            mode="gauge+number+delta",
                            value=avg_confidence * 100,
                            domain={'x': [0, 1], 'y': [0, 1]},
                            title={'text': "AI Certainty", 'font': {'color': '#f1f5f9', 'family': 'Lexend'}},
                            number={'suffix': "%", 'font': {'color': '#f1f5f9', 'family': 'Lexend'}},
                            gauge={
                                'axis': {'range': [None, 100], 'tickcolor': '#94a3b8'},
                                'bar': {'color': "#10b981"},
                                'bgcolor': "#1e293b",
                                'borderwidth': 2,
                                'bordercolor': "#334155",
                                'steps': [
                                    {'range': [0, 50], 'color': '#475569'},
                                    {'range': [50, 75], 'color': '#64748b'},
                                    {'range': [75, 100], 'color': '#94a3b8'}
                                ],
                                'threshold': {
                                    'line': {'color': "#fbbf24", 'width': 4},
                                    'thickness': 0.75,
                                    'value': 90
                                }
                            }
                        ))
                        fig.update_layout(
                            paper_bgcolor='rgba(0,0,0,0)',
                            font={'color': "#f1f5f9", 'family': 'Inter'},
                            height=300,
                            margin=dict(l=20, r=20, t=40, b=20)
                        )
                        st.plotly_chart(fig, use_container_width=True)
                
                # Counter-Argument Type Distribution
                if counter_arguments:
                    st.markdown("#### Counter-Argument Type Distribution")
                    types = [arg.get('type', 'Unknown') for arg in counter_arguments]
                    type_counts = {t: types.count(t) for t in set(types)}
                    
                    fig = go.Figure(data=[go.Bar(
                        x=list(type_counts.keys()),
                        y=list(type_counts.values()),
                        marker=dict(
                            color=['#10b981', '#3b82f6', '#fbbf24'][:len(type_counts)],
                            line=dict(color='#1e293b', width=2)
                        ),
                        text=list(type_counts.values()),
                        textposition='auto',
                    )])
                    fig.update_layout(
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        font=dict(color='#f1f5f9', family='Inter'),
                        height=300,
                        xaxis=dict(showgrid=False, color='#94a3b8'),
                        yaxis=dict(showgrid=True, gridcolor='#334155', color='#94a3b8'),
                        margin=dict(l=20, r=20, t=20, b=20)
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                # =============================================================================
                # TOPIC SUMMARY
                # =============================================================================
                st.markdown('<div class="section-header">📝 Topic Summary</div>', unsafe_allow_html=True)
                st.info(data.get('topic_summary', 'No summary available.'))
                
                # =============================================================================
                # EXTRACTED CLAIMS WITH FILTERS
                # =============================================================================
                st.markdown('<div class="section-header">💬 Extracted Claims</div>', unsafe_allow_html=True)
                
                if claims:
                    # Filter controls
                    filter_col1, filter_col2, filter_col3 = st.columns([2, 2, 3])
                    
                    with filter_col1:
                        sentiment_filter = st.selectbox(
                            "Filter by Sentiment",
                            ["All"] + list(set(c.get('sentiment', 'neutral') for c in claims))
                        )
                    
                    with filter_col2:
                        sort_option = st.selectbox(
                            "Sort by",
                            ["Confidence (High to Low)", "Confidence (Low to High)", "Original Order"]
                        )
                    
                    with filter_col3:
                        search_term = st.text_input("🔍 Search claims", placeholder="Enter keywords...")
                    
                    # Apply filters
                    filtered_claims = claims.copy()
                    
                    if sentiment_filter != "All":
                        filtered_claims = [c for c in filtered_claims if c.get('sentiment') == sentiment_filter]
                    
                    if search_term:
                        filtered_claims = [c for c in filtered_claims if search_term.lower() in c.get('text', '').lower()]
                    
                    if sort_option == "Confidence (High to Low)":
                        filtered_claims.sort(key=lambda x: x.get('confidence_score', 0), reverse=True)
                    elif sort_option == "Confidence (Low to High)":
                        filtered_claims.sort(key=lambda x: x.get('confidence_score', 0))
                    
                    st.caption(f"Showing {len(filtered_claims)} of {len(claims)} claims")
                    
                    with st.expander(f"View Claims", expanded=True):
                        for i, claim in enumerate(filtered_claims[:20], 1):
                            sentiment = claim.get('sentiment', 'neutral')
                            badge_class = f"badge-{sentiment}"
                            confidence = claim.get('confidence_score', 0) * 100
                            
                            st.markdown(f"""
                            <div style="background: var(--slate-800); padding: 1.25rem; border-radius: 0.5rem; margin-bottom: 1rem; border-left: 3px solid var(--emerald);">
                                <div style="display: flex; gap: 1rem; align-items: center; margin-bottom: 0.75rem;">
                                    <span class="badge {badge_class}">{sentiment.upper()}</span>
                                    <span style="color: var(--gold); font-size: 0.85rem; font-weight: 600;">
                                        ⚡ {confidence:.0f}% Confidence
                                    </span>
                                </div>
                                <p style="color: var(--text-primary); margin: 0; line-height: 1.7;">
                                    {claim.get('text', '')}
                                </p>
                            </div>
                            """, unsafe_allow_html=True)
                
                # =============================================================================
                # COUNTER-ARGUMENTS & VIDEO SUGGESTIONS
                # =============================================================================
                st.markdown('<div class="section-header">🔓 Alternative Perspectives</div>', unsafe_allow_html=True)
                st.caption("_AI-verified counter-arguments with semantic contrast enforcement_")
                
                if counter_arguments:
                    for counter in counter_arguments:
                        # Counter Argument Header
                        contrast_score = counter.get('semantic_contrast_score', 0.8)
                        
                        st.markdown(f"""
                        <div class="counter-card">
                            <div class="counter-header">
                                <span class="counter-type">{counter.get('type', 'Unknown')}</span>
                                <span class="contrast-badge">⚡ {contrast_score * 100:.0f}% Opposition</span>
                                <h3 class="counter-title">{counter.get('title', 'Untitled')}</h3>
                            </div>
                            <p class="counter-content">{counter.get('content', '')}</p>
                            <p class="counter-reference">📚 {counter.get('source_reference', 'General reference')}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # =============================================================================
                        # V2.2 HYBRID LAYOUT: VIDEO + ACADEMIC TEXT
                        # =============================================================================
                        
                        suggested_videos = counter.get('suggested_videos', [])
                        academic_text = counter.get('academic_insight', "Academic perspective generating...")
                        import html # Import globally for this block
                        
                        # 2-Column Split
                        h_col1, h_col2 = st.columns([1, 1], gap="medium")
                        
                        # --- LEFT COLUMN: TOP VIDEO SOURCE ---
                        with h_col1:
                            st.markdown("#### 📺 Verified Video Source")
                            if suggested_videos:
                                video = suggested_videos[0] # Take top 1
                                
                                # Metadata Calculation
                                relevance = video.get('relevance_score', 0.5)
                                if relevance >= 0.85:
                                    badge_class, badge_text = "relevance-high", "HIGH"
                                elif relevance >= 0.7:
                                    badge_class, badge_text = "relevance-medium", "GOOD"
                                else:
                                    badge_class, badge_text = "relevance-low", "LOW"
                                
                                # Duration & Views
                                duration = video.get('duration')
                                if duration:
                                    mins, secs = divmod(duration, 60)
                                    hours, mins = divmod(mins, 60)
                                    duration_str = f"{hours}:{mins:02d}:{secs:02d}" if hours > 0 else f"{mins}:{secs:02d}"
                                else:
                                    duration_str = "N/A"
                                
                                views = video.get('view_count', 0)
                                if views >= 1000000: views_str = f"{views/1000000:.1f}M"
                                elif views >= 1000: views_str = f"{views/1000:.1f}K"
                                else: views_str = str(views)
                                
                                thumbnail_url = video.get('thumbnail', '')
                                channel = video.get('channel_name', 'Unknown Channel')

                                # Render Card (Construct HTML first to ensure valid DOM)
                                safe_title = html.escape(video.get('title', 'Untitled Video'))
                                safe_channel = html.escape(channel)
                                safe_badge_text = html.escape(badge_text)
                                safe_views_str = html.escape(views_str)
                                safe_duration_str = html.escape(duration_str)
                                
                                card_html = f'<div class="video-card">'
                                
                                if thumbnail_url:
                                    # Ensure URL is safe (basic check, usually fine from youtube)
                                    safe_thumb = thumbnail_url.replace('"', '&quot;')
                                    card_html += f"""<div class="video-thumbnail-container"><img src="{safe_thumb}" class="video-thumbnail" alt="Video thumbnail"><div class="relevance-badge {badge_class}">✓ {safe_badge_text}</div><div class="video-metadata-overlay"><span>⏱️ {safe_duration_str}</span><span>👁️ {safe_views_str} views</span></div></div>"""
                                
                                card_html += f"""<div class="video-content"><div class="video-title">{safe_title}</div><div class="video-channel">📺 {safe_channel}</div><div class="video-stats">Relevance Score: {relevance * 100:.0f}%</div><a href="{video.get('url', '#')}" target="_blank" class="video-link">▶️ Watch Now</a></div></div>"""
                                
                                st.markdown(card_html, unsafe_allow_html=True)
                                
                            else:
                                st.info("⚠️ No high-quality video source found for this specific angle.")

                        # --- RIGHT COLUMN: ACADEMIC INSIGHT ---
                        with h_col2:
                            st.markdown("#### 🏛️ Academic Perspective")
                            
                            safe_academic_text = html.escape(academic_text)
                            safe_query = html.escape(counter.get('youtube_query', 'N/A'))
                            
                            # Compact HTML to prevent markdown code block rendering
                            academic_html = f"""<div style="background: var(--slate-800); border: 1px solid var(--slate-700); border-radius: 0.75rem; padding: 1.5rem; height: 100%; border-left: 4px solid var(--blue);"><div style="color: var(--text-secondary); font-style: italic; font-size: 1.05rem; line-height: 1.8; margin-bottom: 1rem;">"{safe_academic_text}"</div><div style="display: flex; gap: 0.75rem; flex-wrap: wrap;"><span style="background: var(--slate-700); padding: 0.25rem 0.75rem; border-radius: 1rem; font-size: 0.75rem; color: var(--text-primary);">🔬 Research Theory</span><span style="background: var(--slate-700); padding: 0.25rem 0.75rem; border-radius: 1rem; font-size: 0.75rem; color: var(--text-primary);">🎓 Verified Context</span></div></div>"""
                            st.markdown(academic_html, unsafe_allow_html=True)
                            
                            st.caption(f"_Search Query: \"{safe_query}\"_")
                        
                        st.markdown("<br>", unsafe_allow_html=True)
                
                else:
                    st.warning("No counter-arguments generated.")
                
                # =============================================================================
                # EXPORT FUNCTIONALITY
                # =============================================================================
                st.markdown("---")
                st.markdown("### 📥 Export Report")
                
                export_col1, export_col2 = st.columns(2)
                
                with export_col1:
                    json_data = json.dumps(data, indent=2)
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    st.download_button(
                        label="📄 Download JSON Report",
                        data=json_data,
                        file_name=f"echobreaker_report_{timestamp}.json",
                        mime="application/json"
                    )
                
                with export_col2:
                    st.info("💡 JSON export includes all analysis data, claims, counter-arguments, and video metadata.")
            
            else:
                st.error(f"❌ Error: {response.status_code} - {response.text}")
        
        except requests.exceptions.Timeout:
            st.error("⏱️ Request timed out. The video may be too long or the AI processing is taking longer than expected.")
        except requests.exceptions.ConnectionError:
            st.error("🔌 Cannot connect to backend. Ensure the API is running at http://localhost:8000")
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: var(--text-secondary); padding: 2rem;">
    <p style="font-size: 1.1rem;"><strong>EchoBreaker V2.0</strong> | Intelligence Dashboard</p>
    <p style="font-size: 0.9rem;">Built with Responsible AI Principles | Powered by Whisper + Llama 3</p>
    <p style="font-size: 0.8rem; color: var(--text-tertiary);">Semantic Contrast Enforcement • Dual-Pass Verification • Source Authority</p>
</div>
""", unsafe_allow_html=True)
