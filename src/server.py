from flask import Flask, render_template, request, jsonify, send_from_directory, redirect, url_for
import json
import os
import sys
import datetime
import requests
import logging
from logging.handlers import RotatingFileHandler
from werkzeug.utils import secure_filename

# Import our modules
from scraper import ImageScraper
from content_creator import ContentCreator
from publisher import SocialPublisher

app = Flask(__name__)

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, 'data', 'config.json')
ASSETS_DIR = os.path.join(BASE_DIR, 'assets')
IMAGES_DIR = os.path.join(ASSETS_DIR, 'images')
OUTPUT_DIR = os.path.join(ASSETS_DIR, 'output')
LOG_DIR = os.path.join(BASE_DIR, 'logs')

# Setup logging
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

log_file = os.path.join(LOG_DIR, 'server.log')
handler = RotatingFileHandler(log_file, maxBytes=100000, backupCount=1)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

app.logger.addHandler(handler)
app.logger.setLevel(logging.INFO)

# Also capture werkzeug logs (Flask server logs)
logging.getLogger('werkzeug').addHandler(handler)

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            pass
    return {}

def save_config(config):
    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)

# --- Routes ---

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(ASSETS_DIR, 'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/logs')
def view_logs():
    log_content = ""
    log_file = os.path.join(LOG_DIR, 'server.log')
    if os.path.exists(log_file):
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                log_content = f.read()
        except Exception as e:
            log_content = f"Error reading log file: {str(e)}"
    return render_template('logs.html', log_content=log_content)

@app.route('/help')
def help_page():
    return render_template('help.html')

@app.route('/manual')
def manual_page():
    return render_template('manual.html')

@app.route('/about')
def about_page():
    readme_path = os.path.join(BASE_DIR, 'README.md')
    content = ""
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
    # Convert markdown to HTML if possible
    try:
        import markdown
        content_html = markdown.markdown(content, extensions=['fenced_code', 'tables'])
    except ImportError:
        # Fallback to simple pre-formatted text if markdown lib not installed
        content_html = f"<pre>{content}</pre>"
        
    return render_template('about.html', content=content_html)

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if request.method == 'POST':
        existing = load_config()

        instagram_password = (request.form.get('instagram_password') or '').strip()
        facebook_access_token = (request.form.get('facebook_access_token') or '').strip()
        tiktok_session_id = (request.form.get('tiktok_session_id') or '').strip()

        if request.form.get('clear_instagram_password') == 'on':
            instagram_password = ''
        if request.form.get('clear_facebook_access_token') == 'on':
            facebook_access_token = ''
        if request.form.get('clear_tiktok_session_id') == 'on':
            tiktok_session_id = ''

        data = {
            'image_source_url': (request.form.get('image_source_url') or '').strip(),
            'scrape_limit': (request.form.get('scrape_limit') or '5').strip(),
            'default_caption': (request.form.get('default_caption') or '').strip(),
            'instagram_username': (request.form.get('instagram_username') or '').strip(),
            'instagram_business_account_id': (request.form.get('instagram_business_account_id') or '').strip(),
            'facebook_page_id': (request.form.get('facebook_page_id') or '').strip(),
            # Preserve existing secrets if user leaves inputs blank.
            'instagram_password': instagram_password if instagram_password else existing.get('instagram_password', ''),
            'facebook_access_token': facebook_access_token if facebook_access_token else existing.get('facebook_access_token', ''),
            'tiktok_session_id': tiktok_session_id if tiktok_session_id else existing.get('tiktok_session_id', ''),
        }
        save_config(data)

        safe_config = dict(data)
        safe_config['instagram_password'] = ''
        safe_config['facebook_access_token'] = ''
        safe_config['tiktok_session_id'] = ''
        return render_template(
            'settings.html',
            config=safe_config,
            success=True,
            instagram_password_set=bool(data.get('instagram_password')),
            facebook_access_token_set=bool(data.get('facebook_access_token')),
            tiktok_session_id_set=bool(data.get('tiktok_session_id')),
        )
    
    config = load_config()
    safe_config = dict(config)
    safe_config['instagram_password'] = ''
    safe_config['facebook_access_token'] = ''
    safe_config['tiktok_session_id'] = ''
    return render_template(
        'settings.html',
        config=safe_config,
        instagram_password_set=bool(config.get('instagram_password')),
        facebook_access_token_set=bool(config.get('facebook_access_token')),
        tiktok_session_id_set=bool(config.get('tiktok_session_id')),
    )


@app.route('/api/test/facebook', methods=['POST'])
def api_test_facebook_token():
    try:
        config = load_config()
        token = (config.get('facebook_access_token') or '').strip()
        if not token:
            return jsonify({'success': False, 'message': 'No Facebook access token configured.'})

        # Basic token check via Graph API
        resp = requests.get('https://graph.facebook.com/me', params={'access_token': token}, timeout=15)
        data = resp.json()
        if resp.status_code >= 400 or 'error' in data:
            message = data.get('error', {}).get('message', 'Invalid token') if isinstance(data, dict) else 'Invalid token'
            return jsonify({'success': False, 'message': message, 'raw': data})

        # Example response: {"name": "...", "id": "..."}
        return jsonify({'success': True, 'message': 'Token is valid.', 'data': data})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/test/instagram', methods=['POST'])
def api_test_instagram_credentials():
    """Tests Instagram credentials via the Graph API using the Business Account ID + Facebook token."""
    try:
        config = load_config()
        token = (config.get('facebook_access_token') or '').strip()
        account_id = (config.get('instagram_business_account_id') or '').strip()

        if not token:
            return jsonify({'success': False, 'message': 'No Facebook access token configured. Instagram Graph API requires it.'})
        if not account_id:
            return jsonify({'success': False, 'message': 'No Instagram Business Account ID configured.'})

        # Verify via Instagram Graph API
        url = f'https://graph.facebook.com/v19.0/{account_id}'
        resp = requests.get(url, params={'fields': 'id,name,username', 'access_token': token}, timeout=15)
        data = resp.json()

        if resp.status_code >= 400 or 'error' in data:
            message = data.get('error', {}).get('message', 'Invalid credentials') if isinstance(data, dict) else 'Invalid credentials'
            return jsonify({'success': False, 'message': message})

        return jsonify({'success': True, 'message': 'Instagram credentials are valid.', 'data': data})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/test/tiktok', methods=['POST'])
def api_test_tiktok_session():
    """Checks whether a TikTok session ID is configured (cannot validate without full TikTok API integration)."""
    try:
        config = load_config()
        session_id = (config.get('tiktok_session_id') or '').strip()
        if not session_id:
            return jsonify({'success': False, 'message': 'No TikTok session ID configured.'})
        # Basic sanity: session IDs are typically long hex strings
        if len(session_id) < 20:
            return jsonify({'success': False, 'message': 'Session ID looks too short — please double-check it.'})
        return jsonify({'success': True, 'message': f'Session ID is set ({len(session_id)} chars). Full validation requires TikTok API integration.'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/gallery')
def gallery():
    images = []
    if os.path.exists(IMAGES_DIR):
        images = [f for f in os.listdir(IMAGES_DIR) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    
    videos = []
    if os.path.exists(OUTPUT_DIR):
        videos = [f for f in os.listdir(OUTPUT_DIR) if f.lower().endswith('.mp4')]
        
    return render_template('gallery.html', images=images, videos=videos)

@app.route('/editor')
def editor():
    images = []
    if os.path.exists(IMAGES_DIR):
        images = [f for f in os.listdir(IMAGES_DIR) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    return render_template('editor.html', images=images)

@app.route('/assets/<path:filename>')
def serve_assets(filename):
    return send_from_directory(ASSETS_DIR, filename)

@app.route('/api/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': 'No file part'})
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'message': 'No selected file'})
            
        file_type = request.form.get('type', 'image') # image or music
        
        filename = secure_filename(file.filename)
        
        if file_type == 'music':
            target_dir = os.path.join(ASSETS_DIR, 'music')
            # Check extension for music
            if not filename.lower().endswith(('.mp3', '.wav', '.ogg')):
                 return jsonify({'success': False, 'message': 'Invalid music file type. Use mp3, wav, or ogg.'})
        else:
            target_dir = IMAGES_DIR
            # Check extension for images
            if not filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                 return jsonify({'success': False, 'message': 'Invalid image file type. Use jpg, png, or gif.'})
            
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
            
        file.save(os.path.join(target_dir, filename))
        
        return jsonify({'success': True, 'message': 'File uploaded successfully', 'filename': filename})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

# --- API Endpoints ---

@app.route('/api/music/list', methods=['GET'])
def get_music_list():
    try:
        music_folder = os.path.join(ASSETS_DIR, 'music')
        if not os.path.exists(music_folder):
             return jsonify({'success': True, 'files': []})
             
        files = [f for f in os.listdir(music_folder) if f.lower().endswith(('.mp3', '.wav', '.ogg'))]
        return jsonify({'success': True, 'files': files})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/tools/add_random_music_to_all', methods=['POST'])
def add_random_music_to_all():
    try:
        # Import the logic dynamically or just reimplement straightforwardly since simple
        from moviepy.editor import VideoFileClip, AudioFileClip, afx
        import random
        
        music_folder = os.path.join(ASSETS_DIR, 'music')
        if not os.path.exists(music_folder):
            return jsonify({'success': False, 'message': 'No music folder found.'})

        music_files = [f for f in os.listdir(music_folder) if f.lower().endswith(('.mp3', '.wav'))]
        if not music_files:
            return jsonify({'success': False, 'message': 'No music files found.'})

        video_files = [f for f in os.listdir(OUTPUT_DIR) if f.lower().endswith('.mp4')]
        count = 0
        
        for video_file in video_files:
            if "_music" in video_file: continue
            
            full_path = os.path.join(OUTPUT_DIR, video_file)
            output_path = os.path.join(OUTPUT_DIR, video_file.replace(".mp4", "_music.mp4"))
            
            if os.path.exists(output_path): continue
            
            try:
                clip = VideoFileClip(full_path)
                # Check for audio (simple check)
                if clip.audio and clip.audio.duration and clip.audio.duration > 0:
                    clip.close()
                    continue
                    
                music_path = os.path.join(music_folder, random.choice(music_files))
                audio_clip = AudioFileClip(music_path)
                
                if audio_clip.duration < clip.duration:
                    audio_clip = afx.audio_loop(audio_clip, duration=clip.duration)
                else:
                    audio_clip = audio_clip.subclip(0, clip.duration)
                
                audio_clip = audio_clip.audio_fadeout(2)
                final_clip = clip.set_audio(audio_clip)
                
                final_clip.write_videofile(output_path, codec='libx264', audio_codec='aac', verbose=False, logger=None)
                
                clip.close()
                audio_clip.close()
                count += 1
            except Exception as e:
                print(f"Error processing {video_file}: {e}")
                
        return jsonify({'success': True, 'message': f'Processed {count} videos.'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/system/restart', methods=['POST'])
def restart_server():
    """Restarts the flask server"""
    try:
        app.logger.info("Restarting server...")
        
        # This will restart the python process
        # We need to restart it in a way that works for both direct python run and via batch/wrapper
        # os.execv replaces the current process
        
        # Response must be sent before exit, although it might be cut short.
        # But clients should handle connection drop.
        
        # We start a thread to restart so we can return response first?
        # No, execv kills everything immediately. 
        # Flask usually relies on the reloader for dev, but we want manual restart.
        
        def restart():
            import time
            import subprocess
            time.sleep(1)  # Give time for response to flush
            python = sys.executable
            # os.execl is unreliable on Windows (doesn't replace process).
            # Instead, spawn a fresh process then exit the current one.
            subprocess.Popen([python] + sys.argv)
            os._exit(0)  # Hard exit current process without triggering atexit

        import threading
        threading.Thread(target=restart, daemon=True).start()
        
        return jsonify({'success': True, 'message': 'Server is restarting. Please wait 5-10 seconds then refresh.'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/image/delete', methods=['DELETE'])
def delete_image():
    try:
        filename = request.args.get('filename')
        filetype = request.args.get('type', 'image') # 'image' or 'video'

        # Security check
        if not filename or '/' in filename or '\\' in filename:
             return jsonify({'success': False, 'message': 'Invalid filename.'})
        
        if filetype == 'video':
            filepath = os.path.join(OUTPUT_DIR, filename)
        else:
            filepath = os.path.join(IMAGES_DIR, filename)

        if os.path.exists(filepath):
            os.remove(filepath)
            return jsonify({'success': True, 'message': f'{filetype.capitalize()} deleted.'})
        else:
            return jsonify({'success': False, 'message': 'File not found.'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/editor/create', methods=['POST'])
def api_editor_create():
    try:
        data = request.json
        selected_filenames = data.get('images', [])
        output_type = data.get('type', 'video') # 'video' or 'post'
        music_file = data.get('music_file')
        
        if not selected_filenames:
            return jsonify({'success': False, 'message': 'No images selected.'})
            
        full_paths = [os.path.join(IMAGES_DIR, f) for f in selected_filenames]
        
        # Verify they exist
        full_paths = [p for p in full_paths if os.path.exists(p)]
        
        if not full_paths:
             return jsonify({'success': False, 'message': 'Selected images not found on server.'})

        creator = ContentCreator(
            output_folder=OUTPUT_DIR,
            metadata_file=os.path.join(BASE_DIR, 'data', 'metadata.json')
        )
        
        if output_type == 'post':
            # Load metadata
            metadata = {}
            metadata_path = os.path.join(BASE_DIR, 'data', 'metadata.json')
            if os.path.exists(metadata_path):
                try:
                    with open(metadata_path, 'r', encoding='utf-8') as f:
                        metadata = json.load(f)
                except:
                    pass
            
            output_paths = creator.create_post(full_paths, metadata)
            
            if output_paths:
                web_paths = [f"/assets/output/{os.path.basename(p)}" for p in output_paths]
                return jsonify({
                    'success': True, 
                    'message': 'Post created successfully.', 
                    'output_type': 'post', 
                    'files': web_paths
                })
            else:
                 return jsonify({'success': False, 'message': 'Failed to create post.'})
        else:
            video_path = creator.create_reel(full_paths, duration_per_image=3, music_file=music_file)
            
            if video_path:
                filename = os.path.basename(video_path)
                return jsonify({
                    'success': True, 
                    'message': 'Reel created!', 
                    'output_type': 'video',
                    'video_url': f'/assets/output/{filename}', 
                    'video_filename': filename
                })
            else:
                 return jsonify({'success': False, 'message': 'Failed to generate video.'})

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/editor/publish', methods=['POST'])
def api_editor_publish():
    try:
        data = request.json
        # Support both 'video_filename' (legacy) and 'media_files' (new)
        media_files = data.get('media_files')
        video_filename = data.get('video_filename')
        
        if video_filename and not media_files:
            media_files = [video_filename]
            
        if not media_files:
             return jsonify({'success': False, 'message': 'No media specified.'})
        
        config = load_config()
        caption = data.get('caption') or f"{config.get('default_caption', 'Check this out! #AleppoGift')} — {datetime.date.today()}"
        platforms = data.get('platforms', [])
        
        # Resolve paths
        full_paths = []
        for f in media_files:
            # Check if it's already a full path (if reusing logic) or base filename
            p = os.path.join(OUTPUT_DIR, os.path.basename(f))
            if os.path.exists(p):
                full_paths.append(p)
            else:
                return jsonify({'success': False, 'message': f'Media file does not exist: {f}'})
        
        # If single file (video), pass as string to match existing signature or pass list?
        # Publisher published_to_instagram now handles list or string.
        # But let's pass list if multiple, single string if one?
        # Actually publisher handle both.
        
        media_payload = full_paths if len(full_paths) > 1 else full_paths[0]
            
        publisher = SocialPublisher()
        results = []
        
        if 'instagram' in platforms:
            if publisher.publish_to_instagram(media_payload, caption):
                results.append("Instagram: Success")
            else:
                results.append("Instagram: Failed")
        
        if 'facebook' in platforms:
            if publisher.publish_to_facebook(media_payload, caption):
                results.append("Facebook: Success")
            else:
                results.append("Facebook: Failed")
        
        if 'tiktok' in platforms:
            if publisher.publish_to_tiktok(media_payload, caption):
                results.append("TikTok: Success")
            else:
                results.append("TikTok: Failed")

        if not results:
            return jsonify({'success': False, 'message': 'No platforms selected.'})

        return jsonify({'success': True, 'message': " | ".join(results)})

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/run/scrape', methods=['POST'])
def run_scrape():
    try:
        config = load_config()
        url = config.get('image_source_url', "https://aleppogift.com/")
        try:
            scrape_limit = int(config.get('scrape_limit', 5))
        except (ValueError, TypeError):
            scrape_limit = 5
        scraper = ImageScraper(
            base_url=url,
            download_folder=IMAGES_DIR,
            history_file=os.path.join(BASE_DIR, 'data', 'history.json'),
            metadata_file=os.path.join(BASE_DIR, 'data', 'metadata.json')
        )
        # Scrape up to configured limit
        new_images = scraper.scrape(limit=scrape_limit)
        return jsonify({'success': True, 'message': f'Downloaded {len(new_images)} new images.', 'data': new_images})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/run/create', methods=['POST'])
def run_create():
    try:
        # Get recent images (last 5 downloaded) or passed in request? 
        # For simplicity, let's grab random 5 from folder or just re-run scraping logic which returns images?
        # Better: Grab 5 random images from the folder to make a reel
        
        all_images = []
        if os.path.exists(IMAGES_DIR):
            all_images = [os.path.join(IMAGES_DIR, f) for f in os.listdir(IMAGES_DIR) if f.lower().endswith(('.jpg', '.png'))]
        
        if len(all_images) < 1:
            return jsonify({'success': False, 'message': 'Not enough images to create a reel.'})
        
        # Take last 5 or random 5
        import random
        selected_images = random.sample(all_images, min(len(all_images), 5))
        
        creator = ContentCreator(
            output_folder=OUTPUT_DIR,
            metadata_file=os.path.join(BASE_DIR, 'data', 'metadata.json')
        )
        video_path = creator.create_reel(selected_images, duration_per_image=3)
        
        if video_path:
            filename = os.path.basename(video_path)
            return jsonify({'success': True, 'message': 'Reel created successfully!', 'video_url': f'/assets/output/{filename}'})
        else:
            return jsonify({'success': False, 'message': 'Failed to create reel.'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/run/publish', methods=['POST'])
def run_publish():
    try:
        # Publish the latest video
        publisher = SocialPublisher()
        
        # Find latest video
        latest_video = None
        if os.path.exists(OUTPUT_DIR):
            files = [os.path.join(OUTPUT_DIR, f) for f in os.listdir(OUTPUT_DIR) if f.endswith('.mp4')]
            if files:
                latest_video = max(files, key=os.path.getmtime)
        
        if not latest_video:
             return jsonify({'success': False, 'message': 'No video found to publish.'})

        config = load_config()
        caption = f"{config.get('default_caption', 'Daily Update! #AleppoGift')} — {datetime.date.today()}"
        
        # This is Simulation
        publisher.publish_to_instagram(latest_video, caption)
        publisher.publish_to_facebook(latest_video, caption)
        
        return jsonify({'success': True, 'message': f'Published {os.path.basename(latest_video)} successfully (Simulated).'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

if __name__ == '__main__':
    print("Starting Admin Server on http://localhost:5000")
    app.run(debug=True, port=5000)
