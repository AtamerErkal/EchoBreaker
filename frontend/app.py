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
    
    [data-testid="stSidebar"] {
        background: #111827;
        border-right: 1px solid #1f2937;
    }
    
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #10b981;
    }
    
    /* Mission Box */
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
    
    /* Video Summary Card */
    .video-summary-card {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 0.75rem;
        padding: 2rem;
        margin: 2rem 0;
        border-left: 4px solid #3b82f6;
    }
    
    .video-title-display {
        color: #f1f5f9;
        font-size: 1.4rem;
        font-weight: 700;
        margin-bottom: 1rem;
    }
    
    .video-meta-row {
        display: flex;
        gap: 2rem;
        flex-wrap: wrap;
        margin-bottom: 1.5rem;
        color: #94a3b8;
        font-size: 0.95rem;
    }
    
    .video-meta-item {
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .topic-label {
        color: #3b82f6;
        font-weight: 700;
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-top: 1rem;
        margin-bottom: 0.5rem;
    }
    
    .topic-text {
        color: #10b981;
        font-size: 1.1rem;
        font-weight: 600;
    }
    
    .claim-label {
        color: #fbbf24;
        font-weight: 700;
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-top: 1.5rem;
        margin-bottom: 0.5rem;
    }
    
    .claim-text {
        color: #cbd5e1;
        font-size: 1.05rem;
        line-height: 1.8;
    }
    
    /* Counter Argument Container */
    .counter-container {
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
        padding: 0.6rem 1.5rem;
        border-radius: 0.5rem;
        font-weight: 700;
        font-size: 1rem;
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
        font-size: 1.3rem;
        font-weight: 700;
        flex: 1;
    }
    
    .counter-content {
        color: #cbd5e1;
        line-height: 1.9;
        font-size: 1.05rem;
        margin-bottom: 2rem;
    }
    
    /* Academic Section */
    .academic-section {
        background: #0f172a;
        border: 1px solid #1e293b;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-bottom: 1.5rem;
        border-left: 3px solid #3b82f6;
    }
    
    .academic-label {
        color: #3b82f6;
        font-weight: 700;
        font-size: 0.9rem;
        margin-bottom: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .academic-text {
        color: #94a3b8;
        font-style: italic;
        line-height: 1.8;
        font-size: 1rem;
        margin-bottom: 1rem;
    }
    
    .academic-link {
        display: inline-block;
        color: #60a5fa;
        text-decoration: none;
        font-size: 0.85rem;
        padding: 0.5rem 1rem;
        background: #1e293b;
        border-radius: 0.5rem;
        border: 1px solid #334155;
        transition: all 0.3s ease;
    }
    
    .academic-link:hover {
        background: #334155;
        border-color: #3b82f6;
    }
    
    /* Videos Section */
    .videos-section {
        margin-top: 1.5rem;
    }
    
    .videos-label {
        color: #10b981;
        font-weight: 700;
        font-size: 0.9rem;
        margin-bottom: 1rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .video-card {
        background: #0f172a;
        border: 1px solid #1e293b;
        border-radius: 0.5rem;
        overflow: hidden;
        transition: all 0.3s ease;
        margin-bottom: 1rem;
    }
    
    .video-card:hover {
        border-color: #10b981;
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(16, 185, 129, 0.15);
    }
    
    .video-thumbnail {
        width: 100%;
        height: 180px;
        object-fit: cover;
        border-bottom: 1px solid #1e293b;
    }
    
    .video-content {
        padding: 1.25rem;
    }
    
    .video-title-card {
        color: #f1f5f9;
        font-weight: 600;
        font-size: 0.95rem;
        margin-bottom: 0.75rem;
        line-height: 1.5;
    }
    
    .video-meta {
        color: #64748b;
        font-size: 0.8rem;
        margin-bottom: 0.75rem;
    }
    
    .relevance-badge {
        display: inline-block;
        padding: 0.35rem 0.8rem;
        border-radius: 0.5rem;
        font-weight: 700;
        font-size: 0.7rem;
        margin-bottom: 0.75rem;
    }
    
    .relevance-high { background: #10b981; color: white; }
    .relevance-medium { background: #fbbf24; color: #0a0e1a; }
    .relevance-low { background: #64748b; color: white; }
    
    .video-link {
        display: inline-block;
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        padding: 0.65rem 1.25rem;
        border-radius: 0.5rem;
        text-decoration: none;
        font-weight: 700;
        font-size: 0.85rem;
        transition: all 0.3s ease;
        text-align: center;
    }
    
    .video-link:hover {
        background: linear-gradient(135deg, #059669 0%, #047857 100%);
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
    
    /* Buttons */
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        font-weight: 700;
        border: none;
        padding: 1rem 2rem;
        border-radius: 0.5rem;
        font-size: 1.05rem;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(16, 185, 129, 0.4);
    }
    
    /* Input Fields */
    .stTextInput>div>div>input {
        background-color: #1e293b;
        border: 1px solid #334155;
        color: #f1f5f9;
        border-radius: 0.5rem;
        padding: 1rem;
        font-size: 1rem;
    }
    
    .stTextInput>div>div>input:focus {
        border-color: #10b981;
        box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.2);
    }
    
    /* Processing Status */
    .processing-stage {
        background: #1e293b;
        border-left: 4px solid #3b82f6;
        padding: 1rem 1.5rem;
        margin: 0.5rem 0;
        border-radius: 0.5rem;
    }
    
    .stage-title {
        color: #3b82f6;
        font-weight: 600;
        font-size: 0.95rem;
    }
    
    .stage-desc {
        color: #94a3b8;
        font-size: 0.85rem;
        margin-top: 0.25rem;
    }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# SIDEBAR
# =============================================================================
with st.sidebar:
    st.markdown("# 🛡️ EchoBreaker")
    st.markdown("### Breaking Algorithmic Echo Chambers")
    
    st.markdown("---")
    
    st.markdown("""
    ### 🎯 Our Mission
    
    Modern platforms like YouTube optimize for engagement, unintentionally creating echo chambers where you only see perspectives similar to what you already believe.
    
    **EchoBreaker doesn't criticize YouTube.** We complement it by surfacing the strongest counter-perspectives the algorithm isn't showing you.
    
    **The goal:** Help you make informed decisions by considering multiple viewpoints before forming opinions.
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
        st.caption("Start with: `uvicorn api.main:app --reload`")
    
    st.markdown("---")
    
    st.markdown("""
    ### 📖 How It Works
    
    1. **Extract** audio from YouTube
    2. **Transcribe** using Whisper AI
    3. **Analyze** claims and arguments
    4. **Generate** counter-perspectives across 3 dimensions:
       - 🔹 **Ethical**: Moral frameworks
       - 🔹 **Empirical**: Research/data
       - 🔹 **Logical**: Reasoning critiques
    5. **Discover** authoritative sources
    6. **Verify** quality (dual-pass filtering)
    
    **All processing happens locally.**
    """)
    
    st.markdown("---")
    st.caption("Powered by Whisper + Llama 3")
    st.caption("100% Local • 100% Private")

# =============================================================================
# MAIN CONTENT
# =============================================================================

# Mission Statement
st.markdown("""
<div class="mission-box">
    <div class="mission-title">🎯 Why EchoBreaker Exists</div>
    <div class="mission-text">
        <strong>The Problem:</strong> Recommendation algorithms create filter bubbles. You watch one viewpoint, 
        the algorithm shows you 10 more supporting it. Over time, you become polarized—not through 
        deliberate choice, but through <strong>algorithmic isolation from diverse perspectives</strong>.
        <br><br>
        <strong>Our Solution:</strong> We surface the <strong>strongest counter-arguments</strong> the algorithm 
        isn't showing you. Not to change your mind, but to help you make informed decisions by considering 
        <strong>multiple sides before forming opinions</strong>.
        <br><br>
        <strong>We respect YouTube.</strong> We're not competitors—we're a complementary tool addressing 
        an inherent challenge in all engagement-optimized platforms.
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# Input Section
st.markdown("## 🔍 Analyze Video Content")
st.markdown("Enter a YouTube URL to discover counter-perspectives you're not algorithmically seeing.")

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
        stages = [
            ("🎬 Extracting audio", "Downloading content from YouTube"),
            ("🎤 Transcribing speech", "Whisper AI processing"),
            ("🧠 Analyzing arguments", "Extracting claims and viewpoints"),
            ("🔍 Generating counter-perspectives", "Ethical, Empirical, Logical dimensions"),
            ("🌐 Discovering sources", "Searching for authoritative counter-content"),
            ("✅ Verifying quality", "Dual-pass relevance checking"),
        ]
        
        progress_bar = st.progress(0)
        status_placeholder = st.empty()
        
        try:
            for i, (stage_title, stage_desc) in enumerate(stages):
                status_placeholder.markdown(f"""
                <div class="processing-stage">
                    <div class="stage-title">{stage_title}</div>
                    <div class="stage-desc">{stage_desc}</div>
                </div>
                """, unsafe_allow_html=True)
                progress_bar.progress((i + 1) / len(stages))
                
                if i == 0:
                    response = requests.post(
                        "http://localhost:8000/analyze",
                        json={"video_url": video_url},
                        timeout=1200
                    )
            
            progress_bar.empty()
            status_placeholder.empty()
            
            if response.status_code == 200:
                data = response.json()
                st.success("✅ Analysis Complete!")
                
                # =============================================================================
                # VIDEO SUMMARY WITH METADATA
                # =============================================================================
                st.markdown('<div class="section-header">📺 Video Summary</div>', unsafe_allow_html=True)
                
                metadata = data.get('video_metadata', {})
                if metadata:
                    # Format duration
                    duration = metadata.get('duration')
                    if duration:
                        mins, secs = divmod(duration, 60)
                        hours, mins = divmod(mins, 60)
                        duration_str = f"{hours}:{mins:02d}:{secs:02d}" if hours > 0 else f"{mins}:{secs:02d}"
                    else:
                        duration_str = "N/A"
                    
                    # Format views
                    views = metadata.get('view_count', 0)
                    if views >= 1000000:
                        views_str = f"{views/1000000:.1f}M views"
                    elif views >= 1000:
                        views_str = f"{views/1000:.1f}K views"
                    else:
                        views_str = f"{views} views"
                    
                    # Format date
                    upload_date = metadata.get('upload_date', '')
                    if upload_date and len(upload_date) == 8:
                        formatted_date = f"{upload_date[0:4]}-{upload_date[4:6]}-{upload_date[6:8]}"
                    else:
                        formatted_date = "N/A"
                    
                    st.markdown(f"""
                    <div class="video-summary-card">
                        <div class="video-title-display">{metadata.get('title', 'Unknown Title')}</div>
                        <div class="video-meta-row">
                            <div class="video-meta-item">📺 {metadata.get('channel_name', 'Unknown Channel')}</div>
                            <div class="video-meta-item">⏱️ {duration_str}</div>
                            <div class="video-meta-item">👁️ {views_str}</div>
                            <div class="video-meta-item">📅 {formatted_date}</div>
                        </div>
                        
                        <div class="topic-label">🎯 Topic</div>
                        <div class="topic-text">{data.get('topic', 'Not specified')}</div>
                        
                        <div class="claim-label">💬 Primary Claim</div>
                        <div class="claim-text">{data.get('primary_claim', data.get('topic_summary', 'No claim extracted.'))}</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.info("Video metadata not available.")
                
                # =============================================================================
                # COUNTER-PERSPECTIVES (3 BIG BOXES)
                # =============================================================================
                st.markdown('<div class="section-header">🔓 Counter-Perspectives</div>', unsafe_allow_html=True)
                st.markdown("These are **opposing viewpoints** the algorithm likely isn't showing you. Each is backed by academic context and verified sources.")
                
                counter_arguments = data.get('counter_arguments', [])
                
                if counter_arguments:
                    for counter in counter_arguments:
                        contrast_score = counter.get('semantic_contrast_score', 0.8)
                        
                        st.markdown(f"""
                        <div class="counter-container">
                            <div class="counter-header">
                                <span class="counter-type">{counter.get('type', 'Unknown')}</span>
                                <span class="contrast-score">⚡ {contrast_score * 100:.0f}% Opposition</span>
                            </div>
                            <h3 class="counter-title">{counter.get('title', 'Untitled')}</h3>
                            <p class="counter-content">{counter.get('content', '')}</p>
                        """, unsafe_allow_html=True)
                        
                        # Academic Insight Section
                        academic_text = counter.get('academic_insight', '')
                        source_link = counter.get('source_link', '')
                        
                        if academic_text:
                            st.markdown(f"""
                            <div class="academic-section">
                                <div class="academic-label">🏛️ Academic Perspective</div>
                                <div class="academic-text">"{academic_text}"</div>
                                {f'<a href="{source_link}" target="_blank" class="academic-link">📚 View Academic Source →</a>' if source_link else ''}
                            </div>
                            """, unsafe_allow_html=True)
                        
                        # Verified Videos Section
                        suggested_videos = counter.get('suggested_videos', [])
                        
                        if suggested_videos:
                            st.markdown(f"""
                            <div class="videos-section">
                                <div class="videos-label">📺 Verified Sources ({len(suggested_videos)})</div>
                            """, unsafe_allow_html=True)
                            
                            for video in suggested_videos:
                                relevance = video.get('relevance_score', 0.5)
                                if relevance >= 0.85:
                                    badge_class, badge_text = "relevance-high", "HIGH RELEVANCE"
                                elif relevance >= 0.7:
                                    badge_class, badge_text = "relevance-medium", "GOOD RELEVANCE"
                                else:
                                    badge_class, badge_text = "relevance-low", "MODERATE"
                                
                                # Format duration
                                duration = video.get('duration')
                                if duration:
                                    mins, secs = divmod(duration, 60)
                                    hours, mins = divmod(mins, 60)
                                    duration_str = f"{hours}:{mins:02d}:{secs:02d}" if hours > 0 else f"{mins}:{secs:02d}"
                                else:
                                    duration_str = "N/A"
                                
                                # Format views
                                views = video.get('view_count', 0)
                                if views >= 1000000:
                                    views_str = f"{views/1000000:.1f}M"
                                elif views >= 1000:
                                    views_str = f"{views/1000:.1f}K"
                                else:
                                    views_str = str(views)
                                
                                thumbnail = video.get('thumbnail', '')
                                
                                st.markdown(f"""
                                <div class="video-card">
                                    {f'<img src="{thumbnail}" class="video-thumbnail" alt="Video thumbnail">' if thumbnail else ''}
                                    <div class="video-content">
                                        <div class="video-title-card">{video.get('title', 'Untitled')}</div>
                                        <div class="video-meta">
                                            📺 {video.get('channel_name', 'Unknown')} • 
                                            ⏱️ {duration_str} • 
                                            👁️ {views_str}
                                        </div>
                                        <span class="relevance-badge {badge_class}">✓ {badge_text} ({relevance * 100:.0f}%)</span>
                                        <br><br>
                                        <a href="{video.get('url', '#')}" target="_blank" class="video-link">
                                            ▶️ Watch on YouTube
                                        </a>
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
                            
                            st.markdown("</div>", unsafe_allow_html=True)
                        else:
                            st.info("⚠️ No high-quality sources found for this counter-perspective.")
                        
                        st.markdown("</div>", unsafe_allow_html=True)
                        st.markdown("<br>", unsafe_allow_html=True)
                
                else:
                    st.warning("No counter-arguments generated.")
                
                # Export
                st.markdown("---")
                st.markdown("### 📥 Export Analysis")
                json_data = json.dumps(data, indent=2)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                st.download_button(
                    label="📄 Download Full Report (JSON)",
                    data=json_data,
                    file_name=f"echobreaker_analysis_{timestamp}.json",
                    mime="application/json"
                )
            
            else:
                st.error(f"❌ Error: {response.status_code}")
        
        except requests.exceptions.Timeout:
            st.error("⏱️ Request timed out.")
        except requests.exceptions.ConnectionError:
            st.error("🔌 Cannot connect to API.")
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #64748b; padding: 2rem;">
    <p style="font-size: 1rem;"><strong>EchoBreaker</strong> | Breaking Algorithmic Echo Chambers</p>
    <p style="font-size: 0.85rem;">We don't tell you what to think. We show you what else to think about.</p>
    <p style="font-size: 0.75rem; color: #475569;">
        100% Local • Privacy-First • Open Source<br>Powered by Whisper + Llama 3
    </p>
</div>
""", unsafe_allow_html=True)