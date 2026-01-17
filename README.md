# EchoBreaker (Local-First Edition)

**Enterprise-Grade AI for Algorithmic Objection**

EchoBreaker is a modular, local-first validation engine designed to combat algorithmic bias on video platforms. It operates entirely on your infrastructure using efficient open-source models, eliminating cloud costs while maintaining enterprise-grade architectural standards.

## 🚀 Features

-   **Data Pipeline**: Extracts audio from YouTube using `yt-dlp`.
-   **Local Transcription**: Uses **OpenAI Whisper** (base model) for accurate, private, and cost-free speech-to-text.
-   **Local Intelligence**: Powered by **Llama 3 (via Ollama)** for single-pass semantic analysis, opinion mining, and counter-argument generation.
-   **Production-Ready API**: Built with **FastAPI**, fully typed, and ready for deployment.

## 🏗 Architecture

The system follows a clean, hexagonal-inspired architecture:

```
EchoBreaker/
├── core/           # Configuration & Shared Utilities
├── services/       # Local AI Integrations (Whisper, Ollama)
├── models/         # Pydantic Data definitions
└── api/            # REST API Orchestrator
```

## 🛠 Technology Stack

-   **Infrastructure**: Local / On-Premise
-   **Speech Model**: OpenAI Whisper (`base`)
-   **LLM**: Meta Llama 3 8B (via Ollama)
-   **Framework**: FastAPI
-   **Tools**: yt-dlp, FFmpeg

## 📦 User Guide

1.  **Prerequisites**
    -   Install [Ollama](https://ollama.com/) and run `ollama run llama3:8b`.
    -   Install `ffmpeg`.

2.  **Environment Setup**
    ```bash
    pip install -r requirements.txt
    ```
    Create `.env` (optional, defaults provided in `core/config.py`).

3.  **Run the API**
    ```bash
    uvicorn api.main:app --reload
    ```

4.  **Analyze a Video**
    Send a POST request to `/analyze`:
    ```json
    {
        "video_url": "https://youtube.com/watch?v=..."
    }
    ```

## ⚖️ Responsible AI

EchoBreaker promotes transparency and objectivity by running entirely on local infrastructure, ensuring data privacy and auditable AI responses.
