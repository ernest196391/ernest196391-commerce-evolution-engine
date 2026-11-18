"""Offline, read-only product CSV quality audit. Standard library only.

The score is a review heuristic, NOT a validated SEO or image quality score.
"""

from __future__ import annotations

import argparse
import csv
import html
import json
import re
from collections import Counter
from pathlib import Path

COLS = {
    "id": ("id", "ID"),
    "name": ("name", "Name"),
    "description": ("description", "Description"),
    "short_description": ("short_description", "Short description", "Short Description"),
    "images": ("images", "Images"),
    "sku": ("sku", "SKU"),
    "status": ("status", "Status", "Published"),
    "categories": ("categories", "Categories"),
}
GENERIC = re.compile(r"^(producto|artículo|articulo|oferta|varios?|nuevo|sin nombre)(?:\s+\d+)?$", re.I)
TAG = re.compile(r"<[^>]+>")


def plain(value: str) -> str:
    text = html.unescape(TAG.sub(" ", value or ""))
    return " ".join(text.split())


def normalize(row: dict) -> dict:
    return {key: next((str(row.get(alias) or "") for alias in options if alias in row), "") for key, options in COLS.items()}


def image_count(value: str) -> int:
    if not value.strip():
        return 0
    # WooCommerce exports comma-separated images, while the demo uses pipes.
    return len([i.strip() for i in re.split(r"[|,]", value) if i.strip()])


def audit(row: dict) -> dict:
    r = normalize(row)
    title = plain(r["name"])
    description = plain(r["description"])
    short = plain(r["short_description"])
    count = image_count(r["images"])
    findings = []
    score = 100

    def issue(name: str, penalty: int):
        nonlocal score
        findings.append(name)
        score -= penalty

    if not title:
        issue("titulo_ausente", 25)
    elif GENERIC.fullmatch(title):
        issue("titulo_generico", 20)
    elif len(title) < 12:
        issue("titulo_muy_corto", 10)
    if not description:
        issue("descripcion_ausente", 25)
    elif len(description) < 100:
        issue("descripcion_breve_revisar", 12)
    if not short:
        issue("descripcion_corta_ausente", 15)
    elif len(short) < 25:
        issue("descripcion_corta_breve_revisar", 8)
    if not count:
        issue("sin_imagen_referenciada", 25)
    elif count < 4:
        issue("menos_de_cuatro_imagenes_referenciadas", 10)
    return {
        "id": r["id"], "sku": r["sku"], "name": title,
        "score": max(0, score), "image_references": count,
        "description_chars": len(description), "short_description_chars": len(short),
        "findings": findings,
    }


def analyze(path: Path) -> dict:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            raise ValueError("CSV sin cabecera")
        if "name" not in reader.fieldnames and "Name" not in reader.fieldnames:
            raise ValueError("Falta columna name/Name")
        audited = [audit(r) for r in reader]
    finding_counts = Counter(issue for product in audited for issue in product["findings"])
    audited.sort(key=lambda x: (x["score"], x["id"], x["sku"]))
    return {
        "schema_version": "0.1", "input_rows": len(audited),
        "score_note": "Heurística de revisión; no evalúa fotos reales, SEO profesional ni veracidad técnica.",
        "findings_counts": dict(sorted(finding_counts.items())), "products": audited,
    }


def main(argv=None):
    p = argparse.ArgumentParser(description="Auditoría offline de CSV de productos; no publica")
    p.add_argument("--input", required=True, type=Path)
    p.add_argument("--outdir", required=True, type=Path)
    args = p.parse_args(argv)
    report = analyze(args.input)
    args.outdir.mkdir(parents=True, exist_ok=True)
    (args.outdir / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    with (args.outdir / "priorities.csv").open("w", encoding="utf-8", newline="") as f:
        fields = ["id", "sku", "name", "score", "image_references", "description_chars", "short_description_chars", "findings"]
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in report["products"]:
            writer.writerow({**row, "findings": "|".join(row["findings"])})
    print(f"Auditados: {report['input_rows']}; resultados: {args.outdir / 'report.json'} y {args.outdir / 'priorities.csv'}")


if __name__ == "__main__":
    main()
