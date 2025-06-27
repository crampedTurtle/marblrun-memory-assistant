import openai
from typing import List, Dict, Any, Optional
import asyncio
import time
from ..config import settings

class EmbeddingService:
    """Service for handling text embeddings using OpenAI API"""
    
    def __init__(self):
        """Initialize the embedding service with OpenAI client"""
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL
        self.embedding_cache: Dict[str, List[float]] = {}
        self.cache_ttl = 3600  # 1 hour cache TTL
    
    async def get_embedding(self, text: str, use_cache: bool = True) -> List[float]:
        """
        Get embedding for a single text string
        
        Args:
            text: The text to embed
            use_cache: Whether to use cached embeddings
            
        Returns:
            List of floats representing the embedding vector
        """
        # Check cache first
        if use_cache and text in self.embedding_cache:
            return self.embedding_cache[text]
        
        try:
            response = self.client.embeddings.create(
                model=self.model,
                input=text
            )
            embedding = response.data[0].embedding
            
            # Cache the result
            if use_cache:
                self.embedding_cache[text] = embedding
            
            return embedding
        except Exception as e:
            raise Exception(f"Failed to create embedding: {str(e)}")
    
    async def get_embeddings(self, texts: List[str], batch_size: int = 100) -> List[List[float]]:
        """
        Get embeddings for multiple text strings with batching
        
        Args:
            texts: List of texts to embed
            batch_size: Number of texts to process in each batch
            
        Returns:
            List of embedding vectors
        """
        all_embeddings = []
        
        # Process in batches to avoid rate limits
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            
            try:
                response = self.client.embeddings.create(
                    model=self.model,
                    input=batch
                )
                batch_embeddings = [data.embedding for data in response.data]
                all_embeddings.extend(batch_embeddings)
                
                # Add small delay between batches to respect rate limits
                if i + batch_size < len(texts):
                    await asyncio.sleep(0.1)
                    
            except Exception as e:
                raise Exception(f"Failed to create embeddings for batch {i//batch_size + 1}: {str(e)}")
        
        return all_embeddings
    
    async def get_embeddings_with_metadata(self, texts: List[str]) -> List[Dict[str, Any]]:
        """
        Get embeddings with additional metadata
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of dictionaries with embedding and metadata
        """
        embeddings = await self.get_embeddings(texts)
        
        results = []
        for i, (text, embedding) in enumerate(zip(texts, embeddings)):
            results.append({
                'text': text,
                'embedding': embedding,
                'model': self.model,
                'dimension': len(embedding),
                'index': i
            })
        
        return results
    
    def get_embedding_dimension(self) -> int:
        """Get the dimension of embeddings produced by the model"""
        return settings.VECTOR_SIZE
    
    def clear_cache(self):
        """Clear the embedding cache"""
        self.embedding_cache.clear()
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            'cache_size': len(self.embedding_cache),
            'cache_ttl': self.cache_ttl,
            'model': self.model,
            'dimension': self.get_embedding_dimension()
        }
    
    async def validate_embedding(self, embedding: List[float]) -> bool:
        """
        Validate that an embedding has the correct format and dimension
        
        Args:
            embedding: The embedding vector to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not isinstance(embedding, list):
            return False
        
        if len(embedding) != self.get_embedding_dimension():
            return False
        
        # Check that all values are floats
        try:
            all(isinstance(x, (int, float)) for x in embedding)
            return True
        except:
            return False 