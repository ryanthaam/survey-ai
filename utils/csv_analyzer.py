import pandas as pd
import numpy as np
import re
from typing import List, Dict, Tuple, Optional
from collections import Counter

class CSVAnalyzer:
    """Intelligent CSV analyzer that can detect and process various survey formats."""
    
    def __init__(self):
        # Common survey response column patterns
        self.response_patterns = [
            r'response', r'answer', r'feedback', r'comment', r'text', r'reply',
            r'input', r'message', r'description', r'detail', r'explanation',
            r'thoughts', r'opinion', r'suggestion', r'improvement', r'issue',
            r'problem', r'concern', r'experience', r'review', r'note'
        ]
        
        # Common question column patterns
        self.question_patterns = [
            r'question', r'prompt', r'query', r'ask', r'title', r'topic',
            r'subject', r'category', r'type', r'field', r'label'
        ]
        
        # Patterns to exclude (likely metadata)
        self.exclude_patterns = [
            r'timestamp', r'time', r'date', r'id', r'email', r'name', r'phone',
            r'age', r'gender', r'location', r'ip', r'browser', r'device',
            r'score', r'rating', r'number', r'count', r'status', r'completion'
        ]
    
    def analyze_csv(self, df: pd.DataFrame) -> Dict:
        """Analyze CSV structure and identify the best columns for analysis."""
        analysis = {
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'text_columns': [],
            'recommended_columns': [],
            'column_analysis': {},
            'preprocessing_suggestions': []
        }
        
        # Analyze each column
        for col in df.columns:
            col_analysis = self._analyze_column(df, col)
            analysis['column_analysis'][col] = col_analysis
            
            # If it's a good text column, add to recommendations
            if col_analysis['is_text_column'] and col_analysis['text_quality_score'] > 0.1:
                analysis['text_columns'].append(col)
                analysis['recommended_columns'].append({
                    'column': col,
                    'score': col_analysis['text_quality_score'],
                    'reason': col_analysis['recommendation_reason']
                })
        
        # Sort recommendations by score
        analysis['recommended_columns'] = sorted(
            analysis['recommended_columns'],
            key=lambda x: x['score'],
            reverse=True
        )
        
        # Generate preprocessing suggestions
        analysis['preprocessing_suggestions'] = self._generate_preprocessing_suggestions(df, analysis)
        
        return analysis
    
    def _analyze_column(self, df: pd.DataFrame, col: str) -> Dict:
        """Analyze a single column to determine if it's suitable for text analysis."""
        col_data = df[col].dropna()
        
        analysis = {
            'column_name': col,
            'non_null_count': len(col_data),
            'null_count': df[col].isnull().sum(),
            'unique_values': col_data.nunique(),
            'is_text_column': False,
            'text_quality_score': 0.0,
            'avg_text_length': 0.0,
            'recommendation_reason': '',
            'sample_values': col_data.head(3).tolist() if len(col_data) > 0 else []
        }
        
        if len(col_data) == 0:
            analysis['recommendation_reason'] = "Column is empty"
            return analysis
        
        # Check if column contains meaningful text
        text_lengths = []
        meaningful_text_count = 0
        
        for value in col_data:
            if pd.isna(value):
                continue
                
            str_value = str(value).strip()
            text_lengths.append(len(str_value))
            
            # Check if it's meaningful text (not just numbers, single words, etc.)
            if self._is_meaningful_text(str_value):
                meaningful_text_count += 1
        
        if len(text_lengths) > 0:
            analysis['avg_text_length'] = np.mean(text_lengths)
        
        # Calculate text quality score
        if len(col_data) > 0:
            meaningful_ratio = meaningful_text_count / len(col_data)
            length_score = min(analysis['avg_text_length'] / 100, 1.0)  # Normalize to 0-1
            uniqueness_score = min(analysis['unique_values'] / len(col_data), 1.0)
            
            # Column name relevance score
            name_score = self._calculate_name_relevance_score(col.lower())
            
            # Combine scores
            analysis['text_quality_score'] = (
                meaningful_ratio * 0.4 +
                length_score * 0.3 +
                uniqueness_score * 0.2 +
                name_score * 0.1
            )
            
            analysis['is_text_column'] = analysis['text_quality_score'] > 0.1
        
        # Generate recommendation reason
        analysis['recommendation_reason'] = self._generate_recommendation_reason(analysis, col)
        
        return analysis
    
    def _is_meaningful_text(self, text: str) -> bool:
        """Check if text is meaningful for analysis."""
        if len(text) < 5:  # Too short
            return False
        
        # Check if it's mostly numbers
        if re.match(r'^[\d\s\-\+\(\)\.]+$', text):
            return False
        
        # Check if it's a single word
        if len(text.split()) < 2:
            return False
        
        # Check if it has some alphabetic characters
        if not re.search(r'[a-zA-Z]', text):
            return False
        
        return True
    
    def _calculate_name_relevance_score(self, col_name: str) -> float:
        """Calculate relevance score based on column name."""
        score = 0.0
        
        # Check for response patterns
        for pattern in self.response_patterns:
            if re.search(pattern, col_name, re.IGNORECASE):
                score += 0.8
                break
        
        # Check for question patterns (lower score)
        for pattern in self.question_patterns:
            if re.search(pattern, col_name, re.IGNORECASE):
                score += 0.3
                break
        
        # Penalize exclude patterns
        for pattern in self.exclude_patterns:
            if re.search(pattern, col_name, re.IGNORECASE):
                score -= 0.5
                break
        
        return max(0.0, min(1.0, score))
    
    def _generate_recommendation_reason(self, analysis: Dict, col: str) -> str:
        """Generate human-readable reason for recommendation."""
        if not analysis['is_text_column']:
            if analysis['avg_text_length'] < 5:
                return "Text too short for meaningful analysis"
            elif analysis['unique_values'] < 3:
                return "Not enough unique values"
            else:
                return "Does not contain meaningful text content"
        
        reasons = []
        
        if analysis['text_quality_score'] > 0.7:
            reasons.append("High-quality text content")
        elif analysis['text_quality_score'] > 0.5:
            reasons.append("Good text content")
        else:
            reasons.append("Basic text content")
        
        if analysis['avg_text_length'] > 50:
            reasons.append("detailed responses")
        elif analysis['avg_text_length'] > 20:
            reasons.append("moderate response length")
        
        if analysis['unique_values'] / max(analysis['non_null_count'], 1) > 0.8:
            reasons.append("high variety")
        
        name_score = self._calculate_name_relevance_score(col.lower())
        if name_score > 0.5:
            reasons.append("relevant column name")
        
        return f"Recommended: {', '.join(reasons)}"
    
    def _generate_preprocessing_suggestions(self, df: pd.DataFrame, analysis: Dict) -> List[str]:
        """Generate suggestions for data preprocessing."""
        suggestions = []
        
        # Check for multiple text columns
        if len(analysis['text_columns']) > 1:
            suggestions.append("Consider combining multiple text columns for comprehensive analysis")
        
        # Check for data quality issues
        for col in analysis['text_columns']:
            col_analysis = analysis['column_analysis'][col]
            
            if col_analysis['null_count'] > len(df) * 0.3:
                suggestions.append(f"Column '{col}' has many missing values - consider data cleaning")
            
            if col_analysis['avg_text_length'] < 10:
                suggestions.append(f"Column '{col}' has short responses - results may be limited")
        
        # Check for potential improvements
        if len(analysis['recommended_columns']) == 0:
            suggestions.append("No ideal text columns found - try preprocessing or combining columns")
        
        return suggestions
    
    def get_best_column(self, df: pd.DataFrame) -> Optional[str]:
        """Get the best column for analysis automatically."""
        analysis = self.analyze_csv(df)
        
        if analysis['recommended_columns']:
            return analysis['recommended_columns'][0]['column']
        
        return None
    
    def preprocess_text_column(self, df: pd.DataFrame, column: str) -> List[str]:
        """Preprocess text column for analysis."""
        texts = []
        
        for value in df[column].dropna():
            if pd.isna(value):
                continue
                
            text = str(value).strip()
            
            # Skip empty or very short texts
            if len(text) < 3:
                continue
            
            # Basic cleaning
            text = re.sub(r'\s+', ' ', text)  # Normalize whitespace
            text = text.strip()
            
            # Skip if it's just a number or single character
            if re.match(r'^[\d\s\-\+\(\)\.]+$', text) or len(text) < 5:
                continue
            
            texts.append(text)
        
        return texts
    
    def auto_detect_and_process(self, df: pd.DataFrame) -> Tuple[List[str], Dict]:
        """Automatically detect best column and process data."""
        analysis = self.analyze_csv(df)
        
        # Get best column
        best_column = self.get_best_column(df)
        
        if not best_column:
            # Try to combine multiple columns if no single good column
            text_columns = analysis['text_columns']
            if len(text_columns) > 1:
                combined_texts = []
                for _, row in df.iterrows():
                    combined_text = []
                    for col in text_columns:
                        if pd.notna(row[col]):
                            combined_text.append(str(row[col]).strip())
                    
                    if combined_text:
                        combined_texts.append(' | '.join(combined_text))
                
                return combined_texts, analysis
            else:
                return [], analysis
        
        # Process the best column
        texts = self.preprocess_text_column(df, best_column)
        
        return texts, analysis