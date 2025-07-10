import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from io import StringIO
import tempfile
import os
from typing import Dict, List, Tuple

# Import utility modules
from utils.clustering import ClusteringService
from utils.summarizer import SummarizerService
from utils.pdf_generator import PDFReportGenerator
from utils.supabase_client import SupabaseService
from utils.csv_analyzer import CSVAnalyzer
from utils.file_processor import FileProcessor
from utils.survey_enhancer import SurveyDataEnhancer
from utils.enhanced_extractor import EnhancedSurveyExtractor

# Configure Streamlit page
st.set_page_config(
    page_title="SurveyGPT-AI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Enhanced CSS with React-style design
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, system-ui, sans-serif;
    }
    
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}
    
    /* Main app background */
    .stApp {
        background: linear-gradient(135deg, #f8fafc 0%, #e0f2fe 50%, #e8f5e8 100%);
    }
    
    /* Navigation Bar */
    .nav-bar {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        z-index: 1000;
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        border-bottom: 1px solid rgba(226, 232, 240, 0.8);
        padding: 1rem 0;
    }
    
    .nav-content {
        max-width: 1200px;
        margin: 0 auto;
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0 2rem;
    }
    
    .logo {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        font-size: 1.25rem;
        font-weight: 700;
        color: #1e293b;
        text-decoration: none;
    }
    
    .logo-icon {
        width: 2.5rem;
        height: 2.5rem;
        background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
        border-radius: 0.75rem;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 1.25rem;
    }
    
    .gradient-text {
        background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    /* Cluster Cards */
    .cluster-card {
        background: white;
        border-radius: 0.75rem;
        padding: 1.5rem;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
        border: 1px solid #f1f5f9;
        margin-bottom: 1rem;
    }
    
    .cluster-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 1rem;
    }
    
    .cluster-title {
        font-size: 1.125rem;
        font-weight: 600;
        color: #1e293b;
    }
    
    .badges {
        display: flex;
        gap: 0.5rem;
        flex-wrap: wrap;
    }
    
    .badge {
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 500;
    }
    
    .badge-positive {
        background: #dcfce7;
        color: #166534;
    }
    
    .badge-negative {
        background: #fecaca;
        color: #991b1b;
    }
    
    .badge-neutral {
        background: #f3f4f6;
        color: #374151;
    }
    
    .badge-outline {
        background: white;
        color: #64748b;
        border: 1px solid #e2e8f0;
    }
    
    /* Responsive */
    @media (max-width: 768px) {
        .nav-content {
            padding: 0 1rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# Initialize services
@st.cache_resource
def get_clustering_service():
    return ClusteringService()

@st.cache_resource
def get_summarizer_service():
    return SummarizerService()

@st.cache_resource
def get_pdf_generator():
    return PDFReportGenerator()

@st.cache_resource
def get_supabase_service():
    try:
        return SupabaseService()
    except Exception as e:
        st.error(f"Failed to initialize Supabase: {str(e)}")
        return None

@st.cache_resource
def get_csv_analyzer():
    return CSVAnalyzer()

@st.cache_resource
def get_file_processor():
    return FileProcessor()

@st.cache_resource
def get_survey_enhancer():
    return SurveyDataEnhancer()

@st.cache_resource
def get_enhanced_extractor():
    return EnhancedSurveyExtractor()

def render_navigation():
    """Render the navigation bar"""
    st.markdown("""
    <div class="nav-bar">
        <div class="nav-content">
            <div class="logo">
                <div class="logo-icon">🧠</div>
                <span class="gradient-text">SurveyGPT-AI</span>
            </div>
            <div style="display: flex; align-items: center; gap: 2rem;">
                <span style="color: #64748b;">AI-Powered Survey Analysis</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_hero_section():
    """Render the hero section using Streamlit components"""
    
    # Add spacing for navigation
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    
    # Hero badge
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <span style="
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            background: linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%);
            border: 1px solid rgba(59, 130, 246, 0.2);
            border-radius: 2rem;
            padding: 0.5rem 1rem;
            font-size: 0.875rem;
            font-weight: 500;
            color: #3b82f6;
        ">
            ✨ AI-Powered Survey Analysis
        </span>
    </div>
    """, unsafe_allow_html=True)
    
    # Hero title
    st.markdown("""
    <div style="text-align: center; margin-bottom: 1.5rem;">
        <h1 style="
            font-size: clamp(2.5rem, 5vw, 4.5rem);
            font-weight: 800;
            line-height: 1.1;
            color: #1e293b;
            margin: 0;
        ">
            Transform<br>
            <span style="
                background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            ">Survey Responses</span><br>
            Into Actionable<br>
            <span style="
                background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            ">Insights</span>
        </h1>
    </div>
    """, unsafe_allow_html=True)
    
    # Hero subtitle
    st.markdown("""
    <div style="text-align: center; margin-bottom: 3rem;">
        <p style="
            font-size: 1.25rem;
            color: #64748b;
            max-width: 48rem;
            margin: 0 auto;
            line-height: 1.6;
        ">
            Upload your CSV files and let our AI instantly cluster feedback, 
            analyze sentiment, and generate comprehensive insights with GPT-4.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # CTA buttons
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("🚀 Start Analyzing For Free", type="primary", use_container_width=True):
                st.session_state.scroll_to_upload = True
        with col_b:
            if st.button("▶️ Watch Demo", use_container_width=True):
                st.info("Demo video coming soon!")

def render_features_section():
    """Render the features section with cards."""
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    st.markdown("""
    <div style="text-align: center; margin-bottom: 3rem;">
        <h2 style="
            font-size: 2.5rem;
            font-weight: 700;
            color: #1e293b;
            margin-bottom: 1rem;
        ">How It Works</h2>
        <p style="
            font-size: 1.125rem;
            color: #64748b;
            max-width: 36rem;
            margin: 0 auto;
            line-height: 1.6;
        ">Simple, powerful AI analysis in three steps</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style="
            background: #f8fafc;
            border-radius: 1rem;
            padding: 2rem;
            border: 1px solid #f1f5f9;
            height: 100%;
            text-align: center;
        ">
            <div style="
                width: 3.5rem;
                height: 3.5rem;
                border-radius: 0.75rem;
                background: linear-gradient(135deg, #3b82f6 0%, #06b6d4 100%);
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 1.5rem;
                margin: 0 auto 1.5rem;
            ">📁</div>
            <h3 style="
                font-size: 1.25rem;
                font-weight: 600;
                color: #1e293b;
                margin-bottom: 0.75rem;
            ">Upload CSV</h3>
            <p style="
                color: #64748b;
                line-height: 1.6;
                margin: 0;
            ">Upload your survey data from any platform</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown("""
        <div style="
            background: #f8fafc;
            border-radius: 1rem;
            padding: 2rem;
            border: 1px solid #f1f5f9;
            height: 100%;
            text-align: center;
        ">
            <div style="
                width: 3.5rem;
                height: 3.5rem;
                border-radius: 0.75rem;
                background: linear-gradient(135deg, #8b5cf6 0%, #ec4899 100%);
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 1.5rem;
                margin: 0 auto 1.5rem;
            ">🧠</div>
            <h3 style="
                font-size: 1.25rem;
                font-weight: 600;
                color: #1e293b;
                margin-bottom: 0.75rem;
            ">AI Clustering</h3>
            <p style="
                color: #64748b;
                line-height: 1.6;
                margin: 0;
            ">Automatically group similar responses</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown("""
        <div style="
            background: #f8fafc;
            border-radius: 1rem;
            padding: 2rem;
            border: 1px solid #f1f5f9;
            height: 100%;
            text-align: center;
        ">
            <div style="
                width: 3.5rem;
                height: 3.5rem;
                border-radius: 0.75rem;
                background: linear-gradient(135deg, #10b981 0%, #34d399 100%);
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 1.5rem;
                margin: 0 auto 1.5rem;
            ">📊</div>
            <h3 style="
                font-size: 1.25rem;
                font-weight: 600;
                color: #1e293b;
                margin-bottom: 0.75rem;
            ">Get Insights</h3>
            <p style="
                color: #64748b;
                line-height: 1.6;
                margin: 0;
            ">Receive GPT-4 powered summaries and analysis</p>
        </div>
        """, unsafe_allow_html=True)

def main():
    # Initialize session state
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = None
    if 'page' not in st.session_state:
        st.session_state.page = 'home'

    # Render navigation
    render_navigation()

    # Handle authentication in sidebar
    with st.sidebar:
        st.markdown("### 🔐 Authentication")
        
        if not st.session_state.authenticated:
            auth_mode = st.radio("Mode", ["Sign In", "Sign Up"])
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            
            if st.button(f"{auth_mode}"):
                supabase_service = get_supabase_service()
                if supabase_service:
                    if auth_mode == "Sign In":
                        result = supabase_service.authenticate_user(email, password)
                    else:
                        result = supabase_service.register_user(email, password)
                    
                    if result["success"]:
                        st.session_state.authenticated = True
                        st.session_state.user_id = result["user"].id
                        st.success(f"{auth_mode} successful!")
                        st.rerun()
                    else:
                        st.error(result["error"])
                else:
                    st.warning("Authentication service unavailable. You can still use the app without saving results.")
                    st.session_state.authenticated = True
                    st.session_state.user_id = "demo_user"
        else:
            st.success("✅ Authenticated")
            if st.button("Sign Out"):
                supabase_service = get_supabase_service()
                if supabase_service:
                    supabase_service.sign_out()
                st.session_state.authenticated = False
                st.session_state.user_id = None
                st.rerun()

    # Page routing
    if not st.session_state.authenticated:
        # Landing page
        render_hero_section()
        render_features_section()
        
        # Upload section for demo
        st.markdown('<div id="file-upload"></div>', unsafe_allow_html=True)
        st.markdown("---")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("""
            <div style="
                background: white;
                border-radius: 1rem;
                padding: 2rem;
                box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
                border: 1px solid #f1f5f9;
                text-align: center;
            ">
                <h3 style="
                    font-size: 1.25rem;
                    font-weight: 600;
                    color: #1e293b;
                    margin-bottom: 0.5rem;
                ">🚀 Try It Now</h3>
                <p style="
                    color: #64748b;
                    font-size: 0.875rem;
                    margin: 0;
                ">Sign in above to start analyzing your survey data</p>
            </div>
            """, unsafe_allow_html=True)
    
    else:
        # Authenticated user - show upload interface
        st.markdown("<br><br><br>", unsafe_allow_html=True)  # Spacer for nav
        
        # File upload section
        st.markdown("### 📁 Upload Your Survey Data")
        st.markdown("""Upload survey data in **any format**! SurveyGPT-AI intelligently processes multiple file types.
        
**🚀 Supported Formats:**
- **📄 CSV**: Google Forms, Typeform, any CSV export
- **📈 Excel**: .xlsx, .xls files with survey data
- **📄 PDF**: Extract text and tables from survey reports
- **📄 Word**: .docx files with survey responses
- **📝 Text**: Plain text files with responses
        
**🧠 Smart Features:**
- Automatically detects the best content for analysis
- Handles structured and unstructured data
- Intelligent preprocessing and data cleaning
- No manual formatting required!
        """)
        
        uploaded_file = st.file_uploader(
            "Choose a file", 
            type=["csv", "xlsx", "xls", "pdf", "docx", "txt"],
            help="Upload survey data in any supported format - SurveyGPT-AI will intelligently process it!"
        )
        
        if uploaded_file is not None:
            try:
                # Process the uploaded file
                file_processor = get_file_processor()
                df, text_data, file_info = file_processor.process_file(uploaded_file)
                
                # Show file processing results
                file_type = file_info.get('file_type', 'unknown')
                
                if 'error' in file_info:
                    st.error(f"❌ {file_info['error']}")
                else:
                    # Success message based on file type
                    if file_type == 'csv':
                        st.success(f"✅ CSV file processed! Found {len(df)} rows with {len(df.columns)} columns.")
                    elif file_type == 'excel':
                        st.success(f"✅ Excel file processed! Found {len(df)} rows with {len(df.columns)} columns from sheet '{file_info.get('sheet_used', 'unknown')}'.")
                        if len(file_info.get('sheet_names', [])) > 1:
                            st.info(f"📄 **Note**: File has {len(file_info['sheet_names'])} sheets. Using: {file_info['sheet_used']}")
                    elif file_type in ['pdf', 'word', 'text']:
                        st.success(f"✅ {file_type.upper()} file processed! Extracted {len(text_data)} text segments.")
                        
                        # Convert text to DataFrame for analysis
                        df = file_processor.convert_text_to_dataframe(text_data, method='auto')
                        st.info(f"🔄 **Converted to structured format**: {len(df)} rows with {len(df.columns)} columns.")
                    
                    # Show processing details
                    with st.expander(f"📊 File Processing Details ({file_type.upper()})"):
                        for key, value in file_info.items():
                            if key != 'error':
                                st.write(f"**{key.replace('_', ' ').title()}**: {value}")
                
                # Display preview
                st.markdown("#### 📊 Data Preview")
                st.dataframe(df.head(10))
                
                # Column selection
                st.markdown("#### 🎯 Select Response Column")
                response_column = st.selectbox(
                    "Choose the column containing the text responses to analyze:",
                    df.columns.tolist(),
                    help="Select the column with the open-ended text responses"
                )
                
                if response_column:
                    # Filter out empty responses
                    responses = df[response_column].dropna().astype(str).tolist()
                    responses = [r for r in responses if r.strip()]
                    
                    if len(responses) < 5:
                        st.warning("⚠️ Need at least 5 responses for meaningful analysis.")
                    else:
                        st.info(f"📝 Ready to analyze {len(responses)} responses.")
                        
                        # Analysis options
                        st.markdown("#### ⚙️ Analysis Options")
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            clustering_method = st.selectbox(
                                "Clustering Method",
                                ["K-Means", "UMAP + HDBSCAN"],
                                help="Choose the clustering algorithm"
                            )
                        
                        with col2:
                            num_clusters = st.slider(
                                "Number of Clusters (K-Means only)",
                                min_value=2,
                                max_value=min(10, len(responses)//2),
                                value=min(5, len(responses)//3),
                                help="Only applies to K-Means clustering"
                            )
                        
                        # Analyze button
                        if st.button("🚀 Start Analysis", type="primary", use_container_width=True):
                            with st.spinner("🧠 Analyzing responses..."):
                                # Initialize services
                                clustering_service = get_clustering_service()
                                summarizer_service = get_summarizer_service()
                                
                                # Set clustering method
                                if clustering_method == "K-Means":
                                    clustering_service.method = "kmeans"
                                else:
                                    clustering_service.method = "umap_hdbscan"
                                
                                # Perform clustering
                                st.info("🔄 Step 1: Clustering responses...")
                                try:
                                    labels, clusters = clustering_service.cluster_texts(responses)
                                    
                                    # Generate summaries
                                    st.info("🔄 Step 2: Generating summaries with GPT-4...")
                                    summaries = {}
                                    sentiments = {}
                                    
                                    for cluster_id, cluster_texts in clusters.items():
                                        if cluster_id != -1:  # Skip noise cluster
                                            summary = summarizer_service.summarize_cluster(cluster_texts, cluster_id)
                                            sentiment = summarizer_service.analyze_sentiment(cluster_texts)
                                            summaries[cluster_id] = summary
                                            sentiments[cluster_id] = sentiment
                                    
                                    # Store results in session state
                                    st.session_state.analysis_results = {
                                        'clusters': clusters,
                                        'summaries': summaries,
                                        'sentiments': sentiments,
                                        'total_responses': len(responses)
                                    }
                                    
                                    st.success("✅ Analysis complete!")
                                    st.rerun()
                                    
                                except Exception as e:
                                    st.error(f"❌ Error during analysis: {str(e)}")
                                
            except Exception as e:
                st.error(f"❌ Error processing file: {str(e)}")
                st.info("💡 **Troubleshooting**: Make sure your file is a valid CSV with text data.")
        
        # Enhanced auto-analysis option 
        if uploaded_file is not None:
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🤖 Smart Auto-Analyze", use_container_width=True, type="primary"):
                    st.session_state.analysis_mode = 'auto'
            with col2:
                if st.button("🚀 Maximum Extraction", use_container_width=True):
                    st.session_state.analysis_mode = 'maximum'
        
        if uploaded_file is not None and st.session_state.get('analysis_mode'):
            with st.spinner("🧠 Auto-analyzing your data..."):
                try:
                    # Multi-tier enhanced survey processing
                    csv_analyzer = get_csv_analyzer()
                    survey_enhancer = get_survey_enhancer()
                    enhanced_extractor = get_enhanced_extractor()
                    
                    st.info("🔍 **Phase 1**: Trying specialized survey analysis...")
                    survey_texts, survey_info = survey_enhancer.extract_survey_responses(df)
                    
                    if len(survey_texts) >= 10:
                        st.success(f"🎯 **Survey-Optimized Success!** Found {len(survey_texts)} responses using specialized analysis")
                        texts = survey_texts
                        analysis = {'method': 'specialized_survey', 'info': survey_info}
                    else:
                        st.info(f"🔄 **Phase 2**: Found {len(survey_texts)} responses. Trying enhanced extraction...")
                        
                        # Use enhanced extractor for more comprehensive analysis
                        enhanced_texts, enhanced_info = enhanced_extractor.extract_all_meaningful_data(df)
                        
                        if len(enhanced_texts) >= 5:
                            st.success(f"🚀 **Enhanced Extraction Success!** Found {len(enhanced_texts)} comprehensive responses")
                            
                            # Show extraction details
                            with st.expander("📊 Enhanced Extraction Details"):
                                st.write(f"**Original Survey Rows**: {enhanced_info['total_original_rows']}")
                                st.write(f"**Columns Processed**: {enhanced_info['extraction_stats']['processed_columns']}")
                                st.write(f"**Extraction Methods**: {', '.join(enhanced_info['extraction_methods'])}")
                                
                                # Show extraction breakdown
                                st.write("**Extraction Breakdown**:")
                                for method, count in enhanced_info['extraction_stats'].items():
                                    if isinstance(count, int) and count > 0:
                                        st.write(f"  - {method.replace('_', ' ').title()}: {count}")
                            
                            texts = enhanced_texts
                            analysis = {'method': 'enhanced_extraction', 'info': enhanced_info}
                        else:
                            # Final fallback to CSV analyzer
                            st.info("🔄 **Phase 3**: Trying general CSV analysis...")
                            texts, analysis = csv_analyzer.auto_detect_and_process(df)
                            
                            if len(texts) < 5:
                                st.error("❌ Could not find sufficient text data for analysis.")
                                st.info("💡 **What we found**:")
                                st.write(f"• Specialized extraction: {len(survey_texts)} responses")
                                st.write(f"• Enhanced extraction: {len(enhanced_texts)} responses")
                                st.write(f"• General analysis: {len(texts)} responses")
                                
                                # Show sample of what was found
                                all_found = survey_texts + enhanced_texts + texts
                                if all_found:
                                    with st.expander("👀 Preview of found responses"):
                                        for i, resp in enumerate(all_found[:5], 1):
                                            st.write(f"{i}. {resp[:150]}...")
                            else:
                                st.info(f"🎯 Found {len(texts)} responses using general analysis")
                    
                    if len(texts) >= 5:
                        # Proceed with automatic analysis
                        
                        # Initialize services
                        clustering_service = get_clustering_service()
                        summarizer_service = get_summarizer_service()
                        clustering_service.method = "umap_hdbscan"  # Use UMAP for auto-analysis
                        
                        # Perform clustering
                        st.info("🔄 AI clustering in progress...")
                        labels, clusters = clustering_service.cluster_texts(texts)
                        
                        # Generate summaries
                        st.info("🔄 Generating AI insights...")
                        summaries = {}
                        sentiments = {}
                        
                        for cluster_id, cluster_texts in clusters.items():
                            if cluster_id != -1:  # Skip noise cluster
                                summary = summarizer_service.summarize_cluster(cluster_texts, cluster_id)
                                sentiment = summarizer_service.analyze_sentiment(cluster_texts)
                                summaries[cluster_id] = summary
                                sentiments[cluster_id] = sentiment
                        
                        # Store results
                        st.session_state.analysis_results = {
                            'clusters': clusters,
                            'summaries': summaries,
                            'sentiments': sentiments,
                            'total_responses': len(texts),
                            'original_data_info': {
                                'auto_analysis': True,
                                'method': 'intelligent_detection',
                                'analysis_summary': analysis
                            }
                        }
                        
                        st.success("✅ Auto-analysis complete!")
                        st.rerun()
                        
                except Exception as e:
                    st.error(f"❌ Auto-analysis failed: {str(e)}")
                    st.info("💡 Try manual column selection instead.")
        
        # Display results if available
        if st.session_state.analysis_results:
            results = st.session_state.analysis_results
            
            st.markdown("---")
            st.markdown("## 📊 AI Analysis Results")
            
            # Show analysis info
            if 'original_data_info' in results:
                info = results['original_data_info']
                if info.get('auto_analysis'):
                    st.info("🤖 **Auto-Analysis**: AI automatically selected the best approach for your data")
                else:
                    st.info(f"📊 **Analysis**: Used column '{info.get('column_used', 'Unknown')}' with intelligent preprocessing")
            
            # Summary metrics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "Total Responses",
                    results['total_responses'],
                    help="Total number of survey responses analyzed"
                )
            
            with col2:
                num_clusters = len([c for c in results['clusters'].keys() if c != -1])
                st.metric(
                    "Clusters Found",
                    num_clusters,
                    help="Number of distinct themes identified"
                )
            
            with col3:
                avg_cluster_size = sum(len(texts) for cluster_id, texts in results['clusters'].items() if cluster_id != -1) / num_clusters if num_clusters > 0 else 0
                st.metric(
                    "Avg Cluster Size",
                    f"{avg_cluster_size:.1f}",
                    help="Average number of responses per cluster"
                )
            
            # Cluster details
            st.markdown("### 🎯 Cluster Analysis")
            
            for cluster_id, cluster_texts in results['clusters'].items():
                if cluster_id == -1:  # Skip noise cluster
                    continue
                    
                with st.expander(f"📂 Cluster {cluster_id + 1} ({len(cluster_texts)} responses)", expanded=True):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.markdown("**Summary:**")
                        st.write(results['summaries'].get(cluster_id, "No summary available"))
                        
                        st.markdown("**Sample Responses:**")
                        for i, text in enumerate(cluster_texts[:5], 1):
                            st.write(f"{i}. {text}")
                        
                        if len(cluster_texts) > 5:
                            st.write(f"... and {len(cluster_texts) - 5} more responses")
                    
                    with col2:
                        sentiment_data = results['sentiments'].get(cluster_id, {})
                        sentiment = sentiment_data.get('sentiment', 'neutral')
                        confidence = sentiment_data.get('confidence', 0)
                        
                        # Sentiment badge
                        if sentiment == 'positive':
                            st.success(f"😊 {sentiment.title()}")
                        elif sentiment == 'negative':
                            st.error(f"😞 {sentiment.title()}")
                        else:
                            st.info(f"😐 {sentiment.title()}")
                        
                        st.metric("Confidence", f"{confidence:.2f}")
                        st.metric("Responses", len(cluster_texts))
            
            # PDF Export
            st.markdown("### 📄 Export Results")
            
            if st.button("📥 Download PDF Report", use_container_width=True):
                try:
                    pdf_generator = get_pdf_generator()
                    pdf_path = pdf_generator.generate_report(
                        results['clusters'],
                        results['summaries'],
                        results['sentiments']
                    )
                    
                    with open(pdf_path, "rb") as pdf_file:
                        st.download_button(
                            label="📥 Download PDF Report",
                            data=pdf_file.read(),
                            file_name="survey_analysis_report.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )
                    
                    # Cleanup temp file
                    os.unlink(pdf_path)
                    
                except Exception as e:
                    st.error(f"❌ Error generating PDF: {str(e)}")
            
            # Clear results
            if st.button("🔄 Start New Analysis", use_container_width=True):
                st.session_state.analysis_results = None
                st.rerun()

if __name__ == "__main__":
    main()