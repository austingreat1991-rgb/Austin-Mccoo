"""
KREA client for GUJIYU — generates cartoon K-beauty avatar images.
Aria is always placed naturally IN a scene (not on a plain background).
"""
import os
import time
import argparse
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Always appended to image prompts to maintain Aria's consistent visual identity
CANONICAL_STYLE_SUFFIX = (
    "K-beauty cartoon style, anime-inspired, pastel colors, cute aesthetic, "
    "cinematic soft lighting, character fits naturally in scene, "
    "big expressive eyes, dewy glass skin, gentle smile, "
    "high quality digital illustration, 9:16 vertical composition"
)


class KreaClient:
    BASE_URL = "https://api.krea.ai"

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        })

    def generate_image(
        self,
        prompt: str,
        width: int = 1080,
        height: int = 1920,
        steps: int = 28,
        guidance_scale: float = 3.5,
    ) -> str:
        """Submit an image generation job. Returns job_id."""
        full_prompt = f"{prompt}, {CANONICAL_STYLE_SUFFIX}"

        payload = {
            "prompt": full_prompt,
            "width": width,
            "height": height,
            "steps": steps,
            "guidance_scale": guidance_scale,
        }

        response = self.session.post(
            f"{self.BASE_URL}/generate/image/bfl/flux-1-dev",
            json=payload,
        )
        response.raise_for_status()
        data = response.json()
        job_id = data.get("id") or data.get("job_id")
        print(f"KREA job submitted: {job_id}")
        return job_id

    def get_job_status(self, job_id: str) -> dict:
        """Check the status of a generation job."""
        response = self.session.get(f"{self.BASE_URL}/jobs/{job_id}")
        response.raise_for_status()
        return response.json()

    def wait_for_result(self, job_id: str, timeout: int = 300, interval: int = 5) -> str:
        """Poll until job completes. Returns first image URL."""
        start = time.time()
        dots = 0
        while time.time() - start < timeout:
            status_data = self.get_job_status(job_id)
            status = status_data.get("status", "")

            if status == "completed":
                result = status_data.get("result", {})
                urls = result.get("urls", [])
                if urls:
                    print(f"\nKREA image ready: {urls[0]}")
                    return urls[0]
                raise RuntimeError(f"KREA job completed but no URLs in result: {status_data}")

            if status == "failed":
                raise RuntimeError(f"KREA job failed: {status_data}")

            print(".", end="", flush=True)
            dots += 1
            if dots % 10 == 0:
                print(f" ({int(time.time() - start)}s)")
            time.sleep(interval)

        raise TimeoutError(f"KREA job {job_id} timed out after {timeout}s")

    def generate_and_wait(self, prompt: str, **kwargs) -> str:
        """Submit a generation job and wait for the result. Returns image URL."""
        job_id = self.generate_image(prompt, **kwargs)
        return self.wait_for_result(job_id)

    def download_image(self, url: str, output_path: str) -> str:
        """Download an image from URL to a local path. Returns the path."""
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        response = requests.get(url, timeout=60)
        response.raise_for_status()
        with open(output_path, "wb") as f:
            f.write(response.content)
        print(f"Image downloaded: {output_path}")
        return output_path


def main():
    parser = argparse.ArgumentParser(description="KREA image generation client")
    parser.add_argument("--test", action="store_true", help="Generate a test image")
    parser.add_argument("--prompt", type=str, help="Image generation prompt (without style suffix)")
    parser.add_argument("--output", type=str, default="output/images/test.jpg")
    args = parser.parse_args()

    api_key = os.getenv("KREA_API_KEY")
    if not api_key:
        print("ERROR: KREA_API_KEY must be set in .env")
        return

    client = KreaClient(api_key)

    if args.test or args.prompt:
        prompt = args.prompt or (
            "Aria, cartoon K-beauty influencer, 24-year-old, holding a glass serum bottle, "
            "standing in a minimalist Seoul apartment with floor-to-ceiling windows, "
            "morning golden hour light, wearing a soft pastel lavender outfit, "
            "looking directly at camera with a warm smile"
        )
        print(f"Generating image for prompt: {prompt[:80]}...")
        print(f"(Full prompt includes canonical style suffix)")
        image_url = client.generate_and_wait(prompt)
        path = client.download_image(image_url, args.output)
        print(f"\nDone!")
        print(f"URL: {image_url}")
        print(f"Local: {path}")


if __name__ == "__main__":
    main()
