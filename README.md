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

## How to create a single executable
You can use [PyInstaller](https://pyinstaller.org/) to bundle everything into a single .exe file. No Python installation or extra folders required.

1. Install PyInstaller:
```powershell
pip install pyinstaller
```

2. Create the .exe (single file, no extra folders):

First ensure `PyInstaller` is installed (recommended inside a virtual environment):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt pyinstaller
```

If the `pyinstaller` command is not found (PowerShell error: "The term 'pyinstaller' is not recognized..."), use the `python -m` form which does not require the script to be on PATH:

```powershell
python -m PyInstaller --onefile --windowed main.py
```

- The resulting `main` will be in the `dist` folder.
- You can rename and move `main` anywhere; it will run standalone.

Common troubleshooting and tips
- If PowerShell says `pyinstaller` is not recognized, it usually means the Python `Scripts` folder (where `pyinstaller.exe` lives) isn't on PATH for the active shell, or PyInstaller isn't installed in the interpreter you're using. The `python -m PyInstaller ...` form always runs the module using the selected `python` and avoids that problem.
- If you prefer to use the `pyinstaller` command directly, make sure you installed it into the same Python environment and that `.<venv>\Scripts` is active or on PATH (activate the venv with `.\.venv\Scripts\Activate.ps1`).
- If you run into missing Qt resources or runtime errors with `PyQt6`, try adding PyInstaller options to collect PyQt resources, e.g.:

```powershell
python -m PyInstaller --onefile --windowed --collect-all PyQt6 main.py
```

or selectively add data/binaries if PyInstaller misses some Qt plugins.

Note: antivirus or SmartScreen on Windows sometimes flags newly-built single-file executables; you may need to sign the exe or mark it as safe on the target machine.

## Notes
- Supported formats: PNG, JPG, JPEG, BMP, TIFF
- You can modify `main.py` to apply other image processing steps.
- The `--windowed` flag prevents a console window from appearing.
- The `--onefile` flag bundles everything into a single executable.
- No need to install Python or dependencies on the target machine.
