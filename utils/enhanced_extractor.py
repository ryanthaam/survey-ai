import pandas as pd
import re
from typing import List, Dict, Tuple
from collections import defaultdict

class EnhancedSurveyExtractor:
    """More aggressive and comprehensive survey data extraction."""
    
    def __init__(self):
        self.skip_columns = [
            'respondent', 'collector', 'start', 'end', 'ip', 'email', 'first', 'last',
            'custom data', 'timestamp', 'id', 'date', 'time'
        ]
    
    def extract_all_meaningful_data(self, df: pd.DataFrame) -> Tuple[List[str], Dict]:
        """Extract ALL meaningful survey data, not just perfect responses."""
        
        # Strategy 1: Extract every non-metadata text response
        all_responses = []
        extraction_stats = defaultdict(int)
        
        for col in df.columns:
            if self._should_skip_column(col):
                extraction_stats['skipped_columns'] += 1
                continue
            
            col_responses = self._extract_from_column(df, col)
            all_responses.extend(col_responses)
            extraction_stats[f'from_{col}'] = len(col_responses)
            extraction_stats['processed_columns'] += 1
        
        # Strategy 2: Combine related answers for context
        contextual_responses = self._create_contextual_responses(df)
        all_responses.extend(contextual_responses)
        extraction_stats['contextual_responses'] = len(contextual_responses)
        
        # Strategy 3: Extract multi-part answers
        multi_part_responses = self._extract_multi_part_responses(df)
        all_responses.extend(multi_part_responses)
        extraction_stats['multi_part_responses'] = len(multi_part_responses)
        
        # Remove duplicates while preserving order
        unique_responses = []
        seen = set()
        for response in all_responses:
            if response not in seen and len(response.strip()) > 1:
                seen.add(response)
                unique_responses.append(response)
        
        # Create detailed info
        info = {
            'total_original_rows': len(df),
            'total_columns': len(df.columns),
            'extracted_responses': len(unique_responses),
            'extraction_stats': dict(extraction_stats),
            'extraction_methods': ['individual_columns', 'contextual_combination', 'multi_part_answers']
        }
        
        return unique_responses, info
    
    def _should_skip_column(self, col: str) -> bool:
        """Check if column should be skipped."""
        col_lower = col.lower()
        return any(skip in col_lower for skip in self.skip_columns)
    
    def _extract_from_column(self, df: pd.DataFrame, col: str) -> List[str]:
        """Extract all meaningful text from a column."""
        responses = []
        
        for value in df[col].dropna():
            text = str(value).strip()
            
            # Very lenient criteria - accept almost anything with text
            if self._is_extractable_text(text):
                # Add context about which question this answers
                clean_col = self._clean_column_name(col)
                responses.append(f"Q: {clean_col} | A: {text}")
        
        return responses
    
    def _is_extractable_text(self, text: str) -> bool:
        """Very lenient check for extractable text."""
        if len(text) < 2:
            return False
        
        # Skip pure numbers or very simple responses
        if re.match(r'^[\d\s\-\+\(\)\.]+$', text):
            return False
        
        # Skip single character responses
        if len(text) == 1:
            return False
        
        # Must have some alphabetic content
        if not re.search(r'[a-zA-Z]', text):
            return False
        
        # Skip very common non-informative responses
        if text.lower().strip() in ['yes', 'no', 'n/a', 'na', 'none', 'null']:
            return False
        
        return True
    
    def _clean_column_name(self, col: str) -> str:
        """Clean column name for better readability."""
        # Remove common survey platform artifacts
        cleaned = re.sub(r'\\(select all that apply\\)', '', col, flags=re.IGNORECASE)
        cleaned = re.sub(r'\\(please specify\\)', '', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'unnamed:\\s*\\d+', 'Additional Field', cleaned, flags=re.IGNORECASE)
        
        # Truncate very long column names
        if len(cleaned) > 60:
            cleaned = cleaned[:57] + "..."
        
        return cleaned.strip()
    
    def _create_contextual_responses(self, df: pd.DataFrame) -> List[str]:
        """Create responses that combine related columns for better context."""
        contextual_responses = []
        
        # Group columns by theme
        column_groups = self._group_related_columns(df)
        
        for theme, columns in column_groups.items():
            if len(columns) > 1:
                # Create combined responses for each row
                for idx, row in df.iterrows():
                    row_responses = []
                    
                    for col in columns:
                        if pd.notna(row[col]):
                            value = str(row[col]).strip()
                            if self._is_extractable_text(value):
                                clean_col = self._clean_column_name(col)
                                row_responses.append(f"{clean_col}: {value}")
                    
                    if len(row_responses) > 1:
                        combined = f"Multi-part response on {theme}: " + " | ".join(row_responses)
                        contextual_responses.append(combined)
        
        return contextual_responses
    
    def _group_related_columns(self, df: pd.DataFrame) -> Dict[str, List[str]]:
        """Group columns that seem related."""
        groups = defaultdict(list)
        processed = set()
        
        for col in df.columns:
            if col in processed or self._should_skip_column(col):
                continue
            
            # Extract key theme words
            theme = self._extract_theme_from_column(col)
            if theme:
                groups[theme].append(col)
                processed.add(col)
        
        # Only return groups with multiple columns
        return {theme: cols for theme, cols in groups.items() if len(cols) > 1}
    
    def _extract_theme_from_column(self, col: str) -> str:
        """Extract main theme from column name."""
        col_lower = col.lower()
        
        # Common survey themes
        themes = {
            'hardware': ['hardware', 'device', 'equipment'],
            'purchase': ['purchase', 'buy', 'source', 'sourcing'],
            'pricing': ['price', 'cost', 'competitive', 'pricing'],
            'support': ['support', 'service', 'help'],
            'delivery': ['delivery', 'shipping', 'time'],
            'brand': ['brand', 'prefer', 'manufacturer'],
            'feedback': ['comment', 'feedback', 'suggestion', 'improve'],
            'satisfaction': ['satisfied', 'happy', 'rating', 'important']
        }
        
        for theme, keywords in themes.items():
            if any(keyword in col_lower for keyword in keywords):
                return theme
        
        # Extract first meaningful word
        words = col_lower.split()
        meaningful_words = [w for w in words if len(w) > 3 and w not in ['what', 'which', 'where', 'when', 'how']]
        
        if meaningful_words:
            return meaningful_words[0]
        
        return 'general'
    
    def _extract_multi_part_responses(self, df: pd.DataFrame) -> List[str]:
        """Extract responses that span multiple columns in the same row."""
        multi_part = []
        
        # Look for rows with multiple meaningful responses
        for idx, row in df.iterrows():
            row_responses = []
            
            for col in df.columns:
                if not self._should_skip_column(col) and pd.notna(row[col]):
                    value = str(row[col]).strip()
                    if self._is_extractable_text(value) and len(value) > 5:  # Slightly higher threshold for multi-part
                        clean_col = self._clean_column_name(col)
                        row_responses.append(f"{clean_col}: {value}")
            
            # If this row has multiple meaningful responses, combine them
            if len(row_responses) > 1:
                combined = f"Complete response #{idx + 1}: " + " || ".join(row_responses)
                multi_part.append(combined)
        
        return multi_part
    
    def analyze_extraction_quality(self, responses: List[str]) -> Dict:
        """Analyze the quality and types of extracted responses."""
        analysis = {
            'total_responses': len(responses),
            'avg_length': sum(len(r) for r in responses) / len(responses) if responses else 0,
            'response_types': defaultdict(int),
            'themes_found': defaultdict(int)
        }
        
        for response in responses:
            # Categorize response types
            if response.startswith('Q:'):
                analysis['response_types']['single_question'] += 1
            elif response.startswith('Multi-part'):
                analysis['response_types']['multi_part'] += 1
            elif response.startswith('Complete'):
                analysis['response_types']['complete_response'] += 1
            else:
                analysis['response_types']['other'] += 1
            
            # Count themes
            for theme in ['price', 'stock', 'quality', 'support', 'delivery', 'hardware']:
                if theme in response.lower():
                    analysis['themes_found'][theme] += 1
        
        return analysis