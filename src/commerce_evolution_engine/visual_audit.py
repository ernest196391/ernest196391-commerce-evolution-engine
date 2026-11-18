"""Public product-page visual audit with Playwright (read-only, opt-in).

No login, credentials, WordPress API or publishing. Browser content is untrusted.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path
from urllib.parse import urlsplit

DENY_PATH = re.compile(r"/(?:wp-admin|wp-login|my-account|mi-cuenta|checkout|finalizar-compra|cart|carrito|account|pedido|order|control)(?:/|$)", re.I)
SIZES = {"mobile360": (360, 800), "mobile390": (390, 844), "desktop1280": (1280, 900)}


def valid_url(raw: str, allowed_hosts: set[str]) -> str:
    """Validate explicit public destination, never trust URL redirects."""
    parsed = urlsplit(raw.strip())
    if (parsed.scheme != "https" or not parsed.hostname or parsed.username
            or parsed.password or parsed.port not in (None, 443)
            or parsed.query or parsed.fragment
            or parsed.hostname.lower() not in allowed_hosts
            or DENY_PATH.search(parsed.path)
            or not parsed.path.startswith("/")):
        raise ValueError(f"URL rechazada: {raw!r}")
    return parsed.geturl()


def load_urls(path: Path, allowed_hosts: set[str], limit: int = 8) -> list[str]:
    lines = path.read_text(encoding="utf-8-sig").splitlines()
    result = []
    for line in lines:
        value = line.strip()
        if not value or value.startswith("#"):
            continue
        url = valid_url(value, allowed_hosts)
        if url not in result:
            result.append(url)
        if len(result) > limit:
            raise ValueError(f"Máximo {limit} páginas por ejecución")
    if not result:
        raise ValueError("La lista de páginas está vacía")
    return result


def signals(payload: dict) -> list[str]:
    issues = []
    if payload["status"] != 200:
        issues.append("respuesta_no_200")
    if not payload["title"]:
        issues.append("sin_title")
    if not payload["h1"]:
        issues.append("sin_h1")
    if payload["h1_count"] > 1:
        issues.append("multiples_h1_revisar")
    if payload["overflow_px"] > 8:
        issues.append("desbordamiento_horizontal")
    if payload["broken_images"] > 0:
        issues.append("imagenes_sin_cargar")
    if payload["images_missing_alt"] > 0:
        issues.append("imagenes_sin_alt")
    if payload["main_text_chars"] < 120:
        issues.append("contenido_principal_breve_revisar")
    return issues


def snapshot(page) -> dict:
    """Only count on-page visible structures; no external writes."""
    return page.evaluate("""() => {
      const isVisible = el => {
        const s = getComputedStyle(el);
        const b = el.getBoundingClientRect();
        return s.display !== 'none' && s.visibility !== 'hidden' && b.width > 0 && b.height > 0;
      };
      const images = [...document.images].filter(isVisible);
      const main = document.querySelector('main, article, .product, #content');
      const heads = [...document.querySelectorAll('h1')].filter(isVisible);
      return {
        title: document.title.trim().slice(0,250),
        h1: (heads[0]?.innerText || '').trim().slice(0,250),
        h1_count: heads.length,
        images_visible: images.length,
        broken_images: images.filter(x => !x.complete || x.naturalWidth === 0).length,
        images_missing_alt: images.filter(x => !(x.getAttribute('alt') || '').trim()).length,
        main_text_chars: (main?.innerText || '').trim().length,
        overflow_px: Math.max(0, Math.round(document.documentElement.scrollWidth - innerWidth)),
        canonical: document.querySelector('link[rel="canonical"]')?.href || ''
      };
    }""")


def run(urls: list[str], outdir: Path, allowed_hosts: set[str]) -> dict:
    try:
        from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
    except ImportError as e:
        raise SystemExit("Instala: python -m pip install playwright; python -m playwright install chromium") from e

    outdir.mkdir(parents=True, exist_ok=True)
    rows = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        try:
            for i, url in enumerate(urls, start=1):
                for label, (width, height) in SIZES.items():
                    page = browser.new_page(viewport={"width": width, "height": height}, device_scale_factor=1)
                    page.set_default_timeout(10000)
                    result = {"url": url, "viewport": label, "status": None,
                              "title": "", "h1": "", "h1_count": 0, "images_visible": 0,
                              "broken_images": 0, "images_missing_alt": 0,
                              "main_text_chars": 0, "overflow_px": 0, "canonical": ""}
                    try:
                        response = page.goto(url, wait_until="domcontentloaded", timeout=20000)
                        result["status"] = response.status if response else None
                        # Fail closed on cross-host redirects (before inspecting/saving).
                        if urlsplit(page.url).hostname not in allowed_hosts:
                            result["error"] = "redireccion_fuera_del_dominio"
                        else:
                            try:
                                page.wait_for_load_state("networkidle", timeout=5000)
                            except PlaywrightTimeout:
                                pass
                            result.update(snapshot(page))
                            filename = f"page-{i:02d}-{label}.png"
                            page.screenshot(path=str(outdir / filename), full_page=False, timeout=15000)
                            result["screenshot"] = filename
                    except Exception as exc:
                        # Never output full URLs or browser context from exception messages.
                        result["error"] = type(exc).__name__
                    finally:
                        page.close()
                    result["issues"] = signals(result) if not result.get("error") else ["no_auditado"]
                    rows.append(result)
        finally:
            browser.close()
    report = {"schema_version": "0.2", "disclaimer": "Señales automatizadas: requieren revisión humana; no verifican veracidad, SEO real ni calidad estética.", "results": rows}
    (outdir / "visual-report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    with (outdir / "visual-report.csv").open("w", newline="", encoding="utf-8") as f:
        fields = ["url", "viewport", "status", "title", "h1", "images_visible", "broken_images",
                  "images_missing_alt", "main_text_chars", "overflow_px", "screenshot", "issues", "error"]
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for row in rows:
            w.writerow({**row, "issues": "|".join(row["issues"])})
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description="Audita páginas públicas autorizadas y captura pantallas.")
    parser.add_argument("--urls", type=Path, required=True, help="Archivo de URLs públicas HTTPS")
    parser.add_argument("--outdir", type=Path, default=Path("results/visual"))
    parser.add_argument("--host", required=True, help="Dominio EXACTO permitido, sin esquema")
    args = parser.parse_args(argv)
    host = args.host.lower().strip()
    if not re.fullmatch(r"[a-z0-9.-]+", host) or not host.count(".") or host.startswith("."):
        parser.error("Dominio no válido")
    urls = load_urls(args.urls, {host})
    report = run(urls, args.outdir, {host})
    print(f"Auditadas {len(urls)} páginas en {len(SIZES)} tamaños; {len(report['results'])} resultados en {args.outdir}")


if __name__ == "__main__":
    main()
