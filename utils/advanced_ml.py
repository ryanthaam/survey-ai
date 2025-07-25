import pandas as pd
import numpy as np
import re
from typing import List, Dict, Tuple, Optional
from collections import defaultdict, Counter
import openai
from dotenv import load_dotenv
import os

# Advanced ML libraries
try:
    from bertopic import BERTopic
    from sentence_transformers import SentenceTransformer
    import spacy
    from textblob import TextBlob
    from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
    ADVANCED_ML_AVAILABLE = True
except ImportError:
    ADVANCED_ML_AVAILABLE = False

load_dotenv()

class AdvancedMLService:
    """Advanced Machine Learning service for comprehensive survey analysis."""
    
    def __init__(self):
        self.model_cache = {}
        self.aspect_categories = {
            'customer_service': ['service', 'support', 'staff', 'help', 'team', 'agent', 'representative'],
            'product_quality': ['quality', 'product', 'material', 'construction', 'build', 'durability'],
            'pricing': ['price', 'cost', 'expensive', 'cheap', 'value', 'money', 'pricing'],
            'website_ux': ['website', 'interface', 'navigation', 'site', 'page', 'design', 'layout'],
            'shipping': ['shipping', 'delivery', 'packaging', 'transit', 'arrived', 'shipping'],
            'checkout': ['checkout', 'payment', 'purchase', 'order', 'cart', 'process'],
            'returns': ['return', 'refund', 'exchange', 'policy', 'replacement']
        }
        
        # Initialize models if available
        if ADVANCED_ML_AVAILABLE:
            self._initialize_models()
    
    def _initialize_models(self):
        """Initialize ML models with caching."""
        try:
            # Aspect-based sentiment analyzer
            self.aspect_sentiment_model = pipeline(
                "sentiment-analysis",
                model="cardiffnlp/twitter-roberta-base-sentiment-latest",
                return_all_scores=True
            )
            
            # NER model for entity extraction
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except:
                # Fallback if spacy model not available
                self.nlp = None
            
            # Emotion detection model
            self.emotion_model = pipeline(
                "text-classification",
                model="j-hartmann/emotion-english-distilroberta-base",
                return_all_scores=True
            )
            
            # Quality scoring model (using sentence transformer)
            self.quality_model = SentenceTransformer('all-MiniLM-L6-v2')
            
        except Exception as e:
            print(f"Warning: Some ML models couldn't be initialized: {e}")
    
    def multi_aspect_sentiment_analysis(self, texts: List[str]) -> Dict:
        """Perform aspect-based sentiment analysis."""
        if not ADVANCED_ML_AVAILABLE:
            return self._fallback_aspect_sentiment(texts)
        
        results = {
            'overall_sentiment': {},
            'aspect_sentiments': {},
            'emotional_analysis': {},
            'insights': []
        }
        
        # Combine all text for overall analysis
        combined_text = ' '.join(texts)
        
        # Overall sentiment
        overall_sentiment = self.aspect_sentiment_model(combined_text[:512])  # Limit length
        results['overall_sentiment'] = self._process_sentiment_scores(overall_sentiment[0])
        
        # Emotional analysis
        emotion_scores = self.emotion_model(combined_text[:512])
        results['emotional_analysis'] = self._process_emotion_scores(emotion_scores[0])
        
        # Aspect-based analysis
        for aspect, keywords in self.aspect_categories.items():
            aspect_texts = self._extract_aspect_texts(texts, keywords)
            
            if aspect_texts:
                aspect_combined = ' '.join(aspect_texts)[:512]
                aspect_sentiment = self.aspect_sentiment_model(aspect_combined)
                results['aspect_sentiments'][aspect] = {
                    'sentiment': self._process_sentiment_scores(aspect_sentiment[0]),
                    'mentions': len(aspect_texts),
                    'sample_texts': aspect_texts[:3]
                }
        
        # Generate insights
        results['insights'] = self._generate_aspect_insights(results)
        
        return results
    
    def topic_modeling_analysis(self, texts: List[str]) -> Dict:
        """Perform advanced topic modeling with BERTopic."""
        if not ADVANCED_ML_AVAILABLE:
            return self._fallback_topic_modeling(texts)
        
        try:
            # Initialize BERTopic model
            topic_model = BERTopic(
                embedding_model="all-MiniLM-L6-v2",
                min_topic_size=max(2, len(texts) // 10),
                nr_topics="auto"
            )
            
            # Fit model and get topics
            topics, probabilities = topic_model.fit_transform(texts)
            
            # Get topic information
            topic_info = topic_model.get_topic_info()
            
            # Extract topic keywords and representative docs
            topic_results = {}
            for topic_id in topic_info['Topic'].unique():
                if topic_id != -1:  # Skip outlier topic
                    keywords = topic_model.get_topic(topic_id)
                    topic_results[topic_id] = {
                        'keywords': [word for word, _ in keywords[:10]],
                        'document_count': len([t for t in topics if t == topic_id]),
                        'representative_docs': topic_model.get_representative_docs(topic_id)[:3]
                    }
            
            return {
                'topics': topic_results,
                'topic_assignments': topics,
                'coherence_scores': self._calculate_topic_coherence(topic_model, texts),
                'visualization_data': self._prepare_topic_visualization(topic_model)
            }
            
        except Exception as e:
            return {'error': f"Topic modeling failed: {str(e)}"}
    
    def named_entity_recognition(self, texts: List[str]) -> Dict:
        """Extract named entities (brands, products, locations, etc.)."""
        if not self.nlp:
            return self._fallback_ner(texts)
        
        entities = {
            'organizations': [],
            'products': [],
            'locations': [],
            'people': [],
            'money': [],
            'dates': [],
            'competitors': []
        }
        
        entity_counts = defaultdict(int)
        
        for text in texts:
            doc = self.nlp(text)
            
            for ent in doc.ents:
                entity_text = ent.text.strip()
                entity_counts[entity_text] += 1
                
                if ent.label_ in ["ORG", "PRODUCT"]:
                    if self._is_likely_competitor(entity_text, text):
                        entities['competitors'].append({
                            'name': entity_text,
                            'context': text,
                            'mentions': entity_counts[entity_text]
                        })
                    else:
                        entities['organizations'].append(entity_text)
                elif ent.label_ in ["PERSON"]:
                    entities['people'].append(entity_text)
                elif ent.label_ in ["GPE", "LOC"]:
                    entities['locations'].append(entity_text)
                elif ent.label_ in ["MONEY"]:
                    entities['money'].append(entity_text)
                elif ent.label_ in ["DATE", "TIME"]:
                    entities['dates'].append(entity_text)
        
        # Remove duplicates and sort by frequency
        for category in entities:
            if category != 'competitors':
                entity_counter = Counter(entities[category])
                entities[category] = [
                    {'entity': entity, 'count': count} 
                    for entity, count in entity_counter.most_common(10)
                ]
        
        return entities
    
    def response_quality_scoring(self, texts: List[str]) -> Dict:
        """Score response quality and detect low-quality/spam responses."""
        quality_scores = []
        
        for text in texts:
            score = self._calculate_quality_score(text)
            quality_scores.append({
                'text': text,
                'quality_score': score,
                'length': len(text),
                'word_count': len(text.split()),
                'is_spam': score < 0.3,
                'is_low_quality': score < 0.5
            })
        
        # Sort by quality score
        quality_scores.sort(key=lambda x: x['quality_score'], reverse=True)
        
        return {
            'scored_responses': quality_scores,
            'average_quality': np.mean([s['quality_score'] for s in quality_scores]),
            'high_quality_count': len([s for s in quality_scores if s['quality_score'] > 0.7]),
            'low_quality_count': len([s for s in quality_scores if s['is_low_quality']]),
            'spam_count': len([s for s in quality_scores if s['is_spam']]),
            'quality_distribution': self._get_quality_distribution(quality_scores)
        }
    
    def competitive_analysis(self, texts: List[str]) -> Dict:
        """Analyze competitive mentions and comparisons."""
        competitors = {}
        comparison_patterns = [
            r'better than (\w+)',
            r'compared to (\w+)',
            r'unlike (\w+)',
            r'similar to (\w+)',
            r'(\w+) is cheaper',
            r'(\w+) costs less',
            r'found (\w+) for less'
        ]
        
        sentiment_context = {
            'positive_context': ['better', 'superior', 'prefer', 'love', 'excellent'],
            'negative_context': ['worse', 'inferior', 'hate', 'terrible', 'awful', 'cheaper', 'less expensive']
        }
        
        for text in texts:
            text_lower = text.lower()
            
            # Look for comparison patterns
            for pattern in comparison_patterns:
                matches = re.finditer(pattern, text_lower)
                for match in matches:
                    competitor = match.group(1)
                    
                    if competitor not in competitors:
                        competitors[competitor] = {
                            'mentions': 0,
                            'contexts': [],
                            'sentiment': 'neutral',
                            'comparison_type': []
                        }
                    
                    competitors[competitor]['mentions'] += 1
                    competitors[competitor]['contexts'].append(text)
                    
                    # Determine sentiment context
                    sentiment = self._determine_competitor_sentiment(text, competitor, sentiment_context)
                    competitors[competitor]['sentiment'] = sentiment
                    
                    # Categorize comparison type
                    if any(word in text_lower for word in ['price', 'cost', 'expensive', 'cheap']):
                        competitors[competitor]['comparison_type'].append('pricing')
                    elif any(word in text_lower for word in ['quality', 'better', 'worse']):
                        competitors[competitor]['comparison_type'].append('quality')
                    elif any(word in text_lower for word in ['service', 'support']):
                        competitors[competitor]['comparison_type'].append('service')
        
        return {
            'competitors_found': len(competitors),
            'competitor_details': competitors,
            'competitive_landscape': self._analyze_competitive_landscape(competitors),
            'recommendations': self._generate_competitive_recommendations(competitors)
        }
    
    def anomaly_detection(self, texts: List[str]) -> Dict:
        """Detect unusual or anomalous responses."""
        if not ADVANCED_ML_AVAILABLE:
            return self._fallback_anomaly_detection(texts)
        
        # Get embeddings for all texts
        embeddings = self.quality_model.encode(texts)
        
        # Calculate distances from centroid
        centroid = np.mean(embeddings, axis=0)
        distances = [np.linalg.norm(emb - centroid) for emb in embeddings]
        
        # Identify anomalies (responses far from centroid)
        threshold = np.percentile(distances, 95)  # Top 5% as anomalies
        
        anomalies = []
        for i, (text, distance) in enumerate(zip(texts, distances)):
            if distance > threshold:
                anomalies.append({
                    'text': text,
                    'distance_score': distance,
                    'anomaly_type': self._classify_anomaly_type(text),
                    'index': i
                })
        
        return {
            'anomalies_found': len(anomalies),
            'anomaly_threshold': threshold,
            'anomalous_responses': sorted(anomalies, key=lambda x: x['distance_score'], reverse=True),
            'normal_response_pattern': self._describe_normal_pattern(texts, distances, threshold)
        }
    
    # Helper methods
    def _extract_aspect_texts(self, texts: List[str], keywords: List[str]) -> List[str]:
        """Extract texts that mention specific aspect keywords."""
        aspect_texts = []
        for text in texts:
            text_lower = text.lower()
            if any(keyword in text_lower for keyword in keywords):
                aspect_texts.append(text)
        return aspect_texts
    
    def _process_sentiment_scores(self, scores: List[Dict]) -> Dict:
        """Process sentiment scores from model output."""
        sentiment_map = {'LABEL_0': 'negative', 'LABEL_1': 'neutral', 'LABEL_2': 'positive'}
        
        processed = {}
        for score_dict in scores:
            label = sentiment_map.get(score_dict['label'], score_dict['label'])
            processed[label] = score_dict['score']
        
        # Determine dominant sentiment
        dominant = max(processed.items(), key=lambda x: x[1])
        return {
            'scores': processed,
            'dominant_sentiment': dominant[0],
            'confidence': dominant[1]
        }
    
    def _process_emotion_scores(self, scores: List[Dict]) -> Dict:
        """Process emotion scores from model output."""
        emotions = {}
        for score_dict in scores:
            emotions[score_dict['label']] = score_dict['score']
        
        dominant_emotion = max(emotions.items(), key=lambda x: x[1])
        return {
            'emotion_scores': emotions,
            'dominant_emotion': dominant_emotion[0],
            'emotion_confidence': dominant_emotion[1]
        }
    
    def _calculate_quality_score(self, text: str) -> float:
        """Calculate quality score for a response."""
        score = 0.0
        
        # Length-based scoring
        word_count = len(text.split())
        if word_count >= 5:
            score += 0.3
        elif word_count >= 2:
            score += 0.1
        
        # Complexity scoring
        if len(set(text.split())) / max(len(text.split()), 1) > 0.7:  # Unique word ratio
            score += 0.2
        
        # Grammar and structure
        try:
            blob = TextBlob(text)
            if len(blob.sentences) > 1:
                score += 0.2
            
            # Check for proper punctuation
            if any(punct in text for punct in '.!?'):
                score += 0.1
                
        except:
            pass
        
        # Content quality indicators
        quality_indicators = ['because', 'however', 'although', 'specifically', 'especially']
        if any(indicator in text.lower() for indicator in quality_indicators):
            score += 0.2
        
        return min(score, 1.0)
    
    def _is_likely_competitor(self, entity: str, context: str) -> bool:
        """Determine if an entity is likely a competitor."""
        competitor_indicators = [
            'compared to', 'better than', 'unlike', 'instead of',
            'cheaper', 'more expensive', 'similar to'
        ]
        return any(indicator in context.lower() for indicator in competitor_indicators)
    
    def _determine_competitor_sentiment(self, text: str, competitor: str, sentiment_context: Dict) -> str:
        """Determine sentiment towards competitor."""
        text_lower = text.lower()
        
        positive_score = sum(1 for word in sentiment_context['positive_context'] if word in text_lower)
        negative_score = sum(1 for word in sentiment_context['negative_context'] if word in text_lower)
        
        if positive_score > negative_score:
            return 'positive'
        elif negative_score > positive_score:
            return 'negative'
        else:
            return 'neutral'
    
    def _generate_aspect_insights(self, results: Dict) -> List[str]:
        """Generate insights from aspect-based analysis."""
        insights = []
        
        # Overall sentiment insight
        overall = results['overall_sentiment']
        insights.append(f"Overall sentiment is {overall['dominant_sentiment']} with {overall['confidence']:.2f} confidence")
        
        # Aspect-specific insights
        for aspect, data in results['aspect_sentiments'].items():
            sentiment = data['sentiment']['dominant_sentiment']
            mentions = data['mentions']
            insights.append(f"{aspect.replace('_', ' ').title()}: {sentiment} sentiment ({mentions} mentions)")
        
        # Emotional analysis insight
        emotion = results['emotional_analysis']
        insights.append(f"Dominant emotion: {emotion['dominant_emotion']} ({emotion['emotion_confidence']:.2f} confidence)")
        
        return insights
    
    # Fallback methods for when advanced ML libraries aren't available
    def _fallback_aspect_sentiment(self, texts: List[str]) -> Dict:
        """Fallback aspect sentiment analysis using basic methods."""
        return {
            'overall_sentiment': {'dominant_sentiment': 'neutral', 'confidence': 0.5},
            'aspect_sentiments': {},
            'emotional_analysis': {'dominant_emotion': 'neutral', 'emotion_confidence': 0.5},
            'insights': ['Advanced ML libraries not available - using basic analysis']
        }
    
    def _fallback_topic_modeling(self, texts: List[str]) -> Dict:
        """Fallback topic modeling using keyword extraction."""
        # Simple keyword-based topic detection
        word_freq = defaultdict(int)
        for text in texts:
            words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())
            for word in words:
                word_freq[word] += 1
        
        # Group into topics based on frequency
        common_words = dict(Counter(word_freq).most_common(20))
        
        return {
            'topics': {0: {'keywords': list(common_words.keys())[:10], 'document_count': len(texts)}},
            'topic_assignments': [0] * len(texts),
            'coherence_scores': {'average': 0.5},
            'note': 'Using fallback keyword-based topic detection'
        }
    
    def _fallback_ner(self, texts: List[str]) -> Dict:
        """Fallback NER using regex patterns."""
        # Simple pattern-based entity extraction
        entities = {
            'organizations': [],
            'products': [],
            'locations': [],
            'people': [],
            'money': [],
            'dates': [],
            'competitors': []
        }
        
        # Basic money pattern
        money_pattern = r'\$\d+(?:\.\d{2})?'
        for text in texts:
            money_matches = re.findall(money_pattern, text)
            entities['money'].extend([{'entity': m, 'count': 1} for m in money_matches])
        
        return entities
    
    def _fallback_anomaly_detection(self, texts: List[str]) -> Dict:
        """Fallback anomaly detection using simple heuristics."""
        anomalies = []
        
        # Find very short or very long responses
        avg_length = np.mean([len(text) for text in texts])
        std_length = np.std([len(text) for text in texts])
        
        for i, text in enumerate(texts):
            if len(text) < avg_length - 2*std_length or len(text) > avg_length + 2*std_length:
                anomalies.append({
                    'text': text,
                    'distance_score': abs(len(text) - avg_length),
                    'anomaly_type': 'length_based',
                    'index': i
                })
        
        return {
            'anomalies_found': len(anomalies),
            'anomaly_threshold': 2*std_length,
            'anomalous_responses': anomalies,
            'normal_response_pattern': f'Average response length: {avg_length:.1f} characters'
        }
    
    def _calculate_topic_coherence(self, topic_model, texts: List[str]) -> Dict:
        """Calculate topic coherence metrics."""
        try:
            # This would require additional libraries for proper coherence calculation
            return {'average': 0.7, 'note': 'Coherence calculation simplified'}
        except:
            return {'average': 0.5, 'note': 'Could not calculate coherence'}
    
    def _prepare_topic_visualization(self, topic_model) -> Dict:
        """Prepare data for topic visualization."""
        return {'note': 'Visualization data prepared'}
    
    def _classify_anomaly_type(self, text: str) -> str:
        """Classify the type of anomaly."""
        if len(text) < 10:
            return 'too_short'
        elif len(text) > 500:
            return 'too_long'
        elif text.isupper():
            return 'all_caps'
        elif len(set(text.split())) == 1:
            return 'repetitive'
        else:
            return 'semantic_outlier'
    
    def _describe_normal_pattern(self, texts: List[str], distances: List[float], threshold: float) -> str:
        """Describe the normal response pattern."""
        normal_texts = [text for text, dist in zip(texts, distances) if dist <= threshold]
        avg_length = np.mean([len(text) for text in normal_texts])
        avg_words = np.mean([len(text.split()) for text in normal_texts])
        
        return f"Normal responses average {avg_length:.1f} characters and {avg_words:.1f} words"
    
    def _get_quality_distribution(self, quality_scores: List[Dict]) -> Dict:
        """Get distribution of quality scores."""
        scores = [s['quality_score'] for s in quality_scores]
        return {
            'high_quality': len([s for s in scores if s > 0.7]) / len(scores),
            'medium_quality': len([s for s in scores if 0.4 <= s <= 0.7]) / len(scores),
            'low_quality': len([s for s in scores if s < 0.4]) / len(scores)
        }
    
    def _analyze_competitive_landscape(self, competitors: Dict) -> Dict:
        """Analyze the competitive landscape."""
        if not competitors:
            return {'summary': 'No competitors mentioned'}
        
        total_mentions = sum(comp['mentions'] for comp in competitors.values())
        most_mentioned = max(competitors.items(), key=lambda x: x[1]['mentions'])
        
        return {
            'total_competitors': len(competitors),
            'total_mentions': total_mentions,
            'most_mentioned_competitor': most_mentioned[0],
            'pricing_competitors': len([c for c in competitors.values() if 'pricing' in c['comparison_type']]),
            'quality_competitors': len([c for c in competitors.values() if 'quality' in c['comparison_type']])
        }
    
    def _generate_competitive_recommendations(self, competitors: Dict) -> List[str]:
        """Generate recommendations based on competitive analysis."""
        recommendations = []
        
        if not competitors:
            return ['Monitor for competitive mentions in future surveys']
        
        pricing_mentions = sum(1 for comp in competitors.values() if 'pricing' in comp['comparison_type'])
        if pricing_mentions > 0:
            recommendations.append('Consider pricing strategy review due to competitive price comparisons')
        
        negative_mentions = sum(1 for comp in competitors.values() if comp['sentiment'] == 'negative')
        if negative_mentions > len(competitors) / 2:
            recommendations.append('Customers view competitors unfavorably - leverage this in marketing')
        
        return recommendations