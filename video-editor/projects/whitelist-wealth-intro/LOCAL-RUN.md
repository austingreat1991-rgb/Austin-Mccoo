# Whitelist Wealth intro — how to run the rough cut

The cloud web session **can't download the WhisperX model** (its network policy blocks
`huggingface.co`). So the transcription step runs on your own machine. Two options:

---

## Option A — minimal: transcribe locally, let the cloud finish  ⭐ recommended

You only run the one blocked step (transcribe), push the transcript back, and I finish the
edit in the cloud (I still have the raw clip here, and `splice`/graphics don't need Hugging Face).

**On Windows, do this inside WSL2 (Ubuntu), not PowerShell.** (`wsl --install` once if you don't have it.)

```bash
# 1. Get the repo + branch
cd ~
git clone https://github.com/austingreat1991-rgb/Austin-Mccoo.git
cd Austin-Mccoo && git checkout claude/video-draft-6btwe4
cd video-editor

# 2. Prereqs (installs nothing itself — it prints exact commands; run what it flags)
./check-setup.sh
#   e.g.: sudo apt update && sudo apt install -y ffmpeg python3 python3-pip python3-pil
#         uv:  curl -LsSf https://astral.sh/uv/install.sh | sh

# 3. Drop the raw clip in (raw/ is git-ignored, so it isn't in the repo)
mkdir -p projects/whitelist-wealth-intro/raw
cp "/mnt/c/Users/austi/Downloads/video (1).mp4" \
   projects/whitelist-wealth-intro/raw/whitelist-wealth.mp4

# 4. Transcribe (first run builds a torch venv + downloads large-v3, ~few min, needs internet)
bash .claude/skills/rough-cut/scripts/transcribe.sh projects/whitelist-wealth-intro

# 5. Push the transcript back to me
git add projects/whitelist-wealth-intro/transcript/words.json
git commit -m "Add WhisperX transcript for whitelist-wealth-intro"
git push origin claude/video-draft-6btwe4
```

Then tell me **"transcript pushed"** and I'll pull it, build the cut sheet, splice, add long-form
graphics + a thumbnail, and export the first draft.

---

## Option B — do the whole edit locally with Claude Code

Same steps 1–3 above, then open Claude Code in the `video-editor/` folder and say:

> rough cut the whitelist-wealth-intro job — long-form

Local Claude runs transcribe → decides cuts → splices → graphics → export, all on your machine
(full network + faster encode). Nothing to push mid-way.

---

## Notes
- Source is **640×360** — the long-form export upscales to 1080p and will look soft. For a final,
  re-export the original screen recording at full resolution.
- Format is set to **long-form 16:9** (keeps the screen-shares; no vertical reframe).
- `intent.md` in this folder tells the editor what to keep vs cut.
