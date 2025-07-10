import openai
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

class EmbeddingService:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
    
    def get_embeddings(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings for a list of texts using sentence transformers."""
        embeddings = self.model.encode(texts)
        return np.array(embeddings)
    
    def get_openai_embeddings(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings using OpenAI's text-embedding-ada-002 model."""
        from openai import OpenAI
        client = OpenAI()
        embeddings = []
        for text in texts:
            response = client.embeddings.create(
                model="text-embedding-ada-002",
                input=text
            )
            embeddings.append(response.data[0].embedding)
        return np.array(embeddings)

# For backward compatibility
def get_embeddings(texts: List[str]) -> np.ndarray:
    """Generate embeddings for a list of texts."""
    service = EmbeddingService()
    return service.get_embeddings(texts)