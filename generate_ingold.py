from pathlib import Path
import json
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import format_datetime

ORCID = "0000-0001-6703-6137"
url = f"https://pub.orcid.org/v3.0/{ORCID}/works"
req = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": "TimIngoldRSS/1.0 (personal scholarly feed)"})
with urllib.request.urlopen(req, timeout=40) as response:
    data = json.load(response)

rss = ET.Element("rss", version="2.0")
channel = ET.SubElement(rss, "channel")
def add(parent, tag, value):
    ET.SubElement(parent, tag).text = str(value or "")
add(channel, "title", "Tim Ingold — ORCID Research Publications")
add(channel, "link", f"https://orcid.org/{ORCID}")
add(channel, "description", "Public research outputs listed on Tim Ingold's ORCID record; checked daily.")
add(channel, "language", "en")
add(channel, "lastBuildDate", format_datetime(datetime.now(timezone.utc)))
entries = []
seen = set()
for group in data.get("group", []):
    summaries = group.get("work-summary") or []
    if not summaries:
        continue
    work = next((s for s in summaries if s.get("external-ids")), summaries[0])
    title = ((work.get("title") or {}).get("title") or {}).get("value") or "Untitled work"
    ids = (work.get("external-ids") or {}).get("external-id") or []
    doi = next((i.get("external-id-value") for i in ids if (i.get("external-id-type") or "").lower() == "doi"), None)
    if doi:
        doi = doi.strip().removeprefix("https://doi.org/").removeprefix("http://dx.doi.org/")
    key = (doi or title.casefold().strip())
    if key in seen:
        continue
    seen.add(key)
    link = "https://doi.org/" + doi if doi else ((work.get("url") or {}).get("value") or f"https://orcid.org/{ORCID}")
    date = work.get("publication-date") or {}
    def part(k, default):
        return int((date.get(k) or {}).get("value") or default)
    try:
        year = part("year", 1900)
        published = datetime(year, part("month", 1), part("day", 1), tzinfo=timezone.utc) if year > 1900 else None
    except (ValueError, TypeError):
        published = None
    entries.append((published, title, link, doi, work))
for published, title, link, doi, work in sorted(entries, key=lambda x: x[0] or datetime(1900, 1, 1, tzinfo=timezone.utc), reverse=True):
    item = ET.SubElement(channel, "item")
    add(item, "title", title)
    add(item, "link", link)
    add(item, "guid", "doi:" + doi if doi else "orcid:" + str(work.get("put-code") or title))
    add(item, "description", "Publication type: " + str(work.get("publication-type") or "Not specified") + " | Source: Tim Ingold ORCID")
    if published:
        add(item, "pubDate", format_datetime(published))
ET.indent(rss, space="  ")
ET.ElementTree(rss).write(Path(__file__).with_name("tim-ingold.xml"), encoding="utf-8", xml_declaration=True)
print(f"Generated {len(entries)} Tim Ingold publications")
