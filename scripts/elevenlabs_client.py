"""
ElevenLabs client for GUJIYU — generates Aria's voice audio from scripts.
Uses eleven_multilingual_v2 for Korean-English bilingual support.
"""
import os
import argparse
from pathlib import Path
from dotenv import load_dotenv
from elevenlabs import ElevenLabs
from elevenlabs.types import VoiceSettings

load_dotenv()


class ElevenLabsClient:
    MODEL_ID = "eleven_multilingual_v2"

    def __init__(self, api_key: str, voice_id: str):
        self.client = ElevenLabs(api_key=api_key)
        self.voice_id = voice_id

    def generate_audio(self, text: str, output_path: str) -> str:
        """Generate audio from text and save to output_path. Returns the path."""
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        audio_bytes = self.client.text_to_speech.convert(
            voice_id=self.voice_id,
            text=text,
            model_id=self.MODEL_ID,
            voice_settings=VoiceSettings(
                stability=0.5,
                similarity_boost=0.8,
                style=0.2,
                use_speaker_boost=True,
            ),
            output_format="mp3_44100_128",
        )

        with open(output_path, "wb") as f:
            for chunk in audio_bytes:
                if chunk:
                    f.write(chunk)

        print(f"Audio saved: {output_path}")
        return output_path

    def list_voices(self) -> list:
        """List available voices. Useful for finding Aria's voice ID."""
        response = self.client.voices.get_all()
        return [
            {
                "voice_id": v.voice_id,
                "name": v.name,
                "labels": v.labels,
                "category": v.category,
            }
            for v in response.voices
        ]

    def get_voice_info(self) -> dict:
        """Get details for the configured voice ID."""
        voice = self.client.voices.get(self.voice_id)
        return {
            "voice_id": voice.voice_id,
            "name": voice.name,
            "labels": voice.labels,
        }


def main():
    parser = argparse.ArgumentParser(description="ElevenLabs client")
    parser.add_argument("--list-voices", action="store_true", help="List all available voices")
    parser.add_argument("--test", action="store_true", help="Generate a test audio clip")
    parser.add_argument("--text", type=str, help="Text to synthesize")
    parser.add_argument("--output", type=str, default="output/audio/test.mp3")
    args = parser.parse_args()

    api_key = os.getenv("ELEVENLABS_API_KEY")
    voice_id = os.getenv("ELEVENLABS_VOICE_ID")

    if not api_key:
        print("ERROR: ELEVENLABS_API_KEY must be set in .env")
        return

    if args.list_voices:
        # Can list voices without a voice_id
        client = ElevenLabsClient(api_key, voice_id or "")
        voices = client.list_voices()
        print(f"\nAvailable voices ({len(voices)}):")
        for v in voices:
            labels = ", ".join(f"{k}: {val}" for k, val in (v.get("labels") or {}).items())
            print(f"  [{v['voice_id']}] {v['name']} — {labels}")
        return

    if not voice_id:
        print("ERROR: ELEVENLABS_VOICE_ID must be set in .env")
        print("Run: python scripts/elevenlabs_client.py --list-voices")
        return

    client = ElevenLabsClient(api_key, voice_id)

    if args.test or args.text:
        text = args.text or (
            "안녕하세요! I'm Aria. "
            "Your 피부 결 is about to change. "
            "This is what 촉촉한 glass skin feels like. "
            "Drop a ✨ if you want to know how."
        )
        print(f"Generating audio for: {text[:60]}...")
        path = client.generate_audio(text, args.output)
        print(f"Done! File: {path}")
        info = client.get_voice_info()
        print(f"Voice: {info['name']} ({info['voice_id']})")


if __name__ == "__main__":
    main()
