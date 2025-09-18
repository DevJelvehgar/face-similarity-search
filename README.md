# FaceHub - Face Similarity Search

A simple and powerful face similarity search application using AI technology.

## Features

- 🔍 **High Accuracy**: Uses ArcFace model for 90%+ similarity detection
- ⚡ **Fast Search**: FAISS-based database for real-time similarity search
- 🎯 **Easy to Use**: Simple web interface with drag-and-drop upload
- 📊 **Database Management**: Automatic database building and status checking
- 🌐 **Modern UI**: Clean and responsive web interface

## Installation

1. **Install required libraries:**
```bash
pip install -r requirements.txt
```

2. **Build the database:**
```bash
python build_database.py
```

3. **Run the application:**
```bash
python app.py
```

4. **Open your browser and go to:**
```
http://127.0.0.1:8000
```

## How to Use

1. **Upload an image** using the web interface
2. **The app finds similar faces** using AI-powered similarity search
3. **Results show similarity percentage** with matching images

## Database Management

### Check Database Status

**Quick Check:**
```python
from database_faiss import get_embedding_count
count = get_embedding_count()
print(f"Database contains {count} face embeddings")
```

**Detailed Check:**
```python
from database_faiss import face_db
face_db.load()
print(f"Total embeddings: {face_db.get_count()}")
print(f"Sample files: {face_db.filenames[:5]}")
```

### Database Files

- `facehub_faiss.index` - FAISS index file
- `facehub_faiss.pkl` - Metadata file

### Build Database

The database is automatically populated with images from the `temp/` folder:
```bash
python build_database.py
```

## File Structure

```
face_similarity/
├── app.py                 # Main web application
├── face_tools.py          # Face detection and processing tools
├── database_faiss.py      # FAISS database management
├── build_database.py      # Database building script
├── requirements.txt       # Python dependencies
├── temp/                  # Source images folder
├── uploads/               # Uploaded images
└── README.md             # This file
```

## API Endpoints

- `GET /` - Main interface
- `POST /upload` - Upload image for similarity search

## Requirements

- Python 3.7+
- FastAPI
- FAISS
- OpenCV
- NumPy

## Troubleshooting

### Database is Empty
1. Check if images exist in `temp/` folder
2. Run `python build_database.py`
3. Verify database files are created

### No Similar Faces Found
1. Check database status
2. Try lowering similarity threshold
3. Ensure uploaded image contains a clear face

## License

This project is open source and available under the MIT License.