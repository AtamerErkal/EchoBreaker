import json
import urllib.parse
from core.config import Config
from models.analysis_result import AnalysisResult

LANG_INSTRUCTION = {
    "en": "",
    "de": "\n\nIMPORTANT: Write ALL text fields (topic, primary_claim, echo_chamber_description, title, key_point, why_it_matters, academic_ref, youtube_query, echo_chamber_query) entirely in GERMAN (Deutsch). Do NOT use English in any field.",
    "tr": "\n\nÖNEMLİ: Tüm metin alanlarını (topic, primary_claim, echo_chamber_description, title, key_point, why_it_matters, academic_ref, youtube_query, echo_chamber_query) tamamen TÜRKÇE yaz. Hiçbir alanda İngilizce kullanma.",
}

SYSTEM_PROMPT = """You are EchoBreaker, an AI that breaks algorithmic echo chambers.
Analyze the transcript and generate sharp, concise counter-perspectives.

Return ONLY this JSON structure:
{
  "topic": "3-5 words",
  "primary_claim": "1-2 sentences, the video's core argument",
  "confidence_score": 0.0-1.0,
  "echo_chamber_query": "3-5 word YouTube search that would find MORE videos reinforcing this exact viewpoint",
  "echo_chamber_description": "1 sentence: what the algorithm would keep feeding you if you only watched videos like this",
  "counter_arguments": [
    {
      "type": "Ethical",
      "title": "Punchy title, MAX 10 words",
      "key_point": "Exactly 2 sentences. Clear, direct opposition.",
      "why_it_matters": "1 sentence. Real-world consequence or implication.",
      "academic_ref": "Author, Work Title (Year)",
      "youtube_query": "3-5 word search query for counter-videos"
    }
  ]
}

RULES:
- Exactly 3 counter-arguments: one Ethical, one Empirical, one Logical.
- title: provocative, under 10 words. Think newspaper headline.
- key_point: EXACTLY 2 sentences. No more.
- why_it_matters: EXACTLY 1 sentence. Make it hit hard.
- academic_ref: a real, well-known work relevant to the counter-perspective.
- echo_chamber_query: terms that would REINFORCE the video's bias (what the algorithm recommends).
- echo_chamber_description: describe the filter bubble this creates.
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
            print(f"Azure OpenAI error: {e}")
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
        except Exception:
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
            print(f"Groq error: {e}")
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
        except Exception:
            return {"score": 0.7, "verdict": "accept", "reason": "Default acceptance"}


def create_reasoning_engine():
    if Config.PROVIDER == "azure" and Config.AZURE_OPENAI_API_KEY:
        print("  Using Azure OpenAI for reasoning")
        return AzureReasoningEngine()
    elif Config.PROVIDER == "groq" and Config.GROQ_API_KEY:
        print("  Using Groq (free tier) for reasoning")
        return GroqReasoningEngine()
    else:
        raise RuntimeError(
            f"No valid provider configured. "
            f"Set PROVIDER=azure with AZURE_OPENAI_API_KEY, "
            f"or PROVIDER=groq with GROQ_API_KEY in your .env file."
        )
