"""
buscar_imagenes.py — Scraper de imagenes vía Apify API REST.

Usa el actor `hooli/google-images-scraper` para buscar imagenes de un tema
historico/conceptual cuando se necesitan como apoyo visual en carruseles.

Workflow (definido en skill/carruseles.md):
  1. Mostrar copies al usuario primero (Regla de Oro)
  2. Identificar que slides necesitan imagen real explicativa
  3. Pedir validacion antes de scrapear
  4. Scrapear: max 5 imagenes por query, tamaño grande
  5. Descargar a fotos/ con nombres descriptivos
  6. Mostrar opciones al usuario para que elija

Uso:
  python scripts/buscar_imagenes.py --proj-dir <ruta> \
      --query "Galileo Galilei trial 1633 painting" \
      --label "galileo" \
      --max 3
"""

import argparse
import json
import os
import sys
import time
import urllib.request
from pathlib import Path


def _load_apify_token() -> str:
    """Carga el token desde ~/.apify/auth.json (creado por `apify login`)."""
    auth_path = Path.home() / ".apify" / "auth.json"
    if not auth_path.exists():
        sys.exit("❌ No hay ~/.apify/auth.json. Corre: apify login -t <token>")
    data = json.loads(auth_path.read_text(encoding="utf-8"))
    token = data.get("token")
    if not token:
        sys.exit("❌ No hay 'token' en auth.json")
    return token


def run_actor_sync(actor: str, payload: dict, token: str, timeout: int = 180) -> list[dict]:
    """Llama al actor con run-sync-get-dataset-items.

    Devuelve la lista de items del dataset (cada item suele tener url, title,
    sourceUrl, width, height).
    """
    actor_slug = actor.replace("/", "~")
    url = f"https://api.apify.com/v2/acts/{actor_slug}/run-sync-get-dataset-items?token={token}"
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode()[:500]
        raise RuntimeError(f"HTTP {e.code}: {body}")


def download_image(url: str, dest: Path) -> bool:
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (compatible; carruseles-ig/1.0)"},
        )
        with urllib.request.urlopen(req, timeout=30) as r:
            dest.write_bytes(r.read())
        return True
    except Exception as e:
        print(f"  ⚠️  no descargo {url[:60]}...: {e}")
        return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--proj-dir", required=True)
    ap.add_argument("--query", required=True, help="Query de busqueda (puede usarse varias separadas por |)")
    ap.add_argument("--label", required=True, help="Etiqueta para nombrar las imagenes descargadas (ej. 'galileo')")
    ap.add_argument("--max", type=int, default=5, help="Maximo de imagenes por query (default 5)")
    ap.add_argument("--size", default="large", help="Tamaño minimo: large|xlarge|huge")
    ap.add_argument("--no-download", action="store_true", help="Solo mostrar URLs, no descargar")
    args = ap.parse_args()

    proj = Path(args.proj_dir).resolve()
    token = _load_apify_token()
    queries = [q.strip() for q in args.query.split("|") if q.strip()]

    payload = {
        "queries": queries,
        "maxResultsPerQuery": args.max,
        "imageSize": args.size,
    }

    print(f"→ scrapeando {len(queries)} query(s) ({args.max} resultados c/u, size={args.size})...")
    for q in queries:
        print(f"    · {q}")

    items = run_actor_sync("hooli/google-images-scraper", payload, token)
    print(f"✓ recibidas {len(items)} imagenes\n")

    # Carpeta de scraping
    dst_dir = proj / "fotos" / "_scraping" / args.label
    dst_dir.mkdir(parents=True, exist_ok=True)

    rows = []
    for i, item in enumerate(items, 1):
        url = item.get("imageUrl") or item.get("url") or item.get("contentUrl")
        title = (item.get("title") or "").replace("/", "_")[:80]
        source = item.get("sourceUrl") or item.get("hostPageUrl") or ""
        w = item.get("width") or 0
        h = item.get("height") or 0

        if not url:
            print(f"  {i}. (sin URL): {json.dumps(item)[:120]}")
            continue

        fname = f"{args.label}_{i:02d}.jpg"
        dest = dst_dir / fname
        downloaded = False
        if not args.no_download:
            downloaded = download_image(url, dest)
        rows.append({
            "n": i,
            "fname": fname if downloaded else None,
            "url": url,
            "title": title,
            "source": source,
            "size": f"{w}x{h}" if w else "?",
        })
        marker = "✓" if downloaded else "·"
        print(f"  {marker} {i:02d}. {w}x{h}  {title[:60]}")
        print(f"        URL: {url[:100]}")

    # Guardar manifest para que Diego pueda revisar
    manifest = dst_dir / "_manifest.json"
    manifest.write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\n✓ manifest en: {manifest}")
    print(f"✓ imagenes descargadas en: {dst_dir}")


if __name__ == "__main__":
    main()
