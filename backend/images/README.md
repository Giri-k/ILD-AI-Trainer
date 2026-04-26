# HRCT Images Directory

This directory contains HRCT (High-Resolution Computed Tomography) chest images for ILD cases.

## Naming Convention

Images are automatically discovered based on the case ID. Use one of these naming patterns:

### Pattern 1 (Recommended): `{case_id}_hrct_{description}.{ext}`
Examples:
- `ild_004_hrct_axial_1.png`
- `ild_004_hrct_axial_2.png`
- `ild_004_hrct_coronal.png`
- `ild_004_hrct_sagittal.png`

### Pattern 2 (Alternative): `{case_id}_{description}.{ext}`
Examples:
- `ild_004_axial_1.png`
- `ild_004_coronal.png`

## Supported Formats
- PNG (`.png`)
- JPEG (`.jpg`)

## How It Works

1. **Automatic Discovery**: When a case is loaded, the system automatically scans this directory for images matching the case ID
2. **No Code Changes Needed**: Just drop images with the correct naming pattern into this directory
3. **Vision Analysis**: When HRCT is ordered, GPT-4 Vision analyzes all images and generates a radiological report
4. **Display in UI**: Images are shown in the chat interface alongside the AI-generated analysis

## Adding Images for a New Case

1. Identify the case ID (e.g., `ild_001`, `ild_002`, `ild_003`, `ild_004`)
2. Name your images following the convention: `{case_id}_hrct_{description}.png`
3. Place them in this directory
4. Restart the backend server
5. Order "HRCT Chest" for that case - images will automatically appear!

## Current Cases with Images

- **ild_004**: Progressive Dyspnea and Joint Stiffness in a 62-Year-Old Woman (RA-ILD)
  - 3 images: 2 axial views, 1 coronal view

## Tips

- Use descriptive names like `axial_1`, `axial_2`, `coronal`, `sagittal` to help identify views
- Keep image file sizes reasonable (< 2MB each) for faster loading
- Use high-quality images for better AI analysis
- Multiple images provide more comprehensive analysis