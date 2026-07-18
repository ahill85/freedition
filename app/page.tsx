const stories = [
  {
    id: 1,
    number: "01",
    eyebrow: "Biggest story",
    icon: "↗",
    tone: "orange",
    headline: "Kawhi trade is stuck",
    happened: "Toronto and LA have paused the agreed Kawhi Leonard trade while the NBA finishes its Clippers investigation.",
    matters: "Two rosters — and seven assets in the deal — remain in limbo. Adam Silver says the teams chose to wait, not the league.",
    impact: 9,
    time: "Updated Jul 15",
    sources: [{ name: "NBA.com", url: "https://www.nba.com/news/raptors-clippers-kawhi-leonard-trade-on-hold" }, { name: "Yahoo Sports", url: "https://sports.yahoo.com/nba/breaking-news/article/adam-silver-says-nba-didnt-pause-kawhi-leonard-trade-that-raptors-clippers-did-confident-probe-will-end-before-new-season-044455115.html" }],
    tag: "TRADE",
  },
  {
    id: 2,
    number: "02",
    eyebrow: "Player trending",
    icon: "↑",
    tone: "blue",
    headline: "Donaldson takes over",
    happened: "Miami rookie Tre Donaldson finished with 20 points, 10 assists and eight rebounds in a 101–87 win over Detroit.",
    matters: "He scored 13 in the fourth as Miami flipped the game 35–15 — the kind of command that earns a longer look in camp.",
    impact: 7,
    time: "Last night · 11:01 PM ET",
    sources: [{ name: "NBA.com", url: "https://www.nba.com/news/live-updates-2026-nba-summer-league-day-9" }],
    tag: "PLAYER",
  },
  {
    id: 3,
    number: "03",
    eyebrow: "Result people are discussing",
    icon: "!",
    tone: "yellow",
    headline: "Kings steal it late",
    happened: "Sacramento beat Charlotte 92–90 after taking the lead inside the final four minutes.",
    matters: "Emanuel Sharp led six Kings in double figures, while Charlotte rookie Hannes Steinbach posted a second straight 20/10 game.",
    impact: 7,
    time: "Today · 1:52 AM ET",
    sources: [{ name: "NBA.com", url: "https://www.nba.com/news/2026-nba-summer-league-kings-hornets" }],
    tag: "RESULT",
  },
  {
    id: 4,
    number: "04",
    eyebrow: "Roster move",
    icon: "+",
    tone: "red",
    headline: "Ja is officially a Blazer",
    happened: "Portland’s trade for Ja Morant is now official, with Jerami Grant and Kris Murray heading to Memphis.",
    matters: "Portland gets a lead guard for its young core; Memphis resets around size, flexibility and future assets.",
    impact: 6,
    time: "Tracker updated Jul 16",
    sources: [{ name: "NBA.com", url: "https://www.nba.com/news/nba-offseason-deals-2026" }],
    tag: "TRADE",
  },
  {
    id: 5,
    number: "05",
    eyebrow: "What matters next",
    icon: "→",
    tone: "green",
    headline: "Four teams, one final",
    happened: "Houston plays Memphis at 6:30 ET, then the unbeaten Lakers face Golden State at 8:30 in tonight’s semifinals.",
    matters: "The winners meet Sunday for the Summer League title. LA enters 4–0 with the tournament’s best point differential.",
    impact: 6,
    time: "Tonight · 6:30 PM ET",
    sources: [{ name: "Yahoo Sports", url: "https://sports.yahoo.com/nba/article/nba-summer-league-2026-daily-schedule-scores-standings-format-how-to-watch-153417060.html" }],
    tag: "NEXT",
  },
];

export default function Home() {
  return (
    <main>
      <header className="site-header">
        <a className="brand" href="#top" aria-label="Five Now home">
          <span className="brand-mark">5</span>
          <span>FIVE NOW</span>
        </a>
        <nav className="league-nav" aria-label="Leagues">
          <a className="active" href="#top">NBA</a>
          <span>NFL</span><span>AFL</span><span>CRICKET</span>
        </nav>
        <span className="updated">UPDATED TODAY</span>
      </header>

      <section className="brief" id="brief">
        <div className="feed-head" id="top">
          <div><span className="live-dot" />NBA · RIGHT NOW</div>
          <span>UPDATED 2:36 PM CT</span>
        </div>

        {stories.map((story, index) => (
          <article className={`story story-${index + 1}`} key={story.id}>
            <div className="story-index">{story.number}</div>
            <div className="story-body">
              <div className={`eyebrow ${story.tone}`}><span>{story.icon}</span>{story.eyebrow}</div>
              <h2>{story.headline}</h2>
              <div className="story-copy">
                <div><label>WHAT HAPPENED</label><p>{story.happened}</p></div>
                <div><label>WHY IT MATTERS</label><p>{story.matters}</p></div>
              </div>
              <div className="story-meta">
                <div className="impact"><span>IMPACT</span><b>{story.impact}</b><small>/10</small><div className="impact-line"><i style={{ width: `${story.impact * 10}%` }} /></div></div>
                <div className="source">{story.time}<br /><span>Sources: {story.sources.map((source, sourceIndex) => <span key={source.url}>{sourceIndex > 0 && " · "}<a href={source.url} target="_blank" rel="noreferrer">{source.name}</a></span>)}</span></div>
              </div>
            </div>
            <div className="story-tag">{story.tag}</div>
          </article>
        ))}
      </section>

    </main>
  );
}
