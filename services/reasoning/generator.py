import os
import json
import urllib.parse
from typing import Any
from core.config import Config
from models.analysis_result import AnalysisResult, CounterArgument

SYSTEM_PROMPT = """
You are EchoBreaker, an AI specialized in breaking algorithmic echo chambers.
Analyze the transcript and provide high-quality, intellectually diverse counter-perspectives.

**MANDATORY JSON STRUCTURE**:
{
  "topic": "3-5 words summarizing the core subject",
  "primary_claim": "2-3 sentences summarizing the video's main argument",
  "confidence_score": 0.0 to 1.0,
  "counter_arguments": [
    {
      "type": "Ethical",
      "title": "Clear title of the opposing view",
      "content": "2-3 sentences explaining why this perspective contradicts the video",
      "youtube_query": "Search terms for finding opposing documentaries/debates",
      "academic_search_query": "Specific terminology for Google Scholar",
      "academic_insight": "150-word sophisticated academic analysis with theoretical references"
    }
  ]
}
CRITICAL REQUIREMENT: You MUST provide exactly THREE counter-arguments.
One of each type: 'Ethical', 'Empirical', and 'Logical'.

For each counter-argument, generate a 'youtube_query' that is broad enough
to find results (e.g., 'critique of [topic]' or '[topic] alternative view').

**RULES**:
1. TOPIC and PRIMARY_CLAIM are mandatory. Do not leave them empty.
2. COUNTER-ARGUMENTS must be diametrically opposed to the video's thesis.
3. ACADEMIC_INSIGHT must be a cohesive paragraph (no bullets) and cite a theoretical framework (e.g., Ref: Rawls' Theory of Justice).
4. Return ONLY the raw JSON object. No markdown, no preamble.
"""

VERIFICATION_PROMPT = """
Check if this video is a valid COUNTER-PERSPECTIVE for the argument below.

Target Argument: {argument_content}
Video Title: {video_title}
Video Description: {video_desc}

Return JSON:
{{
  "score": 0.0 to 1.0,
  "verdict": "accept" or "reject",
  "reason": "1 sentence explanation"
}}
"""


def _extract_json(content: str) -> str:
    try:
        start = content.find('{')
        end = content.rfind('}')
        if start != -1 and end != -1:
            return content[start : end + 1]
        return content
    except Exception:
        return content


def _postprocess(data: dict) -> AnalysisResult:
    if not data.get("topic") or data.get("topic") == "Analysis pending":
        data["topic"] = "General Topic Analysis"
    if not data.get("primary_claim"):
        data["primary_claim"] = "The video presents an argument regarding the topic mentioned above."

    for ca in data.get("counter_arguments", []):
        if not ca.get("youtube_query"):
            ca["youtube_query"] = f"{ca.get('title', 'Opposing view')} debate"
        if not ca.get("academic_search_query"):
            ca["academic_search_query"] = ca.get("title", "academic research")
        safe_query = urllib.parse.quote(ca.get("academic_search_query", ""))
        ca["source_reference"] = f"https://scholar.google.com/scholar?q={safe_query}"

    return AnalysisResult(**data)


def _fallback_result() -> AnalysisResult:
    return AnalysisResult(
        topic="Error in Analysis",
        primary_claim="The system encountered an error while processing the transcript.",
        counter_arguments=[],
        confidence_score=0.0
    )


class AzureReasoningEngine:
    """Uses Azure OpenAI (GPT 5.4 Mini) for fast cloud-based analysis."""

    def __init__(self):
        from openai import AzureOpenAI
        self.client = AzureOpenAI(
            api_key=Config.AZURE_OPENAI_API_KEY,
            api_version=Config.AZURE_OPENAI_API_VERSION,
            azure_endpoint=Config.AZURE_OPENAI_ENDPOINT,
        )
        self.deployment = Config.AZURE_OPENAI_DEPLOYMENT

    def generate_analysis(self, transcript: str, video_url: str) -> AnalysisResult:
        user_prompt = f"Transcript:\n{transcript[:20000]}\n\nVideo URL: {video_url}\n\nGenerate the analysis following the mandatory JSON structure."
        try:
            response = self.client.chat.completions.create(
                model=self.deployment,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                response_format={"type": "json_object"},
                temperature=0.7,
                max_tokens=4000,
            )
            content = response.choices[0].message.content
            data = json.loads(_extract_json(content))
            return _postprocess(data)
        except Exception as e:
            print(f"Azure OpenAI error: {e}")
            return _fallback_result()

    def verify_relevance(self, counter_argument_content: str, video_title: str, video_description: str = "") -> dict:
        prompt = VERIFICATION_PROMPT.format(
            argument_content=counter_argument_content,
            video_title=video_title,
            video_desc=video_description[:300],
        )
        try:
            response = self.client.chat.completions.create(
                model=self.deployment,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                temperature=0.3,
                max_tokens=200,
            )
            return json.loads(_extract_json(response.choices[0].message.content))
        except Exception:
            return {"score": 0.7, "verdict": "accept", "reason": "Default acceptance"}


class OllamaReasoningEngine:
    """Uses local Ollama for fully private, offline analysis."""

    def __init__(self):
        import ollama
        self.ollama = ollama
        self.model = Config.OLLAMA_MODEL

    def generate_analysis(self, transcript: str, video_url: str) -> AnalysisResult:
        user_prompt = f"Transcript:\n{transcript[:20000]}\n\nVideo URL: {video_url}\n\nGenerate the analysis following the mandatory JSON structure."
        try:
            response = self.ollama.chat(model=self.model, messages=[
                {'role': 'system', 'content': SYSTEM_PROMPT},
                {'role': 'user', 'content': user_prompt},
            ], format='json')
            content = response['message']['content']
            data = json.loads(_extract_json(content))
            return _postprocess(data)
        except Exception as e:
            print(f"Ollama error: {e}")
            return _fallback_result()

    def verify_relevance(self, counter_argument_content: str, video_title: str, video_description: str = "") -> dict:
        prompt = VERIFICATION_PROMPT.format(
            argument_content=counter_argument_content,
            video_title=video_title,
            video_desc=video_description[:300],
        )
        try:
            response = self.ollama.chat(model=self.model, messages=[
                {'role': 'user', 'content': prompt}
            ], format='json')
            return json.loads(_extract_json(response['message']['content']))
        except Exception:
            return {"score": 0.7, "verdict": "accept", "reason": "Default acceptance"}


def create_reasoning_engine():
    if Config.PROVIDER == "azure" and Config.AZURE_OPENAI_API_KEY:
        print("  Using Azure OpenAI for reasoning")
        return AzureReasoningEngine()
    else:
        print("  Using Ollama (local) for reasoning")
        return OllamaReasoningEngine()
