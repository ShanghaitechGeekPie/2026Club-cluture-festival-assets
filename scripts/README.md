# Pillbox generator usage

The generator produces a layered actual-size box PDF, an A4 print PDF, a box preview, a leaflet PDF, a leaflet preview and an editable leaflet SVG.

## Generate the NixOS pillbox

Use Python on Windows with Microsoft YaHei and SimSun installed. Run these commands from the project root, which contains assets.

```powershell
python -m pip install -r assets/scripts/pillbox-generator/requirements.txt
python assets/scripts/pillbox-generator/generate.py --config assets/scripts/pillbox-generator/presets/nixos.json --output assets/existing-assets/pillboxes/nixos/output
```

--config selects a JSON configuration. Omitting it uses the NixOS preset.
--output is required and specifies the destination directory. Existing files with the same names are overwritten.
The bundled vendor directory supplies local Python dependencies.

## Customize a pillbox

Copy pillbox-generator/presets/nixos.json and edit the following fields.

| Field | Purpose |
| --- | --- |
| 名称, 架构 | Product name and installation media architecture |
| 设计日期, 批次, 网站 | Packaging date, batch label and website |
| 主题色 | Background theme color in #RRGGBB format |
| 文字替换 | Original phrases or paragraphs mapped to replacement text |
| 说明书 | Warning text and exactly three columns of titled sections |
| 标志SVG, 背景标志SVG | Logo paths relative to the configuration file. Empty fields use NixOS artwork |
| output_prefix | Output filename prefix using ASCII letters, digits, underscores and hyphens |

To adapt another operating system, update the full box paragraphs and leaflet content as well as the name. The NixOS template contains system-specific descriptions.
Custom logo files must exist at the paths specified in the configuration.

```powershell
python assets/scripts/pillbox-generator/generate.py --config assets/scripts/pillbox-generator/presets/custom.json --output assets/existing-assets/pillboxes/custom/output
```

Create custom.json and its referenced artwork before running this example.

## Check and print

Review both PNG previews for spacing, logo rendering and text overflow.
Print the A4 PDF at 100% actual size. The original dieline is approximately 146 by 224 mm.
Test-fold a paper copy before production.

The generator requires the original PDF in ../existing-assets/pillboxes/debian/reference and the default artwork in ../existing-assets/pillboxes/nixos/artwork.
Keep these assets with the scripts when copying the generator.
