import os
import random
from moviepy.editor import VideoFileClip, AudioFileClip, afx

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, 'assets', 'output')
MUSIC_DIR = os.path.join(BASE_DIR, 'assets', 'music')

def process_videos():
    print("--- Checking for silent videos ---")
    
    if not os.path.exists(MUSIC_DIR):
        print(f"Music folder not found at {MUSIC_DIR}")
        return

    music_files = [f for f in os.listdir(MUSIC_DIR) if f.lower().endswith(('.mp3', '.wav'))]
    if not music_files:
        print("No music files found.")
        return

    if not os.path.exists(OUTPUT_DIR):
        print("Output directory does not exist.")
        return

    video_files = [f for f in os.listdir(OUTPUT_DIR) if f.lower().endswith('.mp4')]
    count = 0

    for video_file in video_files:
        # Skip files we just created (avoid infinite loops if re-running)
        if "_music" in video_file:
            continue
            
        full_path = os.path.join(OUTPUT_DIR, video_file)
        output_path = os.path.join(OUTPUT_DIR, video_file.replace(".mp4", "_music.mp4"))
        
        # Skip if the music version already exists
        if os.path.exists(output_path):
             print(f"Skipping {video_file} (music version already exists)")
             continue
        
        try:
            clip = VideoFileClip(full_path)
            
            # Check if video already has audio
            if clip.audio is not None:
                # Sometimes clip.audio is not None but is empty, but usually this check is enough
                # Verify duration to be sure
                if clip.audio.duration and clip.audio.duration > 0:
                    print(f"Skipping {video_file} (already has audio)")
                    clip.close()
                    continue
                
            print(f"Processing {video_file}...")
            
            # Select random music
            music_path = os.path.join(MUSIC_DIR, random.choice(music_files))
            print(f" - Adding: {os.path.basename(music_path)}")
            
            audio_clip = AudioFileClip(music_path)
            
            # Loop or Trim
            if audio_clip.duration < clip.duration:
                audio_clip = afx.audio_loop(audio_clip, duration=clip.duration)
            else:
                audio_clip = audio_clip.subclip(0, clip.duration)
                
            # Fade out
            audio_clip = audio_clip.audio_fadeout(2)
            
            # Set audio
            final_clip = clip.set_audio(audio_clip)
            
            # Write new file
            final_clip.write_videofile(output_path, codec='libx264', audio_codec='aac', verbose=False, logger=None)
            print(f" - Saved: {os.path.basename(output_path)}")
            
            clip.close()
            audio_clip.close()
            count += 1
            
        except Exception as e:
            print(f"Error processing {video_file}: {e}")

    print(f"\n--- Done. Processed {count} videos. ---")

if __name__ == "__main__":
    process_videos()
