import os
import shutil
import time
import json

class SocialPublisher:
    def __init__(self):
        self.config = self._load_config()

    def _load_config(self):
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'config.json')
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {}

    def publish_to_instagram(self, media_path, caption="Check out our new collection! #aleppogift"):
        """
        Stub for Instagram publishing.
        In a real scenario, you would use 'instagrapi' or the official Graph API.
        """
        username = self.config.get('instagram_username', 'Guest')
        print(f"--- ATTEMPTING TO PUBLISH TO INSTAGRAM (User: {username}) ---")
        
        if isinstance(media_path, list):
             print(f"Type: Carousel Post ({len(media_path)} images)")
             for mp in media_path:
                 print(f" - Image: {mp}")
        else:
            print(f"Type: Video/Single Image")
            print(f"Media: {media_path}")
            
        print(f"Caption: {caption}")
        
        # Check existence
        if isinstance(media_path, list):
             for mp in media_path:
                 if not os.path.exists(mp):
                    print(f"Error: File not found: {mp}")
                    return False
        else:
            if not os.path.exists(media_path):
                print("Error: Media file not found.")
                return False

        # SIMULATION
        if not username or username == 'Guest':
            print("Warning: No Instagram username configured in settings.")
        
        print(f"Authenticating as {username}...")
        time.sleep(1)
        print("Uploading...")
        time.sleep(2)
        print("Published successfully!")
        
        return True

    def publish_to_facebook(self, video_path, caption):
        """
        Stub for Facebook publishing.
        """
        token = self.config.get('facebook_access_token', '')
        masked_token = f"{token[:5]}...{token[-5:]}" if len(token) > 10 else "Not Set"
        
        print(f"--- ATTEMPTING TO PUBLISH TO FACEBOOK (Token: {masked_token}) ---")
        print(f"Video: {video_path}")
        print(f"Caption: {caption}")
        # SIMULATION
        time.sleep(1)
        print("Published successfully!")
        return True
    
    def publish_to_tiktok(self, video_path, caption):
        """
        Stub for TikTok publishing.
        """
        session_id = self.config.get('tiktok_session_id', '')
        masked_session = f"{session_id[:5]}...{session_id[-5:]}" if len(session_id) > 10 else "Not Set"
        
        print(f"--- ATTEMPTING TO PUBLISH TO TIKTOK (Session: {masked_session}) ---")
        print(f"Video: {video_path}")
        print(f"Caption: {caption}")
        
        if not session_id:
            print("Warning: No TikTok session ID configured in settings.")
        
        # SIMULATION
        print("Authenticating...")
        time.sleep(1)
        print("Uploading...")
        time.sleep(2)
        print("Published successfully!")
        return True

if __name__ == "__main__":
    pub = SocialPublisher()
    pub.publish_to_instagram("test.mp4")
