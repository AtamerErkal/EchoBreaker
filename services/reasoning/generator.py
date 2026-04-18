import json
import logging
import urllib.parse
from core.config import Config
from models.analysis_result import AnalysisResult

logger = logging.getLogger(__name__)

LANG_INSTRUCTION = {
    "en": "",
    "de": "\n\nIMPORTANT: Write ALL text fields (topic, primary_claim, echo_chamber_description, title, key_point, why_it_matters, common_ground, closing_question, action_prompt, academic_ref, youtube_query, echo_chamber_query) entirely in GERMAN (Deutsch). Do NOT use English in any field.",
    "tr": "\n\nÖNEMLİ: Tüm metin alanlarını (topic, primary_claim, echo_chamber_description, title, key_point, why_it_matters, common_ground, closing_question, action_prompt, academic_ref, youtube_query, echo_chamber_query) tamamen TÜRKÇE yaz. Hiçbir alanda İngilizce kullanma.",
}

SYSTEM_PROMPT = """You are EchoBreaker, an AI that breaks algorithmic echo chambers.
Analyze the transcript. Your goal: help the viewer realize other perspectives exist, WITHOUT dismissing their current view.

TONE RULE: For every counter-argument, follow this exact 3-part structure:
1. First, VALIDATE: acknowledge what is true or understandable in the video's view.
2. Then, EXPAND: "I think we should also consider..." or "Another way to see this..."
3. End with a QUESTION or a REAL EXAMPLE — never a conclusion.

Return ONLY this JSON:
{
  "topic": "3-5 words",
  "primary_claim": "1 sentence stating what the video claims, naturally (not 'The transcript argues that...' - just state the claim directly)",
  "confidence_score": 0.0-1.0,
  "echo_chamber_query": "3-5 word YouTube search reinforcing this view",
  "echo_chamber_description": "1 sentence: what the algorithm keeps feeding you",
  "counter_arguments": [
    {
      "type": "Ethical | Empirical | Logical",
      "title": "emoji + max 8 words, sentence case",
      "key_point": "Max 40 words total. Use at least 2 emojis. CRITICAL: Each sentence MUST be on its own line with EXACTLY double line breaks (\\n\\n) between sentences. Example format: 'Sentence 1.\\n\\nSentence 2.\\n\\nSentence 3.' Sentence 1: validate. Sentence 2: expand. Sentence 3: concrete example.",
      "why_it_matters": "1-2 sentences: who this matters to in real life",
      "common_ground": "1 sentence starting with 'Both views agree that...'",
      "closing_question": "1 soft, open-ended question like 'I wonder if we could also explore...' or 'What if we included this in our thinking...'",
      "action_prompt": "1 concrete action: Search for... / Ask yourself... / Listen to...",
      "academic_ref": "Author, Work (Year >= 2010)",
      "youtube_query": "3-5 word counter-video search",
      "sentiment": "positive (expands view) | negative (flags serious issue) | neutral (adds context) | critical (contradicts with evidence)"
    }
  ]
}

RULES:
- Exactly 3 counter_arguments: Ethical, Empirical, Logical.
- Each perspective must stay in character: Ethical talks about values, Empirical talks about data, Logical talks about reasoning. Do NOT reference other perspectives (e.g., don't say "As the ethical angle suggests...").
- CRITICAL: key_point MUST use EXACT double line breaks (\\n\\n) between sentences. Example: "Sentence 1.\\n\\nSentence 2.\\n\\nSentence 3."
- Never say the video is "wrong" — say it is "incomplete" or "one angle of a larger picture".
- academic_ref: real, well-known work, 2010 or later.
- key_point: Use at least 2 emojis. Max 40 words total.
- closing_question: Make it soft and collaborative, not challenging. Use phrases like "I wonder if we could also explore...", "What if we included this in our thinking...", "Maybe we should consider..."
- Return ONLY raw JSON. No markdown, no preamble."""


def _extract_json(content: str) -> str:
    try:
        start = content.find('{')
        end = content.rfind('}')
        if start != -1 and end != -1:
            return content[start: end + 1]
        return content
    except Exception:
        return content


def _postprocess(data: dict) -> AnalysisResult:
    if not data.get("topic") or data.get("topic") == "Analysis pending":
        data["topic"] = "General Topic Analysis"
    if not data.get("primary_claim"):
        data["primary_claim"] = "The video presents an argument regarding the topic above."

    for ca in data.get("counter_arguments", []):
        if "content" in ca and "key_point" not in ca:
            ca["key_point"] = ca.pop("content")
        if not ca.get("youtube_query"):
            ca["youtube_query"] = f"{ca.get('title', 'opposing view')} debate"

        yt_q = urllib.parse.quote(ca.get("youtube_query", ""))
        ca["youtube_search_url"] = f"https://www.youtube.com/results?search_query={yt_q}"

        scholar_q = urllib.parse.quote(ca.get("academic_ref", ca.get("title", "")))
        ca["scholar_search_url"] = f"https://scholar.google.com/scholar?q={scholar_q}"

    return AnalysisResult(**data)


def _fallback_result() -> AnalysisResult:
    return AnalysisResult(
        topic="Error in Analysis",
        primary_claim="The system encountered an error while processing.",
        counter_arguments=[],
        confidence_score=0.0,
    )


class AzureReasoningEngine:
    def __init__(self):
        from openai import AzureOpenAI
        self.client = AzureOpenAI(
            api_key=Config.AZURE_OPENAI_API_KEY,
            api_version=Config.AZURE_OPENAI_API_VERSION,
            azure_endpoint=Config.AZURE_OPENAI_ENDPOINT,
        )
        self.deployment = Config.AZURE_OPENAI_DEPLOYMENT

    def generate_analysis(self, transcript: str, video_url: str, language: str = "en") -> AnalysisResult:
        try:
            system = SYSTEM_PROMPT + LANG_INSTRUCTION.get(language, "")
            response = self.client.chat.completions.create(
                model=self.deployment,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": f"Transcript:\n{transcript[:20000]}"},
                ],
                response_format={"type": "json_object"},
                temperature=0.7,
                max_completion_tokens=2000,
            )
            data = json.loads(_extract_json(response.choices[0].message.content))
            return _postprocess(data)
        except Exception as e:
            logger.error("Azure OpenAI error: %s", e, exc_info=True)
            return _fallback_result()

    def verify_relevance(self, counter_argument_content: str, video_title: str, video_description: str = "") -> dict:
        prompt = f"""Check if this video is a valid COUNTER-PERSPECTIVE.
Argument: {counter_argument_content}
Video: {video_title} - {video_description[:200]}
Return JSON: {{"score": 0.0-1.0, "verdict": "accept"/"reject", "reason": "1 sentence"}}"""
        try:
            response = self.client.chat.completions.create(
                model=self.deployment,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                temperature=0.3,
                max_completion_tokens=150,
            )
            return json.loads(_extract_json(response.choices[0].message.content))
        except Exception as e:
            logger.warning("Azure verify_relevance failed: %s", e)
            return {"score": 0.7, "verdict": "accept", "reason": "Default acceptance"}


class GroqReasoningEngine:
    def __init__(self):
        from groq import Groq
        self.client = Groq(api_key=Config.GROQ_API_KEY)
        self.model = Config.GROQ_MODEL

    def generate_analysis(self, transcript: str, video_url: str, language: str = "en") -> AnalysisResult:
        try:
            system = SYSTEM_PROMPT + LANG_INSTRUCTION.get(language, "")
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": f"Transcript:\n{transcript[:20000]}"},
                ],
                response_format={"type": "json_object"},
                temperature=0.7,
                max_tokens=2000,
            )
            data = json.loads(_extract_json(response.choices[0].message.content))
            return _postprocess(data)
        except Exception as e:
            logger.error("Groq error: %s", e, exc_info=True)
            return _fallback_result()

    def verify_relevance(self, counter_argument_content: str, video_title: str, video_description: str = "") -> dict:
        prompt = f"""Check if this video is a valid COUNTER-PERSPECTIVE.
Argument: {counter_argument_content}
Video: {video_title} - {video_description[:200]}
Return JSON: {{"score": 0.0-1.0, "verdict": "accept"/"reject", "reason": "1 sentence"}}"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                temperature=0.3,
                max_tokens=150,
            )
            return json.loads(_extract_json(response.choices[0].message.content))
        except Exception as e:
            logger.warning("Groq verify_relevance failed: %s", e)
            return {"score": 0.7, "verdict": "accept", "reason": "Default acceptance"}


def create_reasoning_engine():
    if Config.PROVIDER == "azure" and Config.AZURE_OPENAI_API_KEY:
        logger.info("Using Azure OpenAI for reasoning")
        return AzureReasoningEngine()
    elif Config.PROVIDER == "groq" and Config.GROQ_API_KEY:
        logger.info("Using Groq (free tier) for reasoning")
        return GroqReasoningEngine()
    else:
        raise RuntimeError(
            f"No valid provider configured. "
            f"Set PROVIDER=azure with AZURE_OPENAI_API_KEY, "
            f"or PROVIDER=groq with GROQ_API_KEY in your .env file."
        )
