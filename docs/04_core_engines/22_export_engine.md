# Export Engine Design: Nomen

This document details the background compilers, vector-to-raster conversion steps, brand guideline PDF generation, and secure file delivery pipeline of Nomen's Export Engine.

---

## 1. Asset Compilation Pipeline

When a user requests a "Brand Identity Package" export, the system triggers an asynchronous Celery task that coordinates the asset generation process:

```text
               [ POST /api/v1/export/bundle ]
                             │
                             ▼
               ┌───────────────────────────┐
               │    FastAPI Task Queue     │ (Enqueues work to Celery)
               └─────────────┬─────────────┘
                             │
            ┌────────────────┴────────────────┐
            ▼                                 ▼
   ┌─────────────────┐               ┌─────────────────┐
   │ 1. Vector SVG   │               │ 2. PDF Guideline│ (ReportLab compiler)
   │ variants builder│               │   generator     │
   └────────┬────────┘               └────────┬────────┘
            │                                 │
            ▼                                 ▼
   ┌─────────────────┐                        │
   │ 3. Headless PNG │                        │
   │ Renderer (cairo)│                        │
   └────────┬────────┘                        │
            │                                 │
            └────────────────┬────────────────┘
                             │
                             ▼
               ┌───────────────────────────┐
               │ 4. ZIP Packer & R2 upload │ (Write to Cloudflare R2 bucket)
               └─────────────┬─────────────┘
                             │
                             ▼
               [ Presigned R2 Download Link ]
```

---

## 2. Package Inventory & Formats

The exported ZIP file contains the following structured asset directory:

```text
brand-package-[name]/
├── logo/
│   ├── logo-horizontal.svg    <-- Editable vector logo layout
│   ├── logo-horizontal.png    <-- High-res raster (300 DPI for web)
│   ├── logo-vertical.svg
│   ├── logo-vertical.png
│   ├── monogram-mark.svg      <-- Stand-alone app icon mark
│   └── monogram-mark.png
├── guidelines/
│   └── brand_guide.pdf        <-- Typography, color rules, and phonetic reports
└── config/
    └── theme-tokens.json      <-- Tailwind CSS configuration snippet
```

---

## 3. Technical Core Implementations

### 3.1. Vector-to-Raster Conversion (Cairo / Weasyprint)
To convert generated SVGs to 300 DPI PNG files inside lightweight Docker worker containers (without installing a massive headless Chrome browser), we use **`cairosvg`**, a Python library backed by standard vector rendering pipelines:
```python
import cairosvg

def convert_svg_to_png(svg_filepath: str, png_filepath: str):
    cairosvg.svg2png(
        url=svg_filepath,
        write_to=png_filepath,
        parent_width=1200,   # Set high res boundary
        parent_height=400,
        dpi=300
    )
```

### 3.2. Brand Guidelines Compiler (ReportLab)
The `brand_guide.pdf` is generated programmatically using **`reportlab`** in Python. The document lays out:
- Page 1: Brand cover (Logo display, name phonetic IPA, and startup mission).
- Page 2: Color guidelines (Primary, secondary, neutral HEX/RGB/HSL codes).
- Page 3: Typography sheets (Google Font import links and CSS declaration samples).

### 3.3. JSON Theme Tokens File
To bridge the gap between design and engineering, we export a `theme-tokens.json` file which fits directly into a developer's Tailwind project:
```json
{
  "theme": {
    "extend": {
      "colors": {
        "brand": {
          "primary": "#3b82f6",
          "secondary": "#1e3a8a",
          "neutral": "#f8fafc"
        }
      },
      "fontFamily": {
        "heading": ["Outfit", "sans-serif"],
        "body": ["Plus Jakarta Sans", "sans-serif"]
      }
    }
  }
}
```

---

## 4. Delivery via Cloudflare R2
1. The Celery worker bundles the assets into a ZIP file in `/tmp`.
2. The worker uploads the ZIP to our private **Cloudflare R2 Object Store** using the `boto3` client.
3. Once uploaded, the worker deletes the temporary files and returns a **Presigned URL** to the database record.
4. The presigned link expires in **1 hour**, keeping our hosting bandwidth costs low and preventing public hot-linking of paid exports.
