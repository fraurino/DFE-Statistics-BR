import csv, json, re, time
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from html.parser import HTMLParser
from pathlib import Path
from urllib.request import build_opener, HTTPCookieProcessor, Request
from http.cookiejar import CookieJar

URL = "https://www.nfe.fazenda.gov.br/portal/infoEstatisticas.aspx"
ROOT = Path(__file__).resolve().parent / "docs/api"
PREFIX = "ctl00_ContentPlaceHolder1_lbl"
class Parser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.values = {}
        self.key = None
    def handle_starttag(self, tag, attrs):
        if tag == "span":
            key = dict(attrs).get("id", "")
            if key.startswith(PREFIX):
                self.key = key[len(PREFIX):]
                self.values[self.key] = ""
    def handle_data(self, data):
        if self.key:
            self.values[self.key] += data
    def handle_endtag(self, tag):
        if tag == "span":
            self.key = None

def number(s):
    m = re.fullmatch(r"([\d.,]+)\s+(bilhões|milhões|bilhão|milhão)", s.strip())
    if not m:
        raise ValueError("Formato desconhecido: " + s)
    n = Decimal(m[1].replace(".", "").replace(",", "."))
    return int(n * (10**9 if m[2].startswith("bi") else 10**6))

def parse(html):
    p = Parser()
    p.feed(html)
    result = {}
    for key, suffix in [("nfe", "NFeAutorizada"), ("emissores", "Emissores")]:
        raw = p.values["Valor" + suffix].strip()
        day = datetime.strptime(p.values["Data" + suffix].strip(), "%d/%m/%Y").date()
        result[key] = dict(data=day.isoformat(), valor=number(raw), publicado=raw)
    return result

def save(name, obj):
    (ROOT / name).write_text(json.dumps(obj, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")

def aggregate(rows, kind):
    groups = {}
    for row in rows:
        d = date.fromisoformat(row["data"])
        key = d.isoformat() if kind == "daily" else (d-timedelta(days=d.weekday())).isoformat() if kind == "weekly" else d.isoformat()[:7] if kind == "monthly" else str(d.year)
        groups.setdefault(key, []).append(row)
    return [dict(periodo=k, variacao=sum(x["variacao"] for x in v if x["variacao"] is not None) if any(x["variacao"] is not None for x in v) else None, dias_observados=sum(x["variacao"] is not None for x in v), parcial=True) for k,v in groups.items()]

def publish(history):
    rows = []
    previous = None
    for row in sorted(history["nfe"].values(), key=lambda x:x["data"]):
        delta = None
        if previous and date.fromisoformat(row["data"])-date.fromisoformat(previous["data"]) == timedelta(days=1):
            delta = row["valor"]-previous["valor"]
        rows.append(dict(row, variacao=delta))
        previous = row
    save("history.json", history)
    latest = dict(nfe=rows[-1], emissores=max(history["emissores"].values(), key=lambda x:x["data"]), fonte=URL, aproximado=True)
    save("latest.json", latest)
    for kind in ("daily","weekly","monthly","yearly"):
        save(kind+".json", aggregate(rows,kind))
    with (ROOT/"daily.csv").open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=["data","valor","publicado","variacao"])
        w.writeheader()
        w.writerows(rows)

def main():
    ROOT.mkdir(parents=True, exist_ok=True)
    opener = build_opener(HTTPCookieProcessor(CookieJar()))
    for attempt in range(3):
        try:
            with opener.open(Request(URL, headers={"User-Agent":"DFE-Statistics-BR/1.0 (+https://github.com/fraurino/DFE-Statistics-BR)"}), timeout=40) as response:
                result=parse(response.read().decode(response.headers.get_content_charset() or "utf-8"))
            break
        except Exception:
            if attempt == 2: raise
            time.sleep(5*(attempt+1))
    history=json.loads((ROOT/"history.json").read_text(encoding="utf-8")) if (ROOT/"history.json").exists() else {"nfe":{},"emissores":{}}
    for key,row in result.items():
        history[key][row["data"]]=row
    publish(history)
    print(result)

if __name__ == "__main__":
    main()
