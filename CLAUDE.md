# GUJIYU — AI Influencer Video Studio

## Brand Identity
GUJIYU is a Korean skincare brand built around holistic, glass-skin beauty. Brand voice:
- Warm, knowledgeable — like a K-beauty best friend
- Bilingual: naturally blends Korean phrases (피부 결, 촉촉한, 수분) with conversational English
- Aesthetic-forward: glass skin, minimal, pastel, dewy, ingredient-driven
- Never clinical or harsh — always soft, inviting, educational
- Content format: viral hook-based reels (pattern interrupt → curiosity gap → value → CTA)

## AI Influencer: Aria
- Age: 24, feminine-presenting
- Aesthetic: cartoon/anime K-beauty character, pastel wardrobe, dewy glass skin
- Placed IN scenes (not in front of plain backgrounds) — outdoors, bathhouses, gardens, apartments
- Tone: confident but warm, mixes Korean phrases naturally
- Audience: skincare enthusiasts, K-beauty curious, ages 18-35

## Project Structure
- `scripts/` — Python API client modules and orchestration
- `skills/talking-head-video/` — Claude Code skill for interactive video creation
- `.env` — API keys (never commit this file)
- `output/` — generated images and audio (git-ignored)

## Key Commands
- **Create a new video (interactive)**: invoke the `talking-head-video` skill
- **Run full pipeline**: `python scripts/generate_video.py --auto --product "Product Name" --topic "topic"`
- **Step-by-step**: `python scripts/generate_video.py --step hooks --product "..." --topic "..."`
- **Test connections**: `python scripts/<client>.py --test`

## Workflow
```
Product + Topic
  → Hooks (Claude API — pattern-interrupt format)
  → Script (30-60s, word-by-word caption-friendly)
  → KREA Image (Aria IN a natural scene/environment)
  → ElevenLabs Audio (warm bilingual voice)
  → HeyGen Video (talking photo, 9:16 vertical)
  → Airtable (project tracking)
```

## Airtable Tables
- **Projects** — every video project (Ad Name, Product Name, Image/Video prompts, URLs, status)
- **AI Avatars** — Aria's avatar configs and hero images
- **AI Environments** — scenes: Korean bathhouse, hanok garden, Seoul apartment, rooftop, forest path

## Content Script Format (viral hook structure)
1. Pattern interrupt (0-3s): Shocking/surprising opening
2. Curiosity gap (3-15s): Build tension before the reveal
3. Value delivery (15-45s): The tip, product reveal, or skin transformation
4. CTA (45-60s): "Comment your skin type" / "Drop ✨ if your skin does this"

## Avatar Scene Prompt Strategy
KREA generates Aria placed naturally IN the environment:
`"Aria, cartoon K-beauty influencer, [action], [environment scene], K-beauty cartoon style, anime-inspired, pastel colors, cute aesthetic, soft cinematic lighting, character fits naturally in scene, big expressive eyes, dewy glass skin, high quality digital illustration"`

## Constraints
- Always write scripts in warm, relatable language — never robotic
- KREA images: always use character-in-scene approach, not plain backgrounds
- HeyGen videos: 9:16 vertical, 1080x1920, use_avatar_iv_model enabled
- Video generation takes 3-15 minutes — always poll for completion
- Never commit `.env` — use `.env.example` as the template
