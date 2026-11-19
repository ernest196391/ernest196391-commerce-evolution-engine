"""Turn aggregate, anonymized customer-question topics into product content priorities.

No connection to chats, no personal data, no changes to products.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path

TOPIC_ACTIONS = {
    "producto_detalle": ("research_and_claims", "04-details", "Verificar modelo, materiales, especificaciones y contenido del paquete."),
    "disponibilidad": ("catalog_freshness", None, "Contrastar stock real en WooCommerce; no anunciar existencias con mensajes antiguos."),
    "pedido_estado": ("bot_order_state", None, "Responder únicamente con el estado transaccional real; no incluir en fotos."),
    "envio": ("delivery_information", None, "Publicar tarifas y zonas exactas en checkout/FAQ, no en fotografías del producto."),
    "comision": ("gestora_faq", None, "Explicar regla vigente a gestoras; fuera de la ficha pública."),
    "cobro_comision": ("gestora_faq", None, "Enlazar estado contable real sin prometer cobro."),
    "precio": ("price_accuracy", None, "Usar precio canónico del catálogo; no incrustarlo en imágenes."),
    "material": ("research_materials", "04-details", "Foto de textura/etiqueta y composición verificadas."),
    "dimensiones": ("research_dimensions", "04-details", "Diagramas con cotas solamente si hay medidas corroboradas."),
    "autonomia": ("research_power", "03-benefits", "Aclarar autonomía por condiciones de uso, sin convertirla en garantía."),
    "contenido_paquete": ("what_is_included", "04-details", "Mostrar elementos incluidos solo si aparecen en referencias verificadas."),
    "uso": ("human_outcome", "02-lifestyle", "Demostrar uso humano realista conservando el artículo exacto."),
}


def prioritize(aggregate: list[dict]) -> dict:
    items = []
    for x in aggregate:
        if not isinstance(x, dict) or not isinstance(x.get("topic"), str):
            raise ValueError("Cada señal debe tener topic")
        n = x.get("count")
        if type(n) is not int or n < 0:
            raise ValueError("count debe ser entero no negativo")
        unanswered = x.get("unanswered", 0)
        if type(unanswered) is not int or not 0 <= unanswered <= n:
            raise ValueError("unanswered fuera de rango")
        topic = x["topic"].strip()
        action, slot, reason = TOPIC_ACTIONS.get(topic, ("classify_manually", None, "Clasificar preguntas anonimizadas y buscar evidencia."))
        priority = n + 2 * unanswered
        items.append({"topic": topic, "question_count": n, "unanswered_count": unanswered,
                      "priority": priority, "action": action, "photo_slot": slot,
                      "reason": reason})
    items.sort(key=lambda a: (-a["priority"], a["topic"]))
    return {"schema_version": "0.1", "mode": "aggregate_only", "decision": "review_only",
            "no_product_changes": True, "no_auto_answers": True,
            "disclaimer": "Conteos de tickets; no demuestran exactitud de respuestas ni relevancia SKU. Sin acceso a conversaciones.",
            "signals": items}


def main(argv=None):
    p = argparse.ArgumentParser(description="Priorizar señales agregadas de clientes sin leer chats")
    p.add_argument("--input", required=True, type=Path)
    p.add_argument("--outdir", required=True, type=Path)
    a = p.parse_args(argv)
    data = json.loads(a.input.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        p.error("Se requiere array JSON")
    result = prioritize(data)
    a.outdir.mkdir(parents=True, exist_ok=True)
    dest = a.outdir / "content-signals.json"
    dest.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Señales: {len(data)}; propuestas: {dest}")


if __name__ == "__main__":
    main()
