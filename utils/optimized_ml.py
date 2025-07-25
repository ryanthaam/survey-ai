import pandas as pd
import numpy as np
import re
from typing import List, Dict, Tuple, Optional
from collections import defaultdict, Counter
import openai
from dotenv import load_dotenv
import os

load_dotenv()

class OptimizedMLService:
    """Optimized ML service with lazy loading for fast startup."""
    
    def __init__(self):
        self.model_cache = {}
        self.aspect_categories = {
            'customer_service': ['service', 'support', 'staff', 'help', 'team', 'agent', 'representative'],
            'product_quality': ['quality', 'product', 'material', 'construction', 'build', 'durability'],
            'pricing': ['price', 'cost', 'expensive', 'cheap', 'value', 'money', 'pricing'],
            'website_ux': ['website', 'interface', 'navigation', 'site', 'page', 'design', 'layout'],
            'shipping': ['shipping', 'delivery', 'packaging', 'transit', 'arrived'],
            'checkout': ['checkout', 'payment', 'purchase', 'order', 'cart', 'process'],
            'returns': ['return', 'refund', 'exchange', 'policy', 'replacement']
        }
        
        # Don't initialize models at startup - load when needed
        self._models_loaded = False
    
    def _load_sentiment_model(self):
        """Load sentiment model only when needed."""
        if 'sentiment_model' not in self.model_cache:
            try:
                from transformers import pipeline
                self.model_cache['sentiment_model'] = pipeline(
                    "sentiment-analysis",
                    model="cardiffnlp/twitter-roberta-base-sentiment-latest",
                    return_all_scores=True
                )
            except Exception:
                # Fallback to simple sentiment
                self.model_cache['sentiment_model'] = None
        return self.model_cache['sentiment_model']
    
    def _load_spacy_model(self):
        """Load spaCy model only when needed."""
        if 'spacy_model' not in self.model_cache:
            try:
                import spacy
                self.model_cache['spacy_model'] = spacy.load("en_core_web_sm")
            except Exception:
                self.model_cache['spacy_model'] = None
        return self.model_cache['spacy_model']
    
    def _load_embeddings_model(self):
        """Load embeddings model only when needed."""
        if 'embeddings_model' not in self.model_cache:
            try:
                from sentence_transformers import SentenceTransformer
                self.model_cache['embeddings_model'] = SentenceTransformer('all-MiniLM-L6-v2')
            except Exception:
                self.model_cache['embeddings_model'] = None
        return self.model_cache['embeddings_model']
    
    def quick_sentiment_analysis(self, texts: List[str]) -> Dict:
        """Fast sentiment analysis with basic insights."""
        results = {
            'overall_sentiment': {'dominant_sentiment': 'neutral', 'confidence': 0.5},
            'aspect_sentiments': {},
            'insights': []
        }
        
        # Simple keyword-based sentiment
        positive_words = ['good', 'great', 'excellent', 'love', 'amazing', 'satisfied', 'happy', 'best']
        negative_words = ['bad', 'terrible', 'awful', 'hate', 'disappointed', 'poor', 'worst', 'slow']
        
        total_positive = 0
        total_negative = 0
        
        # Analyze each aspect
        for aspect, keywords in self.aspect_categories.items():
            aspect_texts = [text.lower() for text in texts if any(keyword in text.lower() for keyword in keywords)]
            
            if aspect_texts:
                pos_count = sum(1 for text in aspect_texts if any(word in text for word in positive_words))
                neg_count = sum(1 for text in aspect_texts if any(word in text for word in negative_words))
                
                if pos_count > neg_count:
                    sentiment = 'positive'
                    confidence = 0.7
                elif neg_count > pos_count:
                    sentiment = 'negative'
                    confidence = 0.7
                else:
                    sentiment = 'neutral'
                    confidence = 0.5
                
                results['aspect_sentiments'][aspect] = {
                    'sentiment': {'dominant_sentiment': sentiment, 'confidence': confidence},
                    'mentions': len(aspect_texts),
                    'sample_texts': aspect_texts[:2]
                }
                
                total_positive += pos_count
                total_negative += neg_count
        
        # Overall sentiment
        if total_positive > total_negative:
            results['overall_sentiment'] = {'dominant_sentiment': 'positive', 'confidence': 0.7}
        elif total_negative > total_positive:
            results['overall_sentiment'] = {'dominant_sentiment': 'negative', 'confidence': 0.7}
        
        # Generate insights
        results['insights'] = self._generate_quick_insights(results)
        
        return results
    
    def quick_topic_analysis(self, texts: List[str]) -> Dict:
        """Fast topic analysis using keyword extraction."""
        # Simple keyword frequency analysis
        word_freq = defaultdict(int)
        stop_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'a', 'an', 'is', 'was', 'are', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them'}
        
        for text in texts:
            words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
            for word in words:
                if word not in stop_words:
                    word_freq[word] += 1
        
        # Group into topics based on frequency
        common_words = dict(Counter(word_freq).most_common(15))
        
        # Create simple topic groupings
        topics = {}
        topic_id = 0
        
        # Group related words into topics
        service_words = [w for w in common_words if any(kw in w for kw in ['service', 'support', 'help', 'staff'])]
        if service_words:
            topics[topic_id] = {
                'keywords': service_words[:5],
                'document_count': sum(1 for text in texts if any(word in text.lower() for word in service_words)),
                'representative_docs': [text for text in texts if any(word in text.lower() for word in service_words)][:2]
            }
            topic_id += 1
        
        product_words = [w for w in common_words if any(kw in w for kw in ['product', 'quality', 'material'])]
        if product_words:
            topics[topic_id] = {
                'keywords': product_words[:5],
                'document_count': sum(1 for text in texts if any(word in text.lower() for word in product_words)),
                'representative_docs': [text for text in texts if any(word in text.lower() for word in product_words)][:2]
            }
            topic_id += 1
        
        website_words = [w for w in common_words if any(kw in w for kw in ['website', 'site', 'page', 'navigation'])]
        if website_words:
            topics[topic_id] = {
                'keywords': website_words[:5],
                'document_count': sum(1 for text in texts if any(word in text.lower() for word in website_words)),
                'representative_docs': [text for text in texts if any(word in text.lower() for word in website_words)][:2]
            }
        
        return {
            'topics': topics,
            'topic_assignments': [0] * len(texts),  # Simplified
            'coherence_scores': {'average': 0.6},
            'note': 'Fast keyword-based topic detection'
        }
    
    def quick_entity_analysis(self, texts: List[str]) -> Dict:
        """Fast entity extraction using regex patterns."""
        entities = {
            'organizations': [],
            'products': [],
            'locations': [],
            'people': [],
            'money': [],
            'dates': [],
            'competitors': []
        }
        
        # Simple patterns
        money_pattern = r'\$\d+(?:\.\d{2})?'
        competitor_patterns = ['amazon', 'google', 'apple', 'microsoft', 'facebook', 'competitor']
        
        for text in texts:
            # Money extraction
            money_matches = re.findall(money_pattern, text)
            entities['money'].extend([{'entity': m, 'count': 1} for m in money_matches])
            
            # Simple competitor detection
            text_lower = text.lower()
            for comp in competitor_patterns:
                if comp in text_lower:
                    entities['competitors'].append({
                        'name': comp,
                        'context': text,
                        'mentions': 1
                    })
        
        return entities
    
    def quick_quality_scoring(self, texts: List[str]) -> Dict:
        """Fast response quality assessment."""
        quality_scores = []
        
        for text in texts:
            score = 0.0
            
            # Length-based scoring
            word_count = len(text.split())
            if word_count >= 5:
                score += 0.4
            elif word_count >= 2:
                score += 0.2
            
            # Structure scoring
            if any(punct in text for punct in '.!?'):
                score += 0.2
            
            # Content quality
            if len(text) > 20:
                score += 0.2
            
            # Diversity of words
            unique_words = len(set(text.lower().split()))
            if unique_words > word_count * 0.7:
                score += 0.2
            
            quality_scores.append({
                'text': text,
                'quality_score': min(score, 1.0),
                'length': len(text),
                'word_count': word_count,
                'is_spam': score < 0.3,
                'is_low_quality': score < 0.5
            })
        
        return {
            'scored_responses': quality_scores,
            'average_quality': np.mean([s['quality_score'] for s in quality_scores]),
            'high_quality_count': len([s for s in quality_scores if s['quality_score'] > 0.7]),
            'low_quality_count': len([s for s in quality_scores if s['is_low_quality']]),
            'spam_count': len([s for s in quality_scores if s['is_spam']])
        }
    
    def quick_competitive_analysis(self, texts: List[str]) -> Dict:
        """Fast competitive analysis using keyword patterns."""
        competitors = {}
        competitor_keywords = ['competitor', 'other', 'amazon', 'elsewhere', 'different']
        comparison_words = ['better', 'worse', 'cheaper', 'expensive', 'compared']
        
        competitive_mentions = 0
        
        for text in texts:
            text_lower = text.lower()
            
            # Look for competitive mentions
            if any(keyword in text_lower for keyword in competitor_keywords) and any(word in text_lower for word in comparison_words):
                competitive_mentions += 1
                
                # Simple sentiment detection
                if any(word in text_lower for word in ['better', 'prefer', 'good']):
                    sentiment = 'positive'
                elif any(word in text_lower for word in ['worse', 'bad', 'poor']):
                    sentiment = 'negative'
                else:
                    sentiment = 'neutral'
                
                competitors['general_competition'] = {
                    'mentions': competitive_mentions,
                    'contexts': [text],
                    'sentiment': sentiment,
                    'comparison_type': ['pricing' if 'price' in text_lower or 'cost' in text_lower or 'cheap' in text_lower else 'general']
                }
        
        return {
            'competitors_found': len(competitors),
            'competitor_details': competitors,
            'competitive_landscape': {'total_mentions': competitive_mentions},
            'recommendations': ['Monitor competitive mentions' if competitive_mentions > 0 else 'No significant competitive concerns']
        }
    
    def quick_anomaly_detection(self, texts: List[str]) -> Dict:
        """Fast anomaly detection using simple heuristics."""
        anomalies = []
        
        # Calculate basic stats
        lengths = [len(text) for text in texts]
        avg_length = np.mean(lengths)
        std_length = np.std(lengths)
        
        for i, text in enumerate(texts):
            is_anomaly = False
            anomaly_type = 'normal'
            
            # Length-based anomalies
            if len(text) < avg_length - 2*std_length:
                is_anomaly = True
                anomaly_type = 'too_short'
            elif len(text) > avg_length + 2*std_length:
                is_anomaly = True
                anomaly_type = 'too_long'
            
            # Content-based anomalies
            elif text.isupper():
                is_anomaly = True
                anomaly_type = 'all_caps'
            elif len(set(text.split())) <= 2 and len(text.split()) > 2:
                is_anomaly = True
                anomaly_type = 'repetitive'
            
            if is_anomaly:
                anomalies.append({
                    'text': text,
                    'distance_score': abs(len(text) - avg_length),
                    'anomaly_type': anomaly_type,
                    'index': i
                })
        
        return {
            'anomalies_found': len(anomalies),
            'anomaly_threshold': 2*std_length,
            'anomalous_responses': anomalies,
            'normal_response_pattern': f'Average response length: {avg_length:.1f} characters'
        }
    
    def _generate_quick_insights(self, results: Dict) -> List[str]:
        """Generate quick insights from analysis."""
        insights = []
        
        # Overall sentiment insight
        overall = results['overall_sentiment']
        insights.append(f"Overall sentiment is {overall['dominant_sentiment']}")
        
        # Aspect insights
        for aspect, data in results['aspect_sentiments'].items():
            sentiment = data['sentiment']['dominant_sentiment']
            mentions = data['mentions']
            insights.append(f"{aspect.replace('_', ' ').title()}: {sentiment} ({mentions} mentions)")
        
        return insights

    # Method to run all quick analyses
    def run_quick_analysis(self, texts: List[str]) -> Dict:
        """Run all quick analyses - much faster than full ML pipeline."""
        return {
            'aspect_analysis': self.quick_sentiment_analysis(texts),
            'topic_analysis': self.quick_topic_analysis(texts),
            'entity_analysis': self.quick_entity_analysis(texts),
            'quality_analysis': self.quick_quality_scoring(texts),
            'competitive_analysis': self.quick_competitive_analysis(texts),
            'anomaly_analysis': self.quick_anomaly_detection(texts)
        }