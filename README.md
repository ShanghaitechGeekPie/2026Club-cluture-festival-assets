# 2026 社团文化节部分资产

为2026社团文化节准备的3d打印小玩具和小药盒生成器，包含奶蛋模型，Debian/Nix小药盒，以及一个药盒生成器。

Debian药盒来自于[GitHub - moesoha/debian-media-box: “Debian 小药盒”，一个用来包装 Debian 安装介质的盒子设计和介绍用的说明书。 · GitHub](https://github.com/moesoha/debian-media-box)

## 使用

对于包装盒，建议使用足够大的 300g 铜版纸的光面打印出包装盒 TIF 文件（推荐）或者 PDF 文档的第一页，之后沿线裁下并粘胶折叠即可。（注意：喷墨打印机打光面铜版纸很容易掉色。）为了方便制作纸盒，有加入部分辅助线，如果感觉影响美观可以自行删去。

奶蛋可以直接拿去打印，随便玩。

## AI写的说明

This directory contains the retained event design assets and pillbox generation scripts.

```text
assets/
├── scripts/
│   ├── pillbox-generator/
│   ├── legacy-pillbox-tools/
│   └── README.md
├── existing-assets/
│   ├── pillboxes/
│   │   ├── debian/
│   │   ├── nixos/
│   │   └── bundles/
│   ├── naidan-model/
│   └── final-posters/
└── README.md
```

## Scripts

[Generator usage](scripts/README.md) covers installation, NixOS generation, configuration and printing.
pillbox-generator contains the generator, layout code, presets and bundled dependencies.
legacy-pillbox-tools retains the earlier extraction and analysis scripts.

## Existing assets

- [Pillboxes](existing-assets/pillboxes/) contains Debian source designs and reference dielines, NixOS artwork and outputs, and combined PDF/TIFF archives in bundles.
- [Naidan model](existing-assets/naidan-model/) contains seven STL components in parts and the original ZIP archive.
- [Final posters](existing-assets/final-posters/) contains editable PSD files in source and final JPG files in exports. Version selection details are recorded in VERSION-NOTES.md.
