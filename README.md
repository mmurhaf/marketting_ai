# Marketing AI Agent

This automatic agent scrapes images from [aleppogift.com](https://aleppogift.com/), creates video reels/stories, and simulates publishing them to social media.

## Features

- **Scraper**: Fetches new images from the website, checking for duplicates.
- **Content Creator**: Generates MP4 video reels suitable for Instagram/TikTok/Facebook Stories (vertical 9:16).
- **Editor & Uploader**: Web interface to upload your own local images and music, visualize reels, and customize content.
- **Scheduler**: Runs automatically every day at 10:00 AM.
- **Publisher**: (Simulation) Logs publishing events.
- **Web Dashboard**: A user-friendly interface to manage settings, trigger tasks manually, restart the server, and view the gallery.

## Installation

1.  **Install Python**: Ensure you have Python installed.
2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
    *Note: `moviepy` may require ImageMagick installed on your system for some features.*

## Usage

### Option 1: Web Dashboard (Recommended)

Start the web server to access the dashboard, editor, and settings:

```bash
python src/server.py
```

Open your browser and navigate to `http://localhost:5000`. You can:
- Run the scraper, creator, and publisher manually.
- Upload local images and background music directly to the assets folder.
- Edit settings (API keys, passwords).
- View generated videos in the Gallery.
- View this documentation live on the 'About' page.

### Option 2: Command Line (Headless)

Run the main automation script:

```bash
python src/main.py
```

The script will:
1.  Run immediately once for testing.
2.  Stay active and run every day at 10:00 AM.

## Configuration

- **Scraping**: `src/scraper.py` looks for `<img>` tags. You can adjust filters there.
- **Video**: `src/content_creator.py` sets the duration and resolution.
- **Publishing**: `src/publisher.py` is currently a functional stub. To actually publish, you need to integrate a library like `instagrapi` or use official APIs with access tokens.

## Output

- **Images**: Downloaded to `assets/images`.
- **Videos**: Generated in `assets/output`.
- **History**: `data/history.json` tracks downloaded images to avoid reposting.
