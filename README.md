# Sports News

A dependency-free static sports headline feed.

## Update locally

```sh
python3 update.py
```

Then open `index.html` directly in a browser. The GitHub workflow refreshes the feed every 15 minutes and deploys it to GitHub Pages.

## GitHub Pages setup

Create a public GitHub repository, push these files to its `main` branch, then set **Settings → Pages → Source** to **GitHub Actions**.
