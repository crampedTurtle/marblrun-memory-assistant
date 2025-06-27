from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue, Range, GeoBoundingBox
from typing import List, Dict, Any, Optional, Union
import uuid
import time
from ..config import settings

class VectorService:
    """Service for handling vector operations with Qdrant"""
    
    def __init__(self):
        """Initialize the vector service with Qdrant client"""
        self.client = QdrantClient(settings.QDRANT_URL)
        self.collection_name = settings.COLLECTION_NAME
        self.vector_size = settings.VECTOR_SIZE
        self._ensure_collection_exists()
    
    def _ensure_collection_exists(self):
        """Ensure the collection exists, create if it doesn't"""
        try:
            collections = self.client.get_collections()
            collection_names = [col.name for col in collections.collections]
            
            if self.collection_name not in collection_names:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.vector_size,
                        distance=Distance.COSINE
                    )
                )
                print(f"Created Qdrant collection: {self.collection_name}")
        except Exception as e:
            print(f"Error ensuring collection exists: {e}")
            raise
    
    async def store_vector(self, vector: List[float], metadata: Dict[str, Any]) -> str:
        """
        Store a vector with metadata in Qdrant
        
        Args:
            vector: The embedding vector
            metadata: Metadata to store with the vector
            
        Returns:
            The point ID as string
        """
        point_id = str(uuid.uuid4())
        
        point = PointStruct(
            id=point_id,
            vector=vector,
            payload=metadata
        )
        
        try:
            self.client.upsert(
                collection_name=self.collection_name,
                points=[point]
            )
            return point_id
        except Exception as e:
            raise Exception(f"Failed to store vector: {str(e)}")
    
    async def store_vectors_batch(self, vectors_with_metadata: List[Dict[str, Any]]) -> List[str]:
        """
        Store multiple vectors in batch
        
        Args:
            vectors_with_metadata: List of dicts with 'vector' and 'metadata' keys
            
        Returns:
            List of point IDs
        """
        points = []
        point_ids = []
        
        for item in vectors_with_metadata:
            point_id = str(uuid.uuid4())
            point = PointStruct(
                id=point_id,
                vector=item['vector'],
                payload=item['metadata']
            )
            points.append(point)
            point_ids.append(point_id)
        
        try:
            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )
            return point_ids
        except Exception as e:
            raise Exception(f"Failed to store vectors in batch: {str(e)}")
    
    async def search_vectors(self, query_vector: List[float], limit: int = 10, 
                           score_threshold: float = None, filter_conditions: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Search for similar vectors in Qdrant with advanced filtering
        
        Args:
            query_vector: The query embedding vector
            limit: Maximum number of results
            score_threshold: Minimum similarity score threshold
            filter_conditions: Optional filter conditions for metadata
            
        Returns:
            List of search results with scores and metadata
        """
        if score_threshold is None:
            score_threshold = settings.SIMILARITY_THRESHOLD
        
        # Build filter if conditions provided
        search_filter = None
        if filter_conditions:
            search_filter = self._build_filter(filter_conditions)
        
        try:
            search_result = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=limit,
                score_threshold=score_threshold,
                query_filter=search_filter
            )
            
            results = []
            for point in search_result:
                results.append({
                    'id': point.id,
                    'score': point.score,
                    'payload': point.payload
                })
            
            return results
        except Exception as e:
            raise Exception(f"Search failed: {str(e)}")
    
    def _build_filter(self, conditions: Dict[str, Any]) -> Filter:
        """Build Qdrant filter from conditions dictionary"""
        must_conditions = []
        
        for field, value in conditions.items():
            if isinstance(value, dict):
                # Handle range queries
                if 'gte' in value or 'lte' in value:
                    range_conditions = {}
                    if 'gte' in value:
                        range_conditions['gte'] = value['gte']
                    if 'lte' in value:
                        range_conditions['lte'] = value['lte']
                    must_conditions.append(Range(key=field, **range_conditions))
            else:
                # Handle exact match
                must_conditions.append(FieldCondition(key=field, match=MatchValue(value=value)))
        
        return Filter(must=must_conditions)
    
    async def search_by_text_similarity(self, query_text: str, limit: int = 10, 
                                      score_threshold: float = None) -> List[Dict[str, Any]]:
        """
        Search by text similarity using content field
        
        Args:
            query_text: Text to search for
            limit: Maximum number of results
            score_threshold: Minimum similarity score
            
        Returns:
            List of search results
        """
        if score_threshold is None:
            score_threshold = settings.SIMILARITY_THRESHOLD
        
        try:
            search_result = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_text,  # This will be converted to embedding by the service
                limit=limit,
                score_threshold=score_threshold,
                query_filter=Filter(
                    must=[
                        FieldCondition(key="content", match=MatchValue(text=query_text))
                    ]
                )
            )
            
            results = []
            for point in search_result:
                results.append({
                    'id': point.id,
                    'score': point.score,
                    'payload': point.payload
                })
            
            return results
        except Exception as e:
            raise Exception(f"Text similarity search failed: {str(e)}")
    
    async def get_vectors_by_ids(self, point_ids: List[str]) -> List[Dict[str, Any]]:
        """
        Retrieve vectors by their IDs
        
        Args:
            point_ids: List of point IDs to retrieve
            
        Returns:
            List of vectors with metadata
        """
        try:
            points = self.client.retrieve(
                collection_name=self.collection_name,
                ids=point_ids
            )
            
            results = []
            for point in points:
                results.append({
                    'id': point.id,
                    'vector': point.vector,
                    'payload': point.payload
                })
            
            return results
        except Exception as e:
            raise Exception(f"Failed to retrieve vectors: {str(e)}")
    
    async def update_vector_metadata(self, point_id: str, metadata: Dict[str, Any]) -> bool:
        """
        Update metadata for an existing vector
        
        Args:
            point_id: The ID of the point to update
            metadata: New metadata to set
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.client.set_payload(
                collection_name=self.collection_name,
                payload=metadata,
                points=[point_id]
            )
            return True
        except Exception:
            return False
    
    async def delete_vector(self, point_id: str) -> bool:
        """
        Delete a vector from Qdrant
        
        Args:
            point_id: The ID of the point to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=[point_id]
            )
            return True
        except Exception:
            return False
    
    async def delete_vectors_batch(self, point_ids: List[str]) -> bool:
        """
        Delete multiple vectors in batch
        
        Args:
            point_ids: List of point IDs to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=point_ids
            )
            return True
        except Exception:
            return False
    
    async def get_collection_info(self) -> Dict[str, Any]:
        """Get information about the collection"""
        try:
            info = self.client.get_collection(self.collection_name)
            return {
                'name': info.name,
                'vectors_count': info.vectors_count,
                'points_count': info.points_count,
                'status': info.status,
                'config': {
                    'vector_size': info.config.params.vectors.size,
                    'distance': info.config.params.vectors.distance
                }
            }
        except Exception as e:
            raise Exception(f"Failed to get collection info: {str(e)}")
    
    async def get_collection_stats(self) -> Dict[str, Any]:
        """Get detailed collection statistics"""
        try:
            info = await self.get_collection_info()
            
            # Get some sample points for analysis
            sample_points = self.client.scroll(
                collection_name=self.collection_name,
                limit=100
            )[0]
            
            # Analyze metadata fields
            metadata_fields = set()
            for point in sample_points:
                if point.payload:
                    metadata_fields.update(point.payload.keys())
            
            return {
                **info,
                'metadata_fields': list(metadata_fields),
                'sample_size': len(sample_points)
            }
        except Exception as e:
            raise Exception(f"Failed to get collection stats: {str(e)}")
    
    async def optimize_collection(self) -> bool:
        """
        Optimize the collection for better performance
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.client.update_collection(
                collection_name=self.collection_name,
                optimizer_config={
                    "default_segment_number": 2,
                    "memmap_threshold": 20000
                }
            )
            return True
        except Exception:
            return False 