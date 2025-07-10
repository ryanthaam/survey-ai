# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

SurveyGPT-AI is an intelligent survey analysis application that can process multiple file formats and automatically generate insights using AI clustering and GPT-4 summarization.

### Key Features
- **Multi-format file support**: CSV, Excel (.xlsx/.xls), PDF, Word (.docx), Text files
- **Intelligent column detection**: Automatically identifies the best text content for analysis
- **Smart preprocessing**: Filters noise and enhances data quality automatically
- **AI-powered clustering**: K-Means and UMAP+HDBSCAN algorithms
- **GPT-4 insights**: Automatic summary generation and sentiment analysis
- **PDF export**: Comprehensive report generation
- **Modern UI**: React-inspired design with professional styling

## Common Development Commands

### Installing Dependencies
```bash
pip install -r requirements.txt
```

### Running the Application

#### Streamlit Frontend (Main Application)
```bash
# Run the main Streamlit application
streamlit run app.py

# Access at: http://localhost:8501
```

#### FastAPI Backend (Optional API)
```bash
# Start the FastAPI backend server
uvicorn backend.main:app --reload

# Access at: http://localhost:8000
# API docs at: http://localhost:8000/docs
```

### Testing the API
```bash
# Test the analyze endpoint
curl -X POST "http://localhost:8000/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "responses": ["Great product!", "Needs improvement", "Love it!"],
    "clustering_method": "umap_hdbscan"
  }'
```

## Architecture Overview

SurveyGPT-AI is a comprehensive survey analysis application that transforms free-text responses into structured insights using AI clustering and summarization.

### Primary Architecture (Streamlit-based)

**Frontend Application (`app.py`):**
- Streamlit web interface with file upload, analysis, and visualization
- Handles CSV file processing from Google Forms, Typeform, etc.
- Integrated authentication via Supabase
- Real-time analysis with progress tracking
- PDF report generation and download
- Interactive dashboards with plotly visualizations

**Core Services:**
- `utils/clustering.py`: ClusteringService with K-means and UMAP+HDBSCAN
- `utils/summarizer.py`: SummarizerService with GPT-4 integration
- `utils/embeddings.py`: EmbeddingService with sentence-transformers
- `utils/pdf_generator.py`: PDFReportGenerator for comprehensive reports
- `utils/supabase_client.py`: SupabaseService for auth and data persistence

### Secondary Architecture (FastAPI-based)

**Backend API (`backend/main.py`):**
- FastAPI application with comprehensive endpoints
- `/analyze` - Main analysis endpoint with clustering and summarization
- `/embeddings` - Generate embeddings for text analysis
- `/summarize` - Text summarization service
- CORS enabled for frontend integration

### Data Flow
1. User uploads CSV file via Streamlit interface
2. System extracts responses from selected column
3. EmbeddingService generates embeddings using sentence-transformers
4. ClusteringService groups similar responses (K-means or UMAP+HDBSCAN)
5. SummarizerService generates insights and sentiment analysis via GPT-4
6. Results displayed with interactive visualizations
7. PDF reports generated via ReportLab
8. Analysis saved to Supabase for authenticated users

### Key Dependencies
- **Streamlit**: Primary frontend framework
- **FastAPI**: Secondary API framework
- **OpenAI**: GPT-4 integration for summarization
- **scikit-learn**: Machine learning utilities
- **sentence-transformers**: Text embedding generation
- **umap-learn & hdbscan**: Advanced clustering algorithms
- **plotly**: Interactive visualizations
- **pandas**: Data manipulation
- **supabase**: Authentication and database
- **reportlab**: PDF generation

### Environment Configuration
Create a `.env` file with:
```
OPENAI_API_KEY=your_openai_api_key_here
SUPABASE_URL=your_supabase_url_here
SUPABASE_KEY=your_supabase_anon_key_here
```

### Authentication & Database
- Supabase Auth for user management
- PostgreSQL database for storing analyses
- Session state management in Streamlit
- Role-based access control ready

### Current Development Status
- ✅ Complete Streamlit frontend with all PRD features
- ✅ Full clustering and embedding implementations
- ✅ GPT-4 summarization and sentiment analysis
- ✅ PDF report generation
- ✅ Supabase integration for auth and storage
- ✅ FastAPI backend with comprehensive endpoints
- ✅ Interactive visualizations and dashboards
- ⚠️ Requires environment variables setup
- ⚠️ Supabase database schema needs setup