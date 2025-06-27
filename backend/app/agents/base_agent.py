import os
import json
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from openai import OpenAI
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from ..config import settings

class BaseAgent(ABC):
    def __init__(self, name: str):
        self.name = name
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.qdrant_client = QdrantClient(settings.QDRANT_URL)
        self.collection_name = f"agent_{name.lower()}"
        self._ensure_collection_exists()
        self.system_prompt = self._load_system_prompt()
    
    def _ensure_collection_exists(self):
        """Ensure Qdrant collection exists for this agent"""
        try:
            self.qdrant_client.get_collection(self.collection_name)
        except:
            self.qdrant_client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=settings.VECTOR_SIZE,
                    distance=Distance.COSINE
                )
            )
    
    def _load_system_prompt(self) -> str:
        """Load system prompt from prompts directory"""
        # Try multiple possible paths
        possible_paths = [
            f"prompts/{self.name.lower()}.txt",
            f"../prompts/{self.name.lower()}.txt",
            f"app/prompts/{self.name.lower()}.txt"
        ]
        
        for prompt_file in possible_paths:
            if os.path.exists(prompt_file):
                with open(prompt_file, 'r') as f:
                    return f.read().strip()
        
        return self._get_default_prompt()
    
    @abstractmethod
    def _get_default_prompt(self) -> str:
        """Return default system prompt for this agent"""
        pass
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text using OpenAI"""
        response = self.client.embeddings.create(
            model=settings.EMBEDDING_MODEL,
            input=text
        )
        return response.data[0].embedding
    
    def store_memory(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Store text in agent's memory (Qdrant)"""
        embedding = self.generate_embedding(text)
        point_id = f"{self.name}_{len(embedding)}"
        
        point = PointStruct(
            id=point_id,
            vector=embedding,
            payload={
                "text": text,
                "agent": self.name,
                "metadata": metadata or {}
            }
        )
        
        self.qdrant_client.upsert(
            collection_name=self.collection_name,
            points=[point]
        )
        
        return point_id
    
    def search_memory(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search agent's memory for relevant information"""
        query_embedding = self.generate_embedding(query)
        
        results = self.qdrant_client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding,
            limit=limit,
            score_threshold=settings.SIMILARITY_THRESHOLD
        )
        
        return [
            {
                "text": result.payload["text"],
                "score": result.score,
                "metadata": result.payload.get("metadata", {})
            }
            for result in results
        ]
    
    def generate_response(self, user_input: str, context: Optional[str] = None) -> str:
        """Generate response using OpenAI with agent's system prompt and memory"""
        # Search for relevant memories
        memories = self.search_memory(user_input, limit=3)
        memory_context = ""
        if memories:
            memory_context = "\n\nRelevant memories:\n" + "\n".join([
                f"- {memory['text']}" for memory in memories
            ])
        
        # Build conversation context
        conversation_context = ""
        if context:
            conversation_context = f"\n\nConversation context: {context}"
        
        # Create messages for OpenAI
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": f"{user_input}{memory_context}{conversation_context}"}
        ]
        
        # Generate response
        response = self.client.chat.completions.create(
            model=settings.AGENT_MODEL,
            messages=messages,
            max_tokens=1000,
            temperature=0.7
        )
        
        return response.choices[0].message.content
    
    def store_note(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Store a note in agent's memory"""
        return self.store_memory(content, metadata) 