import PIL.Image

# Monkey patch for Pillow 10+ compatibility with MoviePy
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.LANCZOS

from moviepy.editor import ImageClip, concatenate_videoclips, CompositeVideoClip, ColorClip, TextClip, AudioFileClip, afx
import os
import random
import textwrap
from PIL import Image, ImageDraw, ImageFont

class ContentCreator:
    def __init__(self, output_folder='assets/output', metadata_file='data/metadata.json'):
        self.output_folder = output_folder
        self.metadata_file = metadata_file
        # Try to find a font
        self.font = "arial.ttf" # Default for Windows usually
        if os.name != 'nt':
           self.font = "DejaVuSans.ttf" # Linux/Mac maybe

        os.makedirs(output_folder, exist_ok=True)

    def create_post(self, image_paths, metadata=None):
        if not image_paths:
            print("No images provided for post creation.")
            return None
            
        processed_images = []
        
        for img_path in image_paths:
            try:
                # Load image
                img = Image.open(img_path)
                
                # Get metadata
                filename = os.path.basename(img_path)
                data = {}
                if metadata and filename in metadata:
                    data = metadata[filename]
                
                title = data.get('title', '')
                description = data.get('description', '')

                # 1. Resize/Crop to Square (1080x1080) or Portrait (1080x1350) for Instagram
                # Let's do 1080x1080 square for simplicity
                target_size = (1080, 1080)
                img = self._resize_fill(img, target_size)

                # 2. Overlay Text
                if title:
                    draw = ImageDraw.Draw(img)
                    # Try to load font
                    try:
                        font_title = ImageFont.truetype(self.font, 60)
                        font_desc = ImageFont.truetype(self.font, 40)
                    except:
                        font_title = ImageFont.load_default()
                        font_desc = ImageFont.load_default()
                    
                    # Add a semi-transparent background for text at the bottom
                    # (Simple approach: darker rectangle at bottom)
                    overlay = Image.new('RGBA', img.size, (0,0,0,0))
                    draw_overlay = ImageDraw.Draw(overlay)
                    
                    text_bg_height = 300
                    draw_overlay.rectangle(
                        [(0, target_size[1] - text_bg_height), (target_size[0], target_size[1])],
                        fill=(0, 0, 0, 150)
                    )
                    img = Image.alpha_composite(img.convert('RGBA'), overlay)
                    
                    # Draw text with proper word-wrapping
                    draw = ImageDraw.Draw(img)
                    text_color = (255, 255, 255)
                    max_text_width = target_size[0] - 100  # 50px margin on each side

                    # Draw wrapped title (font size 60)
                    title_lines = self._wrap_text(title, font_title, max_text_width)
                    y_title = target_size[1] - 260
                    for line in title_lines[:2]:  # max 2 lines for title
                        draw.text((50, y_title), line, font=font_title, fill=text_color)
                        y_title += 70

                    # Draw wrapped description (font size 40)
                    desc_lines = self._wrap_text(description, font_desc, max_text_width)
                    y_desc = target_size[1] - 115
                    for line in desc_lines[:2]:  # max 2 lines for description
                        draw.text((50, y_desc), line, font=font_desc, fill=text_color)
                        y_desc += 50
                
                # Save processed image to output
                output_filename = f"post_{random.randint(1000, 9999)}_{filename}"
                output_path = os.path.join(self.output_folder, output_filename)
                
                img.convert('RGB').save(output_path)
                processed_images.append(output_path)
                
            except Exception as e:
                print(f"Error processing image for post {img_path}: {e}")

        return processed_images

    def _wrap_text(self, text, font, max_width):
        """Wrap text to fit within max_width pixels, returning a list of lines."""
        words = text.split()
        lines = []
        current_line = []

        for word in words:
            test_line = ' '.join(current_line + [word])
            try:
                # Pillow >= 9.2: use getlength; fall back to getsize for older versions
                bbox = font.getbbox(test_line)
                line_width = bbox[2] - bbox[0]
            except AttributeError:
                line_width, _ = font.getsize(test_line)

            if line_width <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]

        if current_line:
            lines.append(' '.join(current_line))

        return lines if lines else [text]

    def _resize_fill(self, img, size):
        img_ratio = img.width / img.height
        ratio = size[0] / size[1]
        
        if ratio > img_ratio:
            # Fit to width
            scale = size[0] / img.width
            new_size = (size[0], int(img.height * scale))
        else:
            # Fit to height
            scale = size[1] / img.height
            new_size = (int(img.width * scale), size[1])
            
        img = img.resize(new_size, Image.LANCZOS)
        
        # Center Crop
        left = (img.width - size[0]) / 2
        top = (img.height - size[1]) / 2
        right = (img.width + size[0]) / 2
        bottom = (img.height + size[1]) / 2
        
        return img.crop((left, top, right, bottom))

    def create_reel(self, image_paths, duration_per_image=3, music_file=None):
        if not image_paths:
            print("No images provided for content creation.")
            return None

        print("Creating reel from images...")
        clips = []
        
        # Social Media Portrait Format (9:16)
        w, h = 1080, 1920
        
        for img_path in image_paths:
            try:
                # Create main image clip
                # Resize to width 1080, maintain aspect ratio
                clip = ImageClip(img_path).set_duration(duration_per_image)
                
                # Resize logic to fit 1080x1920 nicely
                # Calculate scale to fit width
                img_w, img_h = clip.size
                
                # If image is landscape or square, we might want to center it on a background
                # If it's portrait, we might want to fill
                
                # Simple logic: resize to width 1080
                new_h = int(img_h * w / img_w)
                clip = clip.resize(width=w)
                
                # If new height is less than 1920, center it
                if new_h < h:
                    clip = clip.set_position(("center", "center"))
                    # Create a blurred background or a solid color
                    # For simplicity, let's use a black background
                    bg = ColorClip(size=(w, h), color=(0,0,0), duration=duration_per_image)
                    final_clip = CompositeVideoClip([bg, clip])
                else:
                    # Crop center if it's too tall (rare for resizing by width, but possible)
                    # Or just resize to height 1920 if needed
                    clip = clip.resize(height=h)
                    clip = clip.crop(x1=clip.w/2 - w/2, width=w, height=h)
                    final_clip = clip

                # Add a fade in/out effect
                final_clip = final_clip.crossfadein(0.5)
                clips.append(final_clip)
                
            except Exception as e:
                print(f"Error processing image {img_path}: {e}")

        if not clips:
            return None

        final_video = concatenate_videoclips(clips, method="compose")
        
        # --- Add Background Music ---
        # Try to find 'assets/music' parallel to 'assets/output'
        music_folder = os.path.join(os.path.dirname(self.output_folder), 'music')
        if not os.path.exists(music_folder):
             music_folder = os.path.join('assets', 'music')

        selected_music_path = None
        
        if music_file and os.path.exists(os.path.join(music_folder, music_file)):
             selected_music_path = os.path.join(music_folder, music_file)
        elif music_file and os.path.exists(music_file):
             selected_music_path = music_file
        else:
            # Random selection if no specific file provided
            music_files = []
            if os.path.exists(music_folder):
                music_files = [f for f in os.listdir(music_folder) if f.lower().endswith(('.mp3', '.wav'))]
            
            if music_files:
                selected_music_path = os.path.join(music_folder, random.choice(music_files))

        if selected_music_path:
            try:
                print(f"Adding background music: {os.path.basename(selected_music_path)}")
                
                audio_clip = AudioFileClip(selected_music_path)
                
                # Loop if audio is shorter than video, clip if longer
                if audio_clip.duration < final_video.duration:
                    audio_clip = afx.audio_loop(audio_clip, duration=final_video.duration)
                else:
                    audio_clip = audio_clip.subclip(0, final_video.duration)
                
                # Fade out audio at the end (2 seconds)
                audio_clip = audio_clip.audio_fadeout(2)
                
                final_video = final_video.set_audio(audio_clip)
            except Exception as e:
                print(f"Failed to add background music: {e}")
        # -----------------------------
        
        output_filename = f"reel_{random.randint(1000, 9999)}.mp4"
        output_path = os.path.join(self.output_folder, output_filename)
        
        # Write video file
        # codec 'libx264' is standard for mp4
        # fps=24 is standard for cinematic feeling, 30 is also good
        try:
            # audio=True is default if audio is set, but explicit is fine.
            # If no music found, audio remains None and it will write silence/no track.
            final_video.write_videofile(output_path, fps=24, codec='libx264', audio_codec='aac')
            print(f"Reel created successfully: {output_path}")
            return output_path
        except Exception as e:
            print(f"Error writing video file: {e}")
            return None

if __name__ == "__main__":
    # Test stub
    pass
