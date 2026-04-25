#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.40"]
# ///
"""Capture screenshots of every tablero declared in podio + finalistas YAMLs.

Para cada entrada carga `url` con Playwright (Chrome del sistema), espera a
que la red quede inactiva y guarda la captura en `imagen`. Las entradas sin
`imagen` se omiten.

Uso:
    uv run scripts/screenshot-tableros.py            # todos
    uv run scripts/screenshot-tableros.py pcaboys    # solo los que coincidan

El argumento opcional filtra por substring (case-insensitive) contra el
campo `equipo` o el nombre de archivo en `imagen`.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from playwright.sync_api import TimeoutError as PWTimeout, sync_playwright

ROOT = Path(__file__).resolve().parent.parent
SOURCES = [ROOT / "tableros-podio.yml", ROOT / "tableros-finalistas.yml"]
WIDTH, HEIGHT = 1400, 900
NAV_TIMEOUT_MS = 45_000  # tope duro por si una página nunca se aquieta
SETTLE_MS = 2_000  # margen post-resize para que bslib + plotly terminen de pintar

_KV = re.compile(r"^\s*([A-Za-z_][\w-]*)\s*:\s*(.*)$")


def _strip_value(raw: str) -> str:
    raw = raw.strip()
    if len(raw) >= 2 and raw[0] == raw[-1] and raw[0] in ('"', "'"):
        return raw[1:-1]
    return raw


def parse_yaml_list(text: str) -> list[dict]:
    """Parsea una lista YAML simple (sin anidados, sin multilinea)."""
    items: list[dict] = []
    current: dict | None = None
    for line in text.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        stripped = line.lstrip()
        if stripped.startswith("- "):
            current = {}
            items.append(current)
            stripped = stripped[2:]
        if current is None:
            continue
        m = _KV.match(stripped)
        if m:
            current[m.group(1)] = _strip_value(m.group(2))
    return items


def entries():
    for src in SOURCES:
        for item in parse_yaml_list(src.read_text(encoding="utf-8")):
            yield item


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "filtro",
        nargs="?",
        default="",
        help="Substring para filtrar por equipo o nombre de imagen.",
    )
    args = parser.parse_args()
    needle = args.filtro.lower()

    targets = []
    skipped: list[str] = []
    for item in entries():
        equipo = item.get("equipo", "?")
        url = (item.get("url") or "").strip()
        imagen = item.get("imagen", "").strip()
        if not url or not imagen:
            skipped.append(f"{equipo} (sin {'url' if not url else 'imagen'})")
            continue
        if needle and needle not in equipo.lower() and needle not in imagen.lower():
            continue
        targets.append((equipo, url, ROOT / imagen))

    if not targets:
        print("Nada por capturar.")
        return 0

    failures: list[str] = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(channel="chrome", headless=True)
        ctx = browser.new_context(viewport={"width": WIDTH, "height": HEIGHT})
        page = ctx.new_page()
        for equipo, url, out in targets:
            out.parent.mkdir(parents=True, exist_ok=True)
            print(f"→ {equipo}  ({url})", flush=True)
            try:
                page.goto(url, wait_until="networkidle", timeout=NAV_TIMEOUT_MS)
            except PWTimeout:
                print(f"  ⚠ networkidle no se alcanzó en {NAV_TIMEOUT_MS}ms; capturo igual")
            except Exception as exc:
                print(f"  ✗ {exc}")
                failures.append(equipo)
                continue
            # Quarto dashboards (bslib) sólo calculan fill-dimensions tras un resize;
            # los plots interactivos necesitan otro tick para pintar.
            page.evaluate("window.dispatchEvent(new Event('resize'))")
            page.wait_for_timeout(SETTLE_MS)
            page.screenshot(path=str(out), full_page=False)
        ctx.close()
        browser.close()

    if skipped:
        print("\nOmitidos:")
        for s in skipped:
            print(f"  · {s}")
    if failures:
        print("\nFallidos:")
        for s in failures:
            print(f"  · {s}")
    print(f"\n✔ Capturas en {ROOT / 'img' / 'tableros'}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
