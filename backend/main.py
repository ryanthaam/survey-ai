import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
from dotenv import load_dotenv

# Import utility modules
from utils.clustering import ClusteringService
from utils.summarizer import SummarizerService
from utils.embeddings import EmbeddingService

load_dotenv()

# FastAPI application instance
app = FastAPI(
    title="SurveyGPT-AI API",
    description="AI-powered survey analysis API",
    version="1.0.0"
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class AnalysisRequest(BaseModel):
    responses: List[str]
    clustering_method: Optional[str] = "umap_hdbscan"
    n_clusters: Optional[int] = None

class ClusterResult(BaseModel):
    cluster_id: int
    responses: List[str]
    summary: str
    sentiment: Dict[str, any]
    size: int

class AnalysisResponse(BaseModel):
    total_responses: int
    clusters: List[ClusterResult]
    clustering_method: str
    success: bool
    message: str

# Initialize services
clustering_service = ClusteringService()
summarizer_service = SummarizerService()
embedding_service = EmbeddingService()

@app.get("/")
async def root():
    return {"message": "SurveyGPT-AI API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_responses(request: AnalysisRequest):
    """Analyze survey responses using clustering and summarization."""
    
    try:
        responses = request.responses
        
        if len(responses) < 2:
            raise HTTPException(
                status_code=400,
                detail="Need at least 2 responses for clustering"
            )
        
        # Set clustering method
        clustering_service.method = request.clustering_method
        
        # Perform clustering
        labels, clusters = clustering_service.cluster_texts(responses)
        
        # Generate summaries and sentiment analysis
        cluster_results = []
        
        for cluster_id, texts in clusters.items():
            if cluster_id == -1:  # Skip noise cluster
                continue
            
            # Generate summary
            summary = summarizer_service.summarize_cluster(texts, cluster_id)
            
            # Analyze sentiment
            sentiment = summarizer_service.analyze_sentiment(texts)
            
            cluster_results.append(ClusterResult(
                cluster_id=cluster_id,
                responses=texts,
                summary=summary,
                sentiment=sentiment,
                size=len(texts)
            ))
        
        return AnalysisResponse(
            total_responses=len(responses),
            clusters=cluster_results,
            clustering_method=request.clustering_method,
            success=True,
            message=f"Analysis complete! Found {len(cluster_results)} clusters."
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )

@app.post("/embeddings")
async def generate_embeddings(texts: List[str]):
    """Generate embeddings for a list of texts."""
    
    try:
        embeddings = embedding_service.get_embeddings(texts)
        return {
            "embeddings": embeddings.tolist(),
            "count": len(embeddings),
            "dimensions": embeddings.shape[1]
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Embedding generation failed: {str(e)}"
        )

@app.post("/summarize")
async def summarize_texts(texts: List[str]):
    """Summarize a list of texts."""
    
    try:
        summary = summarizer_service.summarize_cluster(texts)
        sentiment = summarizer_service.analyze_sentiment(texts)
        
        return {
            "summary": summary,
            "sentiment": sentiment,
            "input_count": len(texts)
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Summarization failed: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
