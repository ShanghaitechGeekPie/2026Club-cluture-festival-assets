# Pillboxes

- debian/source contains the original Illustrator and TeX sources with their artwork.
- debian/reference contains the original PDF dieline and extracted design elements. The generator reads original-box.pdf here.
- nixos/output contains the generator rebuild. nixos/history/original-output preserves the earlier event files, including the TIFF export.
- ubuntu/output contains the Ubuntu example generated with the reusable generator.
- bundles contains the original combined Debian and NixOS PDF and TIFF archives.

Generated PDFs and previews are in each distribution's output directory.
Generator presets are in ../../scripts/pillbox-generator/presets relative to this directory.
Original attribution and license details are retained in debian/UPSTREAM-README.md and nixos/history/ORIGINAL-README.md.
