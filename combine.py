"""Merge Sarah Pink and Tim Ingold ORCID RSS feeds into one RSS 2.0 feed."""
from pathlib import Path
from datetime import datetime, timezone
from email.utils import format_datetime, parsedate_to_datetime
import xml.etree.ElementTree as ET

root = ET.Element("rss", version="2.0")
channel = ET.SubElement(root, "channel")
def add(parent, name, value):
    ET.SubElement(parent, name).text = str(value)
add(channel, "title", "Sarah Pink & Tim Ingold — Research Publications")
add(channel, "link", "https://fusion84ry.github.io/sarah-pink-rss/combined.xml")
add(channel, "description", "Combined ORCID publications of Sarah Pink and Tim Ingold, including coauthored works.")
add(channel, "language", "en")
add(channel, "lastBuildDate", format_datetime(datetime.now(timezone.utc)))

items = []
seen = set()
for filename, author in [("feed.xml", "Sarah Pink"), ("tim-ingold.xml", "Tim Ingold")]:
    source = ET.parse(Path(__file__).with_name(filename)).getroot()
    for item in source.findall("./channel/item"):
        title = item.findtext("title") or "Untitled"
        link = item.findtext("link") or ""
        guid = item.findtext("guid") or link or title
        # Shared DOI/publication appears once, attributed to both researchers.
        key = (link.lower().rstrip("/") if "doi.org/" in link.lower() else guid.lower())
        if key in seen:
            for entry in items:
                if entry[0] == key:
                    entry[2].add(author)
                    break
            continue
        seen.add(key)
        pub = item.findtext("pubDate")
        try:
            dt = parsedate_to_datetime(pub) if pub else datetime(1900, 1, 1, tzinfo=timezone.utc)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
        except (ValueError, TypeError):
            dt = datetime(1900, 1, 1, tzinfo=timezone.utc)
        items.append((key, dt, {author}, title, link, guid, pub, item.findtext("description") or ""))

for _, _, authors, title, link, guid, pub, description in sorted(items, key=lambda e: e[1], reverse=True):
    item = ET.SubElement(channel, "item")
    add(item, "title", title)
    add(item, "link", link)
    add(item, "guid", guid)
    add(item, "author", ", ".join(sorted(authors)))
    add(item, "category", ", ".join(sorted(authors)))
    add(item, "description", "Researcher(s): " + ", ".join(sorted(authors)) + ". " + description)
    if pub:
        add(item, "pubDate", pub)

ET.indent(root, space="  ")
ET.ElementTree(root).write(Path(__file__).with_name("combined.xml"), encoding="utf-8", xml_declaration=True)
print(f"Generated {len(items)} combined publications")
