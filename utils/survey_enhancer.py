import pandas as pd
import re
from typing import List, Dict, Tuple

class SurveyDataEnhancer:
    """Enhanced processor specifically for survey data exports."""
    
    def __init__(self):
        self.survey_platforms = {
            'surveymonkey': ['respondent', 'collector', 'start date', 'end date'],
            'typeform': ['submit date', 'network id', 'response id'],
            'google_forms': ['timestamp', 'email address'],
            'qualtrics': ['response id', 'response type', 'ip address']
        }
        
        # Common survey response indicators
        self.response_indicators = [
            'additional comments', 'feedback', 'suggestions', 'improvements',
            'other (please specify)', 'open-ended', 'anything else',
            'would like to share', 'device needs', 'comments',
            'what would encourage', 'main reasons', 'type of'
        ]
    
    def detect_survey_platform(self, df: pd.DataFrame) -> str:
        """Detect which survey platform generated this data."""
        columns_lower = [col.lower() for col in df.columns]
        
        for platform, indicators in self.survey_platforms.items():
            matches = sum(1 for indicator in indicators 
                         if any(indicator in col for col in columns_lower))
            if matches >= 2:
                return platform
        
        return 'unknown'
    
    def extract_survey_responses(self, df: pd.DataFrame) -> Tuple[List[str], Dict]:
        """Extract meaningful responses from survey data."""
        platform = self.detect_survey_platform(df)
        
        # Strategy 1: Look for open-ended response columns
        open_ended_responses = self._extract_open_ended_responses(df)
        
        # Strategy 2: Extract "Other (please specify)" responses
        other_responses = self._extract_other_responses(df)
        
        # Strategy 3: Combine multiple choice with explanations
        combined_responses = self._extract_combined_responses(df)
        
        # Merge all responses
        all_responses = []
        
        # Add open-ended responses (highest priority)
        for response in open_ended_responses:
            if len(response.strip()) > 5:
                all_responses.append(response)
        
        # Add other responses
        for response in other_responses:
            if len(response.strip()) > 3:
                all_responses.append(response)
        
        # Add combined responses if we don't have enough
        if len(all_responses) < 10:
            for response in combined_responses:
                if len(response.strip()) > 5:
                    all_responses.append(response)
        
        # Remove duplicates while preserving order
        unique_responses = []
        seen = set()
        for response in all_responses:
            if response not in seen:
                seen.add(response)
                unique_responses.append(response)
        
        info = {
            'platform_detected': platform,
            'open_ended_count': len(open_ended_responses),
            'other_specify_count': len(other_responses),
            'combined_responses_count': len(combined_responses),
            'total_unique_responses': len(unique_responses),
            'extraction_strategies_used': ['open_ended', 'other_specify', 'combined']
        }
        
        return unique_responses, info
    
    def _extract_open_ended_responses(self, df: pd.DataFrame) -> List[str]:
        """Extract responses from open-ended question columns."""
        responses = []
        
        for col in df.columns:
            col_lower = col.lower()
            
            # Check if column name suggests open-ended responses
            if any(indicator in col_lower for indicator in self.response_indicators):
                # This looks like an open-ended response column
                for value in df[col].dropna():
                    text = str(value).strip()
                    if self._is_meaningful_response(text):
                        responses.append(f"Q: {col} | A: {text}")
        
        return responses
    
    def _extract_other_responses(self, df: pd.DataFrame) -> List[str]:
        """Extract 'Other (please specify)' type responses."""
        responses = []
        
        for col in df.columns:
            col_lower = col.lower()
            
            # Look for "other" specification columns
            if 'other' in col_lower and ('specify' in col_lower or 'please' in col_lower):
                for value in df[col].dropna():
                    text = str(value).strip()
                    if self._is_meaningful_response(text):
                        responses.append(f"Other: {text}")
        
        return responses
    
    def _extract_combined_responses(self, df: pd.DataFrame) -> List[str]:
        """Combine multiple columns to create comprehensive responses."""
        responses = []
        
        # Group related columns by question themes
        question_groups = self._group_related_columns(df)
        
        for group_name, columns in question_groups.items():
            for _, row in df.iterrows():
                row_responses = []
                
                for col in columns:
                    if pd.notna(row[col]):
                        value = str(row[col]).strip()
                        if self._is_meaningful_response(value):
                            row_responses.append(f"{col}: {value}")
                
                if row_responses:
                    combined = f"Response group '{group_name}': " + " | ".join(row_responses)
                    responses.append(combined)
        
        return responses
    
    def _group_related_columns(self, df: pd.DataFrame) -> Dict[str, List[str]]:
        """Group columns that seem to be related to the same question."""
        groups = {}
        processed_columns = set()
        
        for col in df.columns:
            if col in processed_columns:
                continue
            
            # Look for question patterns
            base_question = self._extract_base_question(col)
            if base_question:
                # Find related columns
                related_cols = [col]
                for other_col in df.columns:
                    if other_col != col and other_col not in processed_columns:
                        if self._are_columns_related(col, other_col):
                            related_cols.append(other_col)
                            processed_columns.add(other_col)
                
                if len(related_cols) > 1:
                    groups[base_question] = related_cols
                
                processed_columns.add(col)
        
        return groups
    
    def _extract_base_question(self, column: str) -> str:
        """Extract the base question from a column name."""
        # Remove common suffixes and prefixes
        clean_col = re.sub(r'\\(select all that apply\\)', '', column, flags=re.IGNORECASE)
        clean_col = re.sub(r'\\(please specify\\)', '', clean_col, flags=re.IGNORECASE)
        clean_col = re.sub(r'other.*', '', clean_col, flags=re.IGNORECASE)
        
        # Take first meaningful part
        if len(clean_col) > 30:
            return clean_col[:30] + "..."
        
        return clean_col.strip()
    
    def _are_columns_related(self, col1: str, col2: str) -> bool:
        """Check if two columns are related to the same question."""
        # Simple similarity check
        col1_words = set(col1.lower().split())
        col2_words = set(col2.lower().split())
        
        # Calculate word overlap
        overlap = len(col1_words.intersection(col2_words))
        total_unique = len(col1_words.union(col2_words))
        
        if total_unique == 0:
            return False
        
        similarity = overlap / total_unique
        return similarity > 0.3
    
    def _is_meaningful_response(self, text: str) -> bool:
        """Check if a response is meaningful for analysis."""
        if len(text) < 2:
            return False
        
        # Skip obvious non-responses
        skip_patterns = [
            r'^\\d+$',  # Just numbers
            r'^[\\d\\s\\-\\+\\(\\)\\.]+$',  # Just numbers and symbols
            r'^(yes|no|n/a|na|none|null|undefined)$',  # Simple yes/no responses
            r'^\\s*$'  # Just whitespace
        ]
        
        for pattern in skip_patterns:
            if re.match(pattern, text.lower().strip()):
                return False
        
        # Must have some alphabetic content
        if not re.search(r'[a-zA-Z]', text):
            return False
        
        return True