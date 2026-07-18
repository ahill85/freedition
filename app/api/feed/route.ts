import { NextRequest, NextResponse } from "next/server";

type Sport = "nba" | "nfl" | "afl" | "cricket";
type Story = { id: string; title: string; url: string; source: string; publishedAt: string; sport: Sport };

const feeds: Record<Sport, string> = {
  nba: "https://www.espn.com/espn/rss/nba/news",
  nfl: "https://www.espn.com/espn/rss/nfl/news",
  afl: "https://www.abc.net.au/news/feed/7077144/rss.xml",
  cricket: "https://www.espncricinfo.com/rss/content/story/feeds/0.xml",
};

const sourceNames: Record<Sport, string> = { nba: "ESPN", nfl: "ESPN", afl: "ABC News", cricket: "ESPNcricinfo" };

function decode(value: string) {
  return value
    .replace(/<!\[CDATA\[([\s\S]*?)\]\]>/g, "$1")
    .replace(/&amp;/g, "&").replace(/&quot;/g, '"').replace(/&#39;|&apos;/g, "'")
    .replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&#8217;/g, "’")
    .replace(/<[^>]+>/g, "").trim();
}

function tag(xml: string, name: string) {
  return decode(xml.match(new RegExp(`<${name}(?:\\s[^>]*)?>([\\s\\S]*?)<\\/${name}>`, "i"))?.[1] ?? "");
}

function parseFeed(xml: string, sport: Sport): Story[] {
  return [...xml.matchAll(/<item>([\s\S]*?)<\/item>/gi)].slice(0, 25).map((match) => {
    const item = match[1];
    const rawTitle = tag(item, "title");
    const source = tag(item, "source") || sourceNames[sport];
    const title = rawTitle.endsWith(` - ${source}`) ? rawTitle.slice(0, -(source.length + 3)) : rawTitle;
    const url = tag(item, "link");
    const publishedAt = tag(item, "pubDate") || new Date().toISOString();
    return { id: `${sport}-${url}`, title, url, source, publishedAt, sport };
  }).filter((story) => story.title && story.url);
}

function key(title: string) {
  return title.toLowerCase().replace(/[^a-z0-9 ]/g, "").split(/\s+/).filter((word) => word.length > 3).slice(0, 8).sort().join(" ");
}

export async function GET(request: NextRequest) {
  const requested = request.nextUrl.searchParams.get("sport") ?? "all";
  const selected = requested === "all" ? Object.keys(feeds) as Sport[] : Object.keys(feeds).includes(requested) ? [requested as Sport] : [];
  if (!selected.length) return NextResponse.json({ error: "Unknown sport" }, { status: 400 });

  const results = await Promise.allSettled(selected.map(async (sport) => {
    const response = await fetch(feeds[sport], { headers: { "User-Agent": "SportsNewsFeed/1.0" } });
    if (!response.ok) throw new Error(`${sport} feed failed`);
    return parseFeed(await response.text(), sport);
  }));

  const seen = new Set<string>();
  const stories = results.flatMap((result) => result.status === "fulfilled" ? result.value : [])
    .sort((a, b) => new Date(b.publishedAt).getTime() - new Date(a.publishedAt).getTime())
    .filter((story) => { const value = key(story.title); if (seen.has(value)) return false; seen.add(value); return true; })
    .slice(0, requested === "all" ? 40 : 30);

  return NextResponse.json({ stories, fetchedAt: new Date().toISOString() }, {
    headers: { "Cache-Control": "public, max-age=300, s-maxage=900, stale-while-revalidate=3600" },
  });
}
