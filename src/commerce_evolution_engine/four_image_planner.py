"""Plan four evidence-aware product images without calling any image provider.

This module produces a *manifest and prompts*, not pictures.
It requires a real reference image (local path/asset id) and a review gate.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

SLOTS = ("hero", "lifestyle", "benefits", "details")
DEFAULTS = {
    "hero": {"aspect_ratio": "1:1", "channel": "catalog", "source_mode": "reference_composite"},
    "lifestyle": {"aspect_ratio": "4:5", "channel": "ads_and_gallery", "source_mode": "reference_edit"},
    "benefits": {"aspect_ratio": "4:5", "channel": "ads_and_gallery", "source_mode": "reference_edit_and_svg_overlay"},
    "details": {"aspect_ratio": "4:5", "channel": "gallery", "source_mode": "real_crop_and_svg_overlay"},
}
PROHIBITIONS = [
    "No cambiar marca, modelo, proporciones, color, número de aspas o botones.",
    "No añadir accesorios, enchufes, conexiones o funciones inexistentes.",
    "No utilizar imágenes de Amazon ni de otros comerciantes como originales.",
    "No presentar un render como fotografía documental ni un dato anunciado como medición propia.",
    "Si un componente no se ve en referencias reales, no inventar un acercamiento.",
]


def build(product: dict) -> dict:
    if not isinstance(product, dict):
        raise ValueError("Se requiere JSON de objeto")
    required = ("tenant_id", "product_id", "name", "source_image")
    for field in required:
        if not isinstance(product.get(field), str) or not product[field].strip():
            raise ValueError(f"Falta {field}")
    original = product["source_image"].strip()
    # A source image locator alone is not proof it is faithful.
    verified = product.get("source_image_verified") is True
    facts = product.get("facts", [])
    if not isinstance(facts, list):
        raise ValueError("facts debe ser lista")
    for fact in facts:
        if not isinstance(fact, dict) or not isinstance(fact.get("label"), str) or not isinstance(fact.get("value"), str):
            raise ValueError("Fact inválido")
    verified_facts = [f for f in facts if f.get("status") == "verified" and f.get("evidence_id")]
    # Deduplicate and keep at most three short overlay facts. Technical values
    # must already have been verified *outside this module*.
    unique = []
    seen = set()
    for f in verified_facts:
        key = (f["label"].strip().casefold(), f["value"].strip().casefold())
        if key not in seen:
            seen.add(key)
            unique.append({"label": f["label"].strip(), "value": f["value"].strip(), "evidence_id": str(f["evidence_id"])})
    selected = unique[:3]
    title = product["name"].strip()
    intent = str(product.get("customer_outcome", "")).strip()
    if not intent:
        intent = "Mostrar el uso cotidiano del artículo real sin promesas añadidas"
    fingerprint = hashlib.sha256(json.dumps({
        "tenant_id": product["tenant_id"], "product_id": product["product_id"],
        "source_image": original, "verified": verified,
        "facts": selected, "outcome": intent,
    }, ensure_ascii=False, sort_keys=True).encode()).hexdigest()[:20]
    slots = []
    for name in SLOTS:
        config = DEFAULTS[name]
        desc = {
            "hero": "Fondo blanco puro RGB 255,255,255. Producto completo y reconocible, sin texto, sin precios, sin logos superpuestos. Mantener producto real intacto.",
            "lifestyle": f"Escena cotidiana creíble donde una persona use el artículo de referencia para: {intent}. No mostrar funciones no confirmadas.",
            "benefits": "Producto real, composición limpia, reservar espacio libre para superponer texto vectorial después de generar la escena. El generador de imágenes NO escribe los datos.",
            "details": "Composición con recortes de fotos originales y, solo si existen vistas originales suficientes, acercamientos de controles y piezas verificadas. Sin detalles inventados.",
        }[name]
        slots.append({
            "slot": name, **config,
            "prompt": f"Producto identificado como: {title}. Usar obligatoriamente la referencia original: {original}. {desc} Respetar estrictamente geometría, etiquetas y accesorios.",
            "overlay_facts": selected if name == "benefits" else [],
            "evidence_required": True,
            "status": "planned" if verified else "blocked_missing_verified_original",
            "qa_required": ["product_identity", "shape_and_color", "visible_parts", "legibility_mobile", "no_unverified_claims"],
        })
    return {
        "schema_version": "0.1", "product_id": product["product_id"], "tenant_id": product["tenant_id"],
        "source_image": original, "source_image_verified": verified,
        "input_fingerprint": fingerprint, "status": "ready_for_human_review_of_plan" if verified else "blocked_missing_verified_original",
        "mode": "dry_run", "billable_generations": 0, "products_modified": 0,
        "cost_policy": {"default_max_usd": 0, "requires_explicit_billing_approval": True},
        "slots": slots, "prohibitions": PROHIBITIONS,
        "note": "Plan solamente: no renderiza imagen. Incluso con original verificado, la generación y publicación exigen aprobación independiente.",
    }


def main(argv=None):
    p = argparse.ArgumentParser(description="Crear plan de cuatro imágenes, sin generación ni publicaciones")
    p.add_argument("--input", required=True, type=Path)
    p.add_argument("--outdir", required=True, type=Path)
    args = p.parse_args(argv)
    result = build(json.loads(args.input.read_text(encoding="utf-8")))
    args.outdir.mkdir(parents=True, exist_ok=True)
    dest = args.outdir / "four-images-plan.json"
    dest.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Plan: {dest}; estado: {result['status']}; generación facturable: 0")


if __name__ == "__main__":
    main()
