"""
HeyGen client for GUJIYU — creates talking head videos from a KREA image + ElevenLabs audio.
Workflow: upload audio asset → upload talking photo → generate video → poll for completion
"""
import os
import time
import argparse
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


class HeyGenClient:
    UPLOAD_BASE = "https://upload.heygen.com"
    API_BASE = "https://api.heygen.com"

    def __init__(self, api_key: str):
        self.api_key = api_key

    def _api_headers(self) -> dict:
        return {"X-Api-Key": self.api_key, "Accept": "application/json"}

    def upload_audio_asset(self, audio_path: str) -> str:
        """Upload a local MP3 file to HeyGen. Returns audio_asset_id."""
        with open(audio_path, "rb") as f:
            audio_data = f.read()

        response = requests.post(
            f"{self.UPLOAD_BASE}/v1/asset",
            headers={
                "X-Api-Key": self.api_key,
                "Content-Type": "audio/mpeg",
            },
            data=audio_data,
            timeout=120,
        )
        response.raise_for_status()
        data = response.json()
        asset_id = data["data"]["asset_id"]
        print(f"Audio asset uploaded: {asset_id}")
        return asset_id

    def upload_talking_photo(self, image_path: str) -> str:
        """Upload a local image to HeyGen as a talking photo. Returns talking_photo_id."""
        # Determine content type from extension
        ext = Path(image_path).suffix.lower()
        content_type = "image/jpeg" if ext in (".jpg", ".jpeg") else "image/png"

        with open(image_path, "rb") as f:
            image_data = f.read()

        response = requests.post(
            f"{self.UPLOAD_BASE}/v1/talking_photo",
            headers={
                "X-Api-Key": self.api_key,
                "Content-Type": content_type,
            },
            data=image_data,
            timeout=120,
        )
        response.raise_for_status()
        data = response.json()
        photo_id = data["data"]["talking_photo_id"]
        print(f"Talking photo uploaded: {photo_id}")
        return photo_id

    def generate_video(
        self,
        talking_photo_id: str,
        audio_asset_id: str,
        background_type: str = "color",
        background_value: str = "#F8F0FF",
        background_image_url: str = None,
        talking_photo_style: str = "circle",
    ) -> str:
        """Generate a talking head video. Returns video_id.

        background_type: "color" for solid color, "image" for URL-based background
        background_value: hex color if type="color", or URL if type="image"
        background_image_url: convenience param — if set, overrides to type="image"
        """
        if background_image_url:
            background = {"type": "image", "url": background_image_url}
        elif background_type == "image":
            background = {"type": "image", "url": background_value}
        else:
            background = {"type": "color", "value": background_value}

        payload = {
            "video_inputs": [
                {
                    "character": {
                        "type": "talking_photo",
                        "talking_photo_id": talking_photo_id,
                        "talking_photo_style": talking_photo_style,
                        "scale": 1.0,
                    },
                    "voice": {
                        "type": "audio",
                        "audio_asset_id": audio_asset_id,
                    },
                    "background": background,
                }
            ],
            "dimension": {"width": 1080, "height": 1920},
            "aspect_ratio": "9:16",
            "caption": False,
            "use_avatar_iv_model": True,
        }

        response = requests.post(
            f"{self.API_BASE}/v2/video/generate",
            headers={**self._api_headers(), "Content-Type": "application/json"},
            json=payload,
            timeout=60,
        )
        response.raise_for_status()
        data = response.json()
        video_id = data["data"]["video_id"]
        print(f"Video generation started: {video_id}")
        return video_id

    def get_video_status(self, video_id: str) -> dict:
        """Check the status of a video generation job."""
        response = requests.get(
            f"{self.API_BASE}/v1/video_status.get",
            headers=self._api_headers(),
            params={"video_id": video_id},
            timeout=30,
        )
        response.raise_for_status()
        return response.json()["data"]

    def wait_for_video(self, video_id: str, timeout: int = 600, interval: int = 15) -> str:
        """Poll until video is ready. Returns video_url."""
        start = time.time()
        print(f"Waiting for video {video_id} (this takes 3-15 minutes)...")

        while time.time() - start < timeout:
            status_data = self.get_video_status(video_id)
            status = status_data.get("status", "")
            elapsed = int(time.time() - start)

            if status == "completed":
                video_url = status_data.get("video_url")
                print(f"\nVideo ready after {elapsed}s: {video_url}")
                return video_url

            if status == "failed":
                error = status_data.get("error", {})
                raise RuntimeError(f"HeyGen video failed: {error}")

            print(f"  [{elapsed}s] Status: {status} — waiting {interval}s...")
            time.sleep(interval)

        raise TimeoutError(f"Video {video_id} timed out after {timeout}s")

    def list_avatars(self) -> list:
        """List available HeyGen avatars (pre-built)."""
        response = requests.get(
            f"{self.API_BASE}/v2/avatars",
            headers=self._api_headers(),
            timeout=30,
        )
        response.raise_for_status()
        return response.json().get("data", {}).get("avatars", [])

    def list_voices(self) -> list:
        """List available HeyGen native voices."""
        response = requests.get(
            f"{self.API_BASE}/v2/voices",
            headers=self._api_headers(),
            timeout=30,
        )
        response.raise_for_status()
        return response.json().get("data", {}).get("voices", [])

    def get_remaining_quota(self) -> dict:
        """Check remaining video generation quota."""
        response = requests.get(
            f"{self.API_BASE}/v2/user/remaining_quota",
            headers=self._api_headers(),
            timeout=30,
        )
        response.raise_for_status()
        return response.json().get("data", {})


def main():
    parser = argparse.ArgumentParser(description="HeyGen client")
    parser.add_argument("--list-avatars", action="store_true")
    parser.add_argument("--list-voices", action="store_true")
    parser.add_argument("--quota", action="store_true", help="Check remaining quota")
    parser.add_argument("--test-video", action="store_true", help="Generate a test video")
    parser.add_argument("--image", type=str, help="Path to talking photo")
    parser.add_argument("--audio", type=str, help="Path to audio MP3")
    args = parser.parse_args()

    api_key = os.getenv("HEYGEN_API_KEY")
    if not api_key:
        print("ERROR: HEYGEN_API_KEY must be set in .env")
        return

    client = HeyGenClient(api_key)

    if args.quota:
        quota = client.get_remaining_quota()
        print(f"Remaining quota: {quota}")

    if args.list_avatars:
        avatars = client.list_avatars()
        print(f"\nAvailable HeyGen avatars ({len(avatars)}):")
        for a in avatars[:10]:
            print(f"  [{a.get('avatar_id')}] {a.get('avatar_name')}")

    if args.list_voices:
        voices = client.list_voices()
        print(f"\nAvailable HeyGen voices ({len(voices)}):")
        for v in voices[:10]:
            print(f"  [{v.get('voice_id')}] {v.get('name')} — {v.get('language')}")

    if args.test_video:
        if not args.image or not args.audio:
            print("ERROR: --test-video requires --image and --audio")
            return
        print("Uploading assets...")
        audio_asset_id = client.upload_audio_asset(args.audio)
        talking_photo_id = client.upload_talking_photo(args.image)
        print("Generating video...")
        video_id = client.generate_video(talking_photo_id, audio_asset_id)
        video_url = client.wait_for_video(video_id)
        print(f"\nVideo URL: {video_url}")


if __name__ == "__main__":
    main()
