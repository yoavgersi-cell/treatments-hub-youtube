#!/usr/bin/env python3
"""Build a Short from treatmentshub.com itself: a real capture of the page in a
phone-browser frame, an AI voice narrating (HeyGen TTS, no face), captions
timed per character, and the camera moving between page elements.

spec.json (mode "site"):
{
  "mode": "site", "page": "/weight-loss",
  "targets": {"embody": {"text": "Read full embody review", "closest": "article"}, ...},
  "script": [{"say": "...", "shot": {"target": "embody", "zoom": 1.0, "highlight": true,
              "scroll_to": "other_target", "pad": 24}}, ...],
  "caption_replace": {"alt R X": "altRx"},
  "end": {"headline": "...", "url": "treatmentshub.com/weight-loss"},
  "source_note": "...", "music": "bed.mp3"
}
A disclaimer segment (spoken, with the on-screen box) is appended automatically.

Usage: site_video.py <folder> [--out video.mp4] [--fake-voice] [--base URL] [--host-map H=IP:PORT]
--fake-voice: tone instead of TTS with evenly spread timings (layout tests, no key).
"""
import argparse, json, math, os, subprocess, sys, tempfile, shutil, wave, struct
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build  # noqa: E402
from build import W, H, FPS, NAVY, WHITE, SAFE_L, SAFE_R, font, wrap, run  # noqa: E402

Image.MAX_IMAGE_PIXELS = None
ROOT = build.ROOT
SITE = "https://www.treatmentshub.com"
# Browser frame: content window 1000x1040 px, shown 1:1 at zoom 1 (page captured at 2.5x of 400 CSS px).
FX, FY, FW = 40, 470, 1000
BAR = 64
VW, VH = FW, 1560 - FY - BAR
CAP_TOP, CAP_BOT = 236, 450

DISCLAIMER_SAY = ("Quick heads-up: this voice is AI-generated, and TreatmentsHub is a comparison site, not doctors. "
                  "This isn't medical advice. A licensed clinician decides what's right for you, "
                  "and we may earn a commission from some links.")
DISCLAIMER_BOX = ["AI-generated voice", "Comparison site, not a medical provider",
                  "Not medical advice: a licensed clinician decides on any prescription",
                  "We may earn a commission from partner links"]


def ease(t):
    t = max(0.0, min(1.0, t))
    return 4 * t ** 3 if t < 0.5 else 1 - (-2 * t + 2) ** 3 / 2


# ── capture ─────────────────────────────────────────────────────────────
def capture(folder, spec, base, host_map):
    cap = os.path.join(folder, "capture")
    png, meta = os.path.join(cap, "page.png"), os.path.join(cap, "page.json")
    want = json.dumps(spec.get("targets", {}), sort_keys=True)
    if os.path.exists(png) and os.path.exists(meta) and json.load(open(meta)).get("targets_key") == want:
        return png, json.load(open(meta))
    os.makedirs(cap, exist_ok=True)
    tpath = os.path.join(cap, "targets.json")
    json.dump(spec.get("targets", {}), open(tpath, "w"))
    env = dict(os.environ)
    if host_map:
        env["HOST_MAP"] = host_map
    subprocess.run(["node", os.path.join(ROOT, "scripts", "capture_site.mjs"), base + spec["page"], cap, tpath], check=True, env=env)
    m = json.load(open(meta))
    missing = [k for k in spec.get("targets", {}) if k not in m["targets"]]
    if missing:
        raise SystemExit(f"capture: targets not found on {spec['page']}: {missing} (page text changed?)")
    m["targets_key"] = want
    json.dump(m, open(meta, "w"), indent=2)
    return png, m


# ── voice ───────────────────────────────────────────────────────────────
def fake_tts(text, out_wav):
    words = text.split()
    dur = max(1.0, len(words) / 2.6)
    sr = 44100
    with wave.open(out_wav, "w") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes(b"".join(struct.pack("<h", int(2500 * math.sin(2 * math.pi * 210 * i / sr))) for i in range(int(dur * sr))))
    chars, n = [], len(text)
    for i, c in enumerate(text):
        chars.append([c, dur * i / n, dur * (i + 1) / n])
    return {"duration": dur, "chars": chars}


def words_from_chars(chars, offset):
    words, cur = [], None
    for c, a, b in chars:
        if c.isspace():
            if cur:
                words.append(cur); cur = None
            continue
        if cur is None:
            cur = [c, a + offset, b + offset]
        else:
            cur[0] += c; cur[2] = b + offset
    if cur:
        words.append(cur)
    return words


def apply_replacements(words, repl):
    """Merge spoken spellings back into brand spellings for captions,
    e.g. ["alt","R","X"] -> "altRx". Trailing punctuation is kept."""
    for spoken, shown in sorted(repl.items(), key=lambda kv: -len(kv[0].split())):
        parts = [p.lower() for p in spoken.split()]
        out, i = [], 0
        while i < len(words):
            seg = words[i:i + len(parts)]
            norm = [w[0].lower().rstrip(".,!?:;") for w in seg]
            if len(seg) == len(parts) and norm == parts:
                tail = seg[-1][0][len(seg[-1][0].rstrip(".,!?:;")):]
                out.append([shown + tail, seg[0][1], seg[-1][2]])
                i += len(parts)
            else:
                out.append(words[i]); i += 1
        words = out
    return words


def join_wavs(paths, gaps, out):
    with wave.open(paths[0]) as w0:
        params = w0.getparams()
    sr, sw, ch = params.framerate, params.sampwidth, params.nchannels
    with wave.open(out, "w") as o:
        o.setnchannels(ch); o.setsampwidth(sw); o.setframerate(sr)
        for p, g in zip(paths, gaps):
            with wave.open(p) as w:
                if (w.getframerate(), w.getsampwidth(), w.getnchannels()) != (sr, sw, ch):
                    raise SystemExit(f"{p}: audio format differs from the first segment")
                o.writeframes(w.readframes(w.getnframes()))
            o.writeframes(b"\x00" * int(g * sr) * sw * ch)


# ── drawing ─────────────────────────────────────────────────────────────
def chrome(url_label):
    im = build.brand_bg(None)
    d = ImageDraw.Draw(im, "RGBA")
    d.rounded_rectangle([FX - 6, FY - 6, FX + FW + 6, 1560 + 6], 40, fill=(255, 255, 255, 40))
    d.rounded_rectangle([FX, FY, FX + FW, 1560], 34, fill=(243, 245, 248))
    f = font("SemiBold", 30)
    tw = d.textlength(url_label, font=f)
    bx = FX + (FW - tw) / 2
    d.rounded_rectangle([bx - 64, FY + 12, bx + tw + 28, FY + BAR - 10], 20, fill=(226, 230, 236))
    # padlock
    lx, ly = bx - 44, FY + 22
    d.rounded_rectangle([lx, ly + 10, lx + 20, ly + 26], 4, fill=(90, 100, 115))
    d.arc([lx + 3, ly, lx + 17, ly + 18], 180, 360, fill=(90, 100, 115), width=3)
    d.text((bx, FY + 16), url_label, font=f, fill=(60, 70, 85))
    return im


def frame_mask():
    m = Image.new("L", (VW, VH), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, -40, VW, VH], 34, fill=255)
    return m


def top_label():
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    f, fa = font("SemiBold", 34), font("SemiBold", 28)
    label = "TreatmentsHub.com"
    tw = d.textlength(label, font=f)
    d.rounded_rectangle([SAFE_L, 140, SAFE_L + tw + 56, 206], 33, fill=(255, 255, 255, 240))
    d.text((SAFE_L + 28, 154), label, font=f, fill=NAVY)
    x = SAFE_L + tw + 72
    ai = "AI voice"
    aw = d.textlength(ai, font=fa)
    d.rounded_rectangle([x, 146, x + aw + 40, 200], 27, fill=(0, 0, 0, 90))
    d.text((x + 20, 156), ai, font=fa, fill=(230, 238, 245))
    return im


def caption_layer(text):
    im = Image.new("RGBA", (W, CAP_BOT - CAP_TOP), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    f = font("ExtraBold", 70)
    lines = wrap(d, text, f, SAFE_R - SAFE_L + 40)[:2]
    lh = 84
    y = (im.height - len(lines) * lh) // 2
    for line in lines:
        x = (W - d.textlength(line, font=f)) / 2
        d.text((x, y), line, font=f, fill=WHITE, stroke_width=5, stroke_fill=(6, 30, 52))
        y += lh
    return im


def disclaimer_layer():
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    fh, fs = font("ExtraBold", 46), font("SemiBold", 36)
    width = FW - 80
    rows = [wrap(d, t, fs, width - 80) for t in DISCLAIMER_BOX]
    box_h = 40 + 62 + sum(len(r) * 48 + 14 for r in rows) + 30
    top = FY + BAR + (VH - box_h) // 2
    d.rounded_rectangle([FX + 20, FY + BAR, FX + FW - 20, 1540], 30, fill=(8, 30, 50, 150))
    d.rounded_rectangle([FX + 40, top, FX + FW - 40, top + box_h], 30, fill=(12, 75, 117, 245))
    d.text((FX + 80, top + 36), "Please note", font=fh, fill=WHITE)
    y = top + 102
    for r in rows:
        d.ellipse([FX + 82, y + 16, FX + 94, y + 28], fill=(150, 200, 235))
        for line in r:
            d.text((FX + 112, y), line, font=fs, fill=(225, 236, 245))
            y += 48
        y += 14
    return im


# ── camera ──────────────────────────────────────────────────────────────
class Cam:
    def __init__(self, meta):
        self.s = meta["scale"]
        self.pw, self.ph = meta["width"] * self.s, meta["height"] * self.s
        self.t = meta["targets"]

    def view(self, shot, which="target"):
        """(x, y, w) of the page window in screenshot px."""
        zoom = float(shot.get("zoom", 1.0))
        w = self.pw / zoom
        h = w * VH / VW
        name = shot.get(which) if which != "target" else shot.get("target")
        if name is None and which == "target":
            y = float(shot.get("y", 0)) * self.s
            x = (self.pw - w) / 2
        else:
            b = self.t[name]
            cx = (b["x"] + b["w"] / 2) * self.s
            x = cx - w / 2
            pad = float(shot.get("pad", 24)) * self.s
            align = shot.get("align") or ("center" if shot.get("center") else "top")
            if align == "center":
                y = (b["y"] + b["h"] / 2) * self.s - h / 2
            elif align == "bottom":
                y = (b["y"] + b["h"]) * self.s + pad - h
            else:
                y = b["y"] * self.s - pad
        x = max(0, min(self.pw - w, x))
        y = max(0, min(self.ph - h, y))
        return (x, y, w)

    def box(self, name):
        b = self.t[name]
        return [b["x"] * self.s, b["y"] * self.s, (b["x"] + b["w"]) * self.s, (b["y"] + b["h"]) * self.s]


def lerp(a, b, k):
    return tuple(x + (y - x) * k for x, y in zip(a, b))


def build_site(folder, out, fake_voice=False, base=SITE, host_map=None):
    spec = json.load(open(os.path.join(folder, "spec.json")))
    segs = [dict(s) for s in spec["script"]]
    segs.append({"say": DISCLAIMER_SAY, "show": "disclaimer", "shot": {"y": 0}})
    png, meta = capture(folder, spec, base, host_map)
    page = Image.open(png).convert("RGB")
    cam = Cam(meta)

    # voice: one TTS call per segment, so each segment's length is exact
    import heygen
    vdir = os.path.join(folder, "voice")
    os.makedirs(vdir, exist_ok=True)
    settings = None if fake_voice else heygen.narrator_settings(spec)
    metas, wavs = [], []
    for i, s in enumerate(segs):
        wav = os.path.join(vdir, f"{i:02d}.wav")
        metas.append(fake_tts(s["say"], wav) if fake_voice else heygen.tts(s["say"], wav, settings))
        wavs.append(wav)
    gap = 0.28
    t, spans, words = 0.35, [], []
    for s, m in zip(segs, metas):
        dur = m["duration"] or (m["chars"][-1][2] if m["chars"] else 1.0)
        spans.append((t, t + dur))
        if s.get("show") != "disclaimer":
            words += words_from_chars(m["chars"], t)
        t += dur + gap
    total = t + 0.3
    words = apply_replacements(words, spec.get("caption_replace", {}))
    chunks = build.caption_chunks([tuple(w) for w in words], max_words=4, max_chars=24)

    tmp = tempfile.mkdtemp()
    voice = os.path.join(tmp, "voice.wav")
    lead = os.path.join(tmp, "lead.wav")
    with wave.open(wavs[0]) as w0:
        p = w0.getparams()
    with wave.open(lead, "w") as o:
        o.setnchannels(p.nchannels); o.setsampwidth(p.sampwidth); o.setframerate(p.framerate)
        o.writeframes(b"\x00" * int(0.35 * p.framerate) * p.sampwidth * p.nchannels)
    join_wavs([lead] + wavs, [0] + [gap] * (len(wavs) - 1) + [0.3], voice)

    # pre-render layers
    url_label = "treatmentshub.com" + spec["page"]
    base_im = chrome(url_label)
    mask = frame_mask()
    top = top_label()
    caps = [(a, b, caption_layer(text)) for text, a, b in chunks]
    disc = disclaimer_layer()

    # camera keyframes per segment
    views, prev = [], cam.view({"y": 0})
    for s in segs:
        sh = s.get("shot", {})
        v0 = cam.view(sh)
        v1 = (cam.view(dict(sh, target=sh["scroll_to"], align=sh.get("scroll_align", "bottom")))
              if sh.get("scroll_to") else None)
        views.append((prev, v0, v1))
        prev = v1 or v0

    main = os.path.join(tmp, "main.mp4")
    ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                           "-i", "-", "-i", voice, "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p",
                           "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2", "-shortest", main], stdin=subprocess.PIPE)
    nframes = int(total * FPS)
    si = 0
    for fi in range(nframes):
        tt = fi / FPS
        while si < len(segs) - 1 and tt >= spans[si + 1][0] - gap / 2:
            si += 1
        a, b = spans[si]
        frm, to, scroll = views[si]
        move = min(0.9, max(0.3, (b - a) * 0.35))
        k = ease((tt - (a - gap / 2)) / move)
        v = lerp(frm, to, k)
        if scroll is not None:
            ks = ease((tt - (a - gap / 2) - move) / max(0.1, (b - a) - move - 0.3))
            v = lerp(v, scroll, ks) if k >= 1 else v
        x, y, w = v
        h = w * VH / VW
        crop = page.crop((int(x), int(y), int(x + w), int(y + h)))
        if crop.size != (VW, VH):
            crop = crop.resize((VW, VH), Image.BILINEAR)
        im = base_im.copy()
        im.paste(crop, (FX, FY + BAR), mask)
        sh = segs[si].get("shot", {})
        hl = sh.get("highlight")
        if hl and segs[si].get("show") != "disclaimer":
            name = sh["target"] if hl is True else hl
            bx = cam.box(name)
            sc = VW / w
            rx0, ry0 = FX + (bx[0] - x) * sc, FY + BAR + (bx[1] - y) * sc
            rx1, ry1 = FX + (bx[2] - x) * sc, FY + BAR + (bx[3] - y) * sc
            alpha = int(255 * ease((tt - (a - gap / 2) - move * 0.7) / 0.35))
            if alpha > 0:
                ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
                ImageDraw.Draw(ov).rounded_rectangle([rx0 - 10, ry0 - 10, rx1 + 10, ry1 + 10], 26,
                                                     outline=(255, 190, 40, alpha), width=9)
                clip = Image.new("L", (W, H), 0)
                ImageDraw.Draw(clip).rectangle([FX, FY + BAR, FX + FW, 1560], fill=255)
                im.paste(ov, (0, 0), Image.composite(ov.getchannel("A"), Image.new("L", (W, H), 0), clip))
        if segs[si].get("show") == "disclaimer" and tt >= a - gap / 2:
            im.paste(disc, (0, 0), disc)
        im.paste(top, (0, 0), top)
        for ca, cb, layer in caps:
            if ca <= tt < cb + 0.05:
                im.paste(layer, (0, CAP_TOP), layer)
                break
        ff.stdin.write(im.tobytes())
    ff.stdin.close()
    if ff.wait():
        raise SystemExit("ffmpeg failed while encoding frames")

    # end card + music, same as the presenter format
    end = spec.get("end", {})
    endp, endc, endsec = os.path.join(tmp, "end.png"), os.path.join(tmp, "end.mp4"), 4.0
    build.end_card(end.get("headline", "Compare before you choose"), end.get("url", "treatmentshub.com"),
                   build.END_NOTES + ["Narration is AI-generated."], spec.get("source_note")).save(endp)
    run(["ffmpeg", "-y", "-loop", "1", "-i", endp, "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo",
         "-vf", "format=yuv420p", "-t", f"{endsec}", "-r", str(FPS), "-c:v", "libx264", "-preset", "medium", "-crf", "19",
         "-c:a", "aac", "-b:a", "192k", "-shortest", endc])
    joined = os.path.join(tmp, "joined.mp4")
    run(["ffmpeg", "-y", "-i", main, "-i", endc, "-filter_complex", "[0:v][0:a][1:v][1:a]concat=n=2:v=1:a=1[v][a]",
         "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-b:a", "192k", joined])
    length = total + endsec
    mpath = build.find_music(folder, spec.get("music"))
    if mpath:
        vol = float(spec.get("music_volume", 0.10))
        run(["ffmpeg", "-y", "-i", joined, "-stream_loop", "-1", "-i", mpath, "-filter_complex",
             f"[1:a]volume={vol},afade=t=in:st=0:d=0.8,afade=t=out:st={length-2:.2f}:d=2[m];"
             f"[0:a][m]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11[a]",
             "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-t", f"{length:.2f}", out])
    else:
        run(["ffmpeg", "-y", "-i", joined, "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-c:v", "copy", "-c:a", "aac",
             "-b:a", "192k", "-ar", "48000", out])
    shutil.rmtree(tmp)
    return length


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("folder")
    ap.add_argument("--out")
    ap.add_argument("--fake-voice", action="store_true")
    ap.add_argument("--base", default=SITE)
    ap.add_argument("--host-map")
    a = ap.parse_args()
    out = a.out or os.path.join(a.folder, "video.mp4")
    t = build_site(a.folder, out, a.fake_voice, a.base, a.host_map)
    print(f"built {out} ({t:.1f}s)")
