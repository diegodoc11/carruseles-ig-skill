"""
kie_edit.py — Edita una imagen local con Kie AI (nano-banana-pro).

Flujo:
  1) Sube la imagen local a 0x0.st (host público temporal, sin auth).
  2) Llama a Kie createTask con `nano-banana-pro` + image_url + prompt de edición.
  3) Polling hasta success → descarga el resultado.

Uso:
  python scripts/kie_edit.py --proj-dir <ruta> \
      --input "fotos/Screen Instagram.PNG" \
      --output "fotos/Screen Instagram dark.PNG" \
      --prompt "convert this Instagram profile screenshot to dark mode..."
"""

import argparse
import json
import os
import sys
import time
import urllib.request
from pathlib import Path

import requests


def _load_dotenv(proj_dir: Path):
    p = proj_dir / ".env"
    if not p.exists():
        return
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())


def upload_public(path: Path) -> str:
    """Sube un archivo a un host público sin auth y devuelve la URL.
    Intenta catbox.moe primero (estable, persistente), después tmpfiles.org,
    finalmente 0x0.st (a veces tiene rate limit / 503)."""
    errors = []
    # 1) catbox.moe
    try:
        with open(path, "rb") as f:
            r = requests.post(
                "https://catbox.moe/user/api.php",
                data={"reqtype": "fileupload"},
                files={"fileToUpload": (path.name, f, "image/png")},
                headers={"User-Agent": "Mozilla/5.0"},
                timeout=60,
            )
        if r.ok and r.text.startswith("https://"):
            return r.text.strip()
        errors.append(f"catbox: {r.status_code} {r.text[:120]}")
    except Exception as e:
        errors.append(f"catbox exc: {e}")

    # 2) tmpfiles.org
    try:
        with open(path, "rb") as f:
            r = requests.post(
                "https://tmpfiles.org/api/v1/upload",
                files={"file": (path.name, f, "image/png")},
                timeout=60,
            )
        if r.ok:
            data = r.json().get("data", {})
            url = data.get("url", "")
            # tmpfiles devuelve URL de página HTML; convertir a URL directa de descarga
            if "tmpfiles.org/" in url:
                url = url.replace("tmpfiles.org/", "tmpfiles.org/dl/")
            if url.startswith("http"):
                return url
        errors.append(f"tmpfiles: {r.status_code}")
    except Exception as e:
        errors.append(f"tmpfiles exc: {e}")

    # 3) 0x0.st como último recurso
    try:
        with open(path, "rb") as f:
            r = requests.post(
                "https://0x0.st",
                files={"file": (path.name, f, "image/png")},
                headers={"User-Agent": "curl/8.0"},
                timeout=60,
            )
        if r.ok and r.text.startswith("https://"):
            return r.text.strip()
        errors.append(f"0x0: {r.status_code}")
    except Exception as e:
        errors.append(f"0x0 exc: {e}")

    raise RuntimeError("Todos los hosts fallaron: " + " | ".join(errors))


def kie_edit(image_url: str, prompt: str, api_key: str, model: str = "nano-banana-pro") -> str | None:
    """Llama a Kie con image-to-image y devuelve la URL del resultado."""
    payload = {
        "model": model,
        "input": {
            "prompt": prompt,
            "image_urls": [image_url],
            "output_format": "png",
        },
    }
    req = urllib.request.Request(
        "https://api.kie.ai/api/v1/jobs/createTask",
        data=json.dumps(payload).encode(),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
    )
    try:
        resp = json.loads(urllib.request.urlopen(req, timeout=30).read())
    except urllib.error.HTTPError as e:
        print(f"  HTTP {e.code}: {e.read().decode()[:200]}")
        return None
    code = resp.get("code")
    if code != 200:
        print(f"  Kie code={code} msg={resp.get('msg')}")
        return None
    task_id = (resp.get("data") or {}).get("taskId")
    print(f"  taskId: {task_id}")
    for i in range(120):
        time.sleep(3)
        poll = urllib.request.Request(
            f"https://api.kie.ai/api/v1/jobs/recordInfo?taskId={task_id}",
            headers={"Authorization": f"Bearer {api_key}"},
        )
        try:
            info = json.loads(urllib.request.urlopen(poll, timeout=15).read())
        except Exception as e:
            print(f"  poll error: {e}")
            continue
        inner = info.get("data") or {}
        state = inner.get("state")
        if state == "success":
            urls = json.loads(inner.get("resultJson", "{}")).get("resultUrls", [])
            return urls[0] if urls else None
        if state in ("failed", "error"):
            print(f"  fail: {inner.get('failMsg')}")
            return None
        if i % 10 == 9:
            print(f"  ...polling ({(i+1)*3}s, state={state})")
    return None


def download_image(url: str, dest: Path):
    r = requests.get(url, headers={"User-Agent": "Mozilla/5.0", "Referer": "https://kie.ai/"}, timeout=60)
    r.raise_for_status()
    dest.write_bytes(r.content)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--proj-dir", required=True)
    ap.add_argument("--input", required=True, help="Ruta a la imagen local (relativa al proj-dir o absoluta)")
    ap.add_argument("--output", required=True, help="Ruta donde guardar el resultado")
    ap.add_argument("--prompt", required=True)
    ap.add_argument("--model", default="nano-banana-pro")
    args = ap.parse_args()

    proj = Path(args.proj_dir).resolve()
    _load_dotenv(proj)
    cfg = json.loads((proj / "config.json").read_text(encoding="utf-8"))
    kie_key = cfg.get("kie_ai_key") or os.environ.get("KIE_AI_API_KEY")
    if not kie_key:
        sys.exit("❌ no hay KIE_AI_API_KEY")

    src = Path(args.input)
    if not src.is_absolute():
        src = proj / src
    if not src.exists():
        sys.exit(f"❌ no encuentro {src}")

    print(f"→ Subiendo {src.name} a host público...")
    public_url = upload_public(src)
    print(f"  URL pública: {public_url}")

    print(f"→ Editando con {args.model}...")
    print(f"  Prompt: {args.prompt[:80]}...")
    result_url = kie_edit(public_url, args.prompt, kie_key, args.model)
    if not result_url:
        sys.exit("❌ Kie no devolvió URL")

    dst = Path(args.output)
    if not dst.is_absolute():
        dst = proj / dst
    print(f"→ Descargando resultado a {dst.name}...")
    download_image(result_url, dst)
    print(f"✓ guardado: {dst}")


if __name__ == "__main__":
    main()
