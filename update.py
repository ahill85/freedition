#!/usr/bin/env python3
"""Build stories.js from free feeds using only the Python standard library."""
import html
import json
import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from urllib.parse import urlparse

RSS_FEEDS = {
    "nba": [("ESPN", "https://www.espn.com/espn/rss/nba/news")],
    "nfl": [("ESPN", "https://www.espn.com/espn/rss/nfl/news")],
    "afl": [("AFL.com.au", "https://www.afl.com.au/rss")],
    "cricket": [("ESPNcricinfo", "https://www.espncricinfo.com/rss/content/story/feeds/0.xml")],
}
GDELT_AFL = "https://api.gdeltproject.org/api/v2/doc/doc?query=%28AFL%20OR%20%22Australian%20Football%20League%22%29&mode=artlist&maxrecords=50&format=json&sort=datedesc"
LIMIT_PER_SPORT = 30

def clean(value):
    value = html.unescape(re.sub(r"<[^>]+>", " ", value or ""))
    return re.sub(r"\s+", " ", value).strip()

def short(value, limit=170):
    value = clean(value)
    if len(value) <= limit:
        return value
    clipped = value[:limit].rsplit(" ", 1)[0]
    return clipped + "…"

def fetch(url):
    request = urllib.request.Request(url, headers={"User-Agent": "SportsNewsStaticFeed/1.0"})
    with urllib.request.urlopen(request, timeout=25) as response:
        return response.read()

def iso_date(value):
    try:
        parsed = parsedate_to_datetime(value)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc).isoformat()
    except (TypeError, ValueError, OverflowError):
        return datetime.now(timezone.utc).isoformat()

def rss_stories(sport, source, url):
    root = ET.fromstring(fetch(url))
    stories = []
    for item in root.findall(".//item")[:LIMIT_PER_SPORT]:
        title = clean(item.findtext("title"))
        link = clean(item.findtext("link"))
        description = short(item.findtext("description"))
        if description.lower() == title.lower() or title.lower() in description.lower():
            description = ""
        if title and link:
            stories.append({"sport": sport, "title": title, "summary": description,
                            "url": link, "source": source,
                            "publishedAt": iso_date(item.findtext("pubDate"))})
    return stories

def gdelt_afl_stories():
    payload = json.loads(fetch(GDELT_AFL))
    stories = []
    for article in payload.get("articles", [])[:LIMIT_PER_SPORT]:
        title, url = clean(article.get("title")), article.get("url")
        if not title or not url:
            continue
        raw_date = article.get("seendate", "")
        try:
            date = datetime.strptime(raw_date, "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc).isoformat()
        except ValueError:
            date = datetime.now(timezone.utc).isoformat()
        domain = article.get("domain") or urlparse(url).netloc.removeprefix("www.")
        stories.append({"sport": "afl", "title": title, "summary": "", "url": url,
                        "source": domain, "publishedAt": date})
    return stories

def words(title):
    ignored = {"with", "from", "that", "this", "after", "into", "over", "about", "your"}
    return {word for word in re.findall(r"[a-z0-9]+", title.lower()) if len(word) > 3 and word not in ignored}

def duplicate(a, b):
    if a["sport"] != b["sport"]:
        return False
    left, right = words(a["title"]), words(b["title"])
    return bool(left and right) and len(left & right) / len(left | right) >= 0.62

def main():
    stories = []
    failures = []
    for sport, feeds in RSS_FEEDS.items():
        for source, url in feeds:
            try:
                stories.extend(rss_stories(sport, source, url))
            except Exception as error:
                failures.append(f"{source} {sport}: {error}")
    if not any(story["sport"] == "afl" for story in stories):
        try:
            stories.extend(gdelt_afl_stories())
        except Exception as error:
            failures.append(f"GDELT AFL fallback: {error}")

    stories.sort(key=lambda story: story["publishedAt"], reverse=True)
    unique = []
    counts = {}
    for story in stories:
        if counts.get(story["sport"], 0) >= LIMIT_PER_SPORT:
            continue
        if any(duplicate(story, existing) for existing in unique):
            continue
        unique.append(story)
        counts[story["sport"]] = counts.get(story["sport"], 0) + 1

    if not unique:
        raise SystemExit("All feeds failed; keeping the existing stories.js")
    payload = {"updatedAt": datetime.now(timezone.utc).isoformat(), "stories": unique}
    Path("stories.js").write_text("window.SPORTS_FEED=" + json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
    print(f"Wrote {len(unique)} stories. " + ("Failures: " + "; ".join(failures) if failures else "All sources responded."))

if __name__ == "__main__":
    main()
