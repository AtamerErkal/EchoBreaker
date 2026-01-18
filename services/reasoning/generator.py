import os
import json
import ollama
from core.config import Config
from models.analysis_result import AnalysisResult
from pydantic import ValidationError

# #region agent log
LOG_PATH = r"e:\3. projects\EchoBreaker\.cursor\debug.log"
def _log(session_id, run_id, hypothesis_id, location, message, data):
    try:
        import time
        log_entry = {"sessionId": session_id, "runId": run_id, "hypothesisId": hypothesis_id, "location": location, "message": message, "data": data, "timestamp": int(time.time() * 1000)}
        with open(LOG_PATH, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry) + "\n")
            f.flush()
            os.fsync(f.fileno())
        print(f"[DEBUG LOG] {location}: {message}")  # Backup print
    except Exception as ex:
        print(f"[DEBUG LOG ERROR] Failed to write log: {ex}")
# #endregion

class ReasoningEngine:
    def __init__(self):
        self.model = Config.OLLAMA_MODEL
        # Check connectivity? 
        # For now assume Ollama is running at localhost:11434

    def generate_analysis(self, transcript: str, video_url: str) -> AnalysisResult:
        """
        Performs combined Semantic Analysis and Reasoning using a single Llama 3 prompt.
        Enhanced with semantic contrast enforcement and academic search query generation.
        """
        
        system_prompt = """
You are EchoBreaker, an AI designed to combat algorithmic bias through intellectual diversity.
Your task is to analyze video transcripts and provide DIAMETRICALLY OPPOSED counter-perspectives.

**CRITICAL: Semantic Opposition Requirements**
For each counter-argument type, you MUST provide a perspective that DIRECTLY CONTRADICTS the claim:

- **Ethical**: If claim says X is moral, argue why X is immoral OR why an opposing value takes precedence
  Example: If video supports "Gun Control for Safety" → Ethical counter: "Individual Liberty vs. Collective Security Trade-off"
  
- **Empirical**: Provide data/studies that CONTRADICT the claim's factual basis
  Example: If video claims "Gun Control reduces crime" → Empirical counter: "Statistical analysis showing no correlation or inverse effects"
  
- **Logical**: Challenge the REASONING STRUCTURE, identify fallacies, or present alternative causal models
  Example: If video uses "More guns = more deaths" → Logical counter: "Correlation vs. causation fallacy; third variables like poverty"

**Academic/Scientific Insight Generation**
You must generate a "academic_insight" for each counter-argument:
- Write ~150 words of sophisticated, academic text.
- Cite specific theories, general research fields, or philosophical frameworks.
- Use an authoritative, objective tone (like a research abstract).
- Do NOT use bullet points; use cohesive paragraphs.
- **CRITICAL**: End with a reference line, e.g., "Ref: Habermas, Theory of Communicative Action."

**Academic Search Query Engineering**
For the youtube_query field, generate SPECIFIC, ACADEMIC-STYLE search queries:
- Use precise terminology (e.g., "Second Amendment deterrence effect meta-analysis")
- Include qualifiers: "analysis", "research", "documentary", "expert interview", "data", "study"
- Avoid generic keywords; be specific to the counter-perspective
- Target educational, news, or documentary content

**Examples of Good vs. Bad Search Queries**:
❌ BAD: "gun control"
✅ GOOD: "Second Amendment effectiveness research academic analysis"

❌ BAD: "school safety"  
✅ GOOD: "armed deterrence in schools empirical studies"

**Output Schema**:
You must return valid JSON that exactly matches this structure:
{
  "video_url": "URL_PLACEHOLDER", 
  "topic_summary": "string",
  "overall_sentiment": "string",
  "claims": [
    {
      "text": "string",
      "sentiment": "positive" | "negative" | "neutral",
      "confidence_score": 0.0 to 1.0,
      "opinions": [
        { "target": "string", "assessment": "string", "sentiment": "string" }
      ]
    }
  ],
  "counter_arguments": [
    {
      "type": "Ethical" | "Empirical" | "Logical",
      "title": "string (concise, descriptive)",
      "content": "string (2-3 sentences explaining the counter-perspective)",
      "source_reference": "string (general reference to supporting literature/philosophy)",
      "youtube_query": "string (academic-style search query with qualifiers)",
      "semantic_contrast_score": 0.7 to 1.0 (how opposed this is to the original claim),
      "academic_insight": "string (~150 words of academic context/theory)"
    }
  ]
}

**Rules**:
- Do not include markdown code blocks (```json). Just return the raw JSON string.
- Ensure the JSON is valid.
- Counter-arguments must be MAXIMALLY OPPOSED to the video's thesis
- Search queries must be SPECIFIC and ACADEMIC in nature
- Aim for semantic_contrast_score of 0.8+ (highly opposed perspectives)
- academic_insight MUST be populated with high-quality text
"""

        user_prompt = f"""
Analyze the following transcript and generate counter-arguments that are DIAMETRICALLY OPPOSED to its core claims:

{transcript}

Video URL: {video_url}

Remember: Your counter-arguments must present the OPPOSITE perspective, not just related topics.
"""

        try:
            # #region agent log
            _log("debug-session", "run1", "A", "generator.py:107", "LLM request started", {"model": self.model})
            # #endregion
            
            response = ollama.chat(model=self.model, messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_prompt},
            ], format='json')

            content = response['message']['content']
            
            # #region agent log
            _log("debug-session", "run1", "A", "generator.py:127", "Raw LLM response received", {"content_length": len(content), "content_full": content if len(content) < 10000 else content[:10000] + "...[truncated]"})
            # #endregion
            
            # Parse JSON
            data = json.loads(content)
            
            # #region agent log
            _log("debug-session", "run1", "B", "generator.py:134", "JSON parsed successfully", {"has_counter_arguments": "counter_arguments" in data, "counter_arguments_count": len(data.get("counter_arguments", []))})
            # #endregion
            
            # Inject the URL if the model forgot it or used placeholder
            data['video_url'] = video_url
            
            # #region agent log
            if "counter_arguments" in data:
                for idx, ca in enumerate(data["counter_arguments"]):
                    has_youtube_query = "youtube_query" in ca
                    youtube_query_value = ca.get("youtube_query", None)
                    youtube_query_type = type(youtube_query_value).__name__ if youtube_query_value is not None else "NoneType"
                    all_fields = list(ca.keys())
                    _log("debug-session", "run1", "A", f"generator.py:143", f"Counter argument {idx} fields BEFORE fix", {"index": idx, "has_youtube_query": has_youtube_query, "youtube_query_value": str(youtube_query_value)[:200] if youtube_query_value else None, "youtube_query_type": youtube_query_type, "all_fields": all_fields, "type": ca.get("type"), "title": ca.get("title", "")[:50]})
            # #endregion
            
            # Fix missing youtube_query fields - generate from title/content if missing
            if "counter_arguments" in data:
                for idx, ca in enumerate(data["counter_arguments"]):
                    # Check if youtube_query is missing, None, empty, or whitespace-only
                    youtube_query = ca.get("youtube_query")
                    needs_fix = (
                        "youtube_query" not in ca or 
                        youtube_query is None or 
                        (isinstance(youtube_query, str) and not youtube_query.strip())
                    )
                    
                    if needs_fix:
                        # Generate a default query from title, type, and key terms
                        arg_type = ca.get("type", "")
                        title = ca.get("title", "")
                        # Extract key terms from title (first few words)
                        title_words = title.split()[:4] if title else []
                        title_keywords = " ".join(title_words) if title_words else ""
                        # Create academic-style query
                        default_query = f"{title_keywords} {arg_type} perspective research analysis".strip()
                        # Ensure it's not empty
                        if not default_query:
                            default_query = f"{arg_type} counter argument research"
                        ca["youtube_query"] = default_query
                        # #region agent log
                        _log("debug-session", "run1", "C", f"generator.py:161", f"Counter argument {idx} FIXED - added default youtube_query", {"index": idx, "generated_query": default_query, "original_fields": list(ca.keys()), "original_value": str(youtube_query) if youtube_query is not None else "None"})
                        # #endregion
                    else:
                        # #region agent log
                        _log("debug-session", "run1", "C", f"generator.py:166", f"Counter argument {idx} has valid youtube_query", {"index": idx, "youtube_query": str(youtube_query)[:200] if youtube_query else None})
                        # #endregion
            
            # #region agent log
            if "counter_arguments" in data:
                for idx, ca in enumerate(data["counter_arguments"]):
                    has_youtube_query = "youtube_query" in ca
                    youtube_query_value = ca.get("youtube_query", None)
                    _log("debug-session", "run1", "A", f"generator.py:180", f"Counter argument {idx} fields AFTER fix", {"index": idx, "has_youtube_query": has_youtube_query, "youtube_query_value": str(youtube_query_value)[:200] if youtube_query_value else None, "all_fields_after": list(ca.keys())})
            # #endregion
            
            # Validate with Pydantic
            try:
                result = AnalysisResult(**data)
                # #region agent log
                _log("debug-session", "run1", "D", "generator.py:184", "Pydantic validation SUCCESS", {"counter_arguments_count": len(result.counter_arguments)})
                # #endregion
                return result
            except Exception as validation_error:
                # #region agent log
                _log("debug-session", "run1", "E", "generator.py:188", "Pydantic validation FAILED", {"error_type": type(validation_error).__name__, "error_message": str(validation_error)[:1000], "counter_arguments_count": len(data.get("counter_arguments", [])), "data_keys": list(data.keys())})
                if "counter_arguments" in data:
                    for idx, ca in enumerate(data["counter_arguments"]):
                        _log("debug-session", "run1", "E", f"generator.py:190", f"Counter argument {idx} at validation failure", {"index": idx, "all_fields": list(ca.keys()), "has_youtube_query": "youtube_query" in ca, "youtube_query": ca.get("youtube_query")})
                # #endregion
                raise

        except Exception as e:
            # #region agent log
            _log("debug-session", "run1", "A", "generator.py:127", "Exception caught in generate_analysis", {"error_type": type(e).__name__, "error_message": str(e)[:500]})
            # #endregion
            print(f"Error in Ollama generation: {e}")
            # Return empty/error result or re-raise
            raise e
    
    def verify_relevance(self, counter_argument_content: str, video_title: str, video_description: str = "") -> dict:
        """
        Dual-pass verification: Checks if a video is actually relevant to the counter-argument.
        Returns: {'score': 0.0-1.0, 'reason': 'explanation', 'verdict': 'accept'|'reject'}
        """
        
        verification_prompt = f"""
You are a relevance verification system for EchoBreaker, an AI fighting echo chambers.

**Task**: Determine if this YouTube video is RELEVANT and HIGH-QUALITY for the given counter-argument.

**Counter-Argument**:
{counter_argument_content}

**Video Title**:
{video_title}

**Video Description**:
{video_description[:300] if video_description else "N/A"}

**Rejection Criteria** (automatically reject if ANY apply):
1. Clickbait/sensationalist content (e.g., "SHOCKING!", "You won't believe...")
2. Personal vlogs or human-interest stories (unless directly relevant)
3. Off-topic content (title doesn't relate to counter-argument)
4. Low-information content (reaction videos, compilations, entertainment)

**Quality Indicators** (boost score if present):
- News analysis, documentaries, expert interviews
- Academic or research-based content
- Specific terminology matching the counter-argument
- Reputable sources (universities, news organizations, think tanks)

**Output Format** (JSON only, no markdown):
{{
  "score": 0.0 to 1.0,
  "reason": "Brief explanation (1 sentence)",
  "verdict": "accept" or "reject"
}}

**Scoring Guide**:
- 0.0-0.4: Irrelevant or low quality → verdict: "reject"
- 0.5-0.6: Somewhat relevant but questionable → verdict: "reject"  
- 0.7-0.8: Relevant and decent quality → verdict: "accept"
- 0.9-1.0: Highly relevant and authoritative → verdict: "accept"
"""

        try:
            response = ollama.chat(model=self.model, messages=[
                {'role': 'user', 'content': verification_prompt}
            ], format='json')
            
            content = response['message']['content']
            result = json.loads(content)
            
            # Ensure required fields
            if 'score' not in result:
                result['score'] = 0.5
            if 'verdict' not in result:
                result['verdict'] = 'accept' if result['score'] >= 0.7 else 'reject'
            if 'reason' not in result:
                result['reason'] = 'Automated verification'
            
            return result
            
        except Exception as e:
            print(f"Error in relevance verification: {e}")
            # Default to accepting with medium score on error
            return {
                'score': 0.65,
                'reason': f'Verification error: {str(e)}',
                'verdict': 'accept'
            }
