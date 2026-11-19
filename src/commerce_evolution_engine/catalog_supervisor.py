"""Offline supervisor: orchestrates existing checks; never certifies fidelity or publishes."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from .audit import normalize
from .editorial_review import triage
from .four_image_planner import build
from .photo_quality import inspect
from .research_gate import validate
from .commercial_review import WEIGHTS, HARD_GATES

HUMAN_CHECKS = (
    "exact_model_and_variant", "original_photo_and_rights", "physical_fidelity",
    "no_added_parts_or_functions", "hero_complete_without_overlay", "no_prices",
    "distinct_buyer_questions", "mobile_legibility", "claims_and_safety_verified",
    "editorial_no_repetition", "title_and_copy_useful",
)


def _digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def review(product: dict, research: dict, draft: dict, folder: Path) -> dict:
    """Review a candidate, retaining all existing review gates. No approval input."""
    plan = build(product)
    editorial = triage(draft, tenant_id=plan["tenant_id"])
    evidence = validate(research)
    blockers = []
    if normalize(draft)["id"] != plan["product_id"] or any(
        research.get(k) != plan[k] for k in ("tenant_id", "product_id")
    ):
        blockers.append("identidad_inconsistente")
    if not plan["source_image_verified"] or evidence["identity_status"] != "exact_verified":
        blockers.append("identidad_o_original_no_verificados")
    eligible = [c for c in evidence["claims"] if c["eligible_for_draft"]]
    if len(eligible) != evidence["claim_count"]:
        blockers.append("afirmaciones_sin_evidencia")
    for slot in plan["slots"]:
        for fact in slot["overlay_facts"]:
            if not any(c["name"].strip().casefold() == fact["label"].casefold()
                       and c["value"].strip().casefold() == fact["value"].casefold()
                       and fact["evidence_id"] in c["source_ids"] for c in eligible):
                blockers.append("dato_visual_sin_evidencia_correspondiente")
        detail = slot["detail_concept"]
        if detail and not any(detail["evidence_id"] in c["source_ids"] for c in eligible):
            blockers.append("detalle_sin_evidencia_correspondiente")
        context = slot.get("context_concept")
        if context and not any(context["evidence_id"] in c["source_ids"] for c in eligible):
            blockers.append("contexto_sin_evidencia_correspondiente")
    require_details = any(s["slot"] == "details" for s in plan["slots"])
    try:
        photos = inspect(folder, require_details=require_details)
    except RuntimeError:
        photos = {"technical_ready": False, "slots": [], "warning": "QA no disponible"}
    if not photos["technical_ready"]:
        blockers.append("galeria_tecnica_incompleta_o_rechazada")
    if not require_details and (folder / "04-details.png").exists():
        blockers.append("cuarta_foto_no_justificada")
    if any(flag in editorial["flags"] for flag in (
        "titulo_ausente_o_poco_informativo", "descripcion_ausente", "descripcion_corta_ausente",
        "descripcion_corta_repite_titulo",
    )):
        blockers.append("texto_esencial_insuficiente_o_repetido")
    fingerprint = _digest({"product": product, "research": research, "draft": draft,
                           "photo_report": photos})
    return {
        "schema_version": "0.1", "mode": "dry_run", "tenant_id": plan["tenant_id"],
        "product_id": plan["product_id"], "candidate_fingerprint": fingerprint,
        "status": "blocked" if blockers else "awaiting_human_review",
        "blockers": sorted(set(blockers)), "editorial": editorial,
        "evidence": evidence, "photo_qa": photos, "plan": plan,
        "human_checklist": {key: "not_verified" for key in HUMAN_CHECKS},
        "commercial_review": {"minimum_score": 90, "weights": WEIGHTS,
                              "gates": dict.fromkeys(HARD_GATES, "not_verified")},
        "human_approval_required": True, "publish_allowed": False,
        "billable_generations": 0, "products_modified": 0,
        "warning": "La estructura de fuentes y QA técnico no certifican veracidad, fidelidad ni semántica. Revisar manualmente el candidato exacto.",
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description="Supervisor offline sin publicación")
    for key in ("product", "research", "draft", "photos", "report"):
        parser.add_argument("--" + key, required=True, type=Path)
    args = parser.parse_args(argv)
    def read(path):
        return json.loads(path.read_text(encoding="utf-8"))
    result = review(read(args.product), read(args.research), read(args.draft), args.photos)
    # Never overwrite an input file.
    if args.report.resolve() in {p.resolve() for p in (args.product, args.research, args.draft)} or args.photos.resolve() in args.report.resolve().parents:
        raise ValueError("El informe debe estar fuera de los archivos de entrada")
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(result["status"])


if __name__ == "__main__":
    main()
