import io
import zipfile
import xml.etree.ElementTree as ET
import requests

BASE = 'https://public.tableau.com'
headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126.0.0.0 Safari/537.36','Referer':BASE+'/views/EstatsticasNFCe/NFCe'}
with requests.Session() as session:
    session.headers.update(headers)
    for path in ['/workbooks/EstatsticasNFCe.twbx','/workbooks/EstatsticasNFCe.twb']:
        try:
            with session.get(BASE+path,timeout=(10,40),stream=True) as res:
                res.raise_for_status()
                raw = res.raw.read(30_000_001,decode_content=True)
                print('Workbook:',res.status_code,res.headers.get('Content-Type'),len(raw))
            if len(raw)>30_000_000: continue
            if zipfile.is_zipfile(io.BytesIO(raw)):
                with zipfile.ZipFile(io.BytesIO(raw)) as archive:
                    for info in archive.infolist():
                        if info.filename.endswith('.twb') and info.file_size<20_000_000:
                            root=ET.fromstring(archive.read(info))
                            for tag in ['worksheet','dashboard','window']:
                                for item in root.iter(tag):
                                    print(tag,repr(item.get('name')),repr(item.get('class')))
                            for item in root.iter('repository-location'):
                                print('view metadata', {k:v for k,v in item.attrib.items() if k in ('id','path','revision')})
            elif raw.lstrip().startswith(b'<?xml'):
                root=ET.fromstring(raw)
                for tag in ['worksheet','dashboard','window']:
                    for item in root.iter(tag): print(tag,repr(item.get('name')))
        except Exception as exc:
            print('Discovery:',type(exc).__name__,str(exc))
    try:
        res=session.get(BASE+'/profile/api/viz/EstatsticasNFCe',timeout=20)
        print('Metadata:',res.status_code,res.headers.get('Content-Type'))
        if 'json' in res.headers.get('Content-Type',''):
            data=res.json()
            def walk(obj):
                if isinstance(obj,dict):
                    for k,v in obj.items():
                        if k.lower() in ('sheetname','viewname','sheeturl','viewurl','sheetnames','views','sheets') and isinstance(v,(str,list)): print(k,str(v)[:3000])
                        walk(v)
                elif isinstance(obj,list):
                    for v in obj: walk(v)
            walk(data)
    except Exception as exc: print(type(exc).__name__,str(exc))

from urllib.parse import quote
from concurrent.futures import ThreadPoolExecutor
import re
names = [
'Evolução NFCe autorizadas','NFCe autorizadas por ano',
'Acumulado NFC-e Autorizadas','Mapa do acumulado de NFC-e autorizadas']
def probe(name):
    candidates = list(dict.fromkeys([name, re.sub(r'[^a-zA-Z0-9]', '', name), name.replace(' ', ''), name.replace(' ', '_')]))
    for candidate in candidates:
        url = BASE+'/views/EstatsticasNFCe/'+quote(candidate,safe='')+'.csv?:showVizHome=no'
        try:
            res=requests.get(url,headers=headers,timeout=(8,15))
            print('Export:',repr(name),res.status_code,res.headers.get('Content-Type'),len(res.content),url,flush=True)
            if res.ok and 'csv' in res.headers.get('Content-Type','').lower():
                print('CSV sample:',repr(res.text[:500]),flush=True)
        except requests.RequestException as exc:
            print('Export failure:',type(exc).__name__,flush=True)
with ThreadPoolExecutor(max_workers=4) as pool:
    list(pool.map(probe,names))
