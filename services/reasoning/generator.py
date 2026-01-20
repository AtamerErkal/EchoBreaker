import os
import json
import ollama
import urllib.parse
from typing import List, Dict, Any
from core.config import Config
from models.analysis_result import AnalysisResult, CounterArgument
from pydantic import ValidationError

# #region agent log
LOG_PATH = r"e:\3. projects\EchoBreaker\.cursor\debug.log"

def _log(session_id, run_id, hypothesis_id, location, message, data):
    try:
        import time
        log_entry = {
            "sessionId": session_id, 
            "runId": run_id, 
            "hypothesisId": hypothesis_id, 
            "location": location, 
            "message": message, 
            "data": data, 
            "timestamp": int(time.time() * 1000)
        }
        if os.path.exists(os.path.dirname(LOG_PATH)):
            with open(LOG_PATH, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry) + "\n")
                f.flush()
                os.fsync(f.fileno())
        
        print(f"[DEBUG LOG] {location}: {message}")
    except Exception as ex:
        print(f"[DEBUG LOG ERROR] Failed to write log: {ex}")
# #endregion

class ReasoningEngine:
    def __init__(self):
        self.model = Config.OLLAMA_MODEL

    def _extract_json(self, content: str) -> str:
        """Extracts JSON object from potential LLM conversational filler."""
        try:
            start = content.find('{')
            end = content.rfind('}')
            if start != -1 and end != -1:
                return content[start : end + 1]
            return content
        except Exception:
            return content

    def generate_analysis(self, transcript: str, video_url: str) -> AnalysisResult:
        """
        Analyzes transcripts to generate diametrically opposed counter-arguments.
        Synchronized with AnalysisResult Pydantic model.
        """
        
        system_prompt = """
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

        user_prompt = f"""
Transcript:
{transcript[:20000]} 

Video URL: {video_url}

Generate the analysis following the mandatory JSON structure. Ensure the 'topic' and 'primary_claim' are accurately extracted from the content provided.
"""

        try:
            _log("analysis", "gen", "1", "generator.py", "Requesting LLM analysis", {"model": self.model})
            
            response = ollama.chat(model=self.model, messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_prompt},
            ], format='json')

            content = response['message']['content']
            json_str = self._extract_json(content)
            data = json.loads(json_str)
            
            # --- Field Synchronization & Fallbacks ---
            # Ensure 'topic' is present (prevents "Analysis pending" in UI)
            if not data.get("topic") or data.get("topic") == "Analysis pending":
                data["topic"] = "General Topic Analysis"
            
            # Ensure 'primary_claim' is present
            if not data.get("primary_claim"):
                data["primary_claim"] = "The video presents an argument regarding the topic mentioned above."

            # Process Counter-Arguments
            if "counter_arguments" in data:
                for idx, ca in enumerate(data["counter_arguments"]):
                    # Ensure queries exist for the Search Service
                    if not ca.get("youtube_query"):
                        ca["youtube_query"] = f"{ca.get('title', 'Opposing view')} debate"
                    
                    if not ca.get("academic_search_query"):
                        ca["academic_search_query"] = ca.get("title", "academic research")

                    # Generate Google Scholar link for the UI
                    query_term = ca.get("academic_search_query")
                    safe_query = urllib.parse.quote(query_term)
                    ca["source_reference"] = f"https://scholar.google.com/scholar?q={safe_query}"

            # Validate against Pydantic Model
            result = AnalysisResult(**data)
            return result

        except Exception as e:
            _log("analysis", "gen", "error", "generator.py", "Critical LLM Error", {"error": str(e)})
            # Ultimate Fallback to prevent UI crash
            return AnalysisResult(
                topic="Error in Analysis",
                primary_claim="The system encountered an error while processing the transcript.",
                counter_arguments=[],
                confidence_score=0.0
            )

    def verify_relevance(self, video_data: Any, argument_content: str) -> dict:
        """
        Verifies if a found YouTube video is truly relevant to the counter-argument.
        """
        # Note: video_data is usually a VideoSuggestion object
        video_title = getattr(video_data, 'title', 'Unknown')
        video_desc = getattr(video_data, 'description', '')

        verification_prompt = f"""
Check if this video is a valid COUNTER-PERSPECTIVE for the argument below.

Target Argument: {argument_content}
Video Title: {video_title}
Video Description: {video_desc[:300]}

Return JSON:
{{
  "score": 0.0 to 1.0,
  "verdict": "accept" or "reject",
  "reason": "1 sentence explanation"
}}
"""

        try:
            response = ollama.chat(model=self.model, messages=[
                {'role': 'user', 'content': verification_prompt}
            ], format='json')
            
            result = json.loads(self._extract_json(response['message']['content']))
            return result
        except Exception:
            # Fallback: Accept with a medium score to avoid empty results
            return {"score": 0.7, "verdict": "accept", "reason": "Default acceptance"}