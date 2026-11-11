import json, urllib.request, xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import format_datetime
from pathlib import Path

ORCID='0000-0003-0073-8382'
URL=f'https://pub.orcid.org/v3.0/{ORCID}/works'
req=urllib.request.Request(URL,headers={'Accept':'application/json','User-Agent':'SarahPinkRSS/1.0 (personal scholarly feed)'})
with urllib.request.urlopen(req,timeout=35) as response:
    data=json.load(response)

rss=ET.Element('rss',version='2.0')
channel=ET.SubElement(rss,'channel')
def node(parent,tag,value): ET.SubElement(parent,tag).text=str(value or '')
node(channel,'title','Sarah Pink — ORCID Research Publications')
node(channel,'link',f'https://orcid.org/{ORCID}')
node(channel,'description','Public research outputs listed on Sarah Pink’s ORCID record; updated daily.')
node(channel,'language','en')
node(channel,'lastBuildDate',format_datetime(datetime.now(timezone.utc)))
seen=set()
entries=[]
for group in data.get('group',[]):
    summaries=group.get('work-summary') or []
    if not summaries: continue
    w=next((x for x in summaries if x.get('external-ids')),summaries[0])
    title=((w.get('title') or {}).get('title') or {}).get('value') or 'Untitled work'
    ids=(w.get('external-ids') or {}).get('external-id') or []
    doi=next((x.get('external-id-value') for x in ids if (x.get('external-id-type') or '').lower()=='doi'),None)
    doi=doi.strip().removeprefix('https://doi.org/').removeprefix('http://dx.doi.org/') if doi else None
    link=('https://doi.org/'+doi) if doi else ((w.get('url') or {}).get('value') or f'https://orcid.org/{ORCID}')
    key=(doi or title.strip().casefold())
    if key in seen: continue
    seen.add(key)
    date=w.get('publication-date') or {}
    def val(k,default):
        x=date.get(k) or {}
        return int(x.get('value') or default)
    year=val('year',1900); month=val('month',1); day=val('day',1)
    try: published=datetime(year,month,day,tzinfo=timezone.utc) if year>1900 else None
    except ValueError: published=None
    entries.append((published or datetime(1900,1,1,tzinfo=timezone.utc),title,link,doi,w))
for published,title,link,doi,w in sorted(entries,key=lambda x:x[0],reverse=True):
    item=ET.SubElement(channel,'item')
    node(item,'title',title)
    node(item,'link',link)
    node(item,'guid',('doi:'+doi) if doi else 'orcid:'+str(w.get('put-code') or title))
    node(item,'description','Publication type: '+str(w.get('publication-type') or 'Not specified')+' | Source: Sarah Pink ORCID')
    if published.year>1900: node(item,'pubDate',format_datetime(published))
ET.indent(rss,space='  ')
ET.ElementTree(rss).write(Path(__file__).with_name('feed.xml'),encoding='utf-8',xml_declaration=True)
print(f'Generated {len(entries)} items')
