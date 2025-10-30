
# PixFix

Batch image processing with a simple GUI (PyQt6).
Target a black picture (taken in total darkness) for reference, the hot pixels of all the pictures around will automatically be treated and saved in a `treated` subfolder

## Quick Start
1. Install Python 3.8+.
2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
3. Run:
   ```sh
   python main.py
   ```

## Create a single executable (Windows)
1. Install PyInstaller:
   ```powershell
   pip install pyinstaller
   ```
2. Build:
   ```powershell
   python -m PyInstaller --onefile --windowed main.py
   ```
3. Find your standalone app in the `dist` folder.

## Notes
- Supported formats: PNG, JPG, JPEG, BMP, TIFF
- The GUI lets you select a reference image and strength, then processes all images in the folder.
- No need to install Python or dependencies on the target machine if you use the .exe.
