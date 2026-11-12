"""Generate a layered box, an actual-size A4 sheet and a leaflet from JSON."""
import argparse
import importlib.util
import json
import re
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

HERE = Path(__file__).resolve().parent


def load(name):
    spec = importlib.util.spec_from_file_location(name, HERE / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=HERE / "presets" / "nixos.json")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    config = json.loads(args.config.read_text(encoding="utf-8"))
    if not config["名称"] or any(c in config["名称"] for c in '/\\'):
        raise ValueError("名称不能包含路径分隔符")
    color = config["主题色"]
    prefix = config.get("output_prefix", "nixos-pillbox")
    if not re.fullmatch(r"[A-Za-z0-9_-]+", prefix):
        raise ValueError("output_prefix must contain only ASCII letters, numbers, hyphens or underscores")
    if not re.fullmatch(r"#[0-9a-fA-F]{6}", color):
        raise ValueError("主题色须为 #RRGGBB")
    rgb = tuple(int(color[i:i+2], 16) / 255 for i in (1, 3, 5))
    replacements = {
        "NixOS": config["名称"],
        "x86_64": config["架构"],
        "2026-10-28": config["设计日期"],
        "20261028": config["批次"],
        "www.nixos.org": config["网站"],
        **config.get("文字替换", {}),
    }

    def replace(text):
        pattern = "|".join(re.escape(key) for key in sorted(replacements, key=len, reverse=True))
        return re.sub(pattern, lambda match: replacements[match.group()], text)

    box = load("box_layout")
    leaflet = load("leaflet_layout")
    original_draw, original_para = box.draw_text, box.para
    box.draw_text = lambda c, x, y, s, *a, **kw: original_draw(c, x, y, replace(s), *a, **kw)
    box.para = lambda c, x, y, s, *a, **kw: original_para(c, x, y, replace(s), *a, **kw)
    # Keep the upstream content-stream classification and recolor its forms.
    box.THEME_RGB = rgb
    box.PRODUCT_NAME = config["名称"]
    original_svg = box.clean_svg

    def svg(path, pale=False, wordmark=False):
        custom = config.get("标志SVG" if wordmark else "背景标志SVG")
        if custom:
            source = (args.config.resolve().parent / custom).resolve()
            root = ET.fromstring(source.read_bytes())
            # MuPDF does not resolve SVG stylesheet class fills.
            fills = {}
            for style in root.findall(".//{http://www.w3.org/2000/svg}style"):
                for classes, value in re.findall(r"([^{}]+)\{([^{}]+)\}", style.text or ""):
                    fill = re.search(r"fill\s*:\s*([^;]+)", value)
                    if fill:
                        for name in classes.split(","):
                            fills[name.strip().lstrip(".")] = fill.group(1)
            for element in root.iter():
                for name in element.get("class", "").split():
                    if name in fills:
                        element.set("fill", fills[name])
            with box.fitz.open("svg", ET.tostring(root)) as doc:
                return box.fitz.open("pdf", doc.convert_to_pdf())
        return original_svg(box.ROOT / "artwork" / path.name, pale=pale, wordmark=wordmark)

    box.clean_svg = svg
    leaflet.box = box
    original_text, original_body = leaflet.text, leaflet.para
    leaflet.text = lambda c, x, y, s, *a, **kw: original_text(c, x, y, replace(s), *a, **kw)
    leaflet.para = lambda c, x, y, s, *a, **kw: original_body(c, x, y, replace(s), *a, **kw)
    content = config["说明书"]
    if len(content["栏目"]) != 3:
        raise ValueError("说明书需要三栏")
    leaflet.WARNING, leaflet.COLS = content["警示语"], content["栏目"]
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    # Complete both builds before publishing their files.
    with tempfile.TemporaryDirectory(dir=output) as temp:
        stage = Path(temp)
        box.OUT = leaflet.OUT = stage
        leaflet.ROOT = stage
        box.make()
        leaflet.build()
        for file in stage.iterdir():
            if file.suffix == ".pdf":
                with box.fitz.open(file) as document:
                    metadata = document.metadata
                    metadata["title"] = replace(metadata.get("title", ""))
                    if config.get("标志SVG"):
                        metadata["author"] = "Adapted from moesoha/debian-media-box"
                    document.set_metadata(metadata)
                    document.saveIncr()
            target = output / file.name.replace("nixos-pillbox", prefix)
            if target.parent != output or not config["名称"] or any(c in config["名称"] for c in '/\\'):
                raise ValueError("名称不能包含路径分隔符")
            target.write_bytes(file.read_bytes())
    print("输出目录", output)


if __name__ == "__main__":
    main()
