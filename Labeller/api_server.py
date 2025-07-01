from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Optional, Dict
import uvicorn
import json
import os
import shutil
from pathlib import Path

# Get the directory where this script is located
SCRIPT_DIR = Path(os.path.dirname(os.path.abspath(__file__)))

app = FastAPI(title="Image Labeling API",
            description="API for supporting the image labeling application")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Create data directories if they don't exist
UPLOAD_DIR = SCRIPT_DIR / "uploaded_images"
LABELS_DIR = SCRIPT_DIR / "labels"

UPLOAD_DIR.mkdir(exist_ok=True)
LABELS_DIR.mkdir(exist_ok=True)

# Store labels in memory for simplicity
labels_data = {}

# Default categories - using absolute path to ensure file is found
try:
    categories_file = SCRIPT_DIR / "src" / "list.json"
    with open(categories_file, 'r') as f:
        default_categories = json.load(f)
except FileNotFoundError:
    print(f"Warning: Categories file not found at {categories_file}. Using empty categories.")
    default_categories = {}

@app.get("/")
async def root():
    return {"message": "Image Labeling API is running"}

@app.get("/categories")
async def get_categories():
    return default_categories

@app.post("/categories")
async def update_categories(categories: Dict):
    global default_categories
    default_categories = categories
    
    # Save to file
    categories_file = SCRIPT_DIR / "src" / "list.json"
    try:
        with open(categories_file, 'w') as f:
            json.dump(default_categories, f, indent=2)
        return {"message": "Categories updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update categories: {str(e)}")

@app.post("/upload")
async def upload_images(files: List[UploadFile] = File(...)):
    saved_files = []
    
    for file in files:
        file_path = UPLOAD_DIR / file.filename
        
        # Save the file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        saved_files.append(file.filename)
    
    return {"filenames": saved_files}

@app.post("/label")
async def save_labels(labels: Dict):
    # Store labels
    for image_name, label_data in labels.items():
        labels_data[image_name] = label_data
    
    # Save to JSON file
    with open(LABELS_DIR / "labels.json", "w") as f:
        json.dump(labels_data, f, indent=2)
    
    return {"message": "Labels saved successfully"}

@app.get("/labels")
async def get_labels():
    return labels_data

@app.get("/export")
async def export_labels():
    if not labels_data:
        raise HTTPException(status_code=404, detail="No labels found")
    
    # Create CSV content
    csv_rows = [["image_name", "category", "subcategory", "json_format"]]
    
    for image_name, label_info in labels_data.items():
        category = label_info.get("category", "")
        subcategory = label_info.get("subcategory", "")
        json_str = json.dumps({"category": category, "subcategory": subcategory})
        
        csv_rows.append([image_name, category, subcategory, json_str])
    
    # Join rows into CSV string
    csv_content = "\n".join([",".join(row) for row in csv_rows])
    
    # Save to file
    csv_path = LABELS_DIR / "labels.csv"
    with open(csv_path, "w") as f:
        f.write(csv_content)
    
    return {"message": "CSV exported successfully", "path": str(csv_path)}

if __name__ == "__main__":
    print(f"Starting FastAPI server. API documentation available at http://localhost:8000/docs")
    print(f"API is using categories from: {SCRIPT_DIR / 'src' / 'list.json'}")
    print(f"Uploads will be stored in: {UPLOAD_DIR}")
    print(f"Labels will be stored in: {LABELS_DIR}")
    uvicorn.run("api_server:app", host="0.0.0.0", port=8000, reload=True) 