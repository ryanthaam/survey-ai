import re
from typing import List, Dict
from collections import Counter

class ManualAnalyzer:
    """Provides manual analysis when AI services fail."""
    
    def __init__(self):
        self.positive_words = [
            'good', 'great', 'excellent', 'satisfied', 'happy', 'love', 'like',
            'perfect', 'amazing', 'fantastic', 'wonderful', 'pleased', 'impressed'
        ]
        
        self.negative_words = [
            'bad', 'terrible', 'awful', 'hate', 'dislike', 'poor', 'slow',
            'expensive', 'frustrating', 'disappointed', 'problem', 'issue',
            'complaint', 'difficult', 'confusing', 'limited', 'inadequate'
        ]
        
        self.theme_keywords = {
            'pricing': ['price', 'cost', 'expensive', 'cheap', 'competitive', 'pricing', 'money'],
            'delivery': ['delivery', 'shipping', 'fast', 'slow', 'time', 'quick'],
            'support': ['support', 'service', 'help', 'staff', 'team', 'customer'],
            'quality': ['quality', 'good', 'bad', 'excellent', 'poor', 'materials'],
            'stock': ['stock', 'availability', 'available', 'inventory', 'supply'],
            'technical': ['technical', 'device', 'hardware', 'software', 'system'],
            'website': ['website', 'site', 'interface', 'navigation', 'online'],
            'variety': ['variety', 'options', 'choice', 'selection', 'range', 'brands']
        }
    
    def analyze_cluster_manually(self, texts: List[str], cluster_id: int) -> str:
        """Generate manual analysis when AI fails."""
        if not texts:
            return "No responses in this cluster."
        
        # Extract key themes
        themes = self._extract_themes(texts)
        
        # Analyze sentiment manually
        sentiment = self._analyze_sentiment_manually(texts)
        
        # Generate summary
        summary_parts = []
        
        # Theme analysis
        if themes:
            top_themes = sorted(themes.items(), key=lambda x: x[1], reverse=True)[:3]
            theme_names = [theme for theme, count in top_themes]
            summary_parts.append(f"Main themes: {', '.join(theme_names)}")
        
        # Sentiment
        summary_parts.append(f"Overall sentiment: {sentiment['label']}")
        
        # Key insights
        insights = self._extract_key_insights(texts)
        if insights:
            summary_parts.append(f"Key insights: {insights}")
        
        # Response count
        summary_parts.append(f"Based on {len(texts)} responses")
        
        return " | ".join(summary_parts)
    
    def _extract_themes(self, texts: List[str]) -> Dict[str, int]:
        """Extract themes from text."""
        theme_counts = {}
        
        for theme, keywords in self.theme_keywords.items():
            count = 0
            for text in texts:
                text_lower = text.lower()
                for keyword in keywords:
                    if keyword in text_lower:
                        count += 1
                        break  # Count each text only once per theme
            
            if count > 0:
                theme_counts[theme] = count
        
        return theme_counts
    
    def _analyze_sentiment_manually(self, texts: List[str]) -> Dict[str, any]:
        """Simple manual sentiment analysis."""
        positive_count = 0
        negative_count = 0
        
        for text in texts:
            text_lower = text.lower()
            
            # Count positive words
            pos_score = sum(1 for word in self.positive_words if word in text_lower)
            # Count negative words  
            neg_score = sum(1 for word in self.negative_words if word in text_lower)
            
            if pos_score > neg_score:
                positive_count += 1
            elif neg_score > pos_score:
                negative_count += 1
        
        total = len(texts)
        if positive_count > negative_count:
            sentiment = 'positive'
            confidence = positive_count / total
        elif negative_count > positive_count:
            sentiment = 'negative' 
            confidence = negative_count / total
        else:
            sentiment = 'neutral'
            confidence = 0.5
        
        return {
            'sentiment': sentiment,
            'label': sentiment.title(),
            'confidence': confidence
        }
    
    def _extract_key_insights(self, texts: List[str]) -> str:
        """Extract key insights from responses."""
        insights = []
        
        # Look for specific patterns
        if any('stock' in text.lower() or 'availability' in text.lower() for text in texts):
            insights.append("Stock/availability concerns mentioned")
        
        if any('price' in text.lower() or 'expensive' in text.lower() for text in texts):
            insights.append("Pricing feedback provided")
        
        if any('support' in text.lower() or 'service' in text.lower() for text in texts):
            insights.append("Customer service experiences shared")
        
        if any('website' in text.lower() or 'interface' in text.lower() for text in texts):
            insights.append("Website/interface feedback given")
        
        return ", ".join(insights) if insights else "General feedback"
    
    def generate_cluster_recommendations(self, texts: List[str]) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []
        
        # Analyze themes and suggest actions
        themes = self._extract_themes(texts)
        
        if 'pricing' in themes:
            recommendations.append("Consider reviewing pricing strategy and competitor analysis")
        
        if 'stock' in themes:
            recommendations.append("Improve inventory management and stock availability")
        
        if 'support' in themes:
            recommendations.append("Enhance customer support training and response times")
        
        if 'website' in themes:
            recommendations.append("Invest in website/interface improvements and user experience")
        
        if 'variety' in themes:
            recommendations.append("Expand product range and brand partnerships")
        
        if 'delivery' in themes:
            recommendations.append("Optimize shipping processes and delivery times")
        
        if not recommendations:
            recommendations.append("Review feedback for improvement opportunities")
        
        return recommendations