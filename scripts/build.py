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


def overlay(headline, sub, index, total, pill=True):
    """Transparent text layer: brand pill top, caption card lower-middle."""
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    # bottom gradient for legibility
    grad = Image.new("L", (1, H), 0)
    for y in range(H):
        grad.putpixel((0, y), int(max(0, (y - H * 0.42) / (H * 0.58)) * 200))
    ov.paste(Image.new("RGBA", (W, H), (0, 0, 0, 255)), (0, 0), grad.resize((W, H)))
    # brand pill
    if pill:
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


END_NOTES = [
    "TreatmentsHub is a comparison site, not a medical provider.",
    "General information, not medical advice.",
    "A licensed clinician decides on any prescription.",
    "We may earn a commission from partner links.",
]


def end_card(headline, url, notes=None, source_note=None):
    im = Image.new("RGB", (W, H), NAVY)
    d = ImageDraw.Draw(im)
    for y in range(H):  # soft vertical gradient
        t = y / H
        d.line([(0, y), (W, y)], fill=(int(12 + 10 * t), int(75 - 30 * t), int(117 - 40 * t)))
    # The site's current favicon: the TH monogram (top-weight-loss
    # public/Glossy Blue TH Monogram App Icon.png, live since Oct 22, 2026).
    logo = Image.open(os.path.join(ROOT, "assets", "logo-th.png")).convert("RGBA").resize((230, 230), Image.LANCZOS)
    im.paste(logo, ((W - 230) // 2, 400), logo)
    fh, fu, fs = font("ExtraBold", 66), font("SemiBold", 46), font("Medium", 32)
    y = 700
    for line in wrap(d, headline, fh, W - 2 * SAFE_L):
        d.text(((W - d.textlength(line, font=fh)) / 2, y), line, font=fh, fill=WHITE)
        y += 80
    y += 30
    uw = d.textlength(url, font=fu)
    d.rounded_rectangle([(W - uw) / 2 - 36, y, (W + uw) / 2 + 36, y + 92], 46, fill=WHITE)
    d.text(((W - uw) / 2, y + 20), url, font=fu, fill=NAVY)
    y += 150
    for note in (notes if notes is not None else END_NOTES[1:2]):
        for line in wrap(d, note, fs, W - 2 * SAFE_L):
            d.text(((W - d.textlength(line, font=fs)) / 2, y), line, font=fs, fill=(205, 222, 236))
            y += 44
    if source_note:
        y += 22
        fn = font("Medium", 28)
        for line in wrap(d, source_note, fn, W - 2 * SAFE_L - 40):
            d.text(((W - d.textlength(line, font=fn)) / 2, y), line, font=fn, fill=(170, 196, 218))
            y += 38
    return im


# ───── Presenter mode (HeyGen) ─────
# Spoken disclaimer, appended to every presenter script. The on-screen box
# carries the full text while it is spoken.
DISCLAIMER_SAY = ("Quick heads-up: I'm an AI presenter, and TreatmentsHub is a comparison site, not doctors. "
                  "This isn't medical advice, a licensed clinician decides what's right for you, "
                  "and we may earn a commission from some links.")
DISCLAIMER_BOX = ["AI-generated presenter", "Comparison site, not a medical provider",
                  "Not medical advice: a licensed clinician decides on any prescription",
                  "We may earn a commission from partner links"]
CAP_Y = int(H * 0.665)  # caption centre line: below the face, above the Shorts UI


def parse_srt(path):
    import re
    cues = []
    for block in re.split(r"\n\s*\n", open(path, encoding="utf-8-sig").read().strip()):
        lines = [l for l in block.strip().splitlines() if l.strip()]
        tl = next((i for i, l in enumerate(lines) if "-->" in l), None)
        if tl is None:
            continue
        def ts(s):
            h, m, rest = s.strip().replace(",", ".").split(":")
            return int(h) * 3600 + int(m) * 60 + float(rest)
        a, b = lines[tl].split("-->")
        cues.append((ts(a), ts(b.split()[0]), " ".join(lines[tl + 1:])))
    return cues


def word_times(cues):
    """Spread each cue's time over its words by length: TTS pace is close to even."""
    out = []
    for a, b, text in cues:
        words = text.split()
        if not words:
            continue
        weights = [len(w) + 2 for w in words]
        t, step = a, (b - a) / sum(weights)
        for w, wt in zip(words, weights):
            out.append((w, t, t + wt * step))
            t += wt * step
    return out


def segment_times(segments, words, total):
    """Start/end of each script segment, from the SRT word timings. Falls back to
    character share of the runtime when the word counts don't line up."""
    counts = [len(s["say"].split()) for s in segments]
    if words and sum(counts) == len(words):
        spans, i = [], 0
        for c in counts:
            spans.append([words[i][1], words[i + c - 1][2]])
            i += c
    else:
        print(f"warning: SRT has {len(words)} words, script has {sum(counts)}; timing by characters", file=sys.stderr)
        chars = [len(s["say"]) for s in segments]
        spans, t = [], 0.0
        for c in chars:
            spans.append([t, t + total * c / sum(chars)])
            t = spans[-1][1]
    for k in range(len(spans) - 1):  # close gaps so cutaways hold through pauses
        spans[k][1] = spans[k + 1][0]
    spans[0][0], spans[-1][1] = 0.0, total
    return spans


def caption_chunks(words, max_words=3, max_chars=20):
    chunks, cur = [], []
    for w in words:
        cur.append(w)
        text = " ".join(x[0] for x in cur)
        if len(cur) >= max_words or len(text) >= max_chars or w[0][-1] in ".,!?:;":
            chunks.append(cur)
            cur = []
    if cur:
        chunks.append(cur)
    return [(" ".join(x[0] for x in c), c[0][1], c[-1][2]) for c in chunks]


def caption_png(text):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    f = font("ExtraBold", 78)
    lines = wrap(d, text, f, SAFE_R - SAFE_L)
    y = CAP_Y - len(lines) * 92 // 2
    cx = (SAFE_L + SAFE_R) / 2
    gap = 24  # the stroke eats word spaces, so place words with a wider gap
    for line in lines:
        ws = line.split()
        lw = sum(d.textlength(w, font=f) for w in ws) + gap * (len(ws) - 1)
        x = cx - lw / 2
        for w in ws:
            d.text((x, y), w, font=f, fill=WHITE, stroke_width=8, stroke_fill=(10, 18, 28))
            x += d.textlength(w, font=f) + gap
        y += 92
    return im


def top_bar():
    """Brand pill plus an always-on AI label (transparency, not just the API flag)."""
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    f, fa = font("SemiBold", 34), font("SemiBold", 28)
    label = "TreatmentsHub.com"
    tw = d.textlength(label, font=f)
    d.rounded_rectangle([SAFE_L, 150, SAFE_L + tw + 56, 216], 33, fill=(255, 255, 255, 235))
    d.text((SAFE_L + 28, 164), label, font=f, fill=NAVY)
    ai = "AI presenter"
    x = SAFE_L + tw + 72
    aw = d.textlength(ai, font=fa)
    d.rounded_rectangle([x, 156, x + aw + 40, 210], 27, fill=(10, 18, 28, 170))
    d.text((x + 20, 166), ai, font=fa, fill=(230, 238, 245))
    return im


def disclaimer_png():
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    fh, fs = font("ExtraBold", 46), font("SemiBold", 36)
    width = SAFE_R - SAFE_L - 60
    rows = [wrap(d, t, fs, width - 40) for t in DISCLAIMER_BOX]
    box_h = 40 + 62 + sum(len(r) * 48 + 14 for r in rows) + 30
    top = int(H * 0.79) - box_h
    d.rounded_rectangle([SAFE_L - 12, top, SAFE_R, top + box_h], 30, fill=(12, 75, 117, 238))
    d.text((SAFE_L + 30, top + 36), "Please note", font=fh, fill=WHITE)
    y = top + 40 + 62
    for r in rows:
        d.ellipse([SAFE_L + 32, y + 16, SAFE_L + 44, y + 28], fill=(150, 200, 235))
        for line in r:
            d.text((SAFE_L + 62, y), line, font=fs, fill=(225, 236, 245))
            y += 48
        y += 14
    return im


def brand_bg(folder, image=None):
    """Navy gradient, or a darkened blur of an image when one is given."""
    if image:
        im = ImageOps.fit(ImageOps.exif_transpose(Image.open(os.path.join(folder, image))).convert("RGB"), (W, H), Image.LANCZOS)
        return Image.blend(im.filter(ImageFilter.GaussianBlur(36)), Image.new("RGB", (W, H), (8, 30, 50)), 0.62)
    im = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(im)
    for y in range(H):
        t = y / H
        d.line([(0, y), (W, y)], fill=(int(10 + 6 * t), int(62 - 26 * t), int(100 - 34 * t)))
    return im


def _title(d, text, y, size=68):
    f = font("ExtraBold", size)
    for line in wrap(d, text, f, SAFE_R - SAFE_L):
        d.text((SAFE_L, y), line, font=f, fill=WHITE)
        y += int(size * 1.15)
    return y


def _centered(folder, seg, draw_fn):
    """Draw the card content on its own layer, then centre it in the band
    between the top bar and the Shorts UI."""
    im = brand_bg(folder, seg.get("image")).convert("RGBA")
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    h = draw_fn(ImageDraw.Draw(layer, "RGBA"))
    band_top, band_bot = 270, int(H * 0.79)
    if h > band_bot - band_top:
        raise SystemExit(f"card '{seg.get('title')}' is {h}px tall, band is {band_bot - band_top}px; shorten it")
    top = band_top + max(0, (band_bot - band_top - h) // 2 - 40)
    im.alpha_composite(layer, (0, top))
    return im.convert("RGB")


def compare_card(folder, seg):
    """One criterion, every provider on its own row: readable on a phone,
    unlike a 3-column table. seg: title, label, rows [[provider, value], ...]."""
    def draw(d):
        y = _title(d, seg["title"], 0, 74)
        if seg.get("label"):
            y += 22
            d.text((SAFE_L, y), seg["label"].upper(), font=font("SemiBold", 36), fill=(150, 200, 235))
            y += 64
        fn, fv = font("ExtraBold", 50), font("SemiBold", 44)
        for name, value in seg["rows"]:
            vl = wrap(d, value, fv, SAFE_R - SAFE_L - 64)
            h = 30 + 62 + len(vl) * 56 + 28
            d.rounded_rectangle([SAFE_L - 12, y, SAFE_R, y + h], 28, fill=(255, 255, 255, 238))
            d.text((SAFE_L + 22, y + 26), name, font=fn, fill=NAVY)
            yy = y + 26 + 66
            for line in vl:
                d.text((SAFE_L + 22, yy), line, font=fv, fill=(30, 41, 59))
                yy += 56
            y += h + 22
        return y
    return _centered(folder, seg, draw)


def points_card(folder, seg):
    """A provider (or topic) and 2-4 short points. seg: title, kicker, points."""
    def draw(d):
        y = 0
        if seg.get("kicker"):
            d.text((SAFE_L, y), seg["kicker"].upper(), font=font("SemiBold", 38), fill=(150, 200, 235))
            y += 64
        y = _title(d, seg["title"], y, 80) + 34
        fp = font("SemiBold", 48)
        for p in seg["points"]:
            pl = wrap(d, p, fp, SAFE_R - SAFE_L - 110)
            h = 32 + len(pl) * 60 + 28
            d.rounded_rectangle([SAFE_L - 12, y, SAFE_R, y + h], 26, fill=(255, 255, 255, 34))
            d.ellipse([SAFE_L + 24, y + 48, SAFE_L + 48, y + 72], fill=(110, 190, 245))
            yy = y + 32
            for line in pl:
                d.text((SAFE_L + 78, yy), line, font=fp, fill=WHITE)
                yy += 60
            y += h + 20
        return y
    return _centered(folder, seg, draw)


def still_clip(png, dur, path):
    run(["ffmpeg", "-y", "-loop", "1", "-i", png, "-vf", "fade=in:st=0:d=0.18,format=yuv420p",
         "-t", f"{dur:.3f}", "-r", str(FPS), "-c:v", "libx264", "-preset", "medium", "-crf", "18", path])
    return path


def card_clip(folder, seg, dur, idx, tmp):
    if seg.get("show") in ("compare", "points"):
        png = os.path.join(tmp, f"dc{idx}.png")
        (compare_card if seg["show"] == "compare" else points_card)(folder, seg).save(png)
        return still_clip(png, dur, os.path.join(tmp, f"pc{idx}.mp4"))
    bg, ov = os.path.join(tmp, f"pbg{idx}.png"), os.path.join(tmp, f"pov{idx}.png")
    background(os.path.join(folder, seg["image"])).save(bg)
    overlay(seg["headline"], seg.get("sub", ""), 0, 0, pill=False).save(ov)
    clip = os.path.join(tmp, f"pc{idx}.mp4")
    frames = max(1, int(dur * FPS) + 2)
    z = "min(1+0.0008*on,1.08)" if idx % 2 == 0 else "max(1.08-0.0008*on,1)"
    run(["ffmpeg", "-y", "-loop", "1", "-i", bg, "-loop", "1", "-i", ov, "-filter_complex",
         f"[0]scale={W*2}:{H*2},zoompan=z='{z}':d={frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={W}x{H}:fps={FPS}[bg];"
         f"[1]format=rgba,fade=in:st=0.1:d=0.3:alpha=1[ov];[bg][ov]overlay=0:0,format=yuv420p",
         "-t", f"{dur:.3f}", "-r", str(FPS), "-c:v", "libx264", "-preset", "medium", "-crf", "19", clip])
    return clip


def full_script(spec):
    segs = [dict(s) for s in spec["script"]]
    if not segs or segs[-1].get("show") != "disclaimer":
        segs.append({"say": DISCLAIMER_SAY, "show": "disclaimer"})
    return segs


def build_presenter(folder, out):
    import heygen
    spec = json.load(open(os.path.join(folder, "spec.json")))
    segs = full_script(spec)
    mp4, srt = heygen.render(folder, dict(spec, script=segs))
    total = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", mp4],
                                 check=True, capture_output=True, text=True).stdout.strip())
    words = word_times(parse_srt(srt))
    spans = segment_times(segs, words, total)
    tmp = tempfile.mkdtemp()
    # Captions: one PNG per chunk through the concat demuxer, blank in cutaways
    # and while the disclaimer box is up (the box carries the words then).
    hidden = [(a, b) for s, (a, b) in zip(segs, spans) if s.get("show", "presenter") != "presenter"]
    blank = os.path.join(tmp, "blank.png")
    Image.new("RGBA", (W, H), (0, 0, 0, 0)).save(blank)
    lst, t = [], 0.0
    for n, (text, a, b) in enumerate(caption_chunks(words)):
        mid = (a + b) / 2
        if any(x <= mid < y for x, y in hidden):
            continue
        if a > t:
            lst.append((blank, a - t))
        p = os.path.join(tmp, f"cap{n}.png")
        caption_png(text).save(p)
        lst.append((p, b - a))
        t = b
    if total > t:
        lst.append((blank, total - t))
    with open(os.path.join(tmp, "caps.txt"), "w") as f:
        for p, dur in lst:
            f.write(f"file '{p}'\nduration {max(dur, 0.04):.3f}\n")
        f.write(f"file '{lst[-1][0]}'\n")
    topp, discp = os.path.join(tmp, "top.png"), os.path.join(tmp, "disc.png")
    top_bar().save(topp)
    disclaimer_png().save(discp)
    inputs = ["-i", mp4, "-f", "concat", "-safe", "0", "-i", os.path.join(tmp, "caps.txt"),
              "-loop", "1", "-i", topp, "-loop", "1", "-i", discp]
    fc = [f"[0:v]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS},setsar=1[base]"]
    last, n_in, k = "base", 4, 0
    for s, (a, b) in zip(segs, spans):
        if s.get("show") in ("card", "compare", "points"):
            clip = card_clip(folder, s, b - a, k, tmp)
            inputs += ["-itsoffset", f"{a:.3f}", "-i", clip]
            fc.append(f"[{last}][{n_in}:v]overlay=0:0:eof_action=pass:enable='between(t,{a:.3f},{b:.3f})'[v{k}]")
            last, n_in, k = f"v{k}", n_in + 1, k + 1
        elif s.get("show") == "disclaimer":
            fc.append(f"[3:v]format=rgba[dsc];[{last}][dsc]overlay=0:0:enable='between(t,{a:.3f},{b + 0.05:.3f})'[vd]")
            last = "vd"
    fc.append(f"[1:v]format=rgba,fps={FPS}[cap];[{last}][cap]overlay=0:0:eof_action=pass[vc]")
    fc.append(f"[2:v]format=rgba[top];[vc][top]overlay=0:0,trim=duration={total:.3f},format=yuv420p[vout]")
    main = os.path.join(tmp, "main.mp4")
    run(["ffmpeg", "-y", *inputs, "-filter_complex", ";".join(fc), "-map", "[vout]", "-map", "0:a",
         "-t", f"{total:.3f}", "-r", str(FPS), "-c:v", "libx264", "-preset", "medium", "-crf", "19",
         "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2", main])
    # End card, then join and lay a quiet music bed under the voice.
    end = spec.get("end", {})
    endp, endc, endsec = os.path.join(tmp, "end.png"), os.path.join(tmp, "end.mp4"), 4.0
    end_card(end.get("headline", "Compare before you choose"), end.get("url", "treatmentshub.com"),
             END_NOTES + ["Presenter is AI-generated."], spec.get("source_note")).save(endp)
    run(["ffmpeg", "-y", "-loop", "1", "-i", endp, "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo",
         "-vf", "format=yuv420p", "-t", f"{endsec}", "-r", str(FPS), "-c:v", "libx264", "-preset", "medium", "-crf", "19",
         "-c:a", "aac", "-b:a", "192k", "-shortest", endc])
    joined = os.path.join(tmp, "joined.mp4")
    run(["ffmpeg", "-y", "-i", main, "-i", endc, "-filter_complex",
         "[0:v][0:a][1:v][1:a]concat=n=2:v=1:a=1[v][a]", "-map", "[v]", "-map", "[a]",
         "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", joined])
    length = total + endsec
    mpath = find_music(folder, spec.get("music"))
    if mpath:
        vol = float(spec.get("music_volume", 0.10))
        run(["ffmpeg", "-y", "-i", joined, "-stream_loop", "-1", "-i", mpath, "-filter_complex",
             f"[1:a]volume={vol},afade=t=in:st=0:d=0.8,afade=t=out:st={length-2:.2f}:d=2[m];"
             f"[0:a][m]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11[a]",
             "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
             "-t", f"{length:.2f}", out])
    else:
        run(["ffmpeg", "-y", "-i", joined, "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-c:v", "copy",
             "-c:a", "aac", "-b:a", "192k", "-ar", "48000", out])
    shutil.rmtree(tmp)
    return length


def find_music(folder, music):
    if not music:
        return None
    for cand in (os.path.join(folder, music), os.path.join(ROOT, "assets", "music", music)):
        if os.path.exists(cand):
            return cand
    return None


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
    has_script = "script" in json.load(open(os.path.join(a.folder, "spec.json")))
    t = (build_presenter if has_script else build)(a.folder, out)
    print(f"built {out} ({t:.1f}s)")
