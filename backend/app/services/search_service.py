from typing import List, Dict, Any, Optional, Union
import asyncio
import time
from .embedding_service import EmbeddingService
from .vector_service import VectorService
from ..config import settings

class SearchService:
    """Advanced search service combining embedding and vector operations"""
    
    def __init__(self):
        """Initialize the search service with embedding and vector services"""
        self.embedding_service = EmbeddingService()
        self.vector_service = VectorService()
    
    async def semantic_search(self, query: str, limit: int = 10, 
                            score_threshold: float = None, 
                            filter_conditions: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Perform semantic search using embeddings
        
        Args:
            query: Search query text
            limit: Maximum number of results
            score_threshold: Minimum similarity score
            filter_conditions: Optional metadata filters
            
        Returns:
            Search results with metadata
        """
        start_time = time.time()
        
        try:
            # Generate embedding for the query
            query_embedding = await self.embedding_service.get_embedding(query)
            
            # Search for similar vectors
            search_results = await self.vector_service.search_vectors(
                query_embedding,
                limit=limit,
                score_threshold=score_threshold,
                filter_conditions=filter_conditions
            )
            
            search_time = (time.time() - start_time) * 1000
            
            return {
                'query': query,
                'results': search_results,
                'total_found': len(search_results),
                'search_time_ms': search_time,
                'embedding_model': self.embedding_service.model
            }
            
        except Exception as e:
            raise Exception(f"Semantic search failed: {str(e)}")
    
    async def hybrid_search(self, query: str, limit: int = 10,
                          semantic_weight: float = 0.7,
                          text_weight: float = 0.3) -> Dict[str, Any]:
        """
        Perform hybrid search combining semantic and text similarity
        
        Args:
            query: Search query text
            limit: Maximum number of results
            semantic_weight: Weight for semantic similarity (0-1)
            text_weight: Weight for text similarity (0-1)
            
        Returns:
            Combined search results
        """
        start_time = time.time()
        
        try:
            # Perform semantic search
            semantic_results = await self.semantic_search(query, limit=limit * 2)
            
            # Perform text similarity search
            text_results = await self.vector_service.search_by_text_similarity(
                query, limit=limit * 2
            )
            
            # Combine and rank results
            combined_results = self._combine_search_results(
                semantic_results['results'],
                text_results,
                semantic_weight,
                text_weight
            )
            
            # Take top results
            final_results = combined_results[:limit]
            
            search_time = (time.time() - start_time) * 1000
            
            return {
                'query': query,
                'results': final_results,
                'total_found': len(final_results),
                'search_time_ms': search_time,
                'search_type': 'hybrid',
                'weights': {
                    'semantic': semantic_weight,
                    'text': text_weight
                }
            }
            
        except Exception as e:
            raise Exception(f"Hybrid search failed: {str(e)}")
    
    def _combine_search_results(self, semantic_results: List[Dict], 
                               text_results: List[Dict],
                               semantic_weight: float,
                               text_weight: float) -> List[Dict]:
        """Combine and rank search results from different methods"""
        
        # Create lookup for semantic results
        semantic_lookup = {result['id']: result for result in semantic_results}
        text_lookup = {result['id']: result for result in text_results}
        
        # Combine all unique IDs
        all_ids = set(semantic_lookup.keys()) | set(text_lookup.keys())
        
        combined_results = []
        for point_id in all_ids:
            semantic_score = semantic_lookup.get(point_id, {}).get('score', 0)
            text_score = text_lookup.get(point_id, {}).get('score', 0)
            
            # Calculate weighted score
            combined_score = (semantic_score * semantic_weight) + (text_score * text_weight)
            
            # Use the payload from semantic results (more complete)
            payload = semantic_lookup.get(point_id, {}).get('payload', 
                     text_lookup.get(point_id, {}).get('payload', {}))
            
            combined_results.append({
                'id': point_id,
                'score': combined_score,
                'semantic_score': semantic_score,
                'text_score': text_score,
                'payload': payload
            })
        
        # Sort by combined score
        combined_results.sort(key=lambda x: x['score'], reverse=True)
        
        return combined_results
    
    async def batch_search(self, queries: List[str], limit: int = 5) -> List[Dict[str, Any]]:
        """
        Perform batch search for multiple queries
        
        Args:
            queries: List of search queries
            limit: Maximum results per query
            
        Returns:
            List of search results for each query
        """
        try:
            # Generate embeddings for all queries
            embeddings = await self.embedding_service.get_embeddings(queries)
            
            # Perform searches in parallel
            search_tasks = []
            for query, embedding in zip(queries, embeddings):
                task = self.vector_service.search_vectors(embedding, limit=limit)
                search_tasks.append(task)
            
            search_results = await asyncio.gather(*search_tasks)
            
            # Format results
            results = []
            for i, (query, query_results) in enumerate(zip(queries, search_results)):
                results.append({
                    'query': query,
                    'results': query_results,
                    'total_found': len(query_results),
                    'query_index': i
                })
            
            return results
            
        except Exception as e:
            raise Exception(f"Batch search failed: {str(e)}")
    
    async def search_with_filters(self, query: str, filters: Dict[str, Any], 
                                limit: int = 10) -> Dict[str, Any]:
        """
        Search with advanced filtering options
        
        Args:
            query: Search query
            filters: Filter conditions (e.g., date ranges, tags, etc.)
            limit: Maximum number of results
            
        Returns:
            Filtered search results
        """
        try:
            # Generate embedding
            query_embedding = await self.embedding_service.get_embedding(query)
            
            # Search with filters
            search_results = await self.vector_service.search_vectors(
                query_embedding,
                limit=limit,
                filter_conditions=filters
            )
            
            return {
                'query': query,
                'results': search_results,
                'total_found': len(search_results),
                'filters_applied': filters
            }
            
        except Exception as e:
            raise Exception(f"Filtered search failed: {str(e)}")
    
    async def get_similar_notes(self, note_id: str, limit: int = 5) -> Dict[str, Any]:
        """
        Find notes similar to a specific note
        
        Args:
            note_id: ID of the reference note
            limit: Maximum number of similar notes
            
        Returns:
            Similar notes with similarity scores
        """
        try:
            # Get the reference note
            note_data = await self.vector_service.get_vectors_by_ids([note_id])
            if not note_data:
                raise Exception(f"Note with ID {note_id} not found")
            
            reference_note = note_data[0]
            reference_content = reference_note['payload'].get('content', '')
            
            # Generate embedding for the reference content
            reference_embedding = await self.embedding_service.get_embedding(reference_content)
            
            # Search for similar vectors (excluding the reference note)
            search_results = await self.vector_service.search_vectors(
                reference_embedding,
                limit=limit + 1  # Get one extra to account for the reference note
            )
            
            # Filter out the reference note
            similar_notes = [
                result for result in search_results 
                if result['id'] != note_id
            ][:limit]
            
            return {
                'reference_note_id': note_id,
                'similar_notes': similar_notes,
                'total_found': len(similar_notes)
            }
            
        except Exception as e:
            raise Exception(f"Failed to find similar notes: {str(e)}")
    
    async def get_search_suggestions(self, partial_query: str, limit: int = 5) -> List[str]:
        """
        Get search suggestions based on partial query
        
        Args:
            partial_query: Partial search query
            limit: Maximum number of suggestions
            
        Returns:
            List of suggested search terms
        """
        try:
            # This is a simplified implementation
            # In a real application, you might use a more sophisticated approach
            # like analyzing search patterns or using a suggestion index
            
            # For now, return some basic suggestions
            suggestions = [
                f"{partial_query} ideas",
                f"{partial_query} notes",
                f"{partial_query} thoughts",
                f"{partial_query} memories",
                f"{partial_query} concepts"
            ]
            
            return suggestions[:limit]
            
        except Exception as e:
            raise Exception(f"Failed to get search suggestions: {str(e)}")
    
    async def get_search_analytics(self) -> Dict[str, Any]:
        """
        Get analytics about search performance and patterns
        
        Returns:
            Search analytics data
        """
        try:
            # Get collection statistics
            collection_stats = await self.vector_service.get_collection_stats()
            
            # Get embedding service stats
            embedding_stats = self.embedding_service.get_cache_stats()
            
            return {
                'collection_stats': collection_stats,
                'embedding_stats': embedding_stats,
                'search_config': {
                    'similarity_threshold': settings.SIMILARITY_THRESHOLD,
                    'max_search_results': settings.MAX_SEARCH_RESULTS,
                    'embedding_model': settings.OPENAI_MODEL
                }
            }
            
        except Exception as e:
            raise Exception(f"Failed to get search analytics: {str(e)}") 