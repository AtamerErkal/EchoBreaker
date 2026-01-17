import os
import json
import ollama
from core.config import Config
from models.analysis_result import AnalysisResult
from pydantic import ValidationError

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
      "semantic_contrast_score": 0.7 to 1.0 (how opposed this is to the original claim)
    }
  ]
}

**Rules**:
- Do not include markdown code blocks (```json). Just return the raw JSON string.
- Ensure the JSON is valid.
- Counter-arguments must be MAXIMALLY OPPOSED to the video's thesis
- Search queries must be SPECIFIC and ACADEMIC in nature
- Aim for semantic_contrast_score of 0.8+ (highly opposed perspectives)
"""

        user_prompt = f"""
Analyze the following transcript and generate counter-arguments that are DIAMETRICALLY OPPOSED to its core claims:

{transcript}

Video URL: {video_url}

Remember: Your counter-arguments must present the OPPOSITE perspective, not just related topics.
"""

        try:
            response = ollama.chat(model=self.model, messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_prompt},
            ], format='json')

            content = response['message']['content']
            
            # Parse JSON
            data = json.loads(content)
            
            # Inject the URL if the model forgot it or used placeholder
            data['video_url'] = video_url
            
            # Validate with Pydantic
            result = AnalysisResult(**data)
            return result

        except Exception as e:
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
