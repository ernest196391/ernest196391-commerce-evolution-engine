"""Evidence gate for proposed product claims; offline, read-only.

Does not browse the web, fetch sources or assess whether a source is truthful.
It only ensures proposed claims carry traceable, non-comparable evidence.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path

SOURCE_TYPES = {"manufacturer", "product_label", "manual", "supplier", "official_document", "commercial_comparable"}
IDENTITIES = {"exact_verified", "comparable_only", "unknown"}
ALLOWED_STATUSES = {"verified", "unverified", "conflict"}


def validate(record: dict) -> dict:
    if not isinstance(record, dict):
        raise ValueError("Se requiere un registro JSON")
    identity = record.get("identity_status", "unknown")
    if identity not in IDENTITIES:
        raise ValueError("identity_status no válido")
    sources = record.get("sources", [])
    claims = record.get("claims", [])
    if not isinstance(sources, list) or not isinstance(claims, list):
        raise ValueError("sources y claims deben ser listas")
    indexed = {}
    for s in sources:
        if not isinstance(s, dict) or not isinstance(s.get("id"), str) or not s["id"].strip() or s["id"] in indexed:
            raise ValueError("Fuente sin ID único")
        if s.get("type") not in SOURCE_TYPES:
            raise ValueError("Tipo de fuente no reconocido")
        if not isinstance(s.get("reference"), str) or not s["reference"].strip():
            raise ValueError("Fuente sin referencia")
        indexed[s["id"]] = s
    reviewed = []
    for i, claim in enumerate(claims):
        if not isinstance(claim, dict):
            raise ValueError("Claim debe ser objeto")
        name = claim.get("name")
        value = claim.get("value")
        source_ids = claim.get("source_ids", [])
        if not isinstance(name, str) or not name.strip() or not isinstance(value, str) or not value.strip():
            raise ValueError("Afirmación sin nombre o valor")
        if not isinstance(source_ids, list):
            raise ValueError("source_ids debe ser lista")
        referenced = [indexed[sid] for sid in source_ids if isinstance(sid, str) and sid in indexed]
        evidence_ok = (len(source_ids)>0 and len(referenced) == len(source_ids)
                       and identity == "exact_verified"
                       and any(s["type"] != "commercial_comparable" for s in referenced))
        reported_status = claim.get("status", "unverified")
        if reported_status not in ALLOWED_STATUSES:
            raise ValueError("Estado no reconocido")
        approved = evidence_ok and reported_status == "verified"
        reviewed.append({
            "name": name, "value": value, "source_ids": source_ids,
            "reported_status": reported_status,
            "eligible_for_draft": approved,
            "required_action": "none" if approved else "verify_exact_product_and_primary_evidence",
        })
    return {"schema_version": "0.1", "mode": "read_only", "identity_status": identity,
            "claim_count": len(reviewed),
            "eligible_claims": sum(c["eligible_for_draft"] for c in reviewed),
            "claims": reviewed,
            "warning": "Control de estructura, NO verificación factual de enlaces o documentos. Revisión humana obligatoria."}


def main(argv=None):
    p = argparse.ArgumentParser(description="Verificación estructural offline de fuentes de producto")
    p.add_argument("--input", type=Path, required=True)
    p.add_argument("--outdir", type=Path, required=True)
    a = p.parse_args(argv)
    result = validate(json.loads(a.input.read_text(encoding="utf-8")))
    a.outdir.mkdir(parents=True, exist_ok=True)
    dest = a.outdir / "claim-evidence-report.json"
    dest.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Revisadas {result['claim_count']} afirmaciones; con evidencia estructural: {result['eligible_claims']}; salida {dest}")


if __name__ == "__main__":
    main()
