"""Editorial triage for product catalogs (not verified SEO ranking).

Pure Python, offline, read-only. No machine-created product claims.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import html
import json
import re
from collections import Counter
from pathlib import Path
from .audit import normalize, plain, image_count

TEMPLATES = re.compile(r"\b(?:excelente calidad|alta calidad|ideal para (?:todo|cualquier)|producto de calidad|la mejor opci[oó]n|s[uú]per oferta|imperdible)\b", re.I)
CLAIMS = re.compile(r"\b(?:hasta|garanti[az]a?|\d+\s*(?:horas?|h|mah|watts?|w|voltios?|v|kg|cm|mm|litros?|l))\b", re.I)
SPEC_HINT = re.compile(r"\b(?:medid[ao]s?|dimensiones|capacidad|potencia|material|modelo|marca|voltaje|alimentaci[oó]n|autonom[ií]a|peso|incluye|tama[nñ]o)\b", re.I)
SENTENCES = re.compile(r"[.!?]+")
WS = re.compile(r"\s+")


def triage(row: dict, *, tenant_id: str = "sample") -> dict:
    """Return review priority, not a truth or visual-quality verdict."""
    p = normalize(row)
    title = plain(p["name"])
    description = plain(p["description"])
    short = plain(p["short_description"])
    images = image_count(p["images"])
    flags = []
    score = 100

    def mark(flag: str, penalty: int):
        nonlocal score
        flags.append(flag)
        score -= penalty

    if not title or len(title) < 15:
        mark("titulo_ausente_o_poco_informativo", 16)
    if len(title) > 95:
        mark("titulo_demasiado_extenso_revisar", 6)
    if title and title.isupper() and len(title) > 12:
        mark("titulo_todo_mayusculas", 5)
    if not description:
        mark("descripcion_ausente", 25)
    elif len(description) < 180:
        mark("descripcion_no_suficiente_para_decidir", 19)
    if not short:
        mark("descripcion_corta_ausente", 15)
    elif len(short) < 35:
        mark("descripcion_corta_poco_informativa", 9)
    if description and len(set(WS.sub(" ", description.lower()).split())) < 12:
        mark("vocabulario_limitado", 6)
    if description and not SPEC_HINT.search(description):
        mark("sin_senales_de_especificaciones_comprobar", 12)
    if description and TEMPLATES.search(description):
        mark("lenguaje_generico_promocional", 8)
    if description and CLAIMS.search(description):
        # Claim presence is NOT an error, but it requires source attribution.
        flags.append("afirmaciones_tecnicas_requieren_fuente")
    if title and short and WS.sub(" ", title.lower()) == WS.sub(" ", short.lower()):
        mark("descripcion_corta_repite_titulo", 12)
    if images < 3:
        mark("referencias_imagen_insuficientes", 15 if images == 0 else 8)
    # Duplicate URLs, broken images, altered photos and false specs require separate review.
    record_key = "|".join([tenant_id, p["id"], p["sku"], p["name"]])
    record_hash = hashlib.sha256(record_key.encode("utf-8")).hexdigest()[:16]
    review_state = "needs_human_review" if flags else "automated_checks_passed_review_still_required"
    return {"tenant_id": tenant_id, "id": p["id"], "sku": p["sku"], "name": title,
            "review_key": record_hash, "editorial_score": max(0, score),
            "flags": flags, "image_references": images,
            "review_state": review_state, "original_description_chars": len(description),
            "original_short_chars": len(short)}


def analyze(path: Path, *, tenant_id: str = "sample") -> dict:
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames or not any(x in reader.fieldnames for x in ("name", "Name")):
            raise ValueError("CSV requiere encabezado name/Name")
        records = [triage(row, tenant_id=tenant_id) for row in reader]
    records.sort(key=lambda x: (x["editorial_score"], x["sku"], x["id"]))
    counts = Counter(flag for row in records for flag in row["flags"])
    return {"schema_version": "0.1", "mode": "read_only",
            "disclaimer": "Heurísticas para priorizar revisión; NO comprueba veracidad, ranking SEO, fidelidad de fotos o conversión.",
            "total_products": len(records), "flag_counts": dict(counts), "products": records}


def main(argv=None):
    parser = argparse.ArgumentParser(description="Diagnóstico editorial orientativo sin cambios de catálogo")
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--outdir", required=True, type=Path)
    parser.add_argument("--tenant", default="demo")
    args = parser.parse_args(argv)
    report = analyze(args.input, tenant_id=args.tenant)
    args.outdir.mkdir(parents=True, exist_ok=True)
    (args.outdir / "editorial-report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    with (args.outdir / "editorial-priorities.csv").open("w", encoding="utf-8", newline="") as f:
        columns = ["tenant_id", "id", "sku", "name", "review_key", "editorial_score", "image_references",
                   "review_state", "original_description_chars", "original_short_chars", "flags"]
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        for p in report["products"]:
            writer.writerow({**p, "flags": "|".join(p["flags"])})
    print(f"Evaluados: {report['total_products']}; salida: {args.outdir}")


if __name__ == "__main__":
    main()
