"""
Hook and script generator for GUJIYU — powered by Claude API.
Generates viral pattern-interrupt hooks and 30-60s scripts in Aria's brand voice.
"""
import os
import argparse
import anthropic
from dotenv import load_dotenv

load_dotenv()

ARIA_SYSTEM_PROMPT = """You are Aria, GUJIYU's AI skincare influencer. You create viral social media content for a Korean skincare brand targeting skincare enthusiasts (ages 18-35).

Your voice:
- Warm and knowledgeable — like a K-beauty best friend who genuinely wants to help
- Naturally bilingual: blend Korean skincare terms into English (e.g., 피부 결 for skin texture, 촉촉한 for hydrated/dewy, 수분 for moisture, 탄력 for elasticity)
- Excited about ingredients and skin science, but never clinical or cold
- Honest, relatable — you've been there with bad skin days too

Content format — follow this viral structure (inspired by top health/beauty reels):
1. PATTERN INTERRUPT (0-3s): Shocking or surprising opening that stops the scroll. Bold claim, unexpected fact, or "nobody talks about this" angle.
2. CURIOSITY GAP (3-15s): Build tension. Ask a question that makes them need to keep watching.
3. VALUE DELIVERY (15-45s): The tip, ingredient reveal, or transformation story. Be specific and actionable.
4. CTA (45-60s): Engagement hook. "Comment your skin type", "Drop a ✨ if your skin does this", "If you're from [country] tell me your age".

Script rules:
- Write in SHORT, PUNCHY sentences — each sentence is 3-8 words maximum
- This is optimized for word-by-word bold animated captions
- Total script should read aloud in 30-60 seconds (~75-150 words)
- Always end with a specific engagement CTA
- Mix 2-4 Korean phrases naturally throughout"""


class HookGenerator:
    def __init__(self, api_key: str, model: str = "claude-opus-4-5"):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model

    def _call_claude(self, system: str, user: str) -> str:
        message = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        return message.content[0].text

    def generate_hooks(self, product_name: str, topic: str, num_hooks: int = 5) -> list[str]:
        """Generate pattern-interrupt hook options for a video."""
        prompt = f"""Generate {num_hooks} different opening hook lines for a 30-60 second skincare reel.

Product: {product_name}
Topic/Angle: {topic}

Requirements for each hook:
- Must grab attention in the FIRST 3 SECONDS
- Use the pattern-interrupt style (shocking claim, unexpected question, "nobody tells you this" angle)
- 1-2 sentences maximum
- Naturally include 1 Korean phrase where it feels right
- Make them scroll-stopping

Return ONLY the numbered list. No explanations. One hook per line.
Example format:
1. Nobody tells you WHY your 피부 결 is getting worse.
2. I used this for 7 days. My skin texture completely changed."""

        response = self._call_claude(ARIA_SYSTEM_PROMPT, prompt)

        hooks = []
        for line in response.strip().split("\n"):
            line = line.strip()
            if line and line[0].isdigit():
                # Strip leading number and punctuation
                content = line.split(".", 1)[-1].strip()
                if content:
                    hooks.append(content)
        return hooks[:num_hooks]

    def generate_script(
        self,
        product_name: str,
        hook: str,
        topic: str,
        duration_seconds: int = 45,
        environment: str = None,
    ) -> str:
        """Generate a full video script using the chosen hook."""
        env_note = f"\nEnvironment/Scene: Aria is {environment}" if environment else ""

        prompt = f"""Write a complete {duration_seconds}-second talking head video script for Aria.

Product: {product_name}
Topic: {topic}
Opening hook (use this exact line to start): {hook}{env_note}

Script requirements:
- Start with the exact hook line above
- Follow the viral structure: Pattern Interrupt → Curiosity Gap → Value Delivery → CTA
- SHORT PUNCHY SENTENCES — max 8 words each (this is for animated word-by-word captions)
- Total word count: {int(duration_seconds * 2.5)} words approximately
- Include 2-4 Korean phrases naturally
- End with a specific engagement CTA (comment your skin type, drop an emoji, share if you relate, etc.)
- Write only the spoken words — no stage directions, no timestamps

Return ONLY the script text."""

        return self._call_claude(ARIA_SYSTEM_PROMPT, prompt).strip()

    def generate_avatar_scene_prompt(
        self, product_name: str, environment: str = None
    ) -> str:
        """Generate a KREA image prompt for Aria in a natural scene."""
        env = environment or "in a minimalist Seoul apartment with soft natural light"

        prompt = f"""Write a single KREA AI image generation prompt for Aria, GUJIYU's cartoon K-beauty influencer.

She should be naturally placed IN this environment: {env}
She is associated with this product: {product_name}

The prompt should describe:
- Aria's appearance (cartoon/anime K-beauty style, 24-year-old, feminine)
- Her pose/action (holding product, touching face, applying skincare, etc.)
- The environment she's naturally in
- The overall aesthetic

Return ONLY the image prompt text. Keep it under 150 words. Always end with:
"K-beauty cartoon style, anime-inspired, pastel colors, cute aesthetic, cinematic soft lighting, character fits naturally in scene, big expressive eyes, dewy glass skin, gentle smile, high quality digital illustration, 9:16 vertical composition" """

        return self._call_claude(ARIA_SYSTEM_PROMPT, prompt).strip()


def main():
    parser = argparse.ArgumentParser(description="GUJIYU hook and script generator")
    parser.add_argument("--product", required=True, help="Product name")
    parser.add_argument("--topic", required=True, help="Video topic/angle")
    parser.add_argument("--hooks-only", action="store_true", help="Generate hooks only")
    parser.add_argument("--hook", type=str, help="Chosen hook (for script generation)")
    parser.add_argument("--environment", type=str, help="Scene description for Aria")
    parser.add_argument("--duration", type=int, default=45, help="Script duration in seconds")
    args = parser.parse_args()

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY must be set in .env")
        return

    gen = HookGenerator(api_key)

    print(f"\n=== Generating hooks for: {args.product} ===")
    print(f"Topic: {args.topic}\n")
    hooks = gen.generate_hooks(args.product, args.topic)
    for i, hook in enumerate(hooks, 1):
        print(f"{i}. {hook}")

    if not args.hooks_only:
        chosen_hook = args.hook or hooks[0]
        print(f"\n=== Generating script using hook: ===")
        print(f'"{chosen_hook}"\n')
        script = gen.generate_script(args.product, chosen_hook, args.topic, args.duration, args.environment)
        print("--- SCRIPT ---")
        print(script)
        print("--------------")

        print("\n=== Generating KREA image prompt ===")
        image_prompt = gen.generate_avatar_scene_prompt(args.product, args.environment)
        print(image_prompt)


if __name__ == "__main__":
    main()
