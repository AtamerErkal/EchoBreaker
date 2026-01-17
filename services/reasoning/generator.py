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
        """
        
        system_prompt = """
You are EchoBreaker, an AI designed to combat algorithmic bias.
Your task is to analyze the provided video transcript and return a structured JSON response containing:
1. A brief summary of the topic.
2. Extracted claims with sentiment and opinion mining details (targets/assessments).
3. Three objective counter-arguments (Ethical, Empirical, Logical) to the core thesis.
4. An overall sentiment classification.

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
      "title": "string",
      "content": "string",
      "source_reference": "string",
      "youtube_query": "string (Plain search keywords describing the counter-argument. DO NOT use quotes or special characters.)"
    }
  ]
}

**Rules**:
- Do not include markdown code blocks (```json). Just return the raw JSON string.
- Ensure the JSON is valid.
- Be objective and neutral in counter-arguments.
"""

        user_prompt = f"""
Analyze the following transcript:
{transcript}

Video URL: {video_url}
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
