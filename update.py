#!/usr/bin/env python3
"""Build stories.js from free feeds using only the Python standard library."""
import html
import json
import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from urllib.parse import urlparse

RSS_FEEDS = {
    "nba": [
        ("RotoWire", "https://www.rotowire.com/rss/news.php?sport=NBA"),
        ("ESPN", "https://www.espn.com/espn/rss/nba/news"),
        ("FOX Sports", "https://api.foxsports.com/v2/content/optimized-rss?partnerKey=MB0Wehpmuj2lUhuRhQaafhBjAJqaPU244mlTDK1i&size=30&tags=fs%2Fnba"),
        ("FantasySP", "https://www.fantasysp.com/rss/nba/fantasysp/"),
        ("Yahoo Sports", "https://sports.yahoo.com/nba/rss/"),
        ("CBS Sports", "https://www.cbssports.com/rss/headlines/nba/"),
        ("Hoops Rumors", "https://www.hoopsrumors.com/feed"),
    ],
    "nbl": [
        ("Google News", "https://news.google.com/rss/search?q=Australian+NBL+basketball&hl=en-AU&gl=AU&ceid=AU:en"),
    ],
    "mlb": [
        ("RotoWire", "https://www.rotowire.com/rss/news.php?sport=MLB"),
        ("ESPN", "https://www.espn.com/espn/rss/mlb/news"),
        ("FOX Sports", "https://api.foxsports.com/v2/content/optimized-rss?partnerKey=MB0Wehpmuj2lUhuRhQaafhBjAJqaPU244mlTDK1i&size=30&tags=fs%2Fmlb"),
        ("FantasySP", "https://www.fantasysp.com/rss/mlb/fantasysp/"),
        ("Yahoo Sports", "https://sports.yahoo.com/mlb/rss/"),
        ("CBS Sports", "https://www.cbssports.com/rss/headlines/mlb/"),
        ("MLB.com", "https://www.mlb.com/feeds/news/rss.xml"),
        ("MLB Trade Rumors", "https://www.mlbtraderumors.com/feed"),
    ],
    "nfl": [
        ("RotoWire", "https://www.rotowire.com/rss/news.php?sport=NFL"),
        ("ESPN", "https://www.espn.com/espn/rss/nfl/news"),
        ("FOX Sports", "https://api.foxsports.com/v2/content/optimized-rss?partnerKey=MB0Wehpmuj2lUhuRhQaafhBjAJqaPU244mlTDK1i&size=30&tags=fs%2Fnfl"),
        ("FantasySP", "https://www.fantasysp.com/rss/nfl/fantasysp/"),
        ("Yahoo Sports", "https://sports.yahoo.com/nfl/rss/"),
        ("CBS Sports", "https://www.cbssports.com/rss/headlines/nfl/"),
        ("BBC Sport", "https://feeds.bbci.co.uk/sport/american-football/rss.xml"),
        ("PFF", "https://www.pff.com/feed"),
        ("Pro Football Rumors", "https://www.profootballrumors.com/feed"),
    ],
    "nhl": [
        ("RotoWire", "https://www.rotowire.com/rss/news.php?sport=NHL"),
        ("ESPN", "https://www.espn.com/espn/rss/nhl/news"),
        ("FOX Sports", "https://api.foxsports.com/v2/content/optimized-rss?partnerKey=MB0Wehpmuj2lUhuRhQaafhBjAJqaPU244mlTDK1i&size=30&tags=fs%2Fnhl"),
        ("FantasySP", "https://www.fantasysp.com/rss/nhl/fantasysp/"),
        ("Yahoo Sports", "https://sports.yahoo.com/nhl/rss/"),
        ("CBS Sports", "https://www.cbssports.com/rss/headlines/nhl/"),
        ("Daily Faceoff", "https://www.dailyfaceoff.com/rss"),
        ("Pro Hockey Rumors", "https://www.prohockeyrumors.com/feed"),
    ],
    "soccer": [
        ("RotoWire", "https://www.rotowire.com/rss/news.php?sport=SOCCER"),
        ("ESPN", "https://www.espn.com/espn/rss/soccer/news"),
        ("FOX Sports", "https://api.foxsports.com/v2/content/optimized-rss?partnerKey=MB0Wehpmuj2lUhuRhQaafhBjAJqaPU244mlTDK1i&size=30&tags=fs%2Fsoccer"),
        ("Yahoo Sports", "https://sports.yahoo.com/soccer/rss/"),
        ("CBS Sports", "https://www.cbssports.com/rss/headlines/soccer/"),
        ("BBC Sport", "https://feeds.bbci.co.uk/sport/football/rss.xml"),
        ("The Guardian", "https://www.theguardian.com/football/rss"),
    ],
    "afl": [
        ("DT Talk", "https://dreamteamtalk.com/feed/"),
        ("Keeper League", "https://keeperleaguepod.com.au/feed/"),
        ("AFL.com.au", "https://www.afl.com.au/rss"),
        ("AFL Fantasy", "https://www.afl.com.au/fantasy/rss"),
    ],
    "cricket": [
        ("ESPNcricinfo", "https://www.espncricinfo.com/rss/content/story/feeds/0.xml"),
        ("BBC Sport", "https://feeds.bbci.co.uk/sport/cricket/rss.xml"),
    ],
}
NBC_PLAYER_NEWS = {
    "nba": "https://www.nbcsports.com/fantasy/basketball/player-news",
    "nfl": "https://www.nbcsports.com/fantasy/football/player-news",
    "mlb": "https://www.nbcsports.com/fantasy/baseball/player-news",
}
GDELT_AFL = "https://api.gdeltproject.org/api/v2/doc/doc?query=%28AFL%20OR%20%22Australian%20Football%20League%22%29&mode=artlist&maxrecords=50&format=json&sort=datedesc"
DEFAULT_LIMIT_PER_SPORT = 30
SPORT_LIMITS = {"nba": 80, "afl": 60}
DEFAULT_LIMIT_PER_SOURCE = 15
SOURCE_LIMITS = {
    ("nba", "NBC Sports Rotoworld"): 45,
    ("nba", "RotoWire"): 25,
    ("afl", "AFL.com.au"): 25,
    ("afl", "DT Talk"): 25,
}
DEFAULT_PRIORITY_LIMIT = 20
PRIORITY_LIMITS = {"nba": 60, "afl": 35}
MAX_STORY_AGE = timedelta(days=14)

def sport_limit(sport):
    return SPORT_LIMITS.get(sport, DEFAULT_LIMIT_PER_SPORT)

def source_limit(sport, source):
    return SOURCE_LIMITS.get((sport, source), DEFAULT_LIMIT_PER_SOURCE)

def priority_limit(sport):
    return PRIORITY_LIMITS.get(sport, DEFAULT_PRIORITY_LIMIT)

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
    with urllib.request.urlopen(request, timeout=12) as response:
        return response.read()

def iso_date(value):
    try:
        parsed = parsedate_to_datetime(value)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc).isoformat()
    except (TypeError, ValueError, OverflowError):
        return datetime.now(timezone.utc).isoformat()

def iso_timestamp(value):
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc).isoformat()
    except (AttributeError, ValueError):
        return datetime.now(timezone.utc).isoformat()

def rss_stories(sport, source, url):
    root = ET.fromstring(fetch(url))
    stories = []
    for item in root.findall(".//item")[:sport_limit(sport)]:
        title = clean(item.findtext("title"))
        item_source = clean(item.findtext("source"))
        if source == "Google News" and item_source:
            suffix = f" - {item_source}"
            if title.endswith(suffix):
                title = title[:-len(suffix)]
        link = clean(item.findtext("link"))
        restricted_feed = source in {"ESPN", "FOX Sports"}
        description = "" if restricted_feed else short(item.findtext("description"))
        if description.lower() == title.lower() or title.lower() in description.lower():
            description = ""
        if title and link:
            players = []
            if source == "RotoWire" and ":" in title:
                player = clean(title.split(":", 1)[0])
                if len(player.split()) >= 2:
                    players = [player]
            stories.append({"sport": sport, "title": title, "summary": description,
                            "url": link, "source": (item_source if source == "Google News" and item_source
                                                     else f"Provided by {source}" if restricted_feed else source),
                            "publishedAt": iso_date(item.findtext("pubDate")),
                            "players": players,
                            "kind": ("player" if source == "RotoWire" else
                                     "fantasy" if source in {"FantasySP", "DT Talk", "Keeper League", "AFL Fantasy", "PFF"} else "news")})
    return stories

def nbc_player_stories(sport, url):
    stories = []
    page_numbers = range(1, 5) if sport == "nba" else range(1, 2)
    for page_number in page_numbers:
        page_url = url if page_number == 1 else f"{url}?p={page_number}"
        try:
            page = fetch(page_url).decode("utf-8", "ignore")
        except Exception:
            if page_number == 1:
                raise
            break
        for block in re.split(r'<li class="PlayerNewsModuleList-item"[^>]*>', page)[1:]:
            player_link = re.search(r'PlayerNewsPost-name-container.*?<a href="([^"]+)"', block, re.S)
            headline = re.search(r'<h3 class="PlayerNewsPost-headline">(.*?)</h3>', block, re.S)
            analysis = re.search(r'<div class="PlayerNewsPost-analysis">(.*?)(?:<div class="PlayerNewsPost-author"|</div>)', block, re.S)
            published = re.search(r'PlayerNewsPost-date[^>]*data-date="([^"]+)"', block)
            first_name = re.search(r'PlayerNewsPost-firstName[^>]*>(.*?)</span>', block, re.S)
            last_name = re.search(r'PlayerNewsPost-lastName[^>]*>(.*?)</span>', block, re.S)
            player = clean(" ".join(part.group(1) for part in (first_name, last_name) if part))
            title = clean(headline.group(1)) if headline else ""
            link = html.unescape(player_link.group(1)) if player_link else ""
            if title and link:
                stories.append({"sport": sport, "title": title,
                                "summary": short(analysis.group(1)) if analysis else "",
                                "url": link, "source": "NBC Sports Rotoworld",
                                "publishedAt": iso_timestamp(published.group(1) if published else ""),
                                "players": [player] if player else [],
                                "kind": "player"})
    return stories[:sport_limit(sport)]

def gdelt_afl_stories():
    payload = json.loads(fetch(GDELT_AFL))
    stories = []
    for article in payload.get("articles", [])[:sport_limit("afl")]:
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

def is_fresh(story):
    try:
        published = datetime.fromisoformat(story["publishedAt"].replace("Z", "+00:00"))
        return published >= datetime.now(timezone.utc) - MAX_STORY_AGE
    except (KeyError, TypeError, ValueError):
        return False

def main():
    stories = []
    failures = []
    for sport, url in NBC_PLAYER_NEWS.items():
        try:
            stories.extend(nbc_player_stories(sport, url))
        except Exception as error:
            failures.append(f"NBC player news {sport}: {error}")
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

    stories = [story for story in stories if is_fresh(story)]
    stories.sort(key=lambda story: story["publishedAt"], reverse=True)
    unique = []
    counts = {}
    source_counts = {}
    priority_counts = {}
    prioritized = [story for story in stories if story.get("kind") == "player"]
    prioritized.extend(story for story in stories if story.get("kind") == "fantasy")
    prioritized.extend(story for story in stories if story.get("kind") not in {"player", "fantasy"})
    for story in prioritized:
        if counts.get(story["sport"], 0) >= sport_limit(story["sport"]):
            continue
        if story.get("kind") in {"player", "fantasy"} and priority_counts.get(story["sport"], 0) >= priority_limit(story["sport"]):
            continue
        source_key = (story["sport"], story["source"])
        if len(RSS_FEEDS.get(story["sport"], [])) > 1 and source_counts.get(source_key, 0) >= source_limit(*source_key):
            continue
        if any(duplicate(story, existing) for existing in unique):
            continue
        unique.append(story)
        counts[story["sport"]] = counts.get(story["sport"], 0) + 1
        source_counts[source_key] = source_counts.get(source_key, 0) + 1
        if story.get("kind") in {"player", "fantasy"}:
            priority_counts[story["sport"]] = priority_counts.get(story["sport"], 0) + 1

    unique.sort(key=lambda story: story["publishedAt"], reverse=True)

    if not unique:
        raise SystemExit("All feeds failed; keeping the existing stories.js")
    try:
        existing = json.loads(Path("stories.json").read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        existing = {}
    if existing.get("stories") == unique:
        print(f"No story changes; kept existing {len(unique)}-story feed.")
        return
    payload = {"updatedAt": datetime.now(timezone.utc).isoformat(), "stories": unique}
    Path("stories.js").write_text("window.SPORTS_FEED=" + json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
    Path("stories.json").write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    print(f"Wrote {len(unique)} stories. " + ("Failures: " + "; ".join(failures) if failures else "All sources responded."))

if __name__ == "__main__":
    main()
