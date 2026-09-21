import requests
from PIL import Image
import io

def generate_free_image(prompt, filename="pollinations_output.png"):
    # Format the text prompt neatly to safely embed it into a URL string
    formatted_prompt = requests.utils.quote(prompt)
    
    # We pass 'flux' as the model query parameter to access high-fidelity open weights
    url = (
        f"https://image.pollinations.ai/prompt/{formatted_prompt}"
        "?model=flux&width=512&height=512&seed=42"
    )

    print("📡 Requesting image from Pollinations Open API...")
    try:
        response = requests.get(url, timeout=120)
        response.raise_for_status()
    except requests.RequestException as exc:
        print(f"❌ Image request failed: {exc}")
        return

    try:
        image = Image.open(io.BytesIO(response.content))
        image.save(filename)
        print(f"🎉 Success! Image saved locally as: {filename}")
    except (OSError, ValueError) as exc:
        print(f"❌ The response was not a valid image: {exc}")

# Test Execution
generate_free_image("A cute cartoon leaf character wearing a tiny chef hat, pencil sketch style")
