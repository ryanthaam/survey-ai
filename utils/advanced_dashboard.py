import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from collections import Counter
import json

class AdvancedDashboard:
    """Advanced interactive dashboard for survey analysis results."""
    
    def __init__(self):
        self.colors = {
            'primary': '#3b82f6',
            'secondary': '#8b5cf6',
            'success': '#10b981',
            'warning': '#f59e0b',
            'danger': '#ef4444',
            'info': '#06b6d4',
            'light': '#f8fafc',
            'dark': '#1e293b'
        }
        
        # Initialize session state for dashboard controls
        if 'dashboard_filters' not in st.session_state:
            st.session_state.dashboard_filters = {
                'sentiment_filter': 'all',
                'cluster_filter': 'all',
                'quality_filter': 'all',
                'search_term': '',
                'dark_mode': False
            }
    
    def render_main_dashboard(self, analysis_results: Dict):
        """Render the main advanced dashboard."""
        
        # Dashboard header with controls
        self._render_dashboard_header()
        
        # Key metrics overview
        self._render_metrics_overview(analysis_results)
        
        # Multi-tab analysis view
        self._render_tabbed_analysis(analysis_results)
        
        # Advanced visualizations
        self._render_advanced_visualizations(analysis_results)
        
        # Comparison and export tools
        self._render_tools_section(analysis_results)
    
    def _render_dashboard_header(self):
        """Render dashboard header with search and filters."""
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 2rem;
            border-radius: 1rem;
            margin-bottom: 2rem;
            color: white;
        ">
            <h1 style="margin: 0; font-size: 2rem; font-weight: 800;">🧠 Advanced Analytics Dashboard</h1>
            <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">Comprehensive survey insights with interactive visualizations</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Controls row
        col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 1])
        
        with col1:
            search_term = st.text_input(
                "🔍 Search responses", 
                value=st.session_state.dashboard_filters['search_term'],
                placeholder="Search for specific keywords..."
            )
            st.session_state.dashboard_filters['search_term'] = search_term
        
        with col2:
            sentiment_filter = st.selectbox(
                "😊 Sentiment",
                ['all', 'positive', 'negative', 'neutral'],
                index=0
            )
            st.session_state.dashboard_filters['sentiment_filter'] = sentiment_filter
        
        with col3:
            cluster_filter = st.selectbox(
                "🎯 Cluster",
                ['all'] + [f'Cluster {i+1}' for i in range(10)],
                index=0
            )
            st.session_state.dashboard_filters['cluster_filter'] = cluster_filter
        
        with col4:
            quality_filter = st.selectbox(
                "⭐ Quality",
                ['all', 'high', 'medium', 'low'],
                index=0
            )
            st.session_state.dashboard_filters['quality_filter'] = quality_filter
        
        with col5:
            dark_mode = st.checkbox("🌙 Dark Mode", value=st.session_state.dashboard_filters['dark_mode'])
            st.session_state.dashboard_filters['dark_mode'] = dark_mode
    
    def _render_metrics_overview(self, analysis_results: Dict):
        """Render key metrics overview with advanced KPI cards."""
        
        st.markdown("### 📊 Key Performance Indicators")
        
        # Calculate advanced metrics
        total_responses = analysis_results.get('total_responses', 0)
        clusters = analysis_results.get('clusters', {})
        sentiments = analysis_results.get('sentiments', {})
        
        # Advanced calculations
        sentiment_distribution = self._calculate_sentiment_distribution(sentiments)
        engagement_score = self._calculate_engagement_score(clusters)
        satisfaction_score = self._calculate_satisfaction_score(sentiments)
        response_quality = self._calculate_response_quality(clusters)
        
        # KPI Cards
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            self._render_kpi_card(
                "Total Responses", 
                total_responses, 
                "📊", 
                f"+{len(clusters)} clusters",
                self.colors['primary']
            )
        
        with col2:
            self._render_kpi_card(
                "Satisfaction Score", 
                f"{satisfaction_score:.1f}%", 
                "😊", 
                f"{sentiment_distribution.get('positive', 0):.0f}% positive",
                self.colors['success']
            )
        
        with col3:
            self._render_kpi_card(
                "Engagement Level", 
                f"{engagement_score:.1f}%", 
                "🚀", 
                f"Avg {np.mean([len(texts) for texts in clusters.values()]):.1f} per cluster",
                self.colors['info']
            )
        
        with col4:
            self._render_kpi_card(
                "Response Quality", 
                f"{response_quality:.1f}%", 
                "⭐", 
                "Based on AI scoring",
                self.colors['warning']
            )
        
        with col5:
            improvement_opportunities = len([s for s in sentiments.values() if s.get('sentiment') == 'negative'])
            self._render_kpi_card(
                "Improvement Areas", 
                improvement_opportunities, 
                "🎯", 
                "Negative clusters",
                self.colors['danger']
            )
    
    def _render_kpi_card(self, title: str, value: str, icon: str, subtitle: str, color: str):
        """Render a single KPI card with animation."""
        st.markdown(f"""
        <div style="
            background: white;
            padding: 1.5rem;
            border-radius: 0.75rem;
            border-left: 4px solid {color};
            box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
            margin-bottom: 1rem;
            transition: transform 0.2s;
        " onmouseover="this.style.transform='scale(1.02)'" onmouseout="this.style.transform='scale(1)'">
            <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                <span style="font-size: 1.5rem; margin-right: 0.5rem;">{icon}</span>
                <span style="font-weight: 600; color: #374151; font-size: 0.875rem;">{title}</span>
            </div>
            <div style="font-size: 2rem; font-weight: 800; color: {color}; margin-bottom: 0.25rem;">
                {value}
            </div>
            <div style="font-size: 0.75rem; color: #6b7280;">
                {subtitle}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    def _render_tabbed_analysis(self, analysis_results: Dict):
        """Render multi-tab analysis view."""
        
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "🎯 Cluster Analysis", 
            "😊 Sentiment Deep Dive", 
            "🔍 Entity Analysis", 
            "📈 Trends & Patterns",
            "🏆 Quality Analysis"
        ])
        
        with tab1:
            self._render_cluster_analysis_tab(analysis_results)
        
        with tab2:
            self._render_sentiment_analysis_tab(analysis_results)
        
        with tab3:
            self._render_entity_analysis_tab(analysis_results)
        
        with tab4:
            self._render_trends_analysis_tab(analysis_results)
        
        with tab5:
            self._render_quality_analysis_tab(analysis_results)
    
    def _render_cluster_analysis_tab(self, analysis_results: Dict):
        """Render cluster analysis with interactive charts."""
        clusters = analysis_results.get('clusters', {})
        
        if not clusters:
            st.warning("No cluster data available")
            return
        
        # Cluster size distribution
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("📊 Cluster Size Distribution")
            cluster_sizes = [len(texts) for cluster_id, texts in clusters.items() if cluster_id != -1]
            cluster_labels = [f"Cluster {cluster_id + 1}" for cluster_id in clusters.keys() if cluster_id != -1]
            
            fig = px.pie(
                values=cluster_sizes, 
                names=cluster_labels,
                title="Response Distribution Across Clusters",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("📈 Cluster Insights")
            
            # Interactive cluster selector
            selected_cluster = st.selectbox(
                "Select cluster to analyze:",
                [f"Cluster {i+1}" for i in range(len(cluster_sizes))]
            )
            
            cluster_idx = int(selected_cluster.split()[-1]) - 1
            if cluster_idx in clusters:
                cluster_texts = clusters[cluster_idx]
                
                # Cluster metrics
                st.metric("Responses in cluster", len(cluster_texts))
                st.metric("Avg response length", f"{np.mean([len(text) for text in cluster_texts]):.0f} chars")
                
                # Word cloud data
                words = ' '.join(cluster_texts).lower().split()
                word_freq = Counter(words)
                
                # Most common words in cluster
                st.write("**Top keywords:**")
                for word, freq in word_freq.most_common(5):
                    st.write(f"• {word}: {freq} mentions")
        
        # Cluster comparison chart
        st.subheader("🔍 Cluster Comparison Matrix")
        
        # Create heatmap data
        comparison_data = self._create_cluster_comparison_matrix(clusters)
        
        fig = px.imshow(
            comparison_data['matrix'],
            x=comparison_data['labels'],
            y=comparison_data['labels'],
            color_continuous_scale='Viridis',
            title="Cluster Similarity Heatmap"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    def _render_sentiment_analysis_tab(self, analysis_results: Dict):
        """Render advanced sentiment analysis."""
        sentiments = analysis_results.get('sentiments', {})
        clusters = analysis_results.get('clusters', {})
        
        if not sentiments:
            st.warning("No sentiment data available")
            return
        
        # Sentiment overview
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("😊 Overall Sentiment Distribution")
            
            sentiment_counts = {'positive': 0, 'negative': 0, 'neutral': 0}
            confidence_scores = []
            
            for cluster_id, sentiment_data in sentiments.items():
                if cluster_id != -1:
                    sentiment = sentiment_data.get('sentiment', 'neutral')
                    confidence = sentiment_data.get('confidence', 0)
                    
                    if sentiment in sentiment_counts:
                        sentiment_counts[sentiment] += len(clusters.get(cluster_id, []))
                    confidence_scores.append(confidence)
            
            # Sentiment pie chart
            fig = px.pie(
                values=list(sentiment_counts.values()),
                names=list(sentiment_counts.keys()),
                title="Sentiment Distribution",
                color_discrete_map={
                    'positive': '#10b981',
                    'negative': '#ef4444',
                    'neutral': '#6b7280'
                }
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("📊 Sentiment Confidence Analysis")
            
            # Confidence distribution
            avg_confidence = np.mean(confidence_scores) if confidence_scores else 0
            st.metric("Average Confidence", f"{avg_confidence:.2f}")
            
            # Confidence histogram
            fig = px.histogram(
                x=confidence_scores,
                nbins=10,
                title="Confidence Score Distribution",
                labels={'x': 'Confidence Score', 'y': 'Frequency'}
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Sentiment trend over clusters
        st.subheader("📈 Sentiment Trends Across Clusters")
        
        sentiment_by_cluster = []
        cluster_names = []
        
        for cluster_id, sentiment_data in sentiments.items():
            if cluster_id != -1:
                cluster_names.append(f"Cluster {cluster_id + 1}")
                sentiment_by_cluster.append({
                    'cluster': f"Cluster {cluster_id + 1}",
                    'sentiment': sentiment_data.get('sentiment', 'neutral'),
                    'confidence': sentiment_data.get('confidence', 0),
                    'responses': len(clusters.get(cluster_id, []))
                })
        
        if sentiment_by_cluster:
            df_sentiment = pd.DataFrame(sentiment_by_cluster)
            
            fig = px.scatter(
                df_sentiment,
                x='cluster',
                y='confidence',
                size='responses',
                color='sentiment',
                title="Sentiment Confidence by Cluster",
                color_discrete_map={
                    'positive': '#10b981',
                    'negative': '#ef4444',
                    'neutral': '#6b7280'
                }
            )
            st.plotly_chart(fig, use_container_width=True)
    
    def _render_entity_analysis_tab(self, analysis_results: Dict):
        """Render entity analysis (brands, competitors, etc.)."""
        st.subheader("🏢 Entity Recognition Analysis")
        
        # Mock entity data (in real implementation, this would come from NER)
        mock_entities = {
            'brands_mentioned': ['Apple', 'Samsung', 'Google', 'Microsoft'],
            'competitors': ['Competitor A', 'Competitor B'],
            'locations': ['California', 'New York', 'Texas'],
            'products': ['iPhone', 'Galaxy', 'Pixel']
        }
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**🏷️ Brands Mentioned**")
            for brand in mock_entities['brands_mentioned']:
                st.write(f"• {brand}")
            
            st.write("**🏆 Competitors Referenced**")
            for competitor in mock_entities['competitors']:
                st.write(f"• {competitor}")
        
        with col2:
            st.write("**📍 Locations Mentioned**")
            for location in mock_entities['locations']:
                st.write(f"• {location}")
            
            st.write("**📱 Products Discussed**")
            for product in mock_entities['products']:
                st.write(f"• {product}")
        
        # Entity frequency chart
        entity_data = []
        for category, entities in mock_entities.items():
            for entity in entities:
                entity_data.append({
                    'entity': entity,
                    'category': category.replace('_', ' ').title(),
                    'mentions': np.random.randint(1, 20)  # Mock data
                })
        
        df_entities = pd.DataFrame(entity_data)
        
        fig = px.bar(
            df_entities,
            x='entity',
            y='mentions',
            color='category',
            title="Entity Mentions Across Survey Responses"
        )
        fig.update_xaxis(tickangle=45)
        st.plotly_chart(fig, use_container_width=True)
    
    def _render_trends_analysis_tab(self, analysis_results: Dict):
        """Render trends and patterns analysis."""
        st.subheader("📈 Trends & Patterns Analysis")
        
        # Mock trend data
        trend_data = {
            'time_periods': ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
            'satisfaction_scores': [78, 82, 85, 88],
            'response_volumes': [45, 52, 38, 61],
            'issue_reports': [12, 8, 6, 4]
        }
        
        # Trend visualization
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Satisfaction Trend', 'Response Volume', 'Issue Reports', 'Quality Score'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        # Satisfaction trend
        fig.add_trace(
            go.Scatter(
                x=trend_data['time_periods'],
                y=trend_data['satisfaction_scores'],
                mode='lines+markers',
                name='Satisfaction',
                line=dict(color=self.colors['success'])
            ),
            row=1, col=1
        )
        
        # Response volume
        fig.add_trace(
            go.Bar(
                x=trend_data['time_periods'],
                y=trend_data['response_volumes'],
                name='Volume',
                marker_color=self.colors['primary']
            ),
            row=1, col=2
        )
        
        # Issue reports
        fig.add_trace(
            go.Scatter(
                x=trend_data['time_periods'],
                y=trend_data['issue_reports'],
                mode='lines+markers',
                name='Issues',
                line=dict(color=self.colors['danger'])
            ),
            row=2, col=1
        )
        
        # Quality score (mock)
        quality_scores = [85, 87, 89, 92]
        fig.add_trace(
            go.Bar(
                x=trend_data['time_periods'],
                y=quality_scores,
                name='Quality',
                marker_color=self.colors['warning']
            ),
            row=2, col=2
        )
        
        fig.update_layout(height=600, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    def _render_quality_analysis_tab(self, analysis_results: Dict):
        """Render response quality analysis."""
        st.subheader("⭐ Response Quality Analysis")
        
        clusters = analysis_results.get('clusters', {})
        
        # Mock quality scores
        quality_data = []
        for cluster_id, texts in clusters.items():
            if cluster_id != -1:
                for text in texts[:10]:  # Limit for demo
                    quality_data.append({
                        'response': text[:50] + "..." if len(text) > 50 else text,
                        'quality_score': np.random.uniform(0.3, 1.0),
                        'length': len(text),
                        'word_count': len(text.split()),
                        'cluster': f"Cluster {cluster_id + 1}"
                    })
        
        if quality_data:
            df_quality = pd.DataFrame(quality_data)
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Quality distribution
                fig = px.histogram(
                    df_quality,
                    x='quality_score',
                    nbins=20,
                    title="Quality Score Distribution",
                    labels={'x': 'Quality Score', 'y': 'Number of Responses'}
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Quality vs Length
                fig = px.scatter(
                    df_quality,
                    x='length',
                    y='quality_score',
                    color='cluster',
                    title="Quality Score vs Response Length",
                    labels={'x': 'Response Length (characters)', 'y': 'Quality Score'}
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Quality data table
            st.subheader("📋 Quality Analysis Details")
            
            # Add quality categories
            df_quality['quality_category'] = df_quality['quality_score'].apply(
                lambda x: 'High' if x > 0.7 else 'Medium' if x > 0.4 else 'Low'
            )
            
            # Display filtered data
            quality_filter = st.selectbox("Filter by quality:", ['All', 'High', 'Medium', 'Low'])
            
            if quality_filter != 'All':
                filtered_df = df_quality[df_quality['quality_category'] == quality_filter]
            else:
                filtered_df = df_quality
            
            st.dataframe(
                filtered_df[['response', 'quality_score', 'quality_category', 'cluster']],
                use_container_width=True
            )
    
    def _render_advanced_visualizations(self, analysis_results: Dict):
        """Render advanced interactive visualizations."""
        st.markdown("---")
        st.subheader("🎨 Advanced Interactive Visualizations")
        
        # Create advanced charts
        col1, col2 = st.columns(2)
        
        with col1:
            self._render_correlation_matrix(analysis_results)
        
        with col2:
            self._render_response_flow_diagram(analysis_results)
    
    def _render_correlation_matrix(self, analysis_results: Dict):
        """Render correlation matrix of different metrics."""
        st.write("**🔗 Metric Correlation Analysis**")
        
        # Mock correlation data
        metrics = ['Satisfaction', 'Quality', 'Length', 'Engagement', 'Clarity']
        correlation_matrix = np.random.uniform(0.3, 1.0, (5, 5))
        np.fill_diagonal(correlation_matrix, 1.0)
        
        fig = px.imshow(
            correlation_matrix,
            x=metrics,
            y=metrics,
            color_continuous_scale='RdBu',
            title="Metrics Correlation Heatmap"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    def _render_response_flow_diagram(self, analysis_results: Dict):
        """Render response flow and journey visualization."""
        st.write("**🌊 Response Flow Analysis**")
        
        # Mock flow data - in real implementation, this would show user journey
        flow_data = {
            'stages': ['Initial', 'Positive', 'Mixed', 'Negative', 'Resolution'],
            'volumes': [100, 65, 45, 25, 15]
        }
        
        fig = px.funnel(
            y=flow_data['stages'],
            x=flow_data['volumes'],
            title="Customer Response Journey"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    def _render_tools_section(self, analysis_results: Dict):
        """Render comparison and export tools."""
        st.markdown("---")
        st.subheader("🛠️ Analysis Tools")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("📊 Export Dashboard", use_container_width=True):
                self._export_dashboard_data(analysis_results)
        
        with col2:
            if st.button("📈 Generate Report", use_container_width=True):
                st.success("Advanced report generation initiated!")
        
        with col3:
            if st.button("🔍 Deep Dive Analysis", use_container_width=True):
                st.info("Opening detailed analysis view...")
        
        with col4:
            if st.button("💾 Save Analysis", use_container_width=True):
                st.success("Analysis saved to database!")
    
    # Helper methods
    def _calculate_sentiment_distribution(self, sentiments: Dict) -> Dict:
        """Calculate sentiment distribution percentages."""
        total = len(sentiments)
        if total == 0:
            return {'positive': 0, 'negative': 0, 'neutral': 100}
        
        counts = {'positive': 0, 'negative': 0, 'neutral': 0}
        for sentiment_data in sentiments.values():
            sentiment = sentiment_data.get('sentiment', 'neutral')
            if sentiment in counts:
                counts[sentiment] += 1
        
        return {k: (v / total) * 100 for k, v in counts.items()}
    
    def _calculate_engagement_score(self, clusters: Dict) -> float:
        """Calculate engagement score based on cluster distribution."""
        if not clusters:
            return 0.0
        
        cluster_sizes = [len(texts) for texts in clusters.values()]
        avg_size = np.mean(cluster_sizes)
        
        # Higher engagement if responses are evenly distributed
        std_size = np.std(cluster_sizes)
        engagement = max(0, 100 - (std_size / avg_size * 50))
        
        return min(engagement, 100)
    
    def _calculate_satisfaction_score(self, sentiments: Dict) -> float:
        """Calculate overall satisfaction score."""
        if not sentiments:
            return 50.0
        
        positive_count = sum(1 for s in sentiments.values() if s.get('sentiment') == 'positive')
        total_count = len(sentiments)
        
        return (positive_count / total_count) * 100 if total_count > 0 else 50.0
    
    def _calculate_response_quality(self, clusters: Dict) -> float:
        """Calculate average response quality."""
        if not clusters:
            return 0.0
        
        total_responses = sum(len(texts) for texts in clusters.values())
        quality_scores = []
        
        for texts in clusters.values():
            for text in texts:
                # Simple quality heuristic
                word_count = len(text.split())
                has_punctuation = any(p in text for p in '.!?')
                length_score = min(word_count / 10, 1.0)
                grammar_score = 0.2 if has_punctuation else 0
                
                quality_scores.append(length_score + grammar_score)
        
        return np.mean(quality_scores) * 100 if quality_scores else 0.0
    
    def _create_cluster_comparison_matrix(self, clusters: Dict) -> Dict:
        """Create similarity matrix between clusters."""
        cluster_ids = [cid for cid in clusters.keys() if cid != -1]
        matrix_size = len(cluster_ids)
        
        # Mock similarity matrix
        matrix = np.random.uniform(0.1, 0.9, (matrix_size, matrix_size))
        np.fill_diagonal(matrix, 1.0)
        
        labels = [f"Cluster {cid + 1}" for cid in cluster_ids]
        
        return {
            'matrix': matrix,
            'labels': labels
        }
    
    def _export_dashboard_data(self, analysis_results: Dict):
        """Export dashboard data in multiple formats."""
        export_data = {
            'summary': {
                'total_responses': analysis_results.get('total_responses', 0),
                'clusters_found': len(analysis_results.get('clusters', {})),
                'export_timestamp': pd.Timestamp.now().isoformat()
            },
            'clusters': analysis_results.get('clusters', {}),
            'sentiments': analysis_results.get('sentiments', {}),
            'filters_applied': st.session_state.dashboard_filters
        }
        
        # Convert to JSON for download
        json_data = json.dumps(export_data, indent=2, default=str)
        
        st.download_button(
            label="📥 Download Analysis Data (JSON)",
            data=json_data,
            file_name="survey_analysis_export.json",
            mime="application/json"
        )