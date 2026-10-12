# How to Use the Image Converter

This tool provides two ways to convert images:
1. **Web Dashboard (Recommended for Non-Technical Team)** — Easy drag-and-drop, folder support, smart one-click presets, and ZIP downloads.
2. **Terminal Script** — Command-line tool with automatic format detection.

---

## Option 1: Web Dashboard (Zero Technical Knowledge Needed)

### Running Locally
1. Open Terminal in the project folder and run:
   ```bash
   pip install -r requirements.txt
   uvicorn app:app --port 8080
   ```
2. Open your browser at `http://localhost:8080`.

### Hosted Cloud Version (GCP Cloud Run Free Tier)
When deployed to Google Cloud Run, your team can access the web application at the provided HTTPS URL from any browser without installing Python or dependencies!

### How Non-Technical Team Members Use It:
1. **Choose a Preset:**
   - **⚡ Web Optimized (Default):** Converts to WebP @ 1920px max width (80% quality). Saves 70–90% file size without visible quality loss. Perfect for website uploads and dashboard.
   - **🛍️ Social & Store:** Converts to JPG @ 1200px max width (85% quality). Perfect for product listings, Instagram, and Facebook.
   - **🎨 Lossless PNG:** Lossless PNG with original dimensions. Preserves crisp vector lines and transparency.
   - **⚙️ Custom:** Manual selection of target format, max width, and compression quality.
2. **Add Files or Folders:**
   - Drag & drop images or entire folders into the dropzone.
   - Or click **"Choose Files"** or **"Choose Folder"**.
   - *Auto-Detection:* No need to know whether the files are Apple iPhone `.HEIC`, `.PNG`, `.JPG`, or `.WEBP`. The system automatically detects and converts all of them.
3. **Convert & Download:**
   - Click **"Convert All Images"**.
   - Review file savings percentages and dimensions.
   - Click **"Download All (ZIP)"** to save all converted images at once, or download individual files.

---

## Option 2: Terminal CLI Script

The script now automatically scans the folder and detects all supported image types.

1. Navigate to the folder with images:
   ```bash
   python3 image_converter.py
   ```
2. The script lists all images found (e.g. `10 HEIC, 4 PNG`).
3. Select your output format (default: `webp`) and optional max width (default: `1920px`).
4. Converted images are placed inside a `processed/` folder. Originals remain untouched.

---

## Supported Formats

| Format | Auto-Detected | Notes |
|---|---|---|
| **HEIC / HEIF** | Yes | Apple iPhone / iPad high-efficiency photos |
| **JPG / JPEG** | Yes | Standard photo format |
| **PNG** | Yes | Lossless, alpha transparency support |
| **WEBP** | Yes | Modern high-efficiency web image |
| **TIFF / BMP** | Yes | High-resolution bitmap images |

