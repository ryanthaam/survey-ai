import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import umap
import hdbscan
from typing import List, Dict, Tuple
from .embeddings import get_embeddings

class ClusteringService:
    def __init__(self, method: str = "umap_hdbscan"):
        self.method = method
    
    def find_optimal_clusters(self, embeddings: np.ndarray, max_clusters: int = 10) -> int:
        """Find optimal number of clusters using silhouette score."""
        if len(embeddings) < 2:
            return 1
            
        best_score = -1
        best_k = 2
        
        for k in range(2, min(max_clusters + 1, len(embeddings))):
            kmeans = KMeans(n_clusters=k, random_state=42)
            labels = kmeans.fit_predict(embeddings)
            score = silhouette_score(embeddings, labels)
            
            if score > best_score:
                best_score = score
                best_k = k
                
        return best_k
    
    def kmeans_clustering(self, embeddings: np.ndarray, n_clusters: int = None) -> np.ndarray:
        """Perform K-means clustering on embeddings."""
        if n_clusters is None:
            n_clusters = self.find_optimal_clusters(embeddings)
        
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        labels = kmeans.fit_predict(embeddings)
        return labels
    
    def umap_hdbscan_clustering(self, embeddings: np.ndarray) -> np.ndarray:
        """Perform UMAP + HDBSCAN clustering on embeddings."""
        # Reduce dimensionality with UMAP
        reducer = umap.UMAP(n_components=5, random_state=42)
        reduced_embeddings = reducer.fit_transform(embeddings)
        
        # Cluster with HDBSCAN
        clusterer = hdbscan.HDBSCAN(min_cluster_size=2, metric='euclidean')
        labels = clusterer.fit_predict(reduced_embeddings)
        
        return labels
    
    def cluster_texts(self, texts: List[str]) -> Tuple[np.ndarray, Dict[int, List[str]]]:
        """Cluster texts and return labels and grouped texts."""
        embeddings = get_embeddings(texts)
        
        if self.method == "kmeans":
            labels = self.kmeans_clustering(embeddings)
        elif self.method == "umap_hdbscan":
            labels = self.umap_hdbscan_clustering(embeddings)
        else:
            raise ValueError(f"Unknown clustering method: {self.method}")
        
        # Group texts by cluster
        clusters = {}
        for text, label in zip(texts, labels):
            if label not in clusters:
                clusters[label] = []
            clusters[label].append(text)
        
        return labels, clusters

# For backward compatibility
def embed_and_cluster(embeddings: np.ndarray) -> np.ndarray:
    """Cluster embeddings using UMAP + HDBSCAN."""
    service = ClusteringService("umap_hdbscan")
    # Reduce dimensionality with UMAP
    reducer = umap.UMAP(n_components=5, random_state=42)
    reduced_embeddings = reducer.fit_transform(embeddings)
    
    # Cluster with HDBSCAN
    clusterer = hdbscan.HDBSCAN(min_cluster_size=2, metric='euclidean')
    labels = clusterer.fit_predict(reduced_embeddings)
    
    return labels