"use client";

import { useEffect, useState } from "react";

const stories = [
  {
    id: 1,
    number: "01",
    eyebrow: "Biggest story",
    icon: "↗",
    tone: "orange",
    headline: "Durant lands in Houston",
    happened: "The Rockets have acquired Kevin Durant in a blockbuster deal with Phoenix.",
    matters: "Houston just paired an elite closer with one of the league’s best young cores. They’re a real title threat now.",
    impact: 9,
    time: "12 min ago",
    sources: ["ESPN", "The Athletic", "NBA.com"],
    tag: "TRADE",
  },
  {
    id: 2,
    number: "02",
    eyebrow: "Player trending",
    icon: "↑",
    tone: "blue",
    headline: "Flagg looks ready already",
    happened: "Cooper Flagg scored 31 points and took over late in his best Summer League performance yet.",
    matters: "Dallas didn’t just draft potential. The 18-year-old already looks comfortable creating against NBA-level length.",
    impact: 7,
    time: "34 min ago",
    sources: ["NBA.com", "CBS Sports"],
    tag: "PLAYER",
  },
  {
    id: 3,
    number: "03",
    eyebrow: "Result people are discussing",
    icon: "!",
    tone: "yellow",
    headline: "Thunder make a statement",
    happened: "Oklahoma City erased a 16-point deficit to beat Indiana 111–104 in a Finals rematch.",
    matters: "The champions’ depth remains the league’s hardest problem — even on a quiet night from Shai Gilgeous-Alexander.",
    impact: 7,
    time: "1 hr ago",
    sources: ["ESPN", "AP"],
    tag: "RESULT",
  },
  {
    id: 4,
    number: "04",
    eyebrow: "Important injury",
    icon: "+",
    tone: "red",
    headline: "Tatum rehab hits next phase",
    happened: "Jayson Tatum has progressed to on-court movement work following Achilles surgery.",
    matters: "There’s still no return date, but this is the first meaningful step toward Boston getting its centerpiece back.",
    impact: 6,
    time: "2 hrs ago",
    sources: ["Boston Globe", "ESPN"],
    tag: "INJURY",
  },
  {
    id: 5,
    number: "05",
    eyebrow: "What matters next",
    icon: "→",
    tone: "green",
    headline: "The rookies get the floor",
    happened: "Summer League’s four-team playoff begins tonight in Las Vegas.",
    matters: "It’s the first elimination test for this class, with Flagg and Edgecombe both expected to feature.",
    impact: 6,
    time: "Tonight · 7:00 PM",
    sources: ["NBA.com"],
    tag: "NEXT",
  },
];

const teams = ["Spurs", "Thunder", "Rockets", "Celtics", "Lakers"];

export default function Home() {
  const [followed, setFollowed] = useState<string[]>([]);
  const [saved, setSaved] = useState<number[]>([]);
  const [menuOpen, setMenuOpen] = useState(false);

  useEffect(() => {
    const stored = localStorage.getItem("signal-followed-teams");
    if (stored) setFollowed(JSON.parse(stored));
  }, []);

  function toggleTeam(team: string) {
    const next = followed.includes(team)
      ? followed.filter((item) => item !== team)
      : [...followed, team];
    setFollowed(next);
    localStorage.setItem("signal-followed-teams", JSON.stringify(next));
  }

  return (
    <main>
      <header className="site-header">
        <a className="brand" href="#top" aria-label="Signal home">
          <span className="brand-mark">S</span>
          <span>SIGNAL</span>
        </a>
        <nav className="league-nav" aria-label="Leagues">
          <a className="active" href="#top">NBA</a>
          <span>NFL</span><span>AFL</span><span>CRICKET</span>
        </nav>
        <button className="menu-button" onClick={() => setMenuOpen(!menuOpen)} aria-expanded={menuOpen}>
          <span /> <span />
          <b>{menuOpen ? "CLOSE" : "MENU"}</b>
        </button>
      </header>

      {menuOpen && (
        <div className="menu-panel">
          <a href="#brief" onClick={() => setMenuOpen(false)}>Right now</a>
          <a href="#follow" onClick={() => setMenuOpen(false)}>Your teams</a>
          <a href="#about" onClick={() => setMenuOpen(false)}>How Signal works</a>
        </div>
      )}

      <section className="hero" id="top">
        <div className="hero-kicker"><i /> LIVE BRIEFING · NBA</div>
        <h1>THE 5 THINGS<br />THAT MATTER <em>NOW.</em></h1>
        <div className="hero-bottom">
          <p>No noise. No 900-word recaps.<br />Just what happened, why it matters, and what’s next.</p>
          <div className="update-stamp"><span>UPDATED</span><strong>10:42 AM</strong><small>Next refresh in 08:17</small></div>
        </div>
      </section>

      <section className="brief" id="brief">
        <div className="section-label"><span>TODAY’S BRIEF</span><span>FRI · JUL 18</span></div>

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
                <div className="source">{story.time}<br /><span>Sources: {story.sources.join(" · ")}</span></div>
                <button
                  className={saved.includes(story.id) ? "save saved" : "save"}
                  onClick={() => setSaved(saved.includes(story.id) ? saved.filter((id) => id !== story.id) : [...saved, story.id])}
                  aria-label={`${saved.includes(story.id) ? "Remove" : "Save"} ${story.headline}`}
                >{saved.includes(story.id) ? "✓" : "+"}</button>
              </div>
            </div>
            <div className="story-tag">{story.tag}</div>
          </article>
        ))}
      </section>

      <section className="follow" id="follow">
        <div>
          <span className="mini-label">MAKE IT YOURS</span>
          <h2>FOLLOW THE TEAMS<br />YOU ACTUALLY CARE ABOUT.</h2>
          <p>We’ll still show you the five biggest stories — and give your teams the attention they deserve. Saved on this device.</p>
        </div>
        <div className="team-picker">
          {teams.map((team) => (
            <button key={team} className={followed.includes(team) ? "selected" : ""} onClick={() => toggleTeam(team)}>
              <span>{team.slice(0, 3).toUpperCase()}</span>{team}<b>{followed.includes(team) ? "✓" : "+"}</b>
            </button>
          ))}
        </div>
      </section>

      <section className="manifesto" id="about">
        <span className="mini-label">THE PROMISE</span>
        <blockquote>“SPORTS NEWS<br />WITHOUT THE <em>BULLSHIT.</em>”</blockquote>
        <p>Five things worth knowing. Updated every 15 minutes.<br />Every fact linked to its original source.</p>
      </section>

      <footer>
        <a className="brand" href="#top"><span className="brand-mark">S</span><span>SIGNAL</span></a>
        <p>AUTOMATED WITH CARE.<br />SOURCES ALWAYS CREDITED.</p>
        <p>© 2026 SIGNAL<br />BUILT FOR PEOPLE WITH LIVES.</p>
      </footer>
    </main>
  );
}
