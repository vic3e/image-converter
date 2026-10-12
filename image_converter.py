import os
import sys
from io import BytesIO
from PIL import Image, ImageOps

# Support HEIC/HEIF files from Apple devices
try:
    from pillow_heif import register_heif_opener
    register_heif_opener()
except ImportError:
    print("Warning: 'pillow-heif' is not installed. HEIC conversions will fail.")
    print("Please run: pip install pillow-heif\n")

SUPPORTED_INPUT_EXTENSIONS = (
    '.heic', '.heif', '.jpg', '.jpeg', '.png',
    '.webp', '.bmp', '.tiff', '.tif', '.gif'
)

def detect_supported_files(main_folder):
    """Auto-detect all supported images in a folder and subfolders."""
    found_by_ext = {}
    total_files = []
    for root, dirs, files in os.walk(main_folder):
        if os.path.basename(root).lower() == 'processed':
            continue
        for f in files:
            ext = os.path.splitext(f)[1].lower()
            if ext in SUPPORTED_INPUT_EXTENSIONS:
                total_files.append(os.path.join(root, f))
                found_by_ext[ext] = found_by_ext.get(ext, 0) + 1
    return total_files, found_by_ext

def process_image(img, out_ext, quality=80, max_width=None):
    """EXIF auto-rotation, downscaling, alpha channel handling."""
    try:
        img = ImageOps.exif_transpose(img)
    except Exception:
        pass

    out_ext = f".{out_ext.lstrip('.')}".lower()
    resized = False
    original_size = (img.width, img.height)

    if max_width and img.width > max_width:
        ratio = max_width / float(img.width)
        new_height = max(1, int(img.height * ratio))
        img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
        resized = True

    save_kwargs = {}
    if out_ext in ['.jpg', '.jpeg']:
        if img.mode in ('RGBA', 'LA', 'P'):
            bg = Image.new("RGB", img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            if 'A' in img.mode:
                bg.paste(img, mask=img.split()[-1])
            else:
                bg.paste(img)
            img = bg
        elif img.mode != 'RGB':
            img = img.convert('RGB')
        save_kwargs['quality'] = quality
        save_kwargs['optimize'] = True
    elif out_ext == '.webp':
        if img.mode not in ('RGB', 'RGBA'):
            img = img.convert('RGBA')
        save_kwargs['quality'] = quality
        save_kwargs['method'] = 6
    elif out_ext == '.png':
        save_kwargs['optimize'] = True

    return img, save_kwargs, resized, original_size

def convert_single_image(input_source, output_dest, out_ext, quality=80, max_width=None):
    """Converts a single image from file path or bytes to output file path or BytesIO buffer."""
    out_ext = f".{out_ext.lstrip('.')}".lower()
    with Image.open(input_source) as img:
        processed_img, save_kwargs, resized, original_size = process_image(
            img, out_ext, quality=quality, max_width=max_width
        )
        fmt = 'JPEG' if out_ext in ['.jpg', '.jpeg'] else out_ext.lstrip('.').upper()
        processed_img.save(output_dest, format=fmt, **save_kwargs)
        return {
            'width': processed_img.width,
            'height': processed_img.height,
            'original_width': original_size[0],
            'original_height': original_size[1],
            'resized': resized
        }

def convert_images(main_folder, out_ext, in_ext=None, max_width=None, quality=80):
    """
    Converts images in main_folder.
    If in_ext is None, auto-detects and converts ALL supported image formats found!
    """
    out_ext = f".{out_ext.lstrip('.')}".lower()
    if in_ext:
        in_ext = f".{in_ext.lstrip('.')}".lower()

    files_found = 0
    converted_count = 0

    for root, dirs, files in os.walk(main_folder):
        if os.path.basename(root).lower() == 'processed':
            continue

        matching_files = [
            f for f in files 
            if (f.lower().endswith(in_ext) if in_ext else os.path.splitext(f)[1].lower() in SUPPORTED_INPUT_EXTENSIONS)
        ]

        if not matching_files:
            continue

        files_found += len(matching_files)
        processed_folder = os.path.join(root, 'processed')
        os.makedirs(processed_folder, exist_ok=True)

        for file_name in matching_files:
            base_name = os.path.splitext(file_name)[0]
            new_file_name = f"{base_name}{out_ext}"
            old_file_path = os.path.join(root, file_name)
            new_file_path = os.path.join(processed_folder, new_file_name)

            try:
                stats = convert_single_image(old_file_path, new_file_path, out_ext, quality=quality, max_width=max_width)
                resize_info = f" (resized to {stats['width']}x{stats['height']})" if stats['resized'] else ""
                print(f"✓ Converted: {file_name} -> {new_file_name}{resize_info}")
                converted_count += 1
            except Exception as e:
                print(f"✗ Error converting {file_name}: {e}")

    return files_found, converted_count

if __name__ == "__main__":
    print("=== Universal Image Converter (Auto-Detect Enabled) ===")
    current_directory = os.getcwd()
    
    files, counts = detect_supported_files(current_directory)
    if not files:
        print(f"\nNo supported image files found in '{current_directory}' or its subfolders.")
        print(f"Supported formats: {', '.join(SUPPORTED_INPUT_EXTENSIONS)}")
        input("\nPress Enter to exit...")
        sys.exit(0)

    print(f"\nAuto-detected {len(files)} image(s) in '{current_directory}':")
    for ext, count in sorted(counts.items()):
        print(f"  • {ext.upper()}: {count} file(s)")

    print("\nOptions:")
    print("1. Convert ALL detected images (Default)")
    print("2. Convert only a specific format")
    choice = input("Enter choice [1]: ").strip() or "1"

    selected_in_ext = None
    if choice == "2":
        selected_in_ext = input("Convert ONLY format (e.g. heic, jpg, png): ").strip()

    output_format = input("Convert TO [default: webp, e.g. webp, jpg, png]: ").strip() or "webp"

    width_input = input("Max width in px [default: 1920, type 'none' to skip]: ").strip()
    if width_input.lower() in ('none', 'skip'):
        max_width = None
    elif width_input == "":
        max_width = 1920
    else:
        try:
            max_width = int(width_input)
        except ValueError:
            print("Invalid width entered — using default 1920px.")
            max_width = 1920

    print(f"\nProcessing images to {output_format.upper()} (max width: {max_width or 'Original'})...")
    found, converted = convert_images(current_directory, output_format, in_ext=selected_in_ext, max_width=max_width)
    print(f"\nAll done! Successfully converted {converted} of {found} image(s).")
    print("Output files saved to 'processed/' subfolders.")
    input("\nPress Enter to exit...")
