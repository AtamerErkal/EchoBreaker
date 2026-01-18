# 🛡️ EchoBreaker

### Breaking Algorithmic Echo Chambers Through Intellectual Diversity

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-red.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **"The algorithm shows you what you want to see. We show you what you need to consider."**

---

## 🎯 The Problem

Modern content platforms like YouTube, Twitter, and TikTok use recommendation algorithms optimized for engagement. While this improves user experience, it creates an unintended consequence: **algorithmic echo chambers**.

### How Echo Chambers Form

1. **You watch** a video expressing viewpoint A
2. **The algorithm learns** you're interested in topic X
3. **You get recommended** 10 more videos supporting viewpoint A
4. **Your beliefs strengthen** - not because you evaluated alternatives, but because you never saw them
5. **Society polarizes** - we live in parallel information universes

This isn't YouTube's fault. It's an inherent challenge in engagement-optimized systems.

### The Impact

- **Individual Level**: Reduced critical thinking, confirmation bias reinforcement
- **Social Level**: Political polarization, decreased empathy for opposing views
- **Democratic Level**: Citizens making decisions based on incomplete information

**EchoBreaker addresses this by surfacing the strongest counter-perspectives you're not algorithmically seeing.**

---

## 💡 Our Solution

EchoBreaker is **not** a criticism of YouTube. It's a complementary tool that helps users:

✅ **Discover** perspectives the algorithm doesn't show  
✅ **Understand** the strongest counter-arguments to any viewpoint  
✅ **Think critically** by seeing multiple sides before forming opinions  
✅ **Reduce polarization** through exposure to intellectual diversity

### Core Philosophy

**We don't tell you what to think. We show you what else to think about.**

- If you watch a pro-climate-action video → We find the best economic cost-benefit analyses
- If you watch a free-market economics video → We find the strongest social welfare arguments
- If you watch a privacy-focused tech video → We find authoritative security trade-off discussions

**The goal: Make you less certain, more curious, and better informed.**

---

## ✨ How It Works

### 1. Analysis Pipeline

```
YouTube URL → Audio Extraction → Whisper Transcription → 
Llama 3 Analysis → Counter-Perspective Generation → 
Source Discovery → Quality Verification
```

### 2. Three-Dimensional Opposition

For every analyzed video, we generate counter-arguments across:

**🔹 Ethical Dimension**  
Moral frameworks and value trade-offs opposing the video's stance  
*Example: Individual liberty vs. collective security perspectives*

**🔹 Empirical Dimension**  
Data, research, and evidence contradicting the video's claims  
*Example: Studies showing different statistical correlations*

**🔹 Logical Dimension**  
Reasoning flaws, alternative causal models, or structural critiques  
*Example: Correlation vs. causation fallacies in arguments*

### 3. Quality Assurance

**Semantic Contrast Enforcement**  
Counter-arguments must score **0.7-1.0** on opposition scale. We reject:
- ❌ Tangentially related content
- ❌ Strawman arguments
- ❌ Weak opposing views

**Dual-Pass Verification**  
Every suggested video goes through:
1. **Academic-style search** → Queries target news, research, documentaries
2. **Relevance verification** → AI scores each video 0.0-1.0 on relevance
3. **Quality filtering** → Clickbait rejection, authority scoring

**Only sources scoring ≥0.7 are shown.**

### 4. Privacy-First Design

**Everything runs locally:**
- No data sent to external APIs
- No user tracking or analytics
- Complete control over your information

**Technologies:**
- Whisper AI (local transcription)
- Llama 3 via Ollama (local analysis)
- yt-dlp (direct YouTube metadata access)

---

## 🚀 Installation & Usage

### Prerequisites

```bash
# 1. Install Ollama
# Download from https://ollama.com/
ollama pull llama3:8b

# 2. Install FFmpeg
# macOS: brew install ffmpeg
# Ubuntu: sudo apt-get install ffmpeg
# Windows: Download from https://ffmpeg.org/

# 3. Python 3.8+
python --version
```

### Setup

```bash
# Clone repository
git clone https://github.com/AtamerErkal/EchoBreaker.git
cd EchoBreaker

# Install dependencies
pip install -r requirements.txt

# Optional: Configure environment
cp .env.template .env
```

### Run the Dashboard

```bash
# Start Streamlit interface
streamlit run frontend/app.py

# Open browser to http://localhost:8501
```

### Example Analysis

**Input:** `https://www.youtube.com/watch?v=example`

**Output:**
- **Topic Summary**: AI-generated overview of video's thesis
- **Extracted Claims**: Key arguments and assertions
- **Counter-Arguments** (3 types):
  - Ethical: Alternative moral frameworks
  - Empirical: Contradicting research/data
  - Logical: Reasoning critiques
- **Verified Sources**: High-quality videos presenting opposing views
- **Academic Context**: Scholarly perspective for each counter-argument

**Processing Time:** 50-90 seconds for a 10-minute video

---

## 🏗️ Architecture

### System Design

```
EchoBreaker/
├── frontend/app.py              # Streamlit dashboard
├── api/main.py                  # FastAPI orchestration
├── services/
│   ├── audio/transcription.py  # Whisper integration
│   ├── reasoning/generator.py  # Llama 3 analysis
│   ├── search/youtube_search.py # Source discovery
│   └── youtube/downloader.py   # Audio extraction
├── models/analysis_result.py   # Data schemas
└── core/config.py              # Configuration
```

### Processing Flow

```
1. Audio Download (yt-dlp)         → 5-15 seconds
2. Whisper Transcription           → 10-30 seconds (GPU)
3. Llama 3 Analysis                → 15-30 seconds
   ├─ Claim extraction
   ├─ Sentiment analysis
   ├─ Counter-argument generation
   └─ Academic context creation
4. YouTube Source Search           → 5-10 seconds
5. Dual-Pass Verification          → 10-20 seconds
6. Dashboard Rendering             → <1 second

Total: 50-90 seconds
```

---

## ⚖️ Responsible AI Principles

### 1. Transparency

We are **not** a black box:
- ✅ 100% open-source code
- ✅ Opposition scores visible (0.0-1.0 scale)
- ✅ Verification reasons logged
- ✅ No hidden algorithmic decisions

### 2. Privacy Protection

Your data stays yours:
- ✅ All processing local (Whisper + Llama 3)
- ✅ No external API calls
- ✅ No user tracking
- ✅ Temporary files auto-deleted

### 3. Intellectual Fairness

We enforce genuine opposition:
- ✅ Semantic contrast scoring (reject weak counters)
- ✅ Three-dimensional analysis (Ethical, Empirical, Logical)
- ✅ Academic grounding (scholarly context for each argument)
- ✅ Quality filters (no clickbait, prioritize research/news)

### 4. Platform Respect

We **complement**, not compete with YouTube:
- ✅ Use public APIs (yt-dlp for metadata)
- ✅ No scraping user data
- ✅ No circumventing paywalls
- ✅ Respect rate limits and Terms of Service

### 5. Human Agency

AI assists, humans decide:
- ✅ We present perspectives, not prescriptions
- ✅ Confidence scores show AI certainty
- ✅ Users evaluate and form their own opinions
- ✅ Export functionality for further research

---

## 🎓 Use Cases

### For Individuals
**Problem:** Algorithm shows only one side of complex issues  
**Solution:** See strongest counter-arguments before forming opinions

### For Educators
**Problem:** Students live in ideological bubbles  
**Solution:** Teach critical thinking through multi-perspective analysis

### For Researchers
**Problem:** Media bias is hard to quantify  
**Solution:** Measure semantic opposition and track polarization

### For Journalists
**Problem:** Balanced coverage requires finding diverse sources  
**Solution:** Discover authoritative counter-perspectives efficiently

### For Content Creators
**Problem:** Unaware of blind spots in arguments  
**Solution:** Self-assess and strengthen narratives with counter-awareness

---

## 🔧 Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Frontend** | Streamlit | Clean, professional dashboard |
| **API** | FastAPI | Async orchestration layer |
| **Speech Recognition** | Whisper (tiny) | Local audio transcription |
| **Language Model** | Llama 3 (8B) | Semantic analysis & verification |
| **LLM Runtime** | Ollama | Local inference engine |
| **Video Processing** | yt-dlp + FFmpeg | Metadata & audio extraction |
| **Data Validation** | Pydantic V2 | Type safety & schemas |
| **Async Processing** | asyncio | Parallel search operations |

### Performance Characteristics

- **Latency**: 50-90s for 10-min video
- **Memory**: ~8GB RAM (Llama 3) + 2GB VRAM (Whisper tiny)
- **GPU Acceleration**: 3x speedup for Whisper transcription
- **Concurrent Users**: Single-user local deployment (scalable with queuing)

---

## 🛣️ Roadmap

### V2.1 (Current)
- [x] Semantic contrast enforcement
- [x] Dual-pass verification
- [x] Academic insight generation
- [x] Streamlit dashboard

### V2.2 (In Development)
- [ ] Multi-language support (Whisper multilingual)
- [ ] Batch processing (analyze playlists)
- [ ] Browser extension (analyze while watching)
- [ ] PDF export (professional reports)

### V3.0 (Planned)
- [ ] Custom LLM integration (Mistral, GPT4All)
- [ ] Historical tracking (see how perspectives evolved)
- [ ] Collaborative filtering (crowdsourced quality ratings)
- [ ] Mobile app (iOS/Android)

---

## 🤝 Contributing

We welcome contributions that advance our mission of reducing polarization through technology.

### Priority Areas

1. **Prompt Engineering**: Improve counter-argument quality
2. **Performance**: Optimize Whisper/Llama 3 inference
3. **UI/UX**: Enhance dashboard clarity
4. **Testing**: Add unit tests for services

### Development Setup

```bash
# Fork and clone
git clone https://github.com/YOUR_USERNAME/EchoBreaker.git
cd EchoBreaker

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dev dependencies
pip install -r requirements.txt
pip install pytest black flake8

# Make changes and submit PR
```

---

## ❓ FAQ

**Q: Is this anti-YouTube?**  
A: No. We're grateful YouTube exists. We're addressing an inherent challenge in all engagement-optimized platforms.

**Q: How do you ensure counter-arguments are high quality?**  
A: Dual-pass verification: academic-style searches + AI relevance scoring (≥0.7 threshold).

**Q: What if I disagree with a counter-argument?**  
A: Perfect! The goal is exposure, not persuasion. Evaluate it yourself.

**Q: Can this be used to spread misinformation?**  
A: We prioritize authoritative sources (news, research, documentaries) and reject clickbait. But users should always verify.

**Q: How long does analysis take?**  
A: 50-90 seconds for a 10-minute video (varies by GPU/CPU).

**Q: Can I use a different LLM?**  
A: Yes! Edit `services/reasoning/generator.py` to integrate other Ollama models.

---

## 📄 License

MIT License - See [LICENSE](LICENSE) for details.

You can use, modify, and distribute this freely, including commercially, as long as you include the original copyright notice.

---

## ⚠️ Disclaimer

**EchoBreaker is a research tool for promoting critical thinking.**

We do **not**:
- ❌ Claim to provide absolute truth
- ❌ Replace professional fact-checking
- ❌ Guarantee unbiased analysis
- ❌ Endorse any viewpoint

**Users should:**
- ✅ Verify information from multiple sources
- ✅ Form their own informed opinions
- ✅ Understand AI limitations
- ✅ Use this as one tool among many

**Ethical Use:**  
This tool is for educational, research, and journalistic purposes. Do not use it to generate misleading content, harass individuals, or violate platform Terms of Service.

---

## 🙏 Acknowledgments

- **YouTube** - For creating a platform enabling global knowledge sharing
- **OpenAI** - Whisper model for speech recognition
- **Meta AI** - Llama 3 for language understanding
- **Ollama Team** - Making local LLMs accessible
- **yt-dlp developers** - Robust YouTube integration
- **The open-source community** - For democratizing AI

---

## 📞 Contact

- **Author**: Atamer Erkal
- **GitHub**: [@AtamerErkal](https://github.com/AtamerErkal)
- **Issues**: [Report bugs or request features](https://github.com/AtamerErkal/EchoBreaker/issues)

---

<div align="center">

## 🎯 Our Mission

**Break echo chambers. Reduce polarization. Enable informed citizenship.**

One video at a time.

---

[![Star this repo](https://img.shields.io/github/stars/AtamerErkal/EchoBreaker?style=social)](https://github.com/AtamerErkal/EchoBreaker)

[⭐ Star](https://github.com/AtamerErkal/EchoBreaker) • [🐛 Report Bug](https://github.com/AtamerErkal/EchoBreaker/issues) • [💡 Request Feature](https://github.com/AtamerErkal/EchoBreaker/issues)

---

*"The test of a first-rate intelligence is the ability to hold two opposed ideas in mind at the same time and still retain the ability to function."* — F. Scott Fitzgerald

</div>
