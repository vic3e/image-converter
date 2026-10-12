# Universal Image Converter (Web & CLI)

A batch image converter that automatically detects image formats (iPhone Apple HEIC, PNG, JPG, WEBP, BMP, TIFF) and converts them into optimized formats with one-click presets or custom controls.

Built with FastAPI, Pillow, and `pillow-heif`, styled according to Zuke design guidelines.

---

## Features

- **Automatic Format Detection**: No need to specify what format images came from. Auto-detects iPhone `.heic`, `.png`, `.jpg`, `.webp`, etc.
- **Minimal, Brand-Aligned Frontend**: Clean drag-and-drop web dashboard with Zuke brand identity (Manrope typography, `#FF8B00` accents).
- **One-Click Presets for Non-Technical Team**:
  - **⚡ Web Optimized (Default)**: WebP · 1920px max · 80% quality (saves 70–90% file size)
  - **🛍️ Social & Store**: JPG · 1200px max · 85% quality
  - **🎨 Lossless PNG**: PNG · Original dimensions · Lossless
  - **⚙️ Custom**: Full control over output format, max dimensions, and compression quality.
- **Folder & Batch Support**: Drop individual files or entire folders.
- **Download All (ZIP)**: Download converted files in a single zip archive with one click.
- **EXIF Auto-Rotation**: Automatically fixes orientation for mobile photos so portraits don't appear sideways.
- **GCP Free Tier Ready**: Deployable to Google Cloud Run under the Always Free tier.

---

## Quickstart (Web UI)

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Start the web application:
   ```bash
   uvicorn app:app --port 8080 --reload
   ```
3. Open `http://localhost:8080` in your browser.

---

## Quickstart (Terminal CLI)

```bash
python3 image_converter.py
```
The script will auto-detect all images in the folder and guide you through conversion.

---

## Deploying to Google Cloud Run (Free Tier)

Google Cloud Run offers 2 million requests/month and scale-to-zero for free.

```bash
gcloud run deploy image-converter \
  --source . \
  --project the-zuke-project \
  --region us-central1 \
  --allow-unauthenticated \
  --min-instances 0 \
  --max-instances 2 \
  --memory 512Mi \
  --cpu 1
```

