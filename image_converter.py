import os
from PIL import Image

# Import and register HEIF opener to support HEIC files from Apple devices
try:
    from pillow_heif import register_heif_opener
    register_heif_opener()
except ImportError:
    print("Warning: 'pillow-heif' is not installed. HEIC conversions will fail.")
    print("Please run: pip install pillow-heif\n")

def convert_images(main_folder, in_ext, out_ext, max_width=None):
    # Ensure extensions start with a dot (e.g., "heic" -> ".heic")
    in_ext = f".{in_ext.lstrip('.')}".lower()
    out_ext = f".{out_ext.lstrip('.')}".lower()
    
    files_found = False

    # Traverse all directories (including the one the script is placed in)
    for root, dirs, files in os.walk(main_folder):
        # Skip 'processed' folders so we don't accidentally scan them
        if os.path.basename(root).lower() == 'processed':
            continue

        # Check if there are any files matching our input extension in this folder
        matching_files = [f for f in files if f.lower().endswith(in_ext)]
        
        if not matching_files:
            continue # Move to the next folder if no matching files are found
            
        files_found = True
        
        # Create a 'processed' folder right here where we found the files
        processed_folder = os.path.join(root, 'processed')
        os.makedirs(processed_folder, exist_ok=True)

        # Process the files
        for file_name in matching_files:
            # Get the original file name without the extension
            base_name = os.path.splitext(file_name)[0]
            new_file_name = f"{base_name}{out_ext}"

            old_file_path = os.path.join(root, file_name)
            new_file_path = os.path.join(processed_folder, new_file_name)

            # Convert it
            convert_image(old_file_path, new_file_path, out_ext, max_width=max_width)
            
    if not files_found:
        print(f"\nNo files ending with '{in_ext}' were found in this folder or its subfolders.")

def convert_image(input_path, output_path, out_ext, quality=80, max_width=None):
    try:
        with Image.open(input_path) as img:
            # Fix transparency issues (e.g., converting HEIC/PNG to JPG)
            if out_ext in ['.jpg', '.jpeg'] and img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert("RGB")
            
            # Resize if a max_width is set and the image is wider than it
            resized = False
            if max_width and img.width > max_width:
                ratio = max_width / img.width
                new_size = (max_width, int(img.height * ratio))
                img = img.resize(new_size, Image.LANCZOS)
                resized = True
            
            # Save the image
            if out_ext in ['.jpg', '.jpeg', '.webp']:
                img.save(output_path, quality=quality)
            else:
                img.save(output_path)
                
            resize_info = f" (resized to {img.width}x{img.height})" if resized else ""
            print(f"Success: {os.path.basename(input_path)} -> {os.path.basename(output_path)}{resize_info}")
    except Exception as e:
        print(f"Error converting {input_path}: {e}")

if __name__ == "__main__":
    print("=== Universal Image Converter ===")
    
    # Ask the user for formats
    input_format = input("Convert FROM (e.g. heic, jpg, png): ").strip()
    output_format = input("Convert TO (e.g. png, webp, jpg): ").strip()

    # Ask for max width (optional, default 1920)
    width_input = input("Max width in px [default: 1920, press Enter to skip resizing]: ").strip()
    if width_input == "":
        max_width = None
    else:
        try:
            max_width = int(width_input)
        except ValueError:
            print("Invalid width entered — skipping resize.")
            max_width = None

    if not input_format or not output_format:
        print("Error: You must provide both an input and output format.")
    else:
        # Get the directory where the script is currently sitting
        current_directory = os.getcwd()
        
        print(f"\nScanning '{current_directory}' for {input_format.upper()} files...")
        convert_images(current_directory, input_format, output_format, max_width=max_width)
        
        print("\nAll done!")
        
    # Keeps the window open if you double-click the script in Windows
    input("Press Enter to exit...")