import os
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import TextAnalyticsClient
from core.config import Config
from models.analysis_result import ExtractedClaim, MinedOpinion

class SemanticAnalyzer:
    def __init__(self):
        if not Config.AZURE_LANGUAGE_KEY or not Config.AZURE_LANGUAGE_ENDPOINT:
            raise ValueError("Azure Language credentials not provided.")
        
        credential = AzureKeyCredential(Config.AZURE_LANGUAGE_KEY)
        self.client = TextAnalyticsClient(endpoint=Config.AZURE_LANGUAGE_ENDPOINT, credential=credential)

    async def analyze_sentiment_and_opinions(self, text: str) -> List[ExtractedClaim]:
        """
        Analyzes the text for sentiment and performs opinion mining to extract key claims and assessments.
        """
        if not text:
            return []

        # Azure Text Analytics is synchronous by default in the python SDK for standard calls, 
        # but we can wrap it or treat it as a blocking call to be purely functional. 
        # Ideally, we chunk the text if it's too long (>5120 chars).
        # For simplicity in this F0 tier implementation, we assume text fits or we truncate/chunk roughly.
        
        # Simple chunking to avoid 5120 char limit per document
        max_chunk_size = 5000 
        chunks = [text[i:i+max_chunk_size] for i in range(0, len(text), max_chunk_size)]
        
        extracted_claims = []

        # Process chunks (in a real async app, run in threadpool if blocking)
        # Here we just iterate.
        for chunk in chunks:
            response = self.client.analyze_sentiment(
                documents=[chunk], 
                show_opinion_mining=True
            )
            
            # Result is a list of AnalyzeSentimentResult, we only sent one document.
            doc_result = response[0]
            
            if doc_result.is_error:
                print(f"Error analyzing chunk: {doc_result.error.code} - {doc_result.error.message}")
                continue

            # Map sentences to Claims
            for sentence in doc_result.sentences:
                opinions = []
                for mined_opinion in sentence.mined_opinions:
                    opinions.append(MinedOpinion(
                        target=mined_opinion.target.text,
                        assessment=mined_opinion.assessments[0].text if mined_opinion.assessments else "N/A",
                        sentiment=mined_opinion.assessments[0].sentiment if mined_opinion.assessments else "neutral"
                    ))
                
                # Only keep sentences that seem like claims (have opinions or strong sentiment)
                if opinions or sentence.sentiment != 'neutral':
                    claim = ExtractedClaim(
                        text=sentence.text,
                        sentiment=sentence.sentiment,
                        confidence_score=sentence.confidence_scores[sentence.sentiment],
                        opinions=opinions
                    )
                    extracted_claims.append(claim)

        return extracted_claims
