"""check_kie.py — ping rápido a Kie AI para saber si está arriba.

Salida en stdout:
  KIE_UP                 → API responde 200, listo para usar
  DNS_FAIL: <error>      → no resuelve el dominio
  API_HTTP: <código>     → DNS ok, API responde con código no-200
  API_BAD: <code> <msg>  → API responde JSON pero con código de error
  API_FAIL: <error>      → otra excepción

Exit code: 0 si KIE_UP, 1 en cualquier otro caso.
"""

import json
import socket
import sys
import urllib.error
import urllib.request
from pathlib import Path


def main() -> int:
    try:
        ip = socket.gethostbyname("api.kie.ai")
        print(f"DNS_OK: {ip}")
    except Exception as e:
        print(f"DNS_FAIL: {e}")
        return 1

    env_path = Path(__file__).parent.parent / ".env"
    key = None
    for line in env_path.read_text(encoding="utf-8").splitlines():
        if line.startswith("KIE_AI_API_KEY"):
            key = line.split("=", 1)[1].strip()
            break
    if not key:
        print("ENV_FAIL: no KIE_AI_API_KEY in .env")
        return 1

    payload = json.dumps({
        "model": "google/nano-banana",
        "input": {
            "prompt": "ping test, simple dark background",
            "aspect_ratio": "4:5",
            "resolution": "1K",
            "output_format": "png",
        },
    }).encode()
    req = urllib.request.Request(
        "https://api.kie.ai/api/v1/jobs/createTask",
        data=payload,
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
    )
    try:
        resp = json.loads(urllib.request.urlopen(req, timeout=15).read())
        if resp.get("code") == 200:
            task_id = (resp.get("data") or {}).get("taskId")
            print(f"KIE_UP (taskId={task_id})")
            return 0
        print(f"API_BAD: {resp.get('code')} {resp.get('msg')}")
        return 1
    except urllib.error.HTTPError as e:
        print(f"API_HTTP: {e.code}")
        return 1
    except Exception as e:
        print(f"API_FAIL: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
