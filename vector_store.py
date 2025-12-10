import os
import chromadb
from chromadb.utils import embedding_functions
from typing import List, Dict
import uuid
from google import genai
from google.genai import types

# Initialize Gemini Client
# Expects GOOGLE_API_KEY in environment variables
try:
    client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))
except Exception as e:
    print(f"Warning: GOOGLE_API_KEY might be missing. {e}")
    client = None

class GeminiEmbeddingFunction(chromadb.EmbeddingFunction):
    """
    Custom Embedding Function for ChromaDB using Google Gemini API.
    """
    def __call__(self, input: chromadb.Documents) -> chromadb.Embeddings:
        if not client:
            raise ValueError("Gemini Client not initialized. Check GOOGLE_API_KEY.")
        
        # Gemini expects a list of strings
        # We need to batch if the list is too large, but for resumes it's likely fine.
        # Model: text-embedding-004 is a good default.
        
        embeddings = []
        for text in input:
            response = client.models.embed_content(
                model="text-embedding-004",
                contents=text,
            )
            embeddings.append(response.embeddings[0].values)
        return embeddings

class VectorStore:
    def __init__(self):
        # Use a persistent client or ephemeral? 
        # Plan said Ephemeral for this specific use case (per request), 
        # but we might want to keep the DB connection open.
        # Check plan: "state management ... create Ephemeral Collection ... delete immediately"
        # We will use an in-memory Client for true ephemerality or just manage collections carefully.
        self.chroma_client = chromadb.EphemeralClient() 
        self.embedding_fn = GeminiEmbeddingFunction()

    def create_collection_from_chunks(self, chunks: List[str]) -> chromadb.Collection:
        collection_name = f"resume_{uuid.uuid4().hex}"
        collection = self.chroma_client.create_collection(
            name=collection_name,
            embedding_function=self.embedding_fn
        )
        
        ids = [f"id_{i}" for i in range(len(chunks))]
        collection.add(
            documents=chunks,
            ids=ids
        )
        return collection, collection_name

    def query_similar(self, collection, query_text: str, n_results: int = 3) -> List[str]:
        results = collection.query(
            query_texts=[query_text],
            n_results=n_results
        )
        return results["documents"][0] # Return list of matched chunks

    def delete_collection(self, collection_name: str):
        self.chroma_client.delete_collection(collection_name)

if __name__ == "__main__":
    # Test
    pass
