import openai
import streamlit as st
import json
import re
from typing import Dict, List, Optional, Any
from datetime import datetime
import pandas as pd
import numpy as np
from dotenv import load_dotenv
import os

load_dotenv()

class AIAnalysisAssistant:
    """AI-powered chat assistant for natural language querying of survey analysis results."""
    
    def __init__(self):
        self.openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Initialize conversation history
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
        
        # Analysis context
        self.analysis_context = {}
        
        # Predefined query templates
        self.query_templates = {
            'sentiment': [
                "What's the overall sentiment?",
                "Which clusters are most positive/negative?",
                "How satisfied are customers?",
                "What makes customers happy/unhappy?"
            ],
            'clusters': [
                "What are the main themes?",
                "Which cluster has the most responses?",
                "What are customers talking about most?",
                "Summarize each cluster for me"
            ],
            'insights': [
                "What are the key insights?",
                "What should we prioritize?",
                "What are the main problems?",
                "Give me actionable recommendations"
            ],
            'comparisons': [
                "Compare positive vs negative feedback",
                "Which aspects need improvement?",
                "What are customers praising?",
                "What are the biggest pain points?"
            ]
        }
        
        # System prompt for the AI assistant
        self.system_prompt = """You are an AI assistant specialized in analyzing survey data and customer feedback. 
        You have access to survey analysis results including clusters, sentiment analysis, and response data.
        
        Your role is to:
        1. Answer questions about survey results in a clear, business-focused manner
        2. Provide actionable insights and recommendations
        3. Help users understand patterns and trends in their data
        4. Suggest follow-up questions or areas to explore
        5. Present information in a way that's useful for business decision-making
        
        Always be:
        - Specific and data-driven in your responses
        - Professional but conversational
        - Focused on actionable insights
        - Clear about limitations or assumptions
        
        When you don't have specific data, acknowledge this and provide general guidance based on best practices."""
    
    def render_chat_interface(self, analysis_results: Dict):
        """Render the main chat interface."""
        self.analysis_context = analysis_results
        
        # Chat header
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 1.5rem;
            border-radius: 0.75rem;
            margin-bottom: 1.5rem;
            color: white;
        ">
            <h3 style="margin: 0; display: flex; align-items: center;">
                🤖 AI Analysis Assistant
                <span style="
                    background: rgba(255,255,255,0.2);
                    padding: 0.25rem 0.5rem;
                    border-radius: 1rem;
                    font-size: 0.75rem;
                    margin-left: 1rem;
                ">Ask me anything about your survey data!</span>
            </h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Quick action buttons
        self._render_quick_actions()
        
        # Chat messages
        self._render_chat_history()
        
        # Chat input
        self._render_chat_input()
        
        # Suggested questions
        self._render_suggested_questions()
    
    def _render_quick_actions(self):
        """Render quick action buttons for common queries."""
        st.markdown("**🚀 Quick Actions:**")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("📊 Overall Summary", use_container_width=True):
                self._handle_quick_query("Give me an overall summary of the survey results")
        
        with col2:
            if st.button("😊 Sentiment Analysis", use_container_width=True):
                self._handle_quick_query("What's the sentiment breakdown and what's driving positive/negative feelings?")
        
        with col3:
            if st.button("🎯 Key Insights", use_container_width=True):
                self._handle_quick_query("What are the most important insights and actionable recommendations?")
        
        with col4:
            if st.button("🔍 Problem Areas", use_container_width=True):
                self._handle_quick_query("What are the main problems or areas that need improvement?")
    
    def _render_chat_history(self):
        """Render the conversation history."""
        if st.session_state.chat_history:
            st.markdown("### 💬 Conversation")
            
            for i, message in enumerate(st.session_state.chat_history):
                if message['role'] == 'user':
                    st.markdown(f"""
                    <div style="
                        background: #e0f2fe;
                        padding: 1rem;
                        border-radius: 0.75rem 0.75rem 0.1rem 0.75rem;
                        margin: 0.5rem 0 0.5rem 2rem;
                        border-left: 3px solid #0ea5e9;
                    ">
                        <strong>You:</strong> {message['content']}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style="
                        background: #f0f9ff;
                        padding: 1rem;
                        border-radius: 0.75rem 0.75rem 0.75rem 0.1rem;
                        margin: 0.5rem 2rem 0.5rem 0;
                        border-left: 3px solid #3b82f6;
                    ">
                        <strong>🤖 AI Assistant:</strong><br>
                        {message['content']}
                    </div>
                    """, unsafe_allow_html=True)
    
    def _render_chat_input(self):
        """Render the chat input interface."""
        st.markdown("---")
        
        # Chat input form
        with st.form("chat_form", clear_on_submit=True):
            col1, col2 = st.columns([4, 1])
            
            with col1:
                user_input = st.text_input(
                    "Ask me anything about your survey data:",
                    placeholder="e.g., 'What are customers saying about pricing?' or 'Which cluster needs attention?'",
                    key="chat_input"
                )
            
            with col2:
                send_button = st.form_submit_button("Send 📤", use_container_width=True)
            
            if send_button and user_input:
                self._handle_user_query(user_input)
                st.rerun()
    
    def _render_suggested_questions(self):
        """Render suggested questions based on available data."""
        if not st.session_state.chat_history:  # Only show if no conversation yet
            st.markdown("### 💡 Suggested Questions")
            
            # Categorize suggestions based on available data
            suggestions = self._generate_contextual_suggestions()
            
            cols = st.columns(2)
            for i, suggestion in enumerate(suggestions[:6]):  # Show max 6 suggestions
                with cols[i % 2]:
                    if st.button(f"💬 {suggestion}", key=f"suggestion_{i}", use_container_width=True):
                        self._handle_quick_query(suggestion)
                        st.rerun()
    
    def _handle_user_query(self, query: str):
        """Handle user query and generate AI response."""
        # Add user message to history
        st.session_state.chat_history.append({
            'role': 'user',
            'content': query,
            'timestamp': datetime.now()
        })
        
        # Generate AI response
        response = self._generate_ai_response(query)
        
        # Add AI response to history
        st.session_state.chat_history.append({
            'role': 'assistant',
            'content': response,
            'timestamp': datetime.now()
        })
    
    def _handle_quick_query(self, query: str):
        """Handle quick action queries."""
        self._handle_user_query(query)
    
    def _generate_ai_response(self, query: str) -> str:
        """Generate AI response using OpenAI API with survey context."""
        try:
            # Prepare context about the survey data
            context = self._prepare_analysis_context()
            
            # Create the full prompt
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": f"""
                Survey Analysis Context:
                {context}
                
                User Question: {query}
                
                Please provide a helpful, specific answer based on the survey data provided. If you need to make assumptions, state them clearly.
                """}
            ]
            
            # Add conversation history for context
            for message in st.session_state.chat_history[-4:]:  # Last 4 messages for context
                if message['role'] in ['user', 'assistant']:
                    messages.append({
                        "role": message['role'],
                        "content": message['content']
                    })
            
            # Call OpenAI API
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                temperature=0.7,
                max_tokens=500
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"I'm sorry, I encountered an error while processing your question: {str(e)}. Please try rephrasing your question or ask something else about your survey data."
    
    def _prepare_analysis_context(self) -> str:
        """Prepare a summary of the analysis results for the AI."""
        if not self.analysis_context:
            return "No survey analysis data available."
        
        context_parts = []
        
        # Basic stats
        total_responses = self.analysis_context.get('total_responses', 0)
        context_parts.append(f"Total survey responses analyzed: {total_responses}")
        
        # Cluster information
        clusters = self.analysis_context.get('clusters', {})
        if clusters:
            context_parts.append(f"Number of response clusters identified: {len(clusters)}")
            
            # Cluster details
            for cluster_id, texts in clusters.items():
                if cluster_id != -1:  # Skip noise cluster
                    sample_texts = texts[:3]  # First 3 responses as examples
                    context_parts.append(f"Cluster {cluster_id + 1} ({len(texts)} responses): Sample responses: {sample_texts}")
        
        # Sentiment information
        sentiments = self.analysis_context.get('sentiments', {})
        if sentiments:
            sentiment_summary = []
            for cluster_id, sentiment_data in sentiments.items():
                if cluster_id != -1:
                    sentiment = sentiment_data.get('sentiment', 'neutral')
                    confidence = sentiment_data.get('confidence', 0)
                    sentiment_summary.append(f"Cluster {cluster_id + 1}: {sentiment} sentiment (confidence: {confidence:.2f})")
            
            if sentiment_summary:
                context_parts.append("Sentiment analysis: " + "; ".join(sentiment_summary))
        
        # Summary information
        summaries = self.analysis_context.get('summaries', {})
        if summaries:
            for cluster_id, summary in summaries.items():
                if cluster_id != -1:
                    context_parts.append(f"Cluster {cluster_id + 1} summary: {summary[:200]}...")
        
        return "\n".join(context_parts)
    
    def _generate_contextual_suggestions(self) -> List[str]:
        """Generate contextual suggestions based on available data."""
        suggestions = []
        
        # Basic suggestions always available
        basic_suggestions = [
            "What are the main themes in the responses?",
            "Which areas need the most improvement?",
            "What are customers most satisfied with?",
            "Give me a business summary of the findings"
        ]
        
        suggestions.extend(basic_suggestions)
        
        # Add context-specific suggestions
        clusters = self.analysis_context.get('clusters', {})
        if len(clusters) > 2:
            suggestions.append(f"Compare the {len(clusters)} different response clusters")
        
        sentiments = self.analysis_context.get('sentiments', {})
        if sentiments:
            negative_clusters = [cid for cid, data in sentiments.items() 
                              if data.get('sentiment') == 'negative']
            if negative_clusters:
                suggestions.append("What's causing negative sentiment?")
        
        return suggestions[:8]  # Return max 8 suggestions
    
    def export_conversation(self) -> str:
        """Export the conversation history."""
        if not st.session_state.chat_history:
            return "No conversation to export."
        
        export_data = {
            'export_date': datetime.now().isoformat(),
            'conversation_length': len(st.session_state.chat_history),
            'messages': []
        }
        
        for message in st.session_state.chat_history:
            export_data['messages'].append({
                'role': message['role'],
                'content': message['content'],
                'timestamp': message['timestamp'].isoformat() if isinstance(message['timestamp'], datetime) else str(message['timestamp'])
            })
        
        return json.dumps(export_data, indent=2)
    
    def clear_conversation(self):
        """Clear the conversation history."""
        st.session_state.chat_history = []
    
    def get_conversation_insights(self) -> Dict:
        """Get insights about the conversation."""
        if not st.session_state.chat_history:
            return {}
        
        user_messages = [msg for msg in st.session_state.chat_history if msg['role'] == 'user']
        
        insights = {
            'total_messages': len(st.session_state.chat_history),
            'user_questions': len(user_messages),
            'conversation_length_minutes': 0,  # Could calculate based on timestamps
            'most_common_topics': self._extract_common_topics(user_messages),
            'question_types': self._categorize_questions(user_messages)
        }
        
        return insights
    
    def _extract_common_topics(self, messages: List[Dict]) -> List[str]:
        """Extract common topics from user messages."""
        # Simple keyword extraction
        topics = {}
        keywords = ['sentiment', 'cluster', 'customer', 'price', 'quality', 'service', 'positive', 'negative']
        
        for message in messages:
            content = message['content'].lower()
            for keyword in keywords:
                if keyword in content:
                    topics[keyword] = topics.get(keyword, 0) + 1
        
        # Return top 3 topics
        sorted_topics = sorted(topics.items(), key=lambda x: x[1], reverse=True)
        return [topic for topic, count in sorted_topics[:3]]
    
    def _categorize_questions(self, messages: List[Dict]) -> Dict[str, int]:
        """Categorize user questions by type."""
        categories = {
            'summary': 0,
            'sentiment': 0,
            'comparison': 0,
            'specific_cluster': 0,
            'recommendation': 0,
            'other': 0
        }
        
        for message in messages:
            content = message['content'].lower()
            
            if any(word in content for word in ['summary', 'overview', 'overall']):
                categories['summary'] += 1
            elif any(word in content for word in ['sentiment', 'feeling', 'emotion', 'satisfied', 'happy', 'positive', 'negative']):
                categories['sentiment'] += 1
            elif any(word in content for word in ['compare', 'vs', 'difference', 'between']):
                categories['comparison'] += 1
            elif any(word in content for word in ['cluster', 'group', 'theme']):
                categories['specific_cluster'] += 1
            elif any(word in content for word in ['recommend', 'suggest', 'should', 'action', 'improve']):
                categories['recommendation'] += 1
            else:
                categories['other'] += 1
        
        return categories

class ChatWidget:
    """Streamlit widget for the AI chat assistant."""
    
    def __init__(self, analysis_results: Dict):
        self.assistant = AIAnalysisAssistant()
        self.analysis_results = analysis_results
    
    def render(self):
        """Render the chat widget."""
        with st.container():
            # Chat toggle
            if 'show_chat' not in st.session_state:
                st.session_state.show_chat = False
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("🤖 AI Assistant Chat", use_container_width=True, type="primary"):
                    st.session_state.show_chat = not st.session_state.show_chat
            
            # Render chat if toggled on
            if st.session_state.show_chat:
                self.assistant.render_chat_interface(self.analysis_results)
                
                # Chat controls
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button("📥 Export Chat", use_container_width=True):
                        chat_data = self.assistant.export_conversation()
                        st.download_button(
                            "Download Chat History",
                            chat_data,
                            file_name="chat_history.json",
                            mime="application/json"
                        )
                
                with col2:
                    if st.button("🧹 Clear Chat", use_container_width=True):
                        self.assistant.clear_conversation()
                        st.rerun()
                
                with col3:
                    if st.button("📊 Chat Insights", use_container_width=True):
                        insights = self.assistant.get_conversation_insights()
                        if insights:
                            st.json(insights)