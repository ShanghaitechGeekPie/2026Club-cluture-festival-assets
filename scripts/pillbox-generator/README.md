# Pillbox generator

Generate a layered actual-size box PDF, an A4 print PDF, a box preview, a leaflet PDF, a leaflet preview and an editable leaflet SVG.

Run from the project root with Python, Microsoft YaHei and SimSun fonts.

```powershell
python -m pip install -r assets/scripts/pillbox-generator/requirements.txt
python assets/scripts/pillbox-generator/generate.py --config assets/scripts/pillbox-generator/presets/ubuntu.json --output assets/existing-assets/pillboxes/ubuntu/output
```

presets/nixos.json and presets/ubuntu.json are working examples.
Copy a preset to customize the product name, architecture, date, batch, website, theme color, text replacements, SVG logos and three-column leaflet content.
Logo paths are relative to the preset file. Empty logo fields use the NixOS artwork.
output_prefix controls output filenames and accepts ASCII letters, numbers, underscores and hyphens.

The original dieline is approximately 146 by 224 mm. Print at 100% actual size.
Review previews and test-fold after changes. Body text has overflow checks.
The original PDF has a SHA-256 check and is located in existing-assets/pillboxes/debian/reference.

Historical analysis scripts are in ../legacy-pillbox-tools and retain their original path assumptions.
Attribution and license details are retained with the source assets.
