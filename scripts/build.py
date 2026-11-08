#!/usr/bin/env python3
"""Build a YouTube Short (1080x1920, 30fps, H.264/AAC) from a spec.json.

spec.json (in the video's folder, next to its images):
{
  "id": "2026-11-09-glp1-prices",
  "title": "...", "description": "...", "tags": ["..."],
  "slides": [{"image": "a.jpg", "headline": "...", "sub": "..."}],
  "end": {"headline": "...", "url": "treatmentshub.com/..."},
  "music": "track.mp3",            # optional, file in the folder or assets/music
  "slide_seconds": 4.5             # optional
}
Usage: build.py <video_folder> [--out out.mp4]
"""
import json, os, subprocess, sys, tempfile, shutil, argparse
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

W, H, FPS = 1080, 1920, 30
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTS = os.path.join(ROOT, "assets", "fonts")
NAVY, WHITE = (12, 75, 117), (255, 255, 255)
# Shorts UI covers the bottom ~18% and a strip on the right: keep text inside.
SAFE_L, SAFE_R = 72, W - 150


def font(weight, size):
    return ImageFont.truetype(os.path.join(FONTS, f"Inter-{weight}.otf"), size)


def wrap(draw, text, fnt, width):
    words, lines, line = text.split(), [], ""
    for w in words:
        t = (line + " " + w).strip()
        if draw.textlength(t, font=fnt) <= width:
            line = t
        else:
            if line:
                lines.append(line)
            line = w
    if line:
        lines.append(line)
    return lines


def background(img_path):
    """Full-bleed frame. Tall images are cover-cropped; wide ones (screenshots)
    sit whole in the upper half over a blurred, darkened copy of themselves."""
    im = ImageOps.exif_transpose(Image.open(img_path)).convert("RGB")
    ar = im.width / im.height
    if ar <= 0.8:
        return ImageOps.fit(im, (W, H), Image.LANCZOS)
    bg = ImageOps.fit(im, (W, H), Image.LANCZOS).filter(ImageFilter.GaussianBlur(40))
    bg = Image.blend(bg, Image.new("RGB", (W, H), (10, 20, 30)), 0.45)
    fg = ImageOps.contain(im, (W - 60, int(H * 0.50)), Image.LANCZOS)
    mask = Image.new("L", fg.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, fg.width, fg.height], 28, fill=255)
    bg.paste(fg, ((W - fg.width) // 2, 270), mask)
    return bg


def overlay(headline, sub, index, total):
    """Transparent text layer: brand pill top, caption card lower-middle."""
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    # bottom gradient for legibility
    grad = Image.new("L", (1, H), 0)
    for y in range(H):
        grad.putpixel((0, y), int(max(0, (y - H * 0.42) / (H * 0.58)) * 200))
    ov.paste(Image.new("RGBA", (W, H), (0, 0, 0, 255)), (0, 0), grad.resize((W, H)))
    # brand pill
    f = font("SemiBold", 34)
    label = "TreatmentsHub.com"
    tw = d.textlength(label, font=f)
    d.rounded_rectangle([SAFE_L, 150, SAFE_L + tw + 56, 150 + 66], 33, fill=(255, 255, 255, 235))
    d.text((SAFE_L + 28, 150 + 14), label, font=f, fill=NAVY)
    # caption card
    width = SAFE_R - SAFE_L - 60
    fh, fs = font("ExtraBold", 84 if index == 0 else 72), font("SemiBold", 44)
    hl = wrap(d, headline, fh, width)
    sl = wrap(d, sub, fs, width) if sub else []
    lh_h, lh_s = int(fh.size * 1.16), int(fs.size * 1.32)
    box_h = 56 + len(hl) * lh_h + (24 + len(sl) * lh_s if sl else 0) + 40
    top = int(H * 0.80) - box_h  # card ends at 80% height (above Shorts UI)
    d.rounded_rectangle([SAFE_L - 12, top, SAFE_R, top + box_h], 34, fill=(12, 75, 117, 232))
    y = top + 44
    for line in hl:
        d.text((SAFE_L + 30, y), line, font=fh, fill=WHITE)
        y += lh_h
    if sl:
        y += 24
        for line in sl:
            d.text((SAFE_L + 30, y), line, font=fs, fill=(214, 230, 242))
            y += lh_s
    # progress dots
    for i in range(total):
        cx = W // 2 - (total - 1) * 14 + i * 28
        r = 7 if i == index else 5
        d.ellipse([cx - r, int(H * 0.82) - r, cx + r, int(H * 0.82) + r], fill=(255, 255, 255, 255 if i == index else 120))
    return ov


def end_card(headline, url):
    im = Image.new("RGB", (W, H), NAVY)
    d = ImageDraw.Draw(im)
    for y in range(H):  # soft vertical gradient
        t = y / H
        d.line([(0, y), (W, y)], fill=(int(12 + 10 * t), int(75 - 30 * t), int(117 - 40 * t)))
    logo = Image.open(os.path.join(ROOT, "assets", "logo-mark.png")).convert("RGBA").resize((220, 220), Image.LANCZOS)
    im.paste(logo, ((W - 220) // 2, 520), logo)
    fh, fu, fs = font("ExtraBold", 66), font("SemiBold", 46), font("Medium", 32)
    y = 820
    for line in wrap(d, headline, fh, W - 2 * SAFE_L):
        d.text(((W - d.textlength(line, font=fh)) / 2, y), line, font=fh, fill=WHITE)
        y += 80
    y += 30
    uw = d.textlength(url, font=fu)
    d.rounded_rectangle([(W - uw) / 2 - 36, y, (W + uw) / 2 + 36, y + 92], 46, fill=WHITE)
    d.text(((W - uw) / 2, y + 20), url, font=fu, fill=NAVY)
    note = "General information, not medical advice."
    d.text(((W - d.textlength(note, font=fs)) / 2, y + 150), note, font=fs, fill=(190, 210, 228))
    return im


def run(cmd):
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)


def build(folder, out):
    spec = json.load(open(os.path.join(folder, "spec.json")))
    secs = float(spec.get("slide_seconds", 4.5))
    xf = 0.45
    tmp = tempfile.mkdtemp()
    clips = []
    slides = spec["slides"]
    for i, s in enumerate(slides):
        bg, ov = os.path.join(tmp, f"bg{i}.png"), os.path.join(tmp, f"ov{i}.png")
        background(os.path.join(folder, s["image"])).save(bg)
        overlay(s["headline"], s.get("sub", ""), i, len(slides)).save(ov)
        clip = os.path.join(tmp, f"c{i}.mp4")
        frames = int(secs * FPS)
        zoom_in = i % 2 == 0
        z = f"min(1+0.0009*on,1.10)" if zoom_in else f"max(1.10-0.0009*on,1)"
        run(["ffmpeg", "-y", "-loop", "1", "-i", bg, "-loop", "1", "-i", ov, "-filter_complex",
             f"[0]scale={W*2}:{H*2},zoompan=z='{z}':d={frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={W}x{H}:fps={FPS}[bg];"
             f"[1]format=rgba,fade=in:st=0.25:d=0.45:alpha=1[ov];[bg][ov]overlay=0:0,format=yuv420p",
             "-t", f"{secs}", "-r", str(FPS), "-c:v", "libx264", "-preset", "medium", "-crf", "19", clip])
        clips.append(clip)
    endp = os.path.join(tmp, "end.png")
    end = spec.get("end", {})
    end_card(end.get("headline", "Verified prices & honest reviews"), end.get("url", "treatmentshub.com")).save(endp)
    endc = os.path.join(tmp, "end.mp4")
    run(["ffmpeg", "-y", "-loop", "1", "-i", endp, "-vf", "format=yuv420p", "-t", "3.5", "-r", str(FPS),
         "-c:v", "libx264", "-preset", "medium", "-crf", "19", endc])
    clips.append(endc)
    # crossfade chain
    inputs, fc, last, offset = [], [], "0:v", 0.0
    durs = [secs] * len(slides) + [3.5]
    for c in clips:
        inputs += ["-i", c]
    for i in range(1, len(clips)):
        offset += durs[i - 1] - xf
        fc.append(f"[{last}][{i}:v]xfade=transition=fade:duration={xf}:offset={offset:.3f}[v{i}]")
        last = f"v{i}"
    total = sum(durs) - xf * (len(clips) - 1)
    video = os.path.join(tmp, "video.mp4")
    run(["ffmpeg", "-y", *inputs, "-filter_complex", ";".join(fc), "-map", f"[{last}]",
         "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p", "-r", str(FPS), video])
    # audio: music bed (looped, faded) or silence
    music = spec.get("music")
    mpath = None
    if music:
        for cand in (os.path.join(folder, music), os.path.join(ROOT, "assets", "music", music)):
            if os.path.exists(cand):
                mpath = cand
    if mpath:
        run(["ffmpeg", "-y", "-i", video, "-stream_loop", "-1", "-i", mpath, "-filter_complex",
             f"[1:a]volume=0.55,afade=t=in:st=0:d=0.8,afade=t=out:st={total-1.6:.2f}:d=1.6[a]",
             "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", "-t", f"{total:.2f}", out])
    else:
        run(["ffmpeg", "-y", "-i", video, "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo", "-map", "0:v", "-map", "1:a",
             "-c:v", "copy", "-c:a", "aac", "-t", f"{total:.2f}", out])
    shutil.rmtree(tmp)
    return total


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("folder")
    ap.add_argument("--out")
    a = ap.parse_args()
    out = a.out or os.path.join(a.folder, "video.mp4")
    t = build(a.folder, out)
    print(f"built {out} ({t:.1f}s)")
