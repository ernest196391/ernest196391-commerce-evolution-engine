"""Offline technical QA on already-generated images (not AI visual fidelity judge).

This only checks files, geometry and exact white corners of the hero.
Requires human comparison with original for identity, fine edges and claims.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

SLOTS = ("01-hero.png", "02-lifestyle.png", "03-benefits.png", "04-details.png")


def inspect(folder: Path, require_details: bool = False) -> dict:
    try:
        from PIL import Image
    except ImportError as exc:
        raise RuntimeError("Pillow requerido para QA visual técnico") from exc
    reports = []
    all_hashes = []
    for filename in SLOTS:
        file = folder / filename
        if not file.is_file():
            if filename == SLOTS[-1] and not require_details:
                continue
            reports.append({"slot": filename, "status": "missing", "issues": ["pieza_no_generada"]})
            continue
        if file.stat().st_size > 25 * 1024 * 1024:
            reports.append({"slot": filename, "status": "rejected", "issues": ["archivo_excesivo"]})
            continue
        issues = []
        try:
            with Image.open(file) as img:
                img.load()
                w, h = img.size
                if w < 800 or h < 800:
                    issues.append("resolucion_insuficiente")
                if filename == "01-hero.png":
                    if w != h:
                        issues.append("hero_no_cuadrado")
                    rgb = img.convert("RGB")
                    samples = [rgb.getpixel(p) for p in ((0, 0), (w-1, 0), (0, h-1), (w-1, h-1))]
                    if any(px != (255, 255, 255) for px in samples):
                        issues.append("esquinas_no_blancas")
                else:
                    if w * 5 != h * 4:
                        issues.append("formato_no_4_5")
        except Exception as exc:
            issues.append("imagen_ilegible_" + type(exc).__name__)
        digest = hashlib.sha256(file.read_bytes()).hexdigest()
        all_hashes.append((filename, digest))
        reports.append({"slot": filename, "status": "technical_review_required" if not issues else "rejected",
                        "issues": issues, "sha256": digest})
    hashes = {}
    for slot, digest in all_hashes:
        hashes.setdefault(digest, []).append(slot)
    duplicates = [slots for slots in hashes.values() if len(slots)>1]
    for item in reports:
        if any(item["slot"] in slots for slots in duplicates):
            item["issues"].append("contenido_binario_duplicado")
            item["status"] = "rejected"
    return {"schema_version": "0.2", "mode": "read_only", "details_required": require_details,
            "slots": reports, "technical_ready": all(item["status"] == "technical_review_required" for item in reports),
            "human_approval_required": True,
            "warning": "No analiza fidelidad del producto, halos, anatomía, exactitud de etiquetas, texto ni hechos."}


def main(argv=None):
    p = argparse.ArgumentParser(description="QA técnico de tres imágenes y detalle opcional, sin publicar")
    p.add_argument("--dir", required=True, type=Path)
    p.add_argument("--report", required=True, type=Path)
    p.add_argument("--require-details", action="store_true", help="Exigir cuarta pieza si el plan la incluye")
    a = p.parse_args(argv)
    result = inspect(a.dir, require_details=a.require_details)
    a.report.parent.mkdir(parents=True, exist_ok=True)
    a.report.write_text(json.dumps(result, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(f"QA: {a.report}; técnico completo: {result['technical_ready']}; humano requerido")


if __name__ == "__main__":
    main()
