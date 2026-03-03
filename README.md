# Marketing AI Agent

An automated social media marketing tool that scrapes product images from a configurable source URL, generates vertical video reels and carousel posts, and publishes them to Instagram, Facebook, and TikTok — all managed through a local web dashboard.

## Features

- **Image Scraper** — Fetches new images from any configurable website, deduplicates via MD5 hashing, and stores metadata (title, alt text, source URL).
- **Content Creator** — Generates 9:16 portrait MP4 reels (1080×1920) with optional background music, fade transitions, and text overlays. Also supports 1:1 carousel post images (1080×1080).
- **Web Dashboard** — Full browser-based UI to trigger tasks, monitor live status, and restart the server.
- **Editor** — Select images, pick background music, preview the result, choose platforms, and publish — all from the browser.
- **Gallery** — Browse downloaded images and generated videos; delete or publish any asset with one click.
- **Settings** — Configure the scrape URL, Instagram credentials (official Graph API or unofficial instagrapi), Facebook Page Access Token, and TikTok session ID. Secrets are stored server-side and never exposed in the UI.
- **Server Logs** — View rotating Flask server logs directly in the browser.
- **Auto-Music Tool** — Batch-add random background music to all silent videos in the output folder.
- **Scheduler (headless mode)** — Runs the full pipeline automatically every day at 10:00 AM.

## Project Structure

```
marketting_ai/
├── src/
│   ├── server.py          # Flask web server & all API routes
│   ├── content_creator.py # Reel & post image generation (MoviePy + Pillow)
│   ├── scraper.py         # Image scraper (requests + BeautifulSoup)
│   ├── publisher.py       # Social media publisher (stub, ready to extend)
│   ├── main.py            # Headless scheduled runner
│   └── templates/         # Jinja2 HTML templates
│       ├── dashboard.html
│       ├── editor.html
│       ├── gallery.html
│       ├── settings.html
│       ├── logs.html
│       ├── help.html
│       └── about.html
├── assets/
│   ├── images/            # Downloaded product images
│   ├── music/             # Background music files (.mp3, .wav)
│   └── output/            # Generated videos & post images
├── data/
│   ├── config.json        # Runtime configuration & credentials
│   ├── history.json       # Hashes of already-downloaded images
│   └── metadata.json      # Image metadata (title, description, source URL)
├── logs/
│   └── server.log         # Rotating Flask server log
├── requirements.txt
└── start_server.bat       # Double-click launcher (Windows)
```

## Requirements

- Python 3.8+
- Windows, Linux, or macOS
- `ffmpeg` must be on your system PATH (required by MoviePy for video encoding)
- *(Optional)* ImageMagick — needed only for `TextClip` in MoviePy

## Installation

1. **Clone the repository** and open a terminal in the project root.

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # Linux / macOS
   source .venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Option 1: Web Dashboard (Recommended)

**Windows** — double-click `start_server.bat`. It opens the browser automatically.

**Any OS** — run manually:
```bash
python src/server.py
```
Then open `http://localhost:5000` in your browser.

| Page | URL | Description |
|---|---|---|
| Dashboard | `/` | Trigger scrape, create, and publish; monitor live output |
| Editor | `/editor` | Select images, add music, preview & publish |
| Gallery | `/gallery` | Browse images and videos; delete or publish |
| Settings | `/settings` | Configure credentials and source URL |
| Server Logs | `/logs` | View real-time Flask logs |
| Setup Guide | `/help` | Step-by-step credential setup for each platform |
| About / Docs | `/about` | Renders this README live |

### Option 2: Headless / Scheduled

```bash
python src/main.py
```

Runs once immediately, then repeats every day at **10:00 AM**. No web UI required.

## Configuration

All settings are saved to `data/config.json` via the Settings page. The following keys are used:

| Key | Description |
|---|---|
| `image_source_url` | Website to scrape images from |
| `instagram_username` | Instagram username (unofficial method) |
| `instagram_password` | Instagram password (unofficial method, stored server-side) |
| `instagram_business_account_id` | Business account ID for the official Graph API |
| `facebook_page_id` | Facebook Page ID (numeric) |
| `facebook_access_token` | Long-lived Page Access Token from Meta for Developers |
| `tiktok_session_id` | TikTok `sessionid` cookie value (unofficial method) |

> **Note:** Credentials are never sent back to the browser after saving. Use the **"Clear saved …"** checkboxes in Settings to remove them.

## Adding Real Publishing

`src/publisher.py` currently **simulates** all publishing (no real API calls). To go live:

- **Instagram (Official)** — implement the [Instagram Graph API](https://developers.facebook.com/docs/instagram-api/) using `instagram_business_account_id` and `facebook_access_token`.
- **Instagram (Unofficial)** — integrate [`instagrapi`](https://github.com/adw0rd/instagrapi) and use the stored username/password.
- **Facebook** — use the [Facebook Graph API](https://developers.facebook.com/docs/graph-api/) with the page access token.
- **TikTok (Unofficial)** — integrate [`TikTokApi`](https://github.com/davidteather/TikTok-Api) with the session ID.

## Output

| Location | Contents |
|---|---|
| `assets/images/` | Raw scraped images (named by MD5 hash) |
| `assets/music/` | Uploaded background music files |
| `assets/output/` | Generated reels (`reel_XXXX.mp4`) and post images |
| `data/history.json` | Set of downloaded image hashes (prevents re-downloads) |
| `data/metadata.json` | Title, description, and source URL for each image |
| `logs/server.log` | Rotating server log (100 KB max, 1 backup) |
