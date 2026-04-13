"""
GUJIYU Simple Video Pipeline — no Airtable, no Anthropic needed.
You provide the script; this script handles KREA image, ElevenLabs audio, HeyGen video.

Usage:
  python scripts/simple_video.py \
    --script "Your script text here" \
    --image-prompt "Aria in Seoul apartment..." \
    --output-name "jiyu-nad-cream-v1"
"""
import os
import sys
import argparse
import time
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

Path("output/images").mkdir(parents=True, exist_ok=True)
Path("output/audio").mkdir(parents=True, exist_ok=True)


def generate_image(api_key: str, prompt: str, output_name: str) -> str:
    """Generate avatar image with KREA. Returns local file path."""
    STYLE = (
        "K-beauty cartoon style, anime-inspired, pastel colors, cute aesthetic, "
        "cinematic soft lighting, character fits naturally in scene, "
        "big expressive eyes, dewy glass skin, gentle smile, "
        "high quality digital illustration, 9:16 vertical composition"
    )
    full_prompt = f"{prompt}, {STYLE}"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    print(f"\n[1/3] Generating Aria's image with KREA...")
    print(f"Prompt: {full_prompt[:100]}...")

    resp = requests.post(
        "https://api.krea.ai/generate/image/bfl/flux-1-dev",
        headers=headers,
        json={"prompt": full_prompt, "width": 1080, "height": 1920, "steps": 28},
        timeout=30,
    )
    resp.raise_for_status()
    job_id = resp.json().get("id") or resp.json().get("job_id")
    print(f"KREA job started: {job_id}")

    # Poll for completion
    for i in range(60):
        time.sleep(5)
        status_resp = requests.get(
            f"https://api.krea.ai/jobs/{job_id}", headers=headers, timeout=15
        )
        status_resp.raise_for_status()
        data = status_resp.json()
        status = data.get("status", "")
        print(f"  [{i*5}s] {status}")
        if status == "completed":
            image_url = data["result"]["urls"][0]
            break
        if status == "failed":
            raise RuntimeError(f"KREA failed: {data}")
    else:
        raise TimeoutError("KREA timed out after 5 minutes")

    # Download image
    local_path = f"output/images/{output_name}.jpg"
    img_data = requests.get(image_url, timeout=60).content
    with open(local_path, "wb") as f:
        f.write(img_data)
    print(f"Image saved: {local_path}")
    return local_path


def generate_audio(api_key: str, voice_id: str, script: str, output_name: str) -> str:
    """Generate voice audio with ElevenLabs. Returns local file path."""
    from elevenlabs import ElevenLabs
    from elevenlabs.types import VoiceSettings

    print(f"\n[2/3] Generating Aria's voice with ElevenLabs...")
    client = ElevenLabs(api_key=api_key)

    audio = client.text_to_speech.convert(
        voice_id=voice_id,
        text=script,
        model_id="eleven_multilingual_v2",
        voice_settings=VoiceSettings(
            stability=0.5,
            similarity_boost=0.8,
            style=0.2,
            use_speaker_boost=True,
        ),
        output_format="mp3_44100_128",
    )

    local_path = f"output/audio/{output_name}.mp3"
    with open(local_path, "wb") as f:
        for chunk in audio:
            if chunk:
                f.write(chunk)
    print(f"Audio saved: {local_path}")
    return local_path


def generate_video(api_key: str, image_path: str, audio_path: str) -> str:
    """Upload to HeyGen and generate talking head video. Returns video URL."""
    print(f"\n[3/3] Generating video with HeyGen...")

    headers = {"X-Api-Key": api_key}

    # Upload audio
    print("  Uploading audio...")
    with open(audio_path, "rb") as f:
        audio_data = f.read()
    resp = requests.post(
        "https://upload.heygen.com/v1/asset",
        headers={**headers, "Content-Type": "audio/mpeg"},
        data=audio_data,
        timeout=120,
    )
    resp.raise_for_status()
    audio_asset_id = resp.json()["data"]["asset_id"]
    print(f"  Audio asset: {audio_asset_id}")

    # Upload talking photo
    print("  Uploading avatar image...")
    ext = Path(image_path).suffix.lower()
    img_content_type = "image/jpeg" if ext in (".jpg", ".jpeg") else "image/png"
    with open(image_path, "rb") as f:
        img_data = f.read()
    resp = requests.post(
        "https://upload.heygen.com/v1/talking_photo",
        headers={**headers, "Content-Type": img_content_type},
        data=img_data,
        timeout=120,
    )
    resp.raise_for_status()
    talking_photo_id = resp.json()["data"]["talking_photo_id"]
    print(f"  Talking photo: {talking_photo_id}")

    # Generate video
    print("  Generating video (3-15 minutes)...")
    payload = {
        "video_inputs": [{
            "character": {
                "type": "talking_photo",
                "talking_photo_id": talking_photo_id,
                "talking_photo_style": "circle",
                "scale": 1.0,
            },
            "voice": {
                "type": "audio",
                "audio_asset_id": audio_asset_id,
            },
            "background": {
                "type": "color",
                "value": "#F8F0FF",
            },
        }],
        "dimension": {"width": 1080, "height": 1920},
        "aspect_ratio": "9:16",
        "caption": False,
        "use_avatar_iv_model": True,
    }
    resp = requests.post(
        "https://api.heygen.com/v2/video/generate",
        headers={**headers, "Content-Type": "application/json", "Accept": "application/json"},
        json=payload,
        timeout=60,
    )
    resp.raise_for_status()
    video_id = resp.json()["data"]["video_id"]
    print(f"  Video ID: {video_id}")

    # Poll for completion
    for i in range(60):
        time.sleep(15)
        elapsed = (i + 1) * 15
        status_resp = requests.get(
            "https://api.heygen.com/v1/video_status.get",
            headers={**headers, "Accept": "application/json"},
            params={"video_id": video_id},
            timeout=30,
        )
        status_resp.raise_for_status()
        data = status_resp.json()["data"]
        status = data.get("status", "")
        print(f"  [{elapsed}s] {status}")
        if status == "completed":
            return data["video_url"]
        if status == "failed":
            raise RuntimeError(f"HeyGen failed: {data.get('error')}")

    raise TimeoutError("HeyGen timed out after 15 minutes")


def main():
    parser = argparse.ArgumentParser(description="GUJIYU Simple Video Pipeline")
    parser.add_argument("--script", required=True, help="The spoken script text for Aria")
    parser.add_argument("--image-prompt", required=True, help="KREA scene description for Aria")
    parser.add_argument("--output-name", default="gujiyu-video", help="Output filename prefix")
    parser.add_argument("--skip-image", type=str, help="Skip KREA — use this local image path instead")
    args = parser.parse_args()

    # Check required keys
    required = {
        "HEYGEN_API_KEY": os.getenv("HEYGEN_API_KEY"),
        "ELEVENLABS_API_KEY": os.getenv("ELEVENLABS_API_KEY"),
        "ELEVENLABS_VOICE_ID": os.getenv("ELEVENLABS_VOICE_ID"),
        "KREA_API_KEY": os.getenv("KREA_API_KEY"),
    }
    missing = [k for k, v in required.items() if not v]
    if missing:
        print(f"ERROR: Missing keys in .env: {', '.join(missing)}")
        sys.exit(1)

    print("=" * 50)
    print("GUJIYU Video Pipeline")
    print("=" * 50)
    print(f"Script: {args.script[:80]}...")

    # Step 1: Image
    if args.skip_image:
        image_path = args.skip_image
        print(f"\n[1/3] Using existing image: {image_path}")
    else:
        image_path = generate_image(
            os.getenv("KREA_API_KEY"), args.image_prompt, args.output_name
        )

    # Step 2: Audio
    audio_path = generate_audio(
        os.getenv("ELEVENLABS_API_KEY"),
        os.getenv("ELEVENLABS_VOICE_ID"),
        args.script,
        args.output_name,
    )

    # Step 3: Video
    video_url = generate_video(os.getenv("HEYGEN_API_KEY"), image_path, audio_path)

    print("\n" + "=" * 50)
    print("VIDEO COMPLETE!")
    print("=" * 50)
    print(f"Video URL: {video_url}")


if __name__ == "__main__":
    main()
