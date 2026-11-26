import csv
import io
import json
import re
from datetime import datetime
from pathlib import Path
import requests

URL = "https://public.tableau.com/views/EstatsticasNFCe/NFCe.csv"
ROOT = Path(__file__).resolve().parent / "docs/api/nfce"

def parse_csv(raw):
    reader = csv.DictReader(io.StringIO(raw.decode("utf-8-sig")))
    fields = {x.strip(): x for x in reader.fieldnames or []}
    metric = "Soma de Emissores  (CNPJ)"
    if not {"Mês", metric}.issubset(fields):
        raise ValueError("Unexpected provider schema")
    rows = {}
    for row in reader:
        date = datetime.strptime(row[fields["Mês"]].strip(), "%d/%m/%Y").date()
        value = row[fields[metric]].strip()
        if date.day != 1 or not re.fullmatch(r"(?:[0-9]+|[0-9]{1,3}(?:\.[0-9]{3})+)", value):
            raise ValueError("Invalid observation")
        key = date.isoformat()
        if key in rows:
            raise ValueError("Duplicate observation")
        rows[key] = dict(data=key, valor=int(value.replace(".", "")), publicado=value)
    if not rows:
        raise ValueError("Empty provider series")
    return rows

def save(name, content):
    target = ROOT / name
    tmp = target.with_suffix(".tmp")
    tmp.write_bytes(content)
    tmp.replace(target)

def main():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "Referer": URL.removesuffix(".csv"),
        "Accept": "text/csv,application/vnd.ms-excel,application/json,text/plain,*/*"
    }
    rows = None
    with requests.Session() as session:
        session.headers.update(headers)
        for query in ("?:showVizHome=no", "?:refresh=yes", "?:showVizHome=n", ""):
            try:
                with session.get(URL + query, timeout=(10, 25), stream=True, allow_redirects=True) as response:
                    response.raise_for_status()
                    raw = response.raw.read(10_000_001, decode_content=True)
                if len(raw) > 10_000_000:
                    raise ValueError("Provider size limit")
                rows = parse_csv(raw)
                print("Provider response validated:", query or "base", flush=True)
                break
            except (requests.RequestException, ValueError, OSError) as exc:
                print("Provider attempt:", query or "base", type(exc).__name__, str(exc), flush=True)
    if rows is None:
        raise RuntimeError("No valid provider response")
    ROOT.mkdir(parents=True, exist_ok=True)
    old = ROOT / "history.json"
    if old.exists():
        previous = json.loads(old.read_text(encoding="utf-8"))["emissores"]
        if max(rows)<max(previous):
            raise ValueError("Stale provider series")
        rows = {**previous, **rows}
    meta = dict(fonte=URL, metrica="emissores", abrangencia="não confirmada", periodicidade="mensal")
    save("source.csv", raw)
    save("history.json", json.dumps(dict(nfe={}, emissores=rows, **meta), ensure_ascii=False, indent=2).encode())
    save("latest.json", json.dumps(dict(documento=None, emissores=rows[max(rows)], **meta), ensure_ascii=False, indent=2).encode())
    print("Provider observations:", len(rows))

if __name__ == "__main__":
    main()
