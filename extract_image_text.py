import os
import csv
import time
import pytesseract
import cv2
import numpy as np
import pandas as pd
from PIL import Image, ImageOps, ImageFilter, ImageEnhance
from pathlib import Path
from datetime import datetime

# Set the path to the Tesseract executable
# Update this path if you installed Tesseract in a different location
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def create_output_dir():
    """Create output directory for CSV files if it doesn't exist"""
    output_dir = "ocr_results"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    return output_dir

def preprocess_none(img):
    """No preprocessing, return original image"""
    return np.array(img)

def preprocess_basic(img):
    """Basic preprocessing: grayscale conversion"""
    img_cv = np.array(img)
    if len(img_cv.shape) == 3:
        return cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
    return img_cv

def preprocess_otsu_threshold(img):
    """Apply Otsu's thresholding to image"""
    img_cv = np.array(img)
    if len(img_cv.shape) == 3:
        gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
    else:
        gray = img_cv
    return cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

def preprocess_adaptive_threshold(img):
    """Apply adaptive thresholding to image"""
    img_cv = np.array(img)
    if len(img_cv.shape) == 3:
        gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
    else:
        gray = img_cv
    return cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)

def preprocess_denoise(img):
    """Apply denoising to image"""
    img_cv = np.array(img)
    if len(img_cv.shape) == 3:
        return cv2.fastNlMeansDenoisingColored(img_cv, None, 10, 10, 7, 21)
    else:
        return cv2.fastNlMeansDenoising(img_cv, None, 10, 7, 21)

def preprocess_sharpen(img):
    """Sharpen image using unsharp masking"""
    pil_img = img
    if isinstance(img, np.ndarray):
        if len(img.shape) == 3:
            pil_img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        else:
            pil_img = Image.fromarray(img)
    
    enhancer = ImageEnhance.Sharpness(pil_img)
    return np.array(enhancer.enhance(2.0))

def preprocess_contrast(img):
    """Enhance contrast in image"""
    pil_img = img
    if isinstance(img, np.ndarray):
        if len(img.shape) == 3:
            pil_img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        else:
            pil_img = Image.fromarray(img)
    
    enhancer = ImageEnhance.Contrast(pil_img)
    return np.array(enhancer.enhance(1.5))

def preprocess_dilate_erode(img):
    """Apply dilation and erosion to connect broken text and remove noise"""
    img_cv = np.array(img)
    if len(img_cv.shape) == 3:
        gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
    else:
        gray = img_cv
    
    # First convert to binary image using Otsu's method
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    # Create kernels for dilation and erosion
    kernel = np.ones((1, 1), np.uint8)
    
    # Dilate first to connect broken parts
    dilated = cv2.dilate(binary, kernel, iterations=1)
    
    # Erode to remove small noise
    eroded = cv2.erode(dilated, kernel, iterations=1)
    
    return eroded

def preprocess_canny(img):
    """Apply Canny edge detector to highlight text edges"""
    img_cv = np.array(img)
    if len(img_cv.shape) == 3:
        gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
    else:
        gray = img_cv
    # Apply Gaussian blur to reduce noise before edge detection
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    # Apply Canny edge detector
    edges = cv2.Canny(blurred, 100, 200)
    # Dilate to connect edges
    kernel = np.ones((2, 2), np.uint8)
    dilated_edges = cv2.dilate(edges, kernel, iterations=1)
    # Invert for better OCR (text should be black on white)
    return cv2.bitwise_not(dilated_edges)

def preprocess_gaussian_blur(img):
    """Apply Gaussian blur to reduce noise"""
    img_cv = np.array(img)
    if len(img_cv.shape) == 3:
        return cv2.GaussianBlur(img_cv, (5, 5), 0)
    else:
        return cv2.GaussianBlur(img_cv, (5, 5), 0)

def preprocess_median_blur(img):
    """Apply median blur to reduce salt-and-pepper noise"""
    img_cv = np.array(img)
    if len(img_cv.shape) == 3:
        return cv2.medianBlur(img_cv, 3)
    else:
        return cv2.medianBlur(img_cv, 3)

def preprocess_bilateral_filter(img):
    """Apply bilateral filter to reduce noise while preserving edges"""
    img_cv = np.array(img)
    if len(img_cv.shape) == 3:
        return cv2.bilateralFilter(img_cv, 9, 75, 75)
    else:
        gray = img_cv.copy()
        return cv2.bilateralFilter(gray, 9, 75, 75)

def preprocess_clahe(img):
    """Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)"""
    img_cv = np.array(img)
    if len(img_cv.shape) == 3:
        # Convert to LAB color space
        lab = cv2.cvtColor(img_cv, cv2.COLOR_BGR2LAB)
        # Split channels
        l, a, b = cv2.split(lab)
    else:
        l = img_cv.copy()
    
    # Apply CLAHE to L channel
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    cl = clahe.apply(l)
    
    if len(img_cv.shape) == 3:
        # Merge channels
        merged = cv2.merge((cl, a, b))
        # Convert back to BGR
        return cv2.cvtColor(merged, cv2.COLOR_LAB2BGR)
    else:
        return cl

def preprocess_binary(img):
    """Apply simple binary thresholding"""
    img_cv = np.array(img)
    if len(img_cv.shape) == 3:
        gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
    else:
        gray = img_cv
    
    # Apply binary threshold
    _, binary = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY)
    return binary

def preprocess_watershed(img):
    """Apply watershed segmentation to separate touching text"""
    img_cv = np.array(img)
    if len(img_cv.shape) == 3:
        gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
    else:
        gray = img_cv
    
    # Apply Otsu's thresholding
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    
    # Noise removal with morphological operations
    kernel = np.ones((3, 3), np.uint8)
    opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=2)
    
    # Sure background area
    sure_bg = cv2.dilate(opening, kernel, iterations=3)
    
    # Finding sure foreground area
    dist_transform = cv2.distanceTransform(opening, cv2.DIST_L2, 5)
    _, sure_fg = cv2.threshold(dist_transform, 0.5 * dist_transform.max(), 255, 0)
    
    # Finding unknown region
    sure_fg = np.uint8(sure_fg)
    unknown = cv2.subtract(sure_bg, sure_fg)
    
    # Marker labelling
    _, markers = cv2.connectedComponents(sure_fg)
    # Add one to all labels so that sure background is not 0, but 1
    markers = markers + 1
    # Mark the unknown region with zero
    markers[unknown == 255] = 0
    
    # Apply watershed
    if len(img_cv.shape) == 3:
        cv2.watershed(img_cv, markers)
        markers[markers == -1] = 0
        markers = markers.astype(np.uint8)
        result = np.zeros_like(gray)
        result[markers > 1] = 255
        return result
    else:
        # For grayscale images, convert to BGR for watershed, then back to gray
        img_color = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
        cv2.watershed(img_color, markers)
        markers[markers == -1] = 0
        markers = markers.astype(np.uint8)
        result = np.zeros_like(gray)
        result[markers > 1] = 255
        return result

def preprocess_contours(img):
    """Extract and emphasize contours in the image"""
    img_cv = np.array(img)
    if len(img_cv.shape) == 3:
        gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
    else:
        gray = img_cv
    
    # Apply Gaussian blur to reduce noise
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # Apply threshold to create binary image
    _, binary = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    
    # Find contours
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Create blank image
    contour_img = np.zeros_like(gray)
    
    # Draw all contours
    cv2.drawContours(contour_img, contours, -1, 255, 1)
    
    # Dilate to make contours more visible
    kernel = np.ones((2, 2), np.uint8)
    dilated = cv2.dilate(contour_img, kernel, iterations=1)
    
    # Invert for better OCR
    return cv2.bitwise_not(dilated)

def try_multiple_orientations(img, lang='fra+eng'):
    """Run OCR on multiple orientations of the image and combine results"""
    pil_img = img
    if isinstance(img, np.ndarray):
        if len(img.shape) == 3:
            pil_img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        else:
            pil_img = Image.fromarray(img)
    
    # Original orientation
    text_0 = pytesseract.image_to_string(pil_img, lang=lang)
    
    # 90 degrees
    img_90 = pil_img.transpose(Image.ROTATE_90)
    text_90 = pytesseract.image_to_string(img_90, lang=lang)
    
    # 180 degrees
    img_180 = pil_img.transpose(Image.ROTATE_180)
    text_180 = pytesseract.image_to_string(img_180, lang=lang)
    
    # 270 degrees
    img_270 = pil_img.transpose(Image.ROTATE_270)
    text_270 = pytesseract.image_to_string(img_270, lang=lang)
    
    # Combine all texts
    all_text = " ".join([text_0, text_90, text_180, text_270])
    return all_text.strip()

# Define different preprocessing and OCR configurations
PREPROCESSING_CONFIGS = {
    "original": {
        "name": "Original Image",
        "preprocess": preprocess_none,
        "multi_orientation": True
    },
    "basic": {
        "name": "Basic Grayscale",
        "preprocess": preprocess_basic,
        "multi_orientation": True
    },
    "otsu": {
        "name": "Otsu Thresholding",
        "preprocess": preprocess_otsu_threshold,
        "multi_orientation": True
    },
    "adaptive": {
        "name": "Adaptive Thresholding",
        "preprocess": preprocess_adaptive_threshold,
        "multi_orientation": True
    },
    "denoise": {
        "name": "Denoising",
        "preprocess": preprocess_denoise,
        "multi_orientation": True
    },
    "sharpen": {
        "name": "Sharpening",
        "preprocess": preprocess_sharpen,
        "multi_orientation": True
    },
    "contrast": {
        "name": "Contrast Enhancement",
        "preprocess": preprocess_contrast,
        "multi_orientation": True
    },
    "dilate_erode": {
        "name": "Dilation & Erosion",
        "preprocess": preprocess_dilate_erode,
        "multi_orientation": True
    },
    "canny": {
        "name": "Canny Edge Detection",
        "preprocess": preprocess_canny,
        "multi_orientation": True
    },
    "gaussian_blur": {
        "name": "Gaussian Blur",
        "preprocess": preprocess_gaussian_blur,
        "multi_orientation": True
    },
    "median_blur": {
        "name": "Median Blur",
        "preprocess": preprocess_median_blur,
        "multi_orientation": True
    },
    "bilateral": {
        "name": "Bilateral Filter",
        "preprocess": preprocess_bilateral_filter,
        "multi_orientation": True
    },
    "clahe": {
        "name": "CLAHE",
        "preprocess": preprocess_clahe,
        "multi_orientation": True
    },
    "binary": {
        "name": "Binary Threshold",
        "preprocess": preprocess_binary,
        "multi_orientation": True
    },
    "watershed": {
        "name": "Watershed Segmentation",
        "preprocess": preprocess_watershed,
        "multi_orientation": True
    },
    "contours": {
        "name": "Contour Extraction",
        "preprocess": preprocess_contours,
        "multi_orientation": True
    },
    "contrast_otsu": {
        "name": "Contrast Enhancement + Otsu",
        "preprocess": lambda img: preprocess_otsu_threshold(preprocess_contrast(img)),
        "multi_orientation": True
    },
    "denoise_sharpen": {
        "name": "Denoise + Sharpen",
        "preprocess": lambda img: preprocess_sharpen(preprocess_denoise(img)),
        "multi_orientation": True
    },
    "sharpen_otsu": {
        "name": "Sharpen + Otsu",
        "preprocess": lambda img: preprocess_otsu_threshold(preprocess_sharpen(img)),
        "multi_orientation": True
    },
    "clahe_adaptive": {
        "name": "CLAHE + Adaptive Threshold",
        "preprocess": lambda img: preprocess_adaptive_threshold(preprocess_clahe(img)),
        "multi_orientation": True
    },
    "gaussian_otsu": {
        "name": "Gaussian Blur + Otsu",
        "preprocess": lambda img: preprocess_otsu_threshold(preprocess_gaussian_blur(img)),
        "multi_orientation": True
    }
}

def process_image(image_path, config, lang='fra+eng'):
    """Process an image with the given preprocessing configuration"""
    try:
        # Open image with PIL
        img = Image.open(image_path)
        
        # Apply preprocessing
        processed_img = config["preprocess"](img)
        
        # Apply OCR - always use multi-orientation as requested
        # Convert numpy array back to PIL Image if needed
        if isinstance(processed_img, np.ndarray):
            if len(processed_img.shape) == 3:
                processed_img = Image.fromarray(cv2.cvtColor(processed_img, cv2.COLOR_BGR2RGB))
            else:
                processed_img = Image.fromarray(processed_img)
        
        text = try_multiple_orientations(processed_img, lang)
        
        # Clean up text
        text = " ".join(text.strip().split())
        return text
    
    except Exception as e:
        print(f"Error processing {image_path} with {config['name']}: {str(e)}")
        return ""

def process_directory(base_dir, lang='fra+eng'):
    """Process all images in a directory with multiple preprocessing techniques"""
    output_dir = create_output_dir()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Create a dictionary to hold results for each configuration
    all_results = {config_id: [] for config_id in PREPROCESSING_CONFIGS.keys()}
    
    # Walk through all subdirectories
    for root, dirs, files in os.walk(base_dir):
        # Filter for jpg files (case insensitive)
        jpg_files = [f for f in files if f.lower().endswith(('.jpg', '.jpeg'))]
        
        # Process each image with each configuration
        for file in jpg_files:
            file_path = os.path.join(root, file)
            folder_name = os.path.basename(root)
            
            print(f"Processing: {file_path}")
            
            # Process with each configuration
            for config_id, config in PREPROCESSING_CONFIGS.items():
                print(f"  Using {config['name']}...")
                
                start_time = time.time()
                extracted_text = process_image(file_path, config, lang)
                processing_time = time.time() - start_time
                
                # Store results
                all_results[config_id].append({
                    'filename': file,
                    'folder': folder_name,
                    'extracted_text': extracted_text,
                    'processing_time': round(processing_time, 2)
                })
    
    # Save results for each configuration to separate CSV files
    for config_id, results in all_results.items():
        if results:
            config_name = PREPROCESSING_CONFIGS[config_id]['name'].replace(' ', '_').lower()
            output_file = os.path.join(output_dir, f"ocr_{config_name}_{timestamp}.csv")
            
            df = pd.DataFrame(results)
            df.to_csv(output_file, index=False, quoting=csv.QUOTE_ALL)
            print(f"Saved results for {config_id} to {output_file}")

def main():
    # Set the base directory path
    base_dir = r'.\data\Par_batchs'
    
    # Ensure base directory exists
    if not os.path.exists(base_dir):
        print(f"Error: Directory {base_dir} does not exist.")
        return
    
    # Language setting
    lang = 'fra+eng'  # French + English
    
    print(f"Starting OCR processing with multiple techniques...")
    print(f"Processing images in: {base_dir}")
    print(f"Language: {lang}")
    print(f"Number of techniques: {len(PREPROCESSING_CONFIGS)}")
    
    # Process directory
    process_directory(base_dir, lang)
    
    print("Processing complete!")

if __name__ == "__main__":
    # Check for required libraries
    try:
        import cv2
    except ImportError:
        print("Error: OpenCV (cv2) is required but not installed.")
        print("Please install it using: pip install opencv-python")
        exit(1)
        
    # Check if pytesseract is properly configured
    try:
        pytesseract.get_tesseract_version()
    except pytesseract.TesseractNotFoundError:
        print("Error: Tesseract OCR is not installed or not in PATH.")
        print("Please install Tesseract OCR and make sure it's in your system PATH.")
        exit(1)
    
    main()