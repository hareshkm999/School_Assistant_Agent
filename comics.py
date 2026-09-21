import io
import requests
import urllib.parse
from pathlib import Path
from PIL import Image, ImageDraw

def generate_comic_strip_from_prompt(story_concept, output_filename="generated_comic_strip.png"):
    """
    Takes a concept text, processes it into 4 comic frames, queries the free open-source 
    Pollinations API, and stitches the outputs horizontally into a unified comic layout.
    """
    print("Processing story concept into a 4-panel storyboard grid...")
    storyboard = [
        {
            "panel_title": "1. The Dilemma",
            "api_prompt": "A cute cartoon leaf character standing alone looking sad and hungry, simple clean line-art style, black and white pencil sketch comic illustration",
            "caption": "Leafy is hungry!"
        },
        {
            "panel_title": "2. The Inputs",
            "api_prompt": "A cute cartoon leaf looking up happily at a smiling cartoon sun and a small floating gas cloud labeled CO2, simple clean line-art style, black and white pencil sketch comic illustration",
            "caption": "Sun & Air Help!"
        },
        {
            "panel_title": "3. The Process",
            "api_prompt": "A tiny cute cartoon chef character inside a kitchen setup mixing liquids inside a bowl, simple clean line-art style, black and white pencil sketch comic illustration",
            "caption": "Chef Inside!"
        },
        {
            "panel_title": "4. The Result",
            "api_prompt": "A joyful cute cartoon leaf character sparkling with energy, with a tiny bubble labeled O2 floating upwards, simple clean line-art style, black and white pencil sketch comic illustration",
            "caption": "Yum! Yummy Food!"
        }
    ]

    panel_width, panel_height = 400, 400
    panel_images = []
    
    print("\nFetching open-source drawings from the free Pollinations API...")
    for index, panel in enumerate(storyboard):
        print(f"Generating Frame {index + 1}: '{panel['panel_title']}'...")
        
        # Cleanly format the text prompt string for secure URL transmission
        safe_prompt = urllib.parse.quote(panel["api_prompt"], safe="")
        base_url = f"https://image.pollinations.ai/prompt/{safe_prompt}"
        
        # Supply configuration details explicitly through a safe parameters dictionary
        query_params = {
            "width": panel_width,
            "height": panel_height,
            "model": "flux",
            "seed": 2026 + index,  # Fixed seed helps maintain a unified structural layout
            "nologo": "true"
        }
        
        try:
            # Send out the connection request with a generous 45-second waiting ceiling
            response = requests.get(base_url, params=query_params, timeout=45)
            
            response.raise_for_status()
            img = Image.open(io.BytesIO(response.content)).convert("RGB")
            img = img.resize((panel_width, panel_height))
        except (requests.RequestException, OSError, ValueError) as e:
            print(f" Panel {index + 1} failed: {e}. Using placeholder.")
            img = Image.new("RGB", (panel_width, panel_height), color=(240, 240, 240))
        
        # Draw bold border lines and overlay textual framing descriptions
        draw = ImageDraw.Draw(img)
        draw.rectangle([(0, 0), (panel_width - 1, panel_height - 1)], outline=(0, 0, 0), width=6)
        
        # Text overlay strings
        draw.text((15, 15), panel["panel_title"], fill=(0, 0, 0))
        draw.text((15, panel_height - 35), panel["caption"], fill=(0, 0, 0))
        
        panel_images.append(img)

    print("\nStitching comic frames horizontally into a single layout strip...")
    total_width = panel_width * len(panel_images)
    comic_strip = Image.new("RGB", (total_width, panel_height), color=(255, 255, 255))
    
    for i, panel_img in enumerate(panel_images):
        comic_strip.paste(panel_img, (i * panel_width, 0))
        
    output_path = Path(output_filename).with_name("generated_comic_strip.png")
    comic_strip.save(output_path)
    print(f"Success! Your sketch comic strip image is complete: '{output_path}'")

if __name__ == "__main__":
    prompt_concept = (
        "A cute little plant leaf goes through the process of photosynthesis by taking in sunlight, "
        "mixing it inside its cellular kitchen with water, and turning it into delicious plant food."
    )
    generate_comic_strip_from_prompt(prompt_concept)
