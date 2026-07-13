# How to Use the Image Converter

## One-time setup

Before using this tool for the first time, install the required packages.
Open a Terminal and run:

```
pip install Pillow pillow-heif
```

---

## Step-by-step instructions

### 1. Place your images

Put the script (`image_converter.py`) in the folder that contains your images,
or in a parent folder with subfolders of images. For example:

```
📁 Photos/
   image_converter.py   ← script goes here
   📁 Beach/
      IMG_001.heic
      IMG_002.heic
   📁 Family/
      IMG_003.heic
```

### 2. Run the script

Open a Terminal, navigate to the folder, and run:

```
python image_converter.py
```

Or on some systems:

```
python3 image_converter.py
```

### 3. Answer the prompts

The script will ask three questions:

**Convert FROM** — the format your images are currently in.
Examples: `heic`, `jpg`, `png`

**Convert TO** — the format you want to convert to.
Examples: `jpg`, `webp`, `png`

**Max width in px** — optionally resize images down to a max width.
- Type a number like `1920` or `1280` to resize
- Press **Enter** (leave blank) to keep the original size

### 4. Find your converted images

Converted files are saved into a `processed/` folder inside each folder where
images were found. Your originals are never touched.

```
📁 Photos/
   📁 Beach/
      IMG_001.heic          ← original, untouched
      IMG_002.heic
      📁 processed/
         IMG_001.jpg        ← converted output
         IMG_002.jpg
   📁 Family/
      IMG_003.heic
      📁 processed/
         IMG_003.jpg
```

---

## Supported formats

| Format | Notes                              |
|--------|------------------------------------|
| HEIC   | iPhone/iPad photos (requires setup)|
| JPG    | Most compatible, smaller file size |
| PNG    | Lossless, supports transparency    |
| WEBP   | Modern web format, small & sharp   |

---

## Troubleshooting

**"pillow-heif is not installed"** — Run `pip install pillow-heif` and try again.

**"No files found"** — Make sure you typed the correct input format and that
the script is in the right folder.

**Script won't open** — Make sure Python is installed. Download it from
[python.org](https://www.python.org/downloads/).
