import os
import shutil
import time
import uuid
import zipfile
from io import BytesIO
from typing import List, Optional

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, Response

from image_converter import (
    SUPPORTED_INPUT_EXTENSIONS,
    convert_single_image,
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SESSIONS_DIR = os.path.join("/tmp", "image_converter_sessions")
os.makedirs(SESSIONS_DIR, exist_ok=True)

app = FastAPI(title="Zuke Image Converter", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def cleanup_old_sessions(max_age_seconds: int = 3600):
    """Removes session directories older than max_age_seconds (default 1 hour)."""
    now = time.time()
    try:
        for item in os.listdir(SESSIONS_DIR):
            folder = os.path.join(SESSIONS_DIR, item)
            if os.path.isdir(folder):
                mtime = os.path.getmtime(folder)
                if now - mtime > max_age_seconds:
                    shutil.rmtree(folder, ignore_errors=True)
    except Exception as e:
        print(f"Cleanup error: {e}")

@app.get("/health")
def health_check():
    return {"status": "ok", "app": "zuke-image-converter"}

@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    return Response(status_code=204)

@app.get("/", response_class=HTMLResponse)
def index():
    html_path = os.path.join(BASE_DIR, "templates", "index.html")
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>Zuke Image Converter</h1>")
def resolve_preset_settings(preset: str, format: Optional[str] = None, max_width: Optional[str] = None, quality: Optional[str] = None):
    target_format = "webp"
    target_width = 1920
    target_quality = 80

    if preset == "ecommerce":
        target_format = "jpg"
        target_width = 1200
        target_quality = 85
    elif preset == "lossless":
        target_format = "png"
        target_width = None
        target_quality = 100
    elif preset == "custom":
        if format:
            target_format = format.strip().lower().lstrip(".")
        if max_width:
            w_str = max_width.strip().lower()
            if w_str in ("none", "original", "", "0"):
                target_width = None
            else:
                try:
                    target_width = int(w_str)
                except ValueError:
                    target_width = 1920
        if quality:
            try:
                target_quality = max(10, min(100, int(quality)))
            except ValueError:
                target_quality = 80

    return target_format, target_width, target_quality

@app.post("/api/session/start")
def session_start():
    cleanup_old_sessions()
    session_id = str(uuid.uuid4())
    session_dir = os.path.join(SESSIONS_DIR, session_id)
    converted_dir = os.path.join(session_dir, "converted")
    os.makedirs(converted_dir, exist_ok=True)
    return {"success": True, "session_id": session_id}

@app.post("/api/session/{session_id}/convert-file")
async def session_convert_file(
    session_id: str,
    file: UploadFile = File(...),
    preset: str = Form("web"),
    format: Optional[str] = Form(None),
    max_width: Optional[str] = Form(None),
    quality: Optional[str] = Form(None)
):
    session_dir = os.path.join(SESSIONS_DIR, session_id)
    converted_dir = os.path.join(session_dir, "converted")
    if not os.path.exists(converted_dir):
        os.makedirs(converted_dir, exist_ok=True)

    target_format, target_width, target_quality = resolve_preset_settings(preset, format, max_width, quality)
    target_ext = f".{target_format}"

    clean_name = os.path.basename(file.filename or "image")
    base_name, in_ext = os.path.splitext(clean_name)
    file_bytes = await file.read()
    orig_size = len(file_bytes)
    detected_ext = in_ext.lower().lstrip(".") or "auto"

    out_filename = f"{base_name}{target_ext}"
    out_filepath = os.path.join(converted_dir, out_filename)
    counter = 1
    while os.path.exists(out_filepath):
        out_filename = f"{base_name}_{counter}{target_ext}"
        out_filepath = os.path.join(converted_dir, out_filename)
        counter += 1

    try:
        stats = convert_single_image(
            BytesIO(file_bytes),
            out_filepath,
            target_ext,
            quality=target_quality,
            max_width=target_width
        )
        converted_size = os.path.getsize(out_filepath)
        savings = 0.0
        if orig_size > 0:
            savings = round(((orig_size - converted_size) / orig_size) * 100, 1)

        return JSONResponse({
            "success": True,
            "file": {
                "id": str(uuid.uuid4())[:8],
                "original_name": clean_name,
                "detected_format": detected_ext.upper(),
                "converted_name": out_filename,
                "target_format": target_format.upper(),
                "original_size": orig_size,
                "converted_size": converted_size,
                "savings_percent": savings,
                "width": stats["width"],
                "height": stats["height"],
                "resized": stats["resized"],
                "status": "success",
                "download_url": f"/api/download/{session_id}/{out_filename}",
                "preview_url": f"/api/preview/{session_id}/{out_filename}"
            }
        })
    except Exception as e:
        return JSONResponse({
            "success": False,
            "file": {
                "id": str(uuid.uuid4())[:8],
                "original_name": clean_name,
                "detected_format": detected_ext.upper(),
                "converted_name": out_filename,
                "target_format": target_format.upper(),
                "original_size": orig_size,
                "converted_size": 0,
                "savings_percent": 0,
                "width": 0,
                "height": 0,
                "resized": False,
                "status": "error",
                "error": str(e)
            }
        })

@app.post("/api/session/{session_id}/finalize")
def session_finalize(session_id: str):
    session_dir = os.path.join(SESSIONS_DIR, session_id)
    converted_dir = os.path.join(session_dir, "converted")
    if not os.path.exists(converted_dir):
        raise HTTPException(status_code=404, detail="Session not found.")

    converted_files = [f for f in os.listdir(converted_dir) if os.path.isfile(os.path.join(converted_dir, f)) and not f.endswith(".zip")]
    zip_url = None
    if converted_files:
        zip_path = os.path.join(session_dir, "converted_images.zip")
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for fname in converted_files:
                zf.write(os.path.join(converted_dir, fname), arcname=fname)
        zip_url = f"/api/download-zip/{session_id}"

    return {"success": True, "session_id": session_id, "zip_url": zip_url, "total_converted": len(converted_files)}

@app.post("/api/convert")
async def convert_api(
    files: List[UploadFile] = File(...),
    preset: str = Form("web"),
    format: Optional[str] = Form(None),
    max_width: Optional[str] = Form(None),
    quality: Optional[str] = Form(None)
):
    cleanup_old_sessions()
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded.")

    target_format, target_width, target_quality = resolve_preset_settings(preset, format, max_width, quality)
    session_id = str(uuid.uuid4())
    session_dir = os.path.join(SESSIONS_DIR, session_id)
    converted_dir = os.path.join(session_dir, "converted")
    os.makedirs(converted_dir, exist_ok=True)

    results = []
    total_original_size = 0
    total_converted_size = 0
    target_ext = f".{target_format}"

    for upload_file in files:
        clean_name = os.path.basename(upload_file.filename or "image")
        base_name, in_ext = os.path.splitext(clean_name)
        file_bytes = await upload_file.read()
        orig_size = len(file_bytes)
        total_original_size += orig_size
        detected_ext = in_ext.lower().lstrip(".") or "auto"

        out_filename = f"{base_name}{target_ext}"
        out_filepath = os.path.join(converted_dir, out_filename)
        counter = 1
        while os.path.exists(out_filepath):
            out_filename = f"{base_name}_{counter}{target_ext}"
            out_filepath = os.path.join(converted_dir, out_filename)
            counter += 1

        try:
            stats = convert_single_image(
                BytesIO(file_bytes),
                out_filepath,
                target_ext,
                quality=target_quality,
                max_width=target_width
            )
            converted_size = os.path.getsize(out_filepath)
            total_converted_size += converted_size
            savings = 0.0
            if orig_size > 0:
                savings = round(((orig_size - converted_size) / orig_size) * 100, 1)

            results.append({
                "id": str(uuid.uuid4())[:8],
                "original_name": clean_name,
                "detected_format": detected_ext.upper(),
                "converted_name": out_filename,
                "target_format": target_format.upper(),
                "original_size": orig_size,
                "converted_size": converted_size,
                "savings_percent": savings,
                "width": stats["width"],
                "height": stats["height"],
                "resized": stats["resized"],
                "status": "success",
                "download_url": f"/api/download/{session_id}/{out_filename}",
                "preview_url": f"/api/preview/{session_id}/{out_filename}"
            })
        except Exception as e:
            results.append({
                "id": str(uuid.uuid4())[:8],
                "original_name": clean_name,
                "detected_format": detected_ext.upper(),
                "converted_name": out_filename,
                "target_format": target_format.upper(),
                "original_size": orig_size,
                "converted_size": 0,
                "savings_percent": 0,
                "width": 0,
                "height": 0,
                "resized": False,
                "status": "error",
                "error": str(e)
            })

    successful_conversions = [r for r in results if r["status"] == "success"]
    zip_url = None
    if successful_conversions:
        zip_path = os.path.join(session_dir, "converted_images.zip")
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for r in successful_conversions:
                f_path = os.path.join(converted_dir, r["converted_name"])
                if os.path.exists(f_path):
                    zf.write(f_path, arcname=r["converted_name"])
        zip_url = f"/api/download-zip/{session_id}"

    total_savings = 0.0
    if total_original_size > 0 and total_converted_size > 0:
        total_savings = round(((total_original_size - total_converted_size) / total_original_size) * 100, 1)

    return JSONResponse({
        "success": True,
        "session_id": session_id,
        "preset_used": preset,
        "target_format": target_format,
        "total_files": len(files),
        "successful_count": len(successful_conversions),
        "total_original_size": total_original_size,
        "total_converted_size": total_converted_size,
        "total_savings_percent": total_savings,
        "zip_url": zip_url,
        "files": results
    })


@app.get("/api/download/{session_id}/{filename}")
def download_file(session_id: str, filename: str):
    file_path = os.path.join(SESSIONS_DIR, session_id, "converted", filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found or expired.")
    return FileResponse(path=file_path, filename=filename, media_type="application/octet-stream")

@app.get("/api/preview/{session_id}/{filename}")
def preview_file(session_id: str, filename: str):
    file_path = os.path.join(SESSIONS_DIR, session_id, "converted", filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found or expired.")
    ext = os.path.splitext(filename)[1].lower()
    media_map = {".webp": "image/webp", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png"}
    return FileResponse(path=file_path, media_type=media_map.get(ext, "image/jpeg"))

@app.get("/api/download-zip/{session_id}")
def download_zip(session_id: str):
    zip_path = os.path.join(SESSIONS_DIR, session_id, "converted_images.zip")
    if not os.path.exists(zip_path):
        raise HTTPException(status_code=404, detail="ZIP archive not found or expired.")
    return FileResponse(path=zip_path, filename=f"converted_images_{session_id[:8]}.zip", media_type="application/zip")
