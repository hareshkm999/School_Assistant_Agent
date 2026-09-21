import requests
from PIL import Image
import io

def generate_free_image(prompt, filename="pollinations_output.png"):
    encoded_prompt = requests.utils.quote(prompt, safe="")
    base_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}"
    attempts = [
        ("flux", {"model": "flux", "width": 512, "height": 512, "seed": 42}),
        ("default", {"width": 512, "height": 512, "seed": 42}),
    ]

    print("Requesting image from Pollinations Open API...")
    for name, parameters in attempts:
        try:
            response = requests.get(base_url, params=parameters, timeout=120)
            response.raise_for_status()
            image = Image.open(io.BytesIO(response.content))
            image.save(filename)
            print(f"Success using the {name} model. Image saved locally as: {filename}")
            return
        except requests.RequestException as exc:
            print(f"Pollinations {name} request failed: {exc}")
        except (OSError, ValueError) as exc:
            print(f"Pollinations {name} returned an invalid image: {exc}")

    print(
        "Pollinations could not generate this image. "
        "The service may be temporarily unavailable or may require authentication."
    )

# Test Execution
generate_free_image("A cute cartoon leaf character wearing a tiny chef hat, pencil sketch style")
