# NixOS pillbox

output contains the latest generator rebuild, including the layered box PDF, A4 print PDF, leaflet PDF, SVG and previews.
artwork contains the logo source SVGs and attribution.
source contains the original leaflet SVG and content configuration.
history/original-output contains the original event exports, including the TIFF.

From the project root, rebuild with

```powershell
python assets/scripts/pillbox-generator/generate.py --config assets/scripts/pillbox-generator/presets/nixos.json --output assets/existing-assets/pillboxes/nixos/output
```
