# Universal Image Converter

A simple Python script that batch converts images from one format to another, recursively scanning a folder and its subfolders.

## Features

- Converts between common image formats: HEIC, JPG, PNG, WEBP, and more
- Supports HEIC files from Apple devices (iPhone/iPad photos)
- Recursively scans subfolders
- Saves converted files into a `processed/` subfolder alongside the originals
- Handles transparency (e.g. RGBA PNG → JPG) automatically
- Optional resize: downscale images to a specified max width while preserving aspect ratio

## Requirements

- Python 3.x
- [Pillow](https://pypi.org/project/Pillow/)
- [pillow-heif](https://pypi.org/project/pillow-heif/) *(required for HEIC support)*

Install dependencies:

```bash
pip install Pillow pillow-heif
```

## Usage

Run the script from the folder containing your images, or place it there and double-click:

```bash
python image_converter.py
```

You will be prompted to enter:
1. The **input format** (e.g. `heic`, `png`, `jpg`)
2. The **output format** (e.g. `jpg`, `webp`, `png`)
3. A **max width** in pixels — press Enter to skip resizing, or type a number (e.g. `1920`, `1280`)

Images already narrower than the specified width are left at their original size. Resizing always preserves the aspect ratio.

The script will scan the current working directory and all subfolders for matching files. Converted images are saved in a `processed/` folder created inside each folder where source files were found. The originals are left untouched.

## Example

```
Convert FROM (e.g. heic, jpg, png): heic
Convert TO (e.g. png, webp, jpg): jpg
Max width in px [default: 1920, press Enter to skip resizing]: 1920

Scanning '/Users/you/Photos' for HEIC files...
Success: IMG_001.heic -> IMG_001.jpg (resized to 1920x1440)
Success: IMG_002.heic -> IMG_002.jpg

All done!
```

## Output Structure

```
Photos/
├── IMG_001.heic          ← original, untouched
├── IMG_002.heic
└── processed/
    ├── IMG_001.jpg       ← converted output
    └── IMG_002.jpg
```
