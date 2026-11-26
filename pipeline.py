import json
import subprocess
import sys
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent
API = ROOT / "docs/api"

def active_models():
    return [m for m in json.loads((API / "models.json").read_text(encoding="utf-8")) if m.get("ativo") and m.get("fonte")]

def run():
    models = active_models()
    for i, model in enumerate(models):
        key = model["id"]
        folder = API if key == "nfe" else API / key
        folder.mkdir(parents=True, exist_ok=True)
        previous = {}
        try:
            previous = json.loads((folder / 'status.json').read_text(encoding='utf-8'))
        except (OSError, ValueError):
            pass
        started = datetime.now(timezone.utc)
        last = previous.get('ultima_consulta_sucesso') or (previous.get('consulta') if previous.get('status') == 'success' else None)
        if last and '--force' not in sys.argv:
            due = datetime.fromisoformat(last).astimezone(timezone.utc).date() + timedelta(days=11)
            if started.date() < due:
                print(f'{key}: deferred', flush=True)
                continue
        clock = time.monotonic()
        status = "failure"
        try:
            result = subprocess.run([sys.executable, str(ROOT / ("provider_nfce.py" if key == "nfce" else "monitor.py")), key], cwd=ROOT, timeout=180)
            status = "success" if result.returncode == 0 else "failure"
        except (OSError, subprocess.TimeoutExpired) as exc:
            print(f"{key}: {type(exc).__name__}", flush=True)
        ended = datetime.now(timezone.utc)
        previous = {}
        try:
            previous = json.loads((folder / "status.json").read_text(encoding="utf-8"))
        except (OSError, ValueError):
            pass
        payload = dict(status=status, consulta=ended.isoformat(), inicio=started.isoformat(),
                       proxima_consulta=(ended.date()+timedelta(days=11 if status=='success' else 1)).isoformat()+'T12:17:00+00:00',
                       duracao_segundos=round(time.monotonic()-clock, 2),
                       ultima_consulta_sucesso=ended.isoformat() if status=="success" else previous.get("ultima_consulta_sucesso") or (previous.get("consulta") if previous.get("status")=="success" else None))
        tmp = folder / "status.tmp"
        tmp.write_text(json.dumps(payload, ensure_ascii=False)+"\n", encoding="utf-8")
        tmp.replace(folder / "status.json")
        print(f"{key}: {status}", flush=True)
        if i+1 < len(models):
            time.sleep(3)

if __name__ == "__main__":
    run()
