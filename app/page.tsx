"use client";

import { useEffect, useState } from "react";

type Sport = "all" | "nba" | "nfl" | "afl" | "cricket";
type Story = { id: string; title: string; url: string; source: string; publishedAt: string; sport: Exclude<Sport, "all"> };

const sports: { id: Sport; label: string }[] = [
  { id: "all", label: "ALL" },
  { id: "nba", label: "NBA" },
  { id: "nfl", label: "NFL" },
  { id: "afl", label: "AFL" },
  { id: "cricket", label: "CRICKET" },
];

function timeAgo(date: string) {
  const minutes = Math.max(1, Math.floor((Date.now() - new Date(date).getTime()) / 60000));
  if (minutes < 60) return `${minutes}m ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h ago`;
  return `${Math.floor(hours / 24)}d ago`;
}

export default function Home() {
  const [sport, setSport] = useState<Sport>("all");
  const [stories, setStories] = useState<Story[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  useEffect(() => {
    const controller = new AbortController();
    setLoading(true);
    setError(false);
    fetch(`/api/feed?sport=${sport}`, { signal: controller.signal })
      .then((response) => {
        if (!response.ok) throw new Error("Feed unavailable");
        return response.json();
      })
      .then((data) => setStories(data.stories ?? []))
      .catch((reason) => { if (reason.name !== "AbortError") setError(true); })
      .finally(() => setLoading(false));
    return () => controller.abort();
  }, [sport]);

  return (
    <main>
      <header className="site-header">
        <a className="brand" href="#top">SPORTS NEWS</a>
        <nav aria-label="Sports">
          {sports.map((item) => (
            <button key={item.id} className={sport === item.id ? "active" : ""} onClick={() => setSport(item.id)}>
              {item.label}
            </button>
          ))}
        </nav>
      </header>

      <section className="feed" id="top">
        <div className="feed-title">
          <h1>{sports.find((item) => item.id === sport)?.label} NEWS</h1>
          <span>LIVE FEED</span>
        </div>

        {loading && <div className="status">Loading latest stories…</div>}
        {error && <div className="status error">The feed could not load. Try again shortly.</div>}
        {!loading && !error && stories.length === 0 && <div className="status">No recent stories found.</div>}

        {!loading && !error && stories.map((story) => (
          <article className="news-item" key={story.id}>
            <span className={`sport sport-${story.sport}`}>{story.sport.toUpperCase()}</span>
            <div>
              <h2><a href={story.url} target="_blank" rel="noreferrer">{story.title}</a></h2>
              <p>{story.source} <span>·</span> {timeAgo(story.publishedAt)}</p>
            </div>
            <a className="open-story" href={story.url} target="_blank" rel="noreferrer" aria-label={`Read ${story.title}`}>↗</a>
          </article>
        ))}
      </section>
    </main>
  );
}
