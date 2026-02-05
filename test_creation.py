from src.content_creator import ContentCreator
import os
import random

def test_reel_creation():
    images_dir = os.path.join("assets", "images")
    all_images = [os.path.join(images_dir, f) for f in os.listdir(images_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    
    if not all_images:
        print("No images found to test.")
        return

    # Select 3 random images
    selected = random.sample(all_images, min(len(all_images), 3))
    
    creator = ContentCreator()
    print("Starting reel creation...")
    output = creator.create_reel(selected, duration_per_image=2) # 2s per image, total 6s video
    
    if output and os.path.exists(output):
        print(f"SUCCESS: Video created at {output}")
    else:
        print("FAILURE: Video was not created.")

if __name__ == "__main__":
    test_reel_creation()
