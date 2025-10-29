# pixfix

A simple Python project for batch image processing using OpenCV.

## Features
- Processes all images in the `original` folder
- Converts images to grayscale and saves them in the `treated` folder

## Installation
1. Install Python 3.8+
2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```

## Usage
1. Place your images in the `original` folder.
2. Run the script:
   ```sh
   python main.py
   ```
3. Processed images will appear in the `treated` folder.

## Notes
- Supported formats: PNG, JPG, JPEG, BMP, TIFF
- You can modify `main.py` to apply other image processing steps.
