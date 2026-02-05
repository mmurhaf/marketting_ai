import schedule
import time
import datetime
import json
import os
from scraper import ImageScraper
from content_creator import ContentCreator
from publisher import SocialPublisher

# Define base paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
ASSETS_DIR = os.path.join(BASE_DIR, 'assets')
IMAGES_DIR = os.path.join(ASSETS_DIR, 'images')
OUTPUT_DIR = os.path.join(ASSETS_DIR, 'output')

def load_config():
    config_file = os.path.join(DATA_DIR, 'config.json')
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except:
            pass
    return {}

def job():
    print(f"\n--- Starting Job: {datetime.datetime.now()} ---")
    
    config = load_config()
    source_url = config.get('image_source_url', "https://aleppogift.com/")

    # 1. Scrape Images
    scraper = ImageScraper(
        base_url=source_url,
        download_folder=IMAGES_DIR,
        history_file=os.path.join(DATA_DIR, 'history.json'),
        metadata_file=os.path.join(DATA_DIR, 'metadata.json')
    )
    # Limit to 5 images per day for the reel
    new_images = scraper.scrape(limit=5)
    
    if not new_images:
        print("No new images found today. Skipping content creation.")
        return

    # 2. Create Content
    creator = ContentCreator(
        output_folder=OUTPUT_DIR,
        metadata_file=os.path.join(DATA_DIR, 'metadata.json')
    )
    # Create a 15-second reel (3 seconds per image * 5 images)
    video_path = creator.create_reel(new_images, duration_per_image=3)
    
    if not video_path:
        print("Failed to create video content.")
        return

    # 3. Publish
    publisher = SocialPublisher()
    caption = f"Discover the beauty of Aleppo Gift! Check out our latest updates. \n\n#AleppoGift #Handmade #Art #DailyUpdate {datetime.date.today()}"
    
    # Attempt to publish
    publisher.publish_to_instagram(video_path, caption)
    publisher.publish_to_facebook(video_path, caption)
    
    print("--- Job Completed ---")

def main():
    print("Marketing AI Agent Started.")
    print("Scheduling daily job at 10:00 AM...")
    
    # Schedule the job every day at 10:00 AM
    schedule.every().day.at("10:00").do(job)
    
    # Also run once immediately for testing purposes (optional, can be commented out)
    print("Running initial check...")
    job()
    
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    main()
