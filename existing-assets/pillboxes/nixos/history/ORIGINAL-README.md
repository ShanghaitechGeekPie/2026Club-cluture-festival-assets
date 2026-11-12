# NixOS 小pillboxes：original矢量改编

保留 Debian 小pillboxes v11 的盒型、刀模、折线、斜纹、印刷辅助线与原尺寸；替换 NixOS 标志、蓝色与中文文案。此版为非官方社区改编，盒面标注 x86_64，实际使用时请确认 U 盘镜像架构。

## 文件和打印

- `output/nixos-pillbox-layered-actual-size.pdf`：original 146 × 224 mm 页面，含白底、background-stripes、dielines-and-folds、印刷辅助、NixOS 标志和text六个可见性图层。使用支持 PDF 图层的编辑器打开；编辑text可能需要相应字体。
- `output/nixos-pillbox-a4-print.pdf`：将原尺寸页面居中放进 A4，打印时选“实际大小”或 100%，不要缩放。建议先用普通纸试折，再选择合适的厚纸打印。
- `artwork/`：下载的官方标志源 SVG、logo-attribution。
- `build.py`：可重复build脚本，依赖 `pypdf`、`pypdfium2`、`reportlab`、`PyMuPDF`，以及 Windows 微软雅黑字体。读取 `../deconstruction/original-box.pdf`；脚本会校验上游original PDF 的 SHA-256。

纸盒实际成品尺寸应以original刀模和试折为准。图中的条码和印刷辅助标记沿用原图，不应视为此 NixOS 产品的真实条码或认证。

## 来源和许可

- 原作：[moesoha/debian-media-box](https://github.com/moesoha/debian-media-box)，基于 [v11 发布版 box.pdf](https://github.com/moesoha/debian-media-box/releases/tag/v11) 改编。原作者与贡献者的完整署名见上游 README。本改编采用 [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/) 许可。
- NixOS 官方标志来自 [NixOS/nixos-artwork](https://github.com/NixOS/nixos-artwork/tree/master/logo)，原设计 Simon Frankau，修订 Tim Cuthbertson，按官方仓库说明采用 CC BY 许可。为保证 PDF 内可编辑并消除 SVG 引用兼容问题，标志中的引用被展开为相同矢量路径，渐变以官方的两个蓝色值替代；大号背景标志另作浅色处理。
- 技术内容参考 [NixOS 官方下载页](https://nixos.org/download/) 和 [NixOS 手册](https://nixos.org/manual/nixos/stable/)。
