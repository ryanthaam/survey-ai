import os
import openai
from dotenv import load_dotenv
from typing import List, Dict

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

class SummarizerService:
    def __init__(self, model: str = "gpt-4"):
        self.model = model
        self.fallback_models = ["gpt-4", "gpt-3.5-turbo", "gpt-4-turbo-preview"]
    
    def summarize_cluster(self, texts: List[str], cluster_id: int = None) -> str:
        """Generate a summary for a cluster of texts."""
        if not texts:
            return "No responses in this cluster."
        
        prompt = f"""Analyze the following survey responses and provide a comprehensive business analysis.
        
Responses ({len(texts)} total):
{chr(10).join(f"- {text}" for text in texts)}
        
Provide a detailed analysis with:

1. **Main Themes/Patterns**: What are the primary topics and concerns?
2. **Key Business Insights**: What do these responses tell us about customer needs, pain points, and opportunities?
3. **Specific Actionable Recommendations**: Concrete steps the business should take, with priority levels
4. **Revenue Impact**: How addressing these issues could affect business performance
5. **Customer Sentiment**: Overall emotional tone and satisfaction indicators

Format your response clearly with headers and bullet points.

Detailed Analysis:"""
        
        return self._call_openai_with_fallback(prompt, temperature=0.3)
    
    def _call_openai_with_fallback(self, prompt: str, temperature: float = 0.3) -> str:
        """Call OpenAI API with model fallbacks."""
        from openai import OpenAI
        client = OpenAI()
        
        # Try models in order of preference
        models_to_try = [self.model] + [m for m in self.fallback_models if m != self.model]
        
        for model in models_to_try:
            try:
                response = client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=temperature
                )
                return response.choices[0].message.content
            except Exception as e:
                if "model" in str(e).lower() and "not" in str(e).lower():
                    # Model not available, try next one
                    continue
                else:
                    # Other error, return it
                    return f"Error generating summary with {model}: {str(e)}"
        
        return "Error: No available OpenAI models found. Please check your API access."
    
    def analyze_sentiment(self, texts: List[str]) -> Dict[str, any]:
        """Analyze sentiment of texts."""
        if not texts:
            return {"sentiment": "neutral", "confidence": 0.0}
        
        prompt = f"""Analyze the sentiment and emotional tone of these survey responses.
        
Responses ({len(texts)} total):
{chr(10).join(f"- {text}" for text in texts)}
        
Analyze:
1. Overall sentiment (positive/negative/neutral)
2. Confidence level (0.0 to 1.0)
3. Emotional intensity (low/medium/high)
4. Key emotional indicators found in the text

Return ONLY in this exact format:
sentiment: [positive/negative/neutral], confidence: [0.0-1.0], intensity: [low/medium/high], indicators: [brief description]

Analysis:"""
        
        result = self._call_openai_with_fallback(prompt, temperature=0.1)
        
        if result.startswith("Error"):
            return {"sentiment": "neutral", "confidence": 0.0}
        
        # Parse the response
        lines = result.lower().split(',')
        sentiment = "neutral"
        confidence = 0.5
        
        for line in lines:
            if "sentiment:" in line:
                sentiment = line.split("sentiment:")[1].strip()
            elif "confidence:" in line:
                try:
                    confidence = float(line.split("confidence:")[1].strip())
                except:
                    confidence = 0.5
        
        return {"sentiment": sentiment, "confidence": confidence}

# For backward compatibility
def summarize_cluster(texts: List[str]) -> str:
    """Generate a summary for a cluster of texts."""
    service = SummarizerService()
    return service.summarize_cluster(texts)
