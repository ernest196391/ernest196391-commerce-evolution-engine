"""Offline image compositor: clean hero and benefit card from an APPROVED transparent PNG.

No AI, no remote APIs, no background removal. This cannot create a lifestyle scene.
Pillow is an optional dependency. Never overwrite original files.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def _pillow():
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError as exc:
        raise RuntimeError("Instalar Pillow explícitamente en entorno autorizado para usar el compositor.") from exc
    return Image, ImageDraw, ImageFont


def _font(ImageFont, size: int, font_path: str | None):
    if font_path:
        return ImageFont.truetype(font_path, size)
    try:
        return ImageFont.truetype("DejaVuSans.ttf", size)
    except OSError:
        return ImageFont.load_default()


def render_hero(cutout_png: Path, destination: Path, *, size: int = 1200, product_fill: float = 0.82) -> dict:
    Image, ImageDraw, ImageFont = _pillow()
    if not (600 <= size <= 2400):
        raise ValueError("Tamaño fuera de límite")
    if not (0.6 <= product_fill <= 0.9):
        raise ValueError("Ocupación fuera de límite")
    src = Image.open(cutout_png).convert("RGBA")
    bbox = src.getchannel("A").getbbox()
    if bbox is None:
        raise ValueError("Imagen totalmente transparente")
    crop = src.crop(bbox)
    w, h = crop.size
    scale = min(size * product_fill / w, size * product_fill / h)
    new_size = (max(1, round(w * scale)), max(1, round(h * scale)))
    item = crop.resize(new_size, Image.Resampling.LANCZOS)
    background = Image.new("RGBA", (size, size), (255, 255, 255, 255))
    x = (size - new_size[0]) // 2
    y = (size - new_size[1]) // 2
    background.alpha_composite(item, (x, y))
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.resolve() == cutout_png.resolve():
        raise ValueError("No sobrescribir original")
    background.convert("RGB").save(destination, format="PNG", optimize=True)
    return {"output": destination.name, "size": [size, size], "source": str(cutout_png),
            "requires_human_qa": True, "cost_usd_api": 0,
            "note": "Revisar halo, fondo eliminado y partes finas del objeto; composición no garantiza fidelidad."}


def render_benefits(cutout_png: Path, destination: Path, *,
                    headline: str, facts: list[dict], font_path: str | None = None,
                    width: int = 1080, height: int = 1350) -> dict:
    Image, ImageDraw, ImageFont = _pillow()
    if not headline.strip() or len(headline) > 52 or "\n" in headline:
        raise ValueError("Titular vacío o demasiado extenso")
    if len(facts) > 2 or any(not f.get("evidence_id") or not f.get("label") or not f.get("value") for f in facts):
        raise ValueError("Infografía: máximo dos datos con evidencia")
    base = Image.new("RGB", (width, height), (248, 248, 246))
    d = ImageDraw.Draw(base)
    title_font = _font(ImageFont, 54, font_path)
    fact_font = _font(ImageFont, 40, font_path)
    small_font = _font(ImageFont, 30, font_path)
    d.text((60, 75), headline, font=title_font, fill=(26, 39, 42))
    src = Image.open(cutout_png).convert("RGBA")
    bbox = src.getchannel("A").getbbox()
    if not bbox:
        raise ValueError("Sin producto visible")
    crop = src.crop(bbox)
    region = (width - 120, 750)
    factor = min(region[0] / crop.width, region[1] / crop.height)
    new = crop.resize((max(1, int(crop.width * factor)), max(1, int(crop.height * factor))), Image.Resampling.LANCZOS)
    base.paste(new, ((width - new.width) // 2, 200 + (region[1] - new.height) // 2), new)
    for i, fact in enumerate(facts):
        y = 1040 + i * 125
        if len(str(fact["value"])) > 28 or len(str(fact["label"])) > 36:
            raise ValueError("Datos demasiado largos para diseño móvil")
        d.text((75, y), str(fact["value"]), font=fact_font, fill=(26, 39, 42))
        d.text((75, y + 53), str(fact["label"]), font=small_font, fill=(70, 78, 82))
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.resolve() == cutout_png.resolve():
        raise ValueError("No sobrescribir original")
    base.save(destination, format="PNG", optimize=True)
    return {"output": destination.name, "facts": len(facts), "requires_human_qa": True, "cost_usd_api": 0}


def main(argv=None):
    p = argparse.ArgumentParser(description="Componer hero y beneficios gratis desde PNG transparente real")
    p.add_argument("--cutout", type=Path, required=True)
    p.add_argument("--outdir", type=Path, required=True)
    p.add_argument("--headline", required=True)
    p.add_argument("--facts-json", type=Path, required=True)
    p.add_argument("--font", type=str, default=None)
    args = p.parse_args(argv)
    facts = json.loads(args.facts_json.read_text(encoding="utf-8"))
    if not isinstance(facts, list):
        p.error("Se requiere lista de hechos verificados")
    hero = render_hero(args.cutout, args.outdir / "01-hero.png")
    benefits = render_benefits(args.cutout, args.outdir / "03-benefits.png",
                               headline=args.headline, facts=facts, font_path=args.font)
    print(json.dumps({"hero": hero, "benefits": benefits, "other_slots": ["02-lifestyle", "04-details"]},
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
