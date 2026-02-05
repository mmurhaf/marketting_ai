import requests
from bs4 import BeautifulSoup
import os
import hashlib
import json
from urllib.parse import urljoin, urlparse

class ImageScraper:
    def __init__(self, base_url, download_folder='assets/images', history_file='data/history.json', metadata_file='data/metadata.json'):
        self.base_url = base_url
        self.download_folder = download_folder
        self.history_file = history_file
        self.metadata_file = metadata_file
        self.downloaded_hashes = set()
        self.metadata = {}
        
        # Ensure directories exist
        os.makedirs(download_folder, exist_ok=True)
        os.makedirs(os.path.dirname(history_file), exist_ok=True)
        
        self.load_history()
        self.load_metadata()

    def load_history(self):
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r') as f:
                    self.downloaded_hashes = set(json.load(f))
            except json.JSONDecodeError:
                self.downloaded_hashes = set()

    def load_metadata(self):
        if os.path.exists(self.metadata_file):
            try:
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    self.metadata = json.load(f)
            except json.JSONDecodeError:
                self.metadata = {}

    def save_history(self):
        with open(self.history_file, 'w') as f:
            json.dump(list(self.downloaded_hashes), f)
            
    def save_metadata(self):
        with open(self.metadata_file, 'w', encoding='utf-8') as f:
            json.dump(self.metadata, f, indent=4)

    def get_image_hash(self, image_content):
        return hashlib.md5(image_content).hexdigest()

    def is_valid_url(self, url):
        parsed = urlparse(url)
        return bool(parsed.netloc) and bool(parsed.scheme)

    def scrape(self, limit=5):
        print(f"Scraping {self.base_url}...")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        try:
            response = requests.get(self.base_url, headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find all image tags
            img_tags = soup.find_all('img')
            
            new_images = []
            count = 0
            
            for img in img_tags:
                if count >= limit:
                    break
                    
                img_url = img.get('src')
                if not img_url:
                    continue
                
                # Handle relative URLs
                if not img_url.startswith('http'):
                    img_url = urljoin(self.base_url, img_url)
                
                # Skip very small icons/logos often found in headers/footers
                # This is a heuristic; downloading headers to check size is better but slower.
                # Here we just filter by extension or keyword if possible
                if any(x in img_url.lower() for x in ['logo', 'icon', 'pixel', 'blank']):
                    continue

                try:
                    img_data = requests.get(img_url, headers=headers).content
                    img_hash = self.get_image_hash(img_data)
                    
                    if img_hash in self.downloaded_hashes:
                        print(f"Skipping duplicate: {img_url}")
                        continue
                        
                    # Check size (ignore excessively small images)
                    if len(img_data) < 10000: # less than 10KB
                        continue
                        
                    filename = os.path.join(self.download_folder, f"{img_hash}.jpg")
                    with open(filename, 'wb') as f:
                        f.write(img_data)
                    
                    # Extract Metadata
                    title = img.get('alt') or img.get('title') or "No Title"
                    # Try to find a caption or nearby text (simple heuristic)
                    description = ""
                    parent = img.parent
                    if parent and parent.name == 'figure':
                        caption = parent.find('figcaption')
                        if caption:
                            description = caption.get_text(strip=True)
                    
                    if not description:
                        description = title # Fallback
                        
                    self.metadata[f"{img_hash}.jpg"] = {
                        "title": title,
                        "description": description,
                        "source_url": img_url,
                        "timestamp": str(os.path.getctime(filename))
                    }
                    
                    self.downloaded_hashes.add(img_hash)
                    new_images.append(filename)
                    print(f"Downloaded: {filename} with title: {title}")
                    count += 1
                    
                except Exception as e:
                    print(f"Failed to download {img_url}: {e}")
            
            self.save_history()
            self.save_metadata()
            return new_images

        except Exception as e:
            print(f"Error scraping website: {e}")
            return []

if __name__ == "__main__":
    scraper = ImageScraper("https://aleppogift.com/")
    scraper.scrape()
