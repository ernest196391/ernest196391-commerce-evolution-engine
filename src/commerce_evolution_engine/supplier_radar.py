"""Offline supplier observations -> review proposals. No network, no WooCommerce writes.

Input is a user-authorized *sanitized* JSON array. Never feed private chats here
without consent and minimization. Evidence IDs must not be customer details.
"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

VALID = {"available", "out_of_stock", "discontinued", "unknown"}
OUT = {"out_of_stock", "discontinued"}


def parse_observation(raw: dict) -> dict:
    required = ("supplier_id", "sku", "variant", "status", "observed_at", "evidence_id")
    if not isinstance(raw, dict) or any(not isinstance(raw.get(k), str) or not raw[k].strip() for k in required):
        raise ValueError("Observación incompleta o incorrecta")
    if raw["status"] not in VALID:
        raise ValueError("Estado no válido")
    try:
        stamp = datetime.fromisoformat(raw["observed_at"].replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("Fecha inválida") from exc
    if stamp.tzinfo is None:
        raise ValueError("Fecha sin zona horaria")
    return {**{k: raw[k].strip() for k in required},
            "observed_at": stamp.astimezone(timezone.utc).isoformat(),
            "_timestamp": stamp.timestamp()}


def assess(observations: list[dict]) -> dict:
    """Latest statement per supplier+SKU+variant; no assumption from silence.

    All statuses are proposals, including multiple sources, and require review.
    """
    latest: dict[tuple[str, str, str], dict] = {}
    for raw in observations:
        row = parse_observation(raw)
        key = (row["supplier_id"], row["sku"], row["variant"])
        prior = latest.get(key)
        if prior is None or row["_timestamp"] > prior["_timestamp"]:
            latest[key] = row
    grouped = defaultdict(list)
    for row in latest.values():
        grouped[(row["sku"], row["variant"])].append(row)
    proposals = []
    for (sku, variant), records in sorted(grouped.items()):
        statuses = {r["status"] for r in records}
        if "available" in statuses:
            candidate = "available_somewhere"
            reason = "Al menos un proveedor declara disponibilidad; requiere confirmación antes de prometer stock."
        elif statuses and statuses.issubset(OUT):
            candidate = "review_possible_outage"
            reason = "Los proveedores observados declaran agotamiento; confirmar cobertura y existencias propias."
        else:
            candidate = "insufficient_evidence"
            reason = "Observaciones desconocidas o contradictorias; no cambiar disponibilidad."
        proposals.append({
            "sku": sku, "variant": variant, "candidate": candidate,
            "reason": reason, "action": "human_review_only",
            "evidence_ids": sorted({r["evidence_id"] for r in records}),
            "supplier_count": len(records),
        })
    return {
        "schema_version": "0.1", "mode": "dry_run",
        "observation_count": len(observations),
        "latest_supplier_item_count": len(latest),
        "proposals": proposals,
        "disclaimer": "No determina stock real de la tienda ni modifica WooCommerce. Confirmar con fuentes y reservas.",
    }


def main(argv=None):
    p = argparse.ArgumentParser(description="Radar offline de proveedores; sin cambios de inventario")
    p.add_argument("--input", type=Path, required=True)
    p.add_argument("--outdir", type=Path, required=True)
    args = p.parse_args(argv)
    data = json.loads(args.input.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        p.error("Entrada debe ser un array JSON")
    report = assess(data)
    args.outdir.mkdir(parents=True, exist_ok=True)
    dst = args.outdir / "supplier-proposals.json"
    dst.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Observaciones: {len(data)}; SKUs/variantes revisados: {len(report['proposals'])}; resultado: {dst}")


if __name__ == "__main__":
    main()
