# FREEDITION

A dependency-free static sports headline feed. It needs Python 3 to refresh the
headlines, but the published website is plain HTML, CSS and JavaScript.

## Run locally

From this folder:

```sh
python3 update.py
python3 -m http.server 8000
```

Open <http://localhost:8000>. Stop the local server with `Ctrl+C`.

Running `python3 update.py` again refreshes `stories.js`. Reload the browser to
see the new stories. There is nothing to install and no Node.js dependency.

## Publish the updater on GitHub

1. Sign in to GitHub and create a new **public** repository named `freedition`.
   Do not initialise it with a README, `.gitignore`, or licence.
2. In this folder, replace `YOUR-USERNAME` below and run:

   ```sh
   git add .
   git commit -m "Launch FREEDITION"
   git remote add origin https://github.com/YOUR-USERNAME/freedition.git
   git push -u origin main
   ```

3. Open **Actions → Update sports feed → Run workflow** once.

The included workflow checks the feed data every 30 minutes. It has a hard two-minute
timeout, so a 31-day month is capped at 1,488 scheduled jobs. The repository is public,
so its standard GitHub-hosted runner usage is free.
It only commits when the story set changes and
can also be run manually from the Actions tab. It uses Python's standard
library only: no server, database, API key, Node.js process, or paid worker.

The public site also reads `stories.json` from this repository, caching it in the
browser for 15 minutes to avoid an origin request on every page view. A copy hosted at
`astarmedia.net/freedition` therefore receives new stories without repeated FTP
uploads. `stories.js` remains a local fallback if GitHub cannot be reached.

## Current feeds

- AFL: DT Talk, Keeper League, AFL.com.au, with GDELT as an emergency fallback
- ICC cricket: ESPNcricinfo
- MLB: NBC Sports Rotoworld player news, RotoWire, FantasySP, ESPN, FOX Sports, Yahoo Sports, CBS Sports
- NBA: NBC Sports Rotoworld player news, RotoWire, FantasySP, ESPN, FOX Sports, Yahoo Sports, CBS Sports
- NBL: Google News RSS, retaining each original publisher's attribution
- NFL: NBC Sports Rotoworld player news, RotoWire, FantasySP, ESPN, FOX Sports, Yahoo Sports, CBS Sports, BBC Sport
- NHL: RotoWire, FantasySP, ESPN, FOX Sports, Yahoo Sports, CBS Sports
- Soccer: RotoWire, ESPN, FOX Sports, Yahoo Sports, CBS Sports, BBC Sport

Stories retain their publisher attribution and link directly to the original
article. Duplicate headlines are merged. NBA keeps up to 80 items, AFL up to
60, and the supporting sports up to 30 each.
