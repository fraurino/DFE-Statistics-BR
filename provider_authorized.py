import csv, io, json, re
from collections import defaultdict
from pathlib import Path
import requests
from provider_nfce import ROOT, save

BASE = "https://public.tableau.com/views/EstatsticasNFCe/"
SHEETS = {"monthly":"EvoluoNFCeautorizadas","states":"NFCeautorizadasporano","national":"AcumuladoNFC-eAutorizadas","map":"MapadoacumuladodeNFC-eautorizadas"}
UFS = set("AC AL AM AP BA CE DF ES GO MA MG MS MT PA PB PE PI PR RJ RN RO RR RS SC SE SP TO".split())
MONTHS = "janeiro fevereiro março abril maio junho julho agosto setembro outubro novembro dezembro".split()
EN = "january february march april may june july august september october november december".split()
def number(v):
    v=v.strip()
    if not re.fullmatch(r"[0-9]+|[0-9]{1,3}(?:[.,][0-9]{3})+",v): raise ValueError("Invalid count")
    return int(v.replace(".","").replace(",",""))
def period(row):
    month=next(v for k,v in row.items() if k.startswith(("Month of","Mês de")))
    year=next(v for k,v in row.items() if k.startswith(("Year of","Ano de")))
    m=month.lower().strip()
    return f"{int(year):04d}-{(MONTHS.index(m) if m in MONTHS else EN.index(m))+1:02d}-01"
def obs(d,v):
    return dict(data=d,valor=v,publicado=f"{v:,}".replace(",","."))
def collect():
    raw={}; tables={}
    with requests.Session() as s:
        s.headers.update({"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126.0.0.0 Safari/537.36","Referer":BASE+"NFCe","Accept":"text/csv"})
        for key,sheet in SHEETS.items():
            response=s.get(BASE+sheet+".csv?:showVizHome=no",timeout=(10,25))
            response.raise_for_status()
            raw[key]=response.content
            if len(raw[key])>10_000_000: raise ValueError("Size limit")
            tables[key]=list(csv.DictReader(io.StringIO(raw[key].decode("utf-8-sig"))))
            if not tables[key]: raise ValueError("Empty table")
    national={}
    for row in tables["national"]:
        d=period(row)
        if d in national: raise ValueError("Duplicate month")
        national[d]=obs(d,number(row["acumuladoAutorizadas"]))
    states={}
    for row in tables["states"]:
        uf=row["UF"]
        if uf not in UFS or uf in states: raise ValueError("Invalid UF")
        states[uf]=number(row["Notas Autorizadas"])
    monthly=defaultdict(dict)
    missing=[]
    for row in tables["monthly"]:
        uf=row["UF"]; d=period(row)
        if uf not in UFS or d in monthly[uf]: raise ValueError("Invalid monthly UF")
        value=row["Notas Autorizadas"]
        if value is None or value.strip().lower() in ("", "null", "none", "n/a", "-", "—"):
            missing.append(dict(uf=uf,data=d))
            monthly[uf][d]=None
        else:
            try: monthly[uf][d]=number(value)
            except ValueError as exc: raise ValueError(f"Invalid monthly count {uf} {d}: {value!r}") from exc
    if set(states)!=UFS or set(monthly)!=UFS: raise ValueError("Incomplete UF coverage")
    last=max(national)
    previous=ROOT/"authorized.json"
    if previous.exists() and json.loads(previous.read_text())["latest"]["data"]>last: raise ValueError("Stale series")
    regions={}
    for uf,rows in monthly.items():
        total=0; hist={}
        for d,v in sorted(rows.items()):
            if v is None: continue
            total+=v; hist[d]=obs(d,total)
        regions[uf]=dict(history=hist,monthly=rows,total=states[uf],consistent=total==states[uf],missing=sum(v is None for v in rows.values()))
    annual=defaultdict(int)
    for rows in monthly.values():
        for d,v in rows.items():
            if v is not None: annual[d[:4]]+=v
    payload=dict(latest=national[last],history=national,states=states,regions=regions,annual=annual,missing=missing,annual_partial=sorted({x["data"][:4] for x in missing}),periodicidade="mensal",state_sum=sum(states.values()),consistent=sum(states.values())==national[last]["valor"],sources={k:BASE+v+".csv?:showVizHome=no" for k,v in SHEETS.items()})
    for key,data in raw.items(): save(key+".csv",data)
    save("authorized.json",json.dumps(payload,ensure_ascii=False,indent=2).encode())
    print("Authorization observations:",len(national),"UF:",len(states),"missing:",len(missing),"consistent:",payload["consistent"],flush=True)
if __name__=="__main__": collect()
