"""
GUJIYU AI Video Pipeline — main orchestration script.

Modes:
  --step hooks     Generate and display hooks for review
  --step script    Generate script from chosen hook
  --step image     Generate KREA avatar image
  --step audio     Generate ElevenLabs voice audio
  --step video     Generate HeyGen talking head video
  --auto           Run full pipeline end-to-end (no pauses)

State is persisted in Airtable, so you can resume from any step with --record-id.
"""
import os
import sys
import json
import argparse
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Ensure output directories exist
Path("output/images").mkdir(parents=True, exist_ok=True)
Path("output/audio").mkdir(parents=True, exist_ok=True)

# Default environments Aria can appear in
DEFAULT_ENVIRONMENTS = [
    "standing in a minimalist Seoul apartment with floor-to-ceiling windows and morning golden hour light",
    "sitting at a sleek marble vanity in a Korean jjimjilbang bathhouse, soft steam in background",
    "in a dewy hanok garden at sunrise, surrounded by cherry blossoms and soft mist",
    "on a rooftop terrace at golden hour with the Seoul skyline behind her",
    "inside a bright K-beauty store with pastel shelving and product displays around her",
    "walking through a soft dewy forest path with filtered morning light",
]


def load_clients():
    """Load and return all API clients."""
    from scripts.airtable_client import AirtableClient
    from scripts.hook_generator import HookGenerator
    from scripts.elevenlabs_client import ElevenLabsClient
    from scripts.krea_client import KreaClient
    from scripts.heygen_client import HeyGenClient

    airtable = AirtableClient(
        os.environ["AIRTABLE_API_KEY"],
        os.environ["AIRTABLE_BASE_ID"],
    )
    hook_gen = HookGenerator(os.environ["ANTHROPIC_API_KEY"])
    elevenlabs = ElevenLabsClient(
        os.environ["ELEVENLABS_API_KEY"],
        os.environ["ELEVENLABS_VOICE_ID"],
    )
    krea = KreaClient(os.environ["KREA_API_KEY"])
    heygen = HeyGenClient(os.environ["HEYGEN_API_KEY"])

    return airtable, hook_gen, elevenlabs, krea, heygen


def step_hooks(args, hook_gen):
    """Generate hooks and print them for review."""
    print(f"\n=== STEP 1: Hook Generation ===")
    print(f"Product: {args.product}")
    print(f"Topic: {args.topic}\n")

    hooks = hook_gen.generate_hooks(args.product, args.topic)
    result = {"hooks": hooks}

    for i, hook in enumerate(hooks, 1):
        print(f"{i}. {hook}")

    if args.json:
        print(f"\nJSON: {json.dumps(result)}")
    return result


def step_script(args, hook_gen):
    """Generate a script from the chosen hook."""
    if not args.hook:
        print("ERROR: --hook is required for --step script")
        sys.exit(1)

    print(f"\n=== STEP 2: Script Generation ===")
    print(f'Hook: "{args.hook}"')
    print(f"Environment: {args.environment or DEFAULT_ENVIRONMENTS[0]}\n")

    script = hook_gen.generate_script(
        args.product, args.hook, args.topic,
        duration_seconds=args.duration,
        environment=args.environment,
    )

    print("--- SCRIPT ---")
    print(script)
    print("--------------")
    print(f"\nWord count: ~{len(script.split())} words")

    image_prompt = hook_gen.generate_avatar_scene_prompt(args.product, args.environment)
    print(f"\n--- KREA IMAGE PROMPT ---")
    print(image_prompt)
    print("-------------------------")

    result = {"script": script, "image_prompt": image_prompt}
    if args.json:
        print(f"\nJSON: {json.dumps(result)}")
    return result


def step_image(args, airtable, krea):
    """Generate KREA avatar image and update Airtable."""
    if not args.record_id or not args.image_prompt:
        print("ERROR: --record-id and --image-prompt are required for --step image")
        sys.exit(1)

    print(f"\n=== STEP 3: KREA Image Generation ===")
    print(f"Prompt: {args.image_prompt[:100]}...\n")

    airtable.update_project_status(
        args.record_id,
        image_status="generating",
        image_prompt=args.image_prompt,
    )

    image_url = krea.generate_and_wait(args.image_prompt)
    local_path = f"output/images/{args.record_id}.jpg"
    krea.download_image(image_url, local_path)

    airtable.update_project_status(
        args.record_id,
        image_url=image_url,
        image_status="completed",
    )

    result = {"image_url": image_url, "image_path": local_path}
    if args.json:
        print(f"\nJSON: {json.dumps(result)}")
    return result


def step_audio(args, airtable, elevenlabs):
    """Generate ElevenLabs audio and save locally."""
    if not args.record_id or not args.script:
        print("ERROR: --record-id and --script are required for --step audio")
        sys.exit(1)

    print(f"\n=== STEP 4: Voice Generation ===")
    print(f"Script preview: {args.script[:100]}...\n")

    audio_path = f"output/audio/{args.record_id}.mp3"
    elevenlabs.generate_audio(args.script, audio_path)

    result = {"audio_path": audio_path}
    if args.json:
        print(f"\nJSON: {json.dumps(result)}")
    return result


def step_video(args, airtable, heygen):
    """Generate HeyGen video from image + audio."""
    if not args.record_id:
        print("ERROR: --record-id is required for --step video")
        sys.exit(1)

    image_path = args.image_path or f"output/images/{args.record_id}.jpg"
    audio_path = args.audio_path or f"output/audio/{args.record_id}.mp3"

    if not Path(image_path).exists():
        print(f"ERROR: Image not found: {image_path}")
        sys.exit(1)
    if not Path(audio_path).exists():
        print(f"ERROR: Audio not found: {audio_path}")
        sys.exit(1)

    print(f"\n=== STEP 5: HeyGen Video Generation ===")
    print(f"Image: {image_path}")
    print(f"Audio: {audio_path}\n")

    airtable.update_project_status(args.record_id, video_status="uploading_assets")

    print("Uploading assets to HeyGen...")
    audio_asset_id = heygen.upload_audio_asset(audio_path)
    talking_photo_id = heygen.upload_talking_photo(image_path)

    airtable.update_project_status(args.record_id, video_status="generating")

    video_id = heygen.generate_video(
        talking_photo_id=talking_photo_id,
        audio_asset_id=audio_asset_id,
        background_image_url=args.background_url,
    )

    video_url = heygen.wait_for_video(video_id)

    airtable.update_project_status(
        args.record_id,
        video_url=video_url,
        video_status="completed",
    )

    print(f"\n=== VIDEO COMPLETE ===")
    print(f"Video URL: {video_url}")
    print(f"Airtable record: {args.record_id}")

    result = {"video_url": video_url, "video_id": video_id}
    if args.json:
        print(f"\nJSON: {json.dumps(result)}")
    return result


def run_auto_pipeline(args, airtable, hook_gen, elevenlabs, krea, heygen):
    """Run the full pipeline end-to-end without pauses."""
    from scripts.airtable_client import PROJECT_FIELDS

    ad_name = args.ad_name or f"{args.product} — {datetime.now():%Y-%m-%d}"
    environment = args.environment or DEFAULT_ENVIRONMENTS[0]

    print(f"\n{'='*50}")
    print(f"GUJIYU Video Pipeline — Auto Mode")
    print(f"Product: {args.product}")
    print(f"Topic: {args.topic}")
    print(f"Ad Name: {ad_name}")
    print(f"{'='*50}\n")

    # Create Airtable project record
    print("Creating Airtable project record...")
    record = airtable.create_project({
        PROJECT_FIELDS["ad_name"]: ad_name,
        PROJECT_FIELDS["product_name"]: args.product,
        PROJECT_FIELDS["image_generator"]: "KREA",
        PROJECT_FIELDS["video_generator"]: "HeyGen",
        PROJECT_FIELDS["image_status"]: "pending",
        PROJECT_FIELDS["video_status"]: "pending",
    })
    record_id = record["id"]
    print(f"Record created: {record_id}")

    # Step 1: Hooks
    hooks = hook_gen.generate_hooks(args.product, args.topic)
    print(f"\nGenerated {len(hooks)} hooks. Using first hook:")
    chosen_hook = hooks[0]
    print(f'"{chosen_hook}"')

    # Step 2: Script
    script = hook_gen.generate_script(
        args.product, chosen_hook, args.topic,
        duration_seconds=args.duration,
        environment=environment,
    )
    image_prompt = hook_gen.generate_avatar_scene_prompt(args.product, environment)

    # Step 3: KREA image
    airtable.update_project_status(record_id, image_status="generating", image_prompt=image_prompt)
    image_url = krea.generate_and_wait(image_prompt)
    image_path = f"output/images/{record_id}.jpg"
    krea.download_image(image_url, image_path)
    airtable.update_project_status(record_id, image_url=image_url, image_status="completed")

    # Step 4: Audio
    audio_path = f"output/audio/{record_id}.mp3"
    elevenlabs.generate_audio(script, audio_path)

    # Step 5: HeyGen video
    airtable.update_project_status(record_id, video_status="uploading_assets", video_prompt=script)
    audio_asset_id = heygen.upload_audio_asset(audio_path)
    talking_photo_id = heygen.upload_talking_photo(image_path)
    airtable.update_project_status(record_id, video_status="generating")
    video_id = heygen.generate_video(talking_photo_id, audio_asset_id)
    video_url = heygen.wait_for_video(video_id)
    airtable.update_project_status(record_id, video_url=video_url, video_status="completed")

    print(f"\n{'='*50}")
    print(f"PIPELINE COMPLETE")
    print(f"{'='*50}")
    print(f"Hook used:     {chosen_hook}")
    print(f"Image URL:     {image_url}")
    print(f"Video URL:     {video_url}")
    print(f"Airtable ID:   {record_id}")

    return {
        "record_id": record_id,
        "hook": chosen_hook,
        "script": script,
        "image_url": image_url,
        "audio_path": audio_path,
        "video_url": video_url,
    }


def main():
    parser = argparse.ArgumentParser(
        description="GUJIYU AI Video Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Full auto pipeline:
  python scripts/generate_video.py --auto --product "Glass Skin Serum" --topic "hydration morning routine"

  # Step-by-step (for skill use):
  python scripts/generate_video.py --step hooks --product "Glass Skin Serum" --topic "hydration"
  python scripts/generate_video.py --step script --product "Glass Skin Serum" --topic "hydration" --hook "Nobody tells you..."
  python scripts/generate_video.py --step image --record-id rec123 --image-prompt "Aria in Seoul apartment..."
  python scripts/generate_video.py --step audio --record-id rec123 --script "Your skin is lying to you..."
  python scripts/generate_video.py --step video --record-id rec123
        """
    )

    # Mode
    parser.add_argument("--auto", action="store_true", help="Run full pipeline automatically")
    parser.add_argument("--step", choices=["hooks", "script", "image", "audio", "video"],
                        help="Run a single pipeline step")

    # Core inputs
    parser.add_argument("--product", type=str, help="Product name")
    parser.add_argument("--topic", type=str, help="Video topic/angle")
    parser.add_argument("--ad-name", type=str, help="Project name for Airtable")
    parser.add_argument("--environment", type=str, help="Scene description for Aria")
    parser.add_argument("--duration", type=int, default=45, help="Script duration in seconds (default: 45)")

    # Step-specific inputs
    parser.add_argument("--record-id", type=str, help="Airtable record ID (for resuming steps)")
    parser.add_argument("--hook", type=str, help="Chosen hook for script generation")
    parser.add_argument("--script", type=str, help="Approved script for audio generation")
    parser.add_argument("--image-prompt", type=str, help="KREA image prompt")
    parser.add_argument("--image-path", type=str, help="Local image path (if pre-existing)")
    parser.add_argument("--audio-path", type=str, help="Local audio path (if pre-existing)")
    parser.add_argument("--background-url", type=str, help="Background image URL for HeyGen")

    # Output
    parser.add_argument("--json", action="store_true", help="Output results as JSON")

    args = parser.parse_args()

    if not args.auto and not args.step:
        parser.print_help()
        sys.exit(1)

    # Validate required env vars
    required_env = ["ANTHROPIC_API_KEY", "HEYGEN_API_KEY", "ELEVENLABS_API_KEY",
                    "ELEVENLABS_VOICE_ID", "KREA_API_KEY", "AIRTABLE_API_KEY", "AIRTABLE_BASE_ID"]
    missing = [k for k in required_env if not os.getenv(k)]
    if missing:
        print(f"ERROR: Missing required environment variables: {', '.join(missing)}")
        print("Copy .env.example to .env and fill in your API keys.")
        sys.exit(1)

    # Add scripts dir to path for imports
    sys.path.insert(0, str(Path(__file__).parent.parent))

    airtable, hook_gen, elevenlabs, krea, heygen = load_clients()

    if args.auto:
        if not args.product or not args.topic:
            print("ERROR: --auto requires --product and --topic")
            sys.exit(1)
        run_auto_pipeline(args, airtable, hook_gen, elevenlabs, krea, heygen)

    elif args.step == "hooks":
        if not args.product or not args.topic:
            print("ERROR: --step hooks requires --product and --topic")
            sys.exit(1)
        step_hooks(args, hook_gen)

    elif args.step == "script":
        if not args.product or not args.topic or not args.hook:
            print("ERROR: --step script requires --product, --topic, and --hook")
            sys.exit(1)
        step_script(args, hook_gen)

    elif args.step == "image":
        step_image(args, airtable, krea)

    elif args.step == "audio":
        step_audio(args, airtable, elevenlabs)

    elif args.step == "video":
        step_video(args, airtable, heygen)


if __name__ == "__main__":
    main()
