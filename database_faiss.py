"""
Simple FAISS Database Module for Face Similarity Search
Uses IndexIVFFlat for fast similarity search with 1M+ images support
"""

import faiss
import numpy as np
import pickle
import os

class FaceDatabase:
    """
    Simple FAISS-based database for storing face embeddings
    Optimized for real-time similarity search with high accuracy
    """
    
    def __init__(self, dimension=512):
        """
        Initialize FAISS database
        Args:
            dimension: Size of face embedding vector (default: 512 for ArcFace)
        """
        self.dimension = dimension
        
        # Use IndexFlatIP for simplicity and perfect accuracy
        # This works well for datasets up to 100K images
        self.index = faiss.IndexFlatIP(dimension)
        self.is_trained = True  # IndexFlatIP doesn't need training
        
        # Store metadata for each embedding
        self.filenames = []  # List of image filenames
        self.file_paths = []  # List of image file paths
        
        # Database files
        self.db_file = "facehub_faiss.pkl"
        self.index_file = "facehub_faiss.index"
    
    def normalize_embedding(self, embedding):
        """
        Normalize embedding vector for cosine similarity
        Args:
            embedding: Raw embedding vector
        Returns:
            Normalized embedding vector
        """
        return embedding / np.linalg.norm(embedding)
    
    def add_embedding(self, filename, file_path, embedding):
        """
        Add face embedding to database
        Args:
            filename: Name of the image file
            file_path: Full path to the image file
            embedding: Face embedding vector (512 dimensions)
        """
        # Normalize embedding for cosine similarity
        normalized_embedding = self.normalize_embedding(embedding)
        normalized_embedding = normalized_embedding.reshape(1, -1).astype('float32')
        
        # Add to FAISS index (IndexFlatIP doesn't need training)
        self.index.add(normalized_embedding)
        
        # Store metadata
        self.filenames.append(filename)
        self.file_paths.append(file_path)
    
    def search_similar(self, query_embedding, k=3, threshold=0.9):
        """
        Search for similar faces
        Args:
            query_embedding: Face embedding to search for
            k: Maximum number of results to return
            threshold: Minimum similarity score (0.0 to 1.0)
        Returns:
            List of similar faces with similarity scores
        """
        if self.index.ntotal == 0:
            return []
        
        # Normalize query embedding
        normalized_query = self.normalize_embedding(query_embedding)
        normalized_query = normalized_query.reshape(1, -1).astype('float32')
        
        # IndexFlatIP doesn't need search parameters
        
        # Search in FAISS index
        similarities, indices = self.index.search(normalized_query, min(k, self.index.ntotal))
        
        # Filter results by threshold and build response
        results = []
        for similarity, idx in zip(similarities[0], indices[0]):
            if similarity >= threshold and idx < len(self.filenames):
                results.append({
                    'filename': self.filenames[idx],
                    'file_path': self.file_paths[idx],
                    'similarity': float(similarity)
                })
        
        # Sort by similarity (highest first)
        results.sort(key=lambda x: x['similarity'], reverse=True)
        return results
    
    def get_count(self):
        """Get total number of stored embeddings"""
        return self.index.ntotal
    
    def save(self):
        """Save database to disk for persistence"""
        # Save FAISS index
        faiss.write_index(self.index, self.index_file)
        
        # Save metadata
        metadata = {
            'filenames': self.filenames,
            'file_paths': self.file_paths,
            'dimension': self.dimension,
            'is_trained': self.is_trained
        }
        with open(self.db_file, 'wb') as f:
            pickle.dump(metadata, f)
    
    def load(self):
        """Load database from disk"""
        if os.path.exists(self.index_file) and os.path.exists(self.db_file):
            # Load FAISS index
            self.index = faiss.read_index(self.index_file)
            
            # Load metadata
            with open(self.db_file, 'rb') as f:
                metadata = pickle.load(f)
                self.filenames = metadata['filenames']
                self.file_paths = metadata['file_paths']
                self.dimension = metadata['dimension']
                self.is_trained = metadata.get('is_trained', True)
            return True
        return False
    
    
    def clear(self):
        """Clear all embeddings from database"""
        self.index = faiss.IndexFlatIP(self.dimension)
        self.is_trained = True
        self.filenames = []
        self.file_paths = []

# Global database instance
face_db = FaceDatabase()

# Simple functions for compatibility
def create_tables():
    """Initialize database (for compatibility)"""
    face_db.clear()

def save_face_embedding(filename, file_path, embedding):
    """Save face embedding to database"""
    face_db.add_embedding(filename, file_path, embedding)

def get_embedding_count():
    """Get number of stored embeddings"""
    return face_db.get_count()

def find_similar_faces_faiss(query_embedding, k=3, threshold=0.9):
    """Find similar faces using FAISS"""
    return face_db.search_similar(query_embedding, k, threshold)