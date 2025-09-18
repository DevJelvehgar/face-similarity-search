"""
Face Recognition Tools Module
Handles face embedding extraction and similarity search
"""

from deepface import DeepFace
import numpy as np
import os
import glob
from database_faiss import create_tables, save_face_embedding, find_similar_faces_faiss

def extract_face_embedding(image_path):
    """
    Extract face embedding from image using DeepFace ArcFace modelIndexIVFFlat 
    Args:
        image_path: Path to the image file
    Returns:
        Face embedding vector (512 dimensions) or None if failed
    """
    try:
        # Use DeepFace with ArcFace model for face recognition
        # ArcFace provides 512-dimensional embeddings
        result = DeepFace.represent(
            img_path=image_path, 
            model_name="ArcFace", 
            enforce_detection=False  # Don't fail if no face detected
        )
        
        # Result is a list of dictionaries, get the first one
        if isinstance(result, list) and len(result) > 0:
            embedding_dict = result[0]
            if isinstance(embedding_dict, dict) and 'embedding' in embedding_dict:
                embedding = embedding_dict['embedding']
            else:
                # If it's not a dict, it might be the embedding directly
                embedding = embedding_dict
        else:
            # If result is not a list, it might be the embedding directly
            embedding = result
        
        # Convert to numpy array with float32 precision
        return np.array(embedding, dtype=np.float32)
        
    except Exception as e:
        print(f"Error extracting face features from {image_path}: {e}")
        return None

def find_similar_faces(uploaded_path):
    """
    Find similar faces in database using FAISS
    Args:
        uploaded_path: Path to uploaded image
    Returns:
        List of similar faces with similarity scores
    """
    # Extract face features from uploaded image
    uploaded_embedding = extract_face_embedding(uploaded_path)
    if uploaded_embedding is None:
        return []
    
    # Search for similar faces using FAISS
    # Returns top 3 matches with similarity >= 0.6 (60%)
    similar_faces = find_similar_faces_faiss(
        query_embedding=uploaded_embedding,
        k=10,  # Maximum 3 results
        threshold=0.6  # 60% similarity threshold (reduced from 90%)
    )
    
    return similar_faces

def populate_database_from_temp():
    """
    Populate database with images from temp folder
    Processes up to 500 images for optimal performance
    Returns:
        Tuple of (success_count, error_count)
    """
    # Initialize database
    create_tables()
    
    # Get image files from temp folder
    image_files = glob.glob("temp/*.jpg")
    print(f"Processing {len(image_files)} images from temp folder")
    
    success_count = 0
    error_count = 0
    
    # Process each image
    for i, image_path in enumerate(image_files):
        filename = os.path.basename(image_path)
        print(f"Processing {i+1}/{len(image_files)}: {filename}")
        
        # Extract face features
        embedding = extract_face_embedding(image_path)
        
        if embedding is not None:
            # Save to database
            save_face_embedding(filename, image_path, embedding)
            success_count += 1
            print(f"✓ {filename} added successfully")
        else:
            error_count += 1
            print(f"✗ Failed to extract features from {filename}")
    
    print(f"\nDatabase population complete!")
    print(f"Successfully processed: {success_count} images")
    print(f"Errors: {error_count} images")
    
    return success_count, error_count