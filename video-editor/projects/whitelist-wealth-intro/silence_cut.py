#!/usr/bin/env python3
"""Dead-air rough cut (no transcript): detect silences, drop them (with padding),
splice video+audio in one ffmpeg filtergraph, normalize, export 1080p 16:9.
Stopgap first draft until a WhisperX transcript enables the real cut."""
import re, subprocess, sys, json, os

RAW = "projects/whitelist-wealth-intro/raw/whitelist-wealth.mp4"
OUT = "projects/whitelist-wealth-intro/outputs/whitelist-wealth.mp4"
NOISE_DB = -32          # below this = silence
MIN_SIL  = 0.65         # only cut silences at least this long
PAD      = 0.12         # keep this much silence on each side of speech
os.makedirs(os.path.dirname(OUT), exist_ok=True)

# duration
dur = float(subprocess.check_output(
    ["ffprobe","-v","error","-show_entries","format=duration",
     "-of","default=nk=1:nw=1", RAW]).decode().strip())

# detect silences
det = subprocess.run(
    ["ffmpeg","-hide_banner","-i",RAW,"-af",
     f"silencedetect=noise={NOISE_DB}dB:d={MIN_SIL}","-f","null","-"],
    stderr=subprocess.PIPE, stdout=subprocess.DEVNULL).stderr.decode()
starts = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", det)]
ends   = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", det)]
sil = list(zip(starts, ends))

# keep = complement of (padded) silences
keeps, cur = [], 0.0
for s, e in sil:
    cs, ce = s + PAD, e - PAD
    if ce <= cs:            # too short once padded -> keep it
        continue
    if cs > cur:
        keeps.append((cur, cs))
    cur = ce
if dur - cur > 0.05:
    keeps.append((cur, dur))
keeps = [(a, b) for a, b in keeps if b - a >= 0.15]

kept = sum(b - a for a, b in keeps)
print(f"raw {dur:.1f}s -> kept {kept:.1f}s across {len(keeps)} segs "
      f"({100*(1-kept/dur):.0f}% cut)", file=sys.stderr)
json.dump({"segments":[{"start":round(a,3),"end":round(b,3)} for a,b in keeps]},
          open("projects/whitelist-wealth-intro/transcript/silence-cuts.json","w"), indent=2)

# build filtergraph: trim v+a per seg -> concat -> scale 1080p -> gain+limiter
parts, labels = [], []
for i,(a,b) in enumerate(keeps):
    parts.append(f"[0:v]trim=start={a:.3f}:end={b:.3f},setpts=PTS-STARTPTS[v{i}]")
    parts.append(f"[0:a]atrim=start={a:.3f}:end={b:.3f},asetpts=PTS-STARTPTS[a{i}]")
    labels.append(f"[v{i}][a{i}]")
concat = "".join(labels) + f"concat=n={len(keeps)}:v=1:a=1[vc][ac]"
vout = "[vc]scale=1920:1080:flags=lanczos,setsar=1[v]"
aout = "[ac]volume=6dB,alimiter=limit=0.89[a]"
fg = ";".join(parts + [concat, vout, aout])

cmd = ["ffmpeg","-y","-hide_banner","-i",RAW,"-filter_complex",fg,
       "-map","[v]","-map","[a]","-r","30",
       "-c:v","libx264","-preset","medium","-crf","20","-pix_fmt","yuv420p",
       "-c:a","aac","-b:a","192k","-movflags","+faststart", OUT]
print("encoding...", file=sys.stderr)
subprocess.run(cmd, check=True)
print(f"WROTE {OUT}", file=sys.stderr)
