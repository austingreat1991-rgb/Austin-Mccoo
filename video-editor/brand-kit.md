# 🎨 Brand Kit — make this editor yours

This is the **one file you personalize.** Everything the editor produces — caption voice, on-thumbnail
copy, the signature graphics look — reads from what you put here. Fill in the blanks, then tell Claude
**"apply my brand kit"** and it pushes these values into the presets for you (the exact map is in
**Part B** at the bottom, if you'd rather do it by hand or want to know precisely what changes).

Until this file is filled in, the editor stays in onboarding mode and won't start a job.

---

# Part A — fill this in

## 1. Identity

- **Name / creator:** `Whitelist Wealth — Austin McCoo`
- **Niche (one line):** `Getting paid to make short brand videos (UGC / whitelisting) + building a paid Skool community`
- **Handles:**
  - Instagram: `@whitelistwealth`  _(placeholder — confirm the real handle)_
  - YouTube: `@whitelistwealth`  ·  channel ID: `TBD — paste the UC… channel ID here`
  - TikTok: `@whitelistwealth`  _(placeholder — confirm the real handle)_

## 2. Voice & tone (drives caption + hook copy)

How your captions should *sound* — punchy? formal? lowercase-casual? slang-heavy? One or two sentences.
Burn-in captions and on-thumbnail copy are written to match this.

```
Confident, motivational, and direct — a hustler-mentor talking straight to camera about making
money online. Casual and energetic (not corporate), speaks to people who want financial freedom
and a real side income. Leads with proof and numbers (MRR, members, earnings math) and concrete
steps. Hook-driven: bold claim → proof → how-it-works → call to join. Clean and punchy; never
hypey-scammy or fake-guru.
```

## 3. Brand colors (the signature look)

Six colors as hex. These drive the short-form explainer graphics (`presets/signature-style.md`) and the
long-form panels (`presets/liquid-glass-style.md`). The roles map 1:1 to the preset's color tokens — pick
a color for each role. (The defaults shown are the starter palette; replace with yours.)

| Role | Token in presets | Default | Yours |
|------|------------------|---------|-------|
| **Background base** (the canvas) | `--sky` | `#ddf4ff` | `#f7f8fa` |
| **Grid lines** (thin texture) | `--grid` | `#74dff6` | `#e3e7ee` |
| **Hero accent** (the ONE loud color) | `--royal` | `#1e48ff` | `#12a150` |
| **Secondary accent** (gradients/decorative) | `--peri` | `#879cff` | `#d4a72c` |
| **Title text** (dark, primary copy) | `--ink` | `#0a1a4d` | `#10151c` |
| **Muted text** (subheads/labels) | `--slate` | `#5e687d` | `#5a6473` |

> **Whitelist Wealth palette:** clean premium canvas, money-green hero, gold secondary — green = money,
> gold = premium, near-black title on a light canvas. Kept light-canvas/dark-ink so the presets render
> correctly out of the box. Want a **dark** premium look instead? Say so and I'll invert it.

> Tip: keep **Background light** and **Title text dark** (or vice-versa) so copy stays readable, and let
> **Hero accent** be your one bold brand color. The graphics use it sparingly for emphasis.

## 4. Fonts

- **Display font** (titles/graphics): `Inter` (keeping the bundled default — clean, bold, modern) — default is **Inter**, bundled in `assets/fonts/`
  (nothing to install). To use your own, drop the `.otf`/`.ttf` (with **Black/Bold/Regular** weights) into
  `assets/fonts/` and name it here. *(Prefer Apple's SF Pro Display? Install from https://developer.apple.com/fonts.)*
- **Caption font** (burn-in): **Coolvetica** ships in `assets/fonts/` (the locked explainer caption look).
  Swap only if you want a different caption identity.

## 5. Hook style (TikTok/raw front card)

- **Default hook text** (leave blank to require it per-job): `` _(blank — set per job; hooks are written fresh per video)_
- **Hook-end trigger word** — the spoken word that makes the hook card disappear (the starter system used
  "larp"). Yours: `` _(blank — falls back to the first sentence break)_

## 6. Brand / product wordlist (caption auto-corrections)

WhisperX sometimes mishears product or brand names. List yours as `heard → correct` so captions fix them
automatically.

```
"whitelist wealth" → "Whitelist Wealth", "skool" → "Skool", "trybe" → "Trybe",
"ugc" → "UGC", "mrr" → "MRR", "whitelisting" → "whitelisting", "mccoo" → "McCoo"
```

## 7. Face references (thumbnails)

Not text — drop **4–8 photos of your own face** (varied angles / expressions / lighting, square-ish,
PNG/JPG/WEBP) into `assets/face-refs/`. The thumbnail generator locks your identity from these. See that
folder's README. *(Only needed if you generate thumbnails — long-form YouTube.)*

---

# Part B — what "apply my brand kit" changes (the exact map)

Tell Claude **"apply my brand kit"** and it does all of this. This section is the precise spec it follows —
read it only if you want to verify or do it by hand.

### Colors → `presets/signature-style.md` + `presets/liquid-glass-style.md`
Replace each **default hex with yours, everywhere it appears** in both files. Most colors live only in the
`--token` table; **four** of them *also* appear inline in the background / glass CSS as an **`rgba(R,G,B,a)`**
triple (same R,G,B numbers, varying alpha). For those four, replace the **R,G,B number group** too (leave
the alpha after it alone):

| Your color | Token | Old hex | Also inline as `rgba()` — replace the R,G,B group |
|------------|-------|---------|---------------------------------------------------|
| Background | `--sky`   | `#ddf4ff` | — (hex / token only, one place) |
| Grid       | `--grid`  | `#74dff6` | `rgba(116,223,246, …)` |
| Hero       | `--royal` | `#1e48ff` | `rgba(30,72,255, …)` |
| Secondary  | `--peri`  | `#879cff` | `rgba(135,156,255, …)` |
| Title ink  | `--ink`   | `#0a1a4d` | `rgba(10,26,77, …)` |
| Muted      | `--slate` | `#5e687d` | — (hex / token only, one place) |

(Find-and-replace each old hex; for the four with an `rgba()` form, also swap its `R,G,B` numbers — the
alpha after them stays. Claude does this in one pass.)

### Fonts → both graphics presets
If you swapped the display font: in `presets/signature-style.md` and `presets/liquid-glass-style.md`,
replace the `Inter-{Black,Bold,Regular}.otf` filenames (and the "Inter" name) with your font's files —
which must live in `assets/fonts/`. Keeping Inter (or installing SF Pro)? Nothing to change.

### Identity → `CLAUDE.md` (Brand Kit section) + voice everywhere
Your name, niche, handles, channel ID, and voice/tone go into `CLAUDE.md`'s **Brand Kit** section. The
voice/tone is what captions and on-thumbnail copy are written to match.

### Wordlist → `presets/caption-corrections.json`
Your `heard → correct` pairs go under `"auto"` (applied silently to caption text). Ambiguous words go in
`"flag"` (printed for you to eyeball each run).

### Hook → `presets/tiktok-raw/build.py`
Your default hook text → `DEFAULT_HOOK_TEXT`. Your hook-end trigger word → the line that detects the end of
the spoken hook (search for the `("lark", "larp")` check and swap in your word).

### Face refs / logos → `assets/`
Your photos in `assets/face-refs/`, any brand logos in `assets/logos/`.

### Verify
After applying, render a quick test — e.g. **"make a short explainer from `assets/fonts/`… "** or just run
one real clip through. Check that titles use your font and your hero color shows up on the emphasis word.
Run `./check-setup.sh` to confirm fonts are found.
