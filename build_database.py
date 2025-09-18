"""
Database Builder Script
Use this script to build/rebuild the face similarity database with images from temp folder
"""

from face_tools import populate_database_from_temp
from database_faiss import face_db, get_embedding_count

def main():
    print("=== FaceHub Database Builder ===")
    print("This script will build the face similarity database")
    print("Processing all images from temp folder...")
    
    # Populate database with all images
    success_count, error_count = populate_database_from_temp()
    
    # Save database
    face_db.save()
    
    # Check final count
    total_count = get_embedding_count()
    
    print(f"\n=== Database Build Complete ===")
    print(f"✅ Successfully processed: {success_count} images")
    print(f"❌ Errors: {error_count} images")
    print(f"📊 Total images in database: {total_count}")
    print("💾 Database saved successfully!")
    
    if total_count > 0:
        print(f"\n🎉 Database is ready with {total_count} images!")
        print("You can now run: python app.py")
    else:
        print("\n❌ No images were added to database.")
        print("Check temp folder for images.")

if __name__ == "__main__":
    main()