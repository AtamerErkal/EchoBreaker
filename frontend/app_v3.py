import streamlit as st
import requests
import json
from datetime import datetime

st.set_page_config(
    page_title="EchoBreaker | Breaking Algorithmic Echo Chambers",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    * { font-family: 'Inter', -apple-system, sans-serif; }
    .main { background-color: #0a0e1a; color: #e2e8f0; }
    [data-testid="stSidebar"] { background: #111827; border-right: 1px solid #1f2937; }
    [data-testid="stSidebar"] h1, h2, h3 { color: #10b981; }
    
    .mission-box {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid #334155; border-left: 4px solid #10b981;
        padding: 2rem; border-radius: 0.75rem; margin: 2rem 0;
    }
    .mission-title { color: #10b981; font-size: 1.5rem; font-weight: 700; margin-bottom: 1rem; }
    .mission-text { color: #cbd5e1; line-height: 1.8; font-size: 1.05rem; }
    
    .video-summary-card {
        background: #1e293b; border: 1px solid #334155; border-radius: 0.75rem;
        padding: 2rem; margin: 2rem 0; border-left: 4px solid #3b82f6;
    }
    .video-title-display { color: #f1f5f9; font-size: 1.4rem; font-weight: 700; margin-bottom: 1rem; }
    .video-meta-row { display: flex; gap: 2rem; flex-wrap: wrap; margin-bottom: 1.5rem; color: #94a3b8; font-size: 0.95rem; }
    .topic-label { color: #3b82f6; font-weight: 700; font-size: 0.85rem; text-transform: uppercase; margin-top: 1rem; margin-bottom: 0.5rem; }
    .topic-text { color: #10b981; font-size: 1.1rem; font-weight: 600; }
    .claim-label { color: #fbbf24; font-weight: 700; font-size: 0.85rem; text-transform: uppercase; margin-top: 1.5rem; margin-bottom: 0.5rem; }
    .claim-text { color: #cbd5e1; font-size: 1.05rem; line-height: 1.8; }
    
    .counter-container {
        background: #1e293b; border: 1px solid #334155; border-radius: 0.75rem;
        padding: 2rem; margin-bottom: 2rem; border-left: 4px solid #fbbf24;
    }
    .counter-header { display: flex; align-items: center; gap: 1rem; margin-bottom: 1.5rem; flex-wrap: wrap; }
    .counter-type { background: #10b981; color: #0a0e1a; padding: 0.6rem 1.5rem; border-radius: 0.5rem; font-weight: 700; font-size: 1rem; text-transform: uppercase; }
    .contrast-score { background: #fbbf24; color: #0a0e1a; padding: 0.5rem 1rem; border-radius: 0.5rem; font-weight: 600; font-size: 0.85rem; }
    .counter-title { color: #f1f5f9; font-size: 1.3rem; font-weight: 700; margin-bottom: 1rem; }
    .counter-content { color: #cbd5e1; line-height: 1.9; font-size: 1.05rem; margin-bottom: 2rem; }
    
    .academic-section {
        background: #0f172a; border: 1px solid #1e293b; padding: 1.5rem; border-radius: 0.5rem;
        margin-bottom: 1.5rem; border-left: 3px solid #3b82f6;
    }
    .academic-label { color: #3b82f6; font-weight: 700; font-size: 0.9rem; margin-bottom: 0.75rem; text-transform: uppercase; }
    .academic-text { color: #94a3b8; font-style: italic; line-height: 1.8; font-size: 1rem; margin-bottom: 1rem; }
    .academic-link {
        display: inline-block; color: #60a5fa; text-decoration: none; font-size: 0.85rem;
        padding: 0.5rem 1rem; background: #1e293b; border-radius: 0.5rem; border: 1px solid #334155; transition: all 0.3s ease;
    }
    .academic-link:hover { background: #334155; border-color: #3b82f6; }
    
    .videos-label { color: #10b981; font-weight: 700; font-size: 0.9rem; margin-bottom: 1rem; text-transform: uppercase; }
    .video-card {
        background: #0f172a; border: 1px solid #1e293b; border-radius: 0.5rem;
        overflow: hidden; transition: all 0.3s ease; margin-bottom: 1rem;
    }
    .video-card:hover { border-color: #10b981; transform: translateY(-2px); box-shadow: 0 8px 24px rgba(16, 185, 129, 0.15); }
    .video-thumbnail { width: 100%; height: 180px; object-fit: cover; border-bottom: 1px solid #1e293b; }
    .video-content { padding: 1.25rem; }
    .video-title-card { color: #f1f5f9; font-weight: 600; font-size: 0.95rem; margin-bottom: 0.75rem; line-height: 1.5; }
    .video-meta { color: #64748b; font-size: 0.8rem; margin-bottom: 0.75rem; }
    .relevance-badge { display: inline-block; padding: 0.35rem 0.8rem; border-radius: 0.5rem; font-weight: 700; font-size: 0.7rem; margin-bottom: 0.75rem; }
    .relevance-high { background: #10b981; color: white; }
    .relevance-medium { background: #fbbf24; color: #0a0e1a; }
    .video-link {
        display: inline-block; background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white; padding: 0.65rem 1.25rem; border-radius: 0.5rem; text-decoration: none;
        font-weight: 700; font-size: 0.85rem; transition: all 0.3s ease;
    }
    .video-link:hover { background: linear-gradient(135deg, #059669 0%, #047857 100%); }
    
    .section-header { color: #10b981; font-size: 1.6rem; font-weight: 700; margin: 3rem 0 1.5rem 0; padding-bottom: 0.75rem; border-bottom: 2px solid #1e293b; }
    .stButton>button { width: 100%; background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white; font-weight: 700; border: none; padding: 1rem 2rem; border-radius: 0.5rem; font-size: 1.05rem; }
    .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 8px 20px rgba(16, 185, 129, 0.4); }
    .stTextInput>div>div>input { background-color: #1e293b; border: 1px solid #334155; color: #f1f5f9; border-radius: 0.5rem; padding: 1rem; font-size: 1rem; }
    .stTextInput>div>div>input:focus { border-color: #10b981; box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.2); }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("# 🛡️ EchoBreaker")
    st.markdown("### Breaking Algorithmic Echo Chambers")
    st.markdown("---")
    st.markdown("""
    ### 🎯 Our Mission
    Modern platforms optimize for engagement, creating echo chambers. **EchoBreaker** surfaces the strongest counter-perspectives the algorithm isn't showing you.
    """)
    st.markdown("---")
    st.markdown("### ⚙️ System Status")
    try:
        health = requests.get("http://localhost:8000/", timeout=2)
        st.success("✅ API Online") if health.status_code == 200 else st.error("⚠️ API Issues")
    except:
        st.error("❌ API Offline")
    st.markdown("---")
    st.caption("Powered by Whisper + Llama 3 • 100% Local")

st.markdown("""
<div class="mission-box">
    <div class="mission-title">🎯 Why EchoBreaker Exists</div>
    <div class="mission-text">
        <strong>The Problem:</strong> Algorithms create filter bubbles—showing you 10 more videos supporting your existing views.
        <br><br>
        <strong>Our Solution:</strong> We surface <strong>verified counter-arguments</strong> to help you consider multiple sides before forming opinions.
        <br><br>
        <strong>We respect YouTube.</strong> We're a complementary tool, not a competitor.
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("---")
st.markdown("## 🔍 Analyze Video Content")

col1, col2 = st.columns([4, 1])
with col1:
    video_url = st.text_input("YouTube URL", placeholder="https://www.youtube.com/watch?v=...", label_visibility="collapsed")
with col2:
    analyze_button = st.button("🔍 Analyze", use_container_width=True)

if analyze_button:
    if not video_url:
        st.error("⚠️ Please enter a valid YouTube URL.")
    else:
        status = st.empty()
        status.info("🧠 Processing... (Download → Transcribe → Analyze)")
        
        try:
            response = requests.post("http://localhost:8000/analyze", json={"video_url": video_url}, timeout=1200)
            status.empty()
            
            if response.status_code == 200:
                data = response.json()
                st.success("✅ Analysis Complete!")
                
                # VIDEO SUMMARY
                st.markdown('<div class="section-header">📊 Intelligence Report</div>', unsafe_allow_html=True)
                
                metadata = data.get('video_metadata', {})
                if metadata:
                    # Use pre-formatted strings from backend
                    st.markdown(f"""
                    <div class="video-summary-card">
                        <div class="video-title-display">{metadata.get('video_title', 'Unknown')}</div>
                        <div class="video-meta-row">
                            <div>📺 {metadata.get('channel_name', 'Unknown')}</div>
                            <div>⏱️ {metadata.get('duration', '00:00')}</div>
                            <div>👁️ {metadata.get('view_count', '0')}</div>
                            <div>📅 {metadata.get('upload_date', 'Unknown')}</div>
                        </div>
                        <div class="topic-label">🎯 Topic</div>
                        <div class="topic-text">{data.get('topic', 'Not specified')}</div>
                        <div class="claim-label">💬 Primary Claim</div>
                        <div class="claim-text">{data.get('primary_claim', 'No claim extracted.')}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                # COUNTER-PERSPECTIVES
                st.markdown('<div class="section-header">🔓 Counter-Perspectives</div>', unsafe_allow_html=True)
                
                counters = data.get('counter_arguments', [])
                if counters:
                    for counter in counters:
                        score = counter.get('semantic_contrast_score', 0.8)
                        st.markdown(f"""
                        <div class="counter-container">
                            <div class="counter-header">
                                <span class="counter-type">{counter.get('type', 'Unknown')}</span>
                                <span class="contrast-score">⚡ {score * 100:.0f}% Opposition</span>
                            </div>
                            <h3 class="counter-title">{counter.get('title', 'Untitled')}</h3>
                            <p class="counter-content">{counter.get('content', '')}</p>
                        """, unsafe_allow_html=True)
                        
                        # Academic Section
                        academic = counter.get('academic_insight', '')
                        link = counter.get('source_link', '')
                        if academic:
                            st.markdown(f"""
                            <div class="academic-section">
                                <div class="academic-label">🏛️ Academic Perspective</div>
                                <div class="academic-text">"{academic}"</div>
                                {f'<a href="{link}" target="_blank" class="academic-link">📚 View Source →</a>' if link else ''}
                            </div>
                            """, unsafe_allow_html=True)
                        
                        # Videos
                        videos = counter.get('suggested_videos', [])
                        if videos:
                            st.markdown(f'<div class="videos-label">📺 Verified Sources ({len(videos)})</div>', unsafe_allow_html=True)
                            for v in videos:
                                rel = v.get('relevance_score', 0.5)
                                badge = "relevance-high" if rel >= 0.85 else "relevance-medium"
                                badge_text = "HIGH" if rel >= 0.85 else "GOOD"
                                
                                # Format view count
                                views = v.get('view_count', 0)
                                if isinstance(views, int):
                                    if views >= 1000000:
                                        views_str = f"{views/1000000:.1f}M"
                                    elif views >= 1000:
                                        views_str = f"{views/1000:.1f}K"
                                    else:
                                        views_str = str(views)
                                else:
                                    views_str = str(views)
                                
                                # Format duration
                                dur = v.get('duration')
                                if dur and isinstance(dur, int):
                                    m, s = divmod(dur, 60)
                                    h, m = divmod(m, 60)
                                    dur_str = f"{h}:{m:02d}:{s:02d}" if h > 0 else f"{m}:{s:02d}"
                                else:
                                    dur_str = str(dur) if dur else "N/A"
                                
                                st.markdown(f"""
                                <div class="video-card">
                                    {f'<img src="{v.get("thumbnail")}" class="video-thumbnail">' if v.get('thumbnail') else ''}
                                    <div class="video-content">
                                        <div class="video-title-card">{v.get('title', 'Untitled')}</div>
                                        <div class="video-meta">📺 {v.get('channel_name', 'Unknown')} • ⏱️ {dur_str} • 👁️ {views_str}</div>
                                        <span class="relevance-badge {badge}">✓ {badge_text} ({rel * 100:.0f}%)</span>
                                        <br><br>
                                        <a href="{v.get('url', '#')}" target="_blank" class="video-link">▶️ Watch on YouTube</a>
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
                        else:
                            st.info("⚠️ No sources found for this counter-perspective.")
                        
                        st.markdown("</div><br>", unsafe_allow_html=True)
                else:
                    st.warning("No counter-arguments generated.")
                
                # Export
                st.markdown("---")
                st.download_button(
                    "📄 Download JSON Report",
                    json.dumps(data, indent=2),
                    f"echobreaker_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    "application/json"
                )
            else:
                st.error(f"❌ Error: {response.status_code}")
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #64748b; padding: 2rem;">
    <p><strong>EchoBreaker</strong> | Breaking Algorithmic Echo Chambers</p>
    <p style="font-size: 0.85rem;">We show you what else to think about.</p>
</div>
""", unsafe_allow_html=True)