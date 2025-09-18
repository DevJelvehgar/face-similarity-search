"""
Simple Face Similarity Search Web Application
Upload an image to find similar faces with 90%+ similarity
"""

from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse
import os
import shutil
from face_tools import find_similar_faces, populate_database_from_temp
from database_faiss import create_tables, get_embedding_count, face_db

# Create FastAPI application
app = FastAPI(title="Face Similarity Search", description="Find similar faces with 90%+ similarity")

@app.on_event("startup")
async def startup_event():
    """
    Initialize application on startup
    Creates database and loads existing data
    """
    print("=== FaceHub Starting ===")
    
    # Initialize database
    create_tables()
    
    # Load existing database if available
    face_db.load()
    
    # Check if database is empty
    count = get_embedding_count()
    if count == 0:
        print("Database is empty. It will be populated when you first upload an image.")
    else:
        print(f"Database loaded: {count} images ready")
    
    print("FaceHub is ready! Visit http://127.0.0.1:8000")

@app.get("/")
async def home():
    """
    Home page with simple upload interface
    Returns HTML page for image upload
    """
    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Face Similarity Search</title>
        <style>
            body { 
                font-family: Arial, sans-serif; 
                text-align: center; 
                padding: 50px; 
                background-color: #f5f5f5;
            }
            .container {
                max-width: 600px;
                margin: 0 auto;
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            .upload-area { 
                border: 2px dashed #007bff; 
                padding: 40px; 
                margin: 20px 0;
                border-radius: 10px;
                background-color: #f8f9fa;
            }
            button { 
                background: #007bff; 
                color: white; 
                padding: 12px 24px; 
                border: none; 
                border-radius: 5px;
                cursor: pointer; 
                font-size: 16px;
            }
            button:hover {
                background: #0056b3;
            }
            .result { 
                margin: 15px 0; 
                padding: 15px; 
                background: #e9ecef; 
                border-radius: 5px;
                text-align: left;
            }
            .similarity {
                color: #28a745;
                font-weight: bold;
            }
            .no-results {
                color: #dc3545;
                font-style: italic;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🔍 Face Similarity Search</h1>
            <p>Upload an image to find similar faces with 90%+ similarity</p>
            
            <div class="upload-area">
                <h3>📸 Upload Your Image</h3>
                <form id="uploadForm" enctype="multipart/form-data">
                    <input type="file" id="imageFile" accept="image/*" required style="margin: 10px 0;">
                    <br><br>
                    <button type="submit">🔍 Find Similar Faces</button>
                </form>
            </div>
            
            <div id="results"></div>
        </div>
        
        <script>
            // Handle form submission
            document.getElementById('uploadForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                
                const file = document.getElementById('imageFile').files[0];
                if (!file) return;
                
                // Show loading message
                document.getElementById('results').innerHTML = '<p>🔍 Searching for similar faces...</p>';
                
                // Prepare form data
                const formData = new FormData();
                formData.append('file', file);
                
                try {
                    // Send request to server
                    const response = await fetch('/upload', {
                        method: 'POST',
                        body: formData
                    });
                    
                    const result = await response.json();
                    displayResults(result);
                    
                } catch (error) {
                    document.getElementById('results').innerHTML = 
                        '<div class="result no-results">❌ Error uploading image. Please try again.</div>';
                }
            });
            
            // Display search results
            function displayResults(matches) {
                const div = document.getElementById('results');
                
                if (matches.length === 0) {
                    div.innerHTML = '<div class="result no-results">❌ No similar faces found (90%+ similarity)</div>';
                    return;
                }
                
                let html = '<h3>🎯 Similar Faces Found:</h3>';
                matches.forEach((match, index) => {
                    const similarityPercent = (match.similarity * 100).toFixed(2);
                    html += `
                        <div class="result">
                            <strong>${index + 1}. ${match.filename}</strong><br>
                            <span class="similarity">Similarity: ${similarityPercent}%</span>
                        </div>
                    `;
                });
                
                div.innerHTML = html;
            }
        </script>
    </body>
    </html>
    """)

@app.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    """
    Handle image upload and similarity search
    Args:
        file: Uploaded image file
    Returns:
        List of similar faces with similarity scores
    """
    # Create temporary file for uploaded image
    temp_path = f"temp_upload_{file.filename}"
    
    try:
        # Save uploaded file temporarily
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Find similar faces using FAISS
        similar_faces = find_similar_faces(temp_path)
        
        return similar_faces
        
    finally:
        # Clean up temporary file
        if os.path.exists(temp_path):
            os.remove(temp_path)

if __name__ == "__main__":
    import uvicorn
    print("Starting FaceHub server...")
    uvicorn.run(app, host="127.0.0.1", port=8000)