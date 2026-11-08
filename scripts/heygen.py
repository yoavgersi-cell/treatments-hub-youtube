#!/usr/bin/env python3
"""Render the presenter clip for one Short with the HeyGen API (v3).

The whole spoken script goes out as one avatar video, 9:16 at 1080p, with an
SRT sidecar. build.py then uses the SRT timings to place captions and image
cutaways. Results are cached in the video's folder:

  heygen.json      {"video_id": ..., "status": ...}  (committed even when a
                   run fails, so a retry re-downloads instead of paying for a
                   second render)
  presenter.mp4    the downloaded avatar video
  presenter.srt    its subtitles

Presenter settings come from presenter.json at the repo root (avatar_id,
voice_id, speed, background). A spec may override any of them under
"presenter". Needs HEYGEN_API_KEY.
API reference: https://developers.heygen.com/reference/create-video
"""
import json, os, sys, time, urllib.request, urllib.error

API = "https://api.heygen.com"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _req(method, path, body=None, headers=None):
    key = os.environ["HEYGEN_API_KEY"]
    h = {"X-Api-Key": key, "Accept": "application/json"}
    data = None
    if body is not None:
        data = json.dumps(body).encode()
        h["Content-Type"] = "application/json"
    h.update(headers or {})
    for attempt in range(6):
        r = urllib.request.Request(API + path, data=data, headers=h, method=method)
        try:
            with urllib.request.urlopen(r, timeout=60) as resp:
                return json.loads(resp.read().decode() or "{}")
        except urllib.error.HTTPError as e:
            msg = e.read().decode(errors="replace")
            if e.code in (429, 500, 502, 503, 504) or (e.code == 409 and "request_in_progress" in msg):
                wait = int(e.headers.get("Retry-After") or 0) or 10 * (attempt + 1)
                print(f"heygen {method} {path}: {e.code}, retrying in {wait}s", file=sys.stderr)
                time.sleep(wait)
                continue
            raise SystemExit(f"heygen {method} {path} failed: {e.code} {msg}")
    raise SystemExit(f"heygen {method} {path}: gave up after retries")


def presenter_settings(spec):
    p = json.load(open(os.path.join(ROOT, "presenter.json")))
    p.update(spec.get("presenter", {}))
    if not p.get("avatar_id") or not p.get("voice_id"):
        raise SystemExit("presenter.json needs avatar_id and voice_id (run the HeyGen catalog workflow and pick one)")
    return p


def spoken_text(spec):
    return " ".join(seg["say"].strip() for seg in spec["script"])


def _download(url, dest):
    with urllib.request.urlopen(url, timeout=300) as r, open(dest + ".part", "wb") as f:
        while True:
            chunk = r.read(1 << 20)
            if not chunk:
                break
            f.write(chunk)
    os.replace(dest + ".part", dest)


def render(folder, spec, poll_seconds=15, timeout_minutes=40):
    mp4, srt = os.path.join(folder, "presenter.mp4"), os.path.join(folder, "presenter.srt")
    state_path = os.path.join(folder, "heygen.json")
    state = json.load(open(state_path)) if os.path.exists(state_path) else {}
    p = presenter_settings(spec)
    import hashlib
    digest = hashlib.sha256(json.dumps([spoken_text(spec), p], sort_keys=True).encode()).hexdigest()[:16]
    if state.get("video_id") and state.get("script_hash") != digest:
        # Script or presenter changed since that render: render again.
        state = {"attempt": state.get("attempt", 0) + 1, "superseded": state.get("video_id")}
        for f in (mp4, srt):
            if os.path.exists(f):
                os.remove(f)
    if state.get("status") == "completed" and os.path.exists(mp4) and os.path.exists(srt):
        return mp4, srt
    if not state.get("video_id"):
        body = {
            "type": "avatar",
            "avatar_id": p["avatar_id"],
            "voice_id": p["voice_id"],
            "script": spoken_text(spec),
            "title": spec.get("id", os.path.basename(folder.rstrip("/"))),
            "aspect_ratio": "9:16",
            "resolution": "1080p",
            "caption": {"file_format": "srt"},
            "voice_settings": {"speed": float(p.get("speed", 1.05)), "locale": p.get("locale", "en-US")},
        }
        bg = p.get("background")
        if bg:
            body["background"] = bg if isinstance(bg, dict) else {"type": "color", "value": bg}
        if p.get("engine"):
            body["engine"] = {"type": p["engine"]}
        if p.get("fit"):
            body["fit"] = p["fit"]
        # One key per queue item: a retry within 24h replays instead of re-billing.
        idem = "th-" + "".join(c for c in body["title"] if c.isalnum() or c in "-_.")[:200] + f"-a{state.get('attempt', 0)}"
        res = _req("POST", "/v3/videos", body, {"Idempotency-Key": idem})
        state.update(video_id=res["data"]["video_id"], status=res["data"].get("status"), script_hash=digest)
        json.dump(state, open(state_path, "w"), indent=2)
        print(f"heygen: submitted {state['video_id']}")
    deadline = time.time() + timeout_minutes * 60
    while True:
        d = _req("GET", f"/v3/videos/{state['video_id']}")["data"]
        status = d.get("status")
        if status == "completed":
            break
        if status == "failed":
            # Drop the id and bump the attempt so the next run submits a fresh
            # render under a new idempotency key (the old one would replay).
            state = {"attempt": state.get("attempt", 0) + 1, "last_failure": {
                "video_id": state["video_id"], "code": d.get("failure_code"), "message": d.get("failure_message")}}
            json.dump(state, open(state_path, "w"), indent=2)
            raise SystemExit(f"heygen render failed: {d.get('failure_code')} {d.get('failure_message')}")
        if time.time() > deadline:
            raise SystemExit(f"heygen render still {status} after {timeout_minutes} min; rerun to resume")
        time.sleep(poll_seconds)
    if not d.get("subtitle_url"):
        raise SystemExit("heygen: completed without subtitle_url")
    _download(d["video_url"], mp4)
    _download(d["subtitle_url"], srt)
    state.update(status="completed", duration=d.get("duration"), video_page_url=d.get("video_page_url"))
    json.dump(state, open(state_path, "w"), indent=2)
    print(f"heygen: downloaded {mp4} ({d.get('duration')}s)")
    return mp4, srt


if __name__ == "__main__":
    folder = sys.argv[1]
    render(folder, json.load(open(os.path.join(folder, "spec.json"))))


# ───── Narration only (no avatar): HeyGen Voice text-to-speech ─────
# https://developers.heygen.com/docs/voices/heygen-voice-speech.md
# heygen-voice-1-turbo-free is free until Nov 30, 2026 (HeyGen's stated
# offer); after that set narrator_model in presenter.json to a paid model.
NADINE = "83548de556df48ba8c09c42a57c51d85"  # public voice named in HeyGen's docs


def narrator_settings(spec):
    p = json.load(open(os.path.join(ROOT, "presenter.json")))
    p.update(spec.get("narrator", {}))
    return {"voice_id": p.get("narrator_voice_id") or NADINE,
            "model": p.get("narrator_model") or "heygen-voice-1-turbo-free"}


def tts(text, out_wav, settings):
    """Speak one segment. Returns {"duration", "chars": [[ch, start, end], ...]}
    and writes the WAV. Cached next to the WAV, keyed on text + voice."""
    import hashlib
    meta_path = out_wav[:-4] + ".json"
    key = hashlib.sha256(json.dumps([text, settings], sort_keys=True).encode()).hexdigest()[:16]
    if os.path.exists(out_wav) and os.path.exists(meta_path):
        meta = json.load(open(meta_path))
        if meta.get("key") == key:
            return meta
    res = _req("POST", "/v3/models/audio/tts", {"model": settings["model"], "voice_id": settings["voice_id"],
                                                 "text": text, "language": "en", "with_timestamps": True})["data"]
    _download(res["audio_url"], out_wav)
    meta = {"key": key, "duration": res.get("duration"),
            "chars": [[c["text"], c["start_time"], c["end_time"]] for c in res.get("original_characters") or []]}
    json.dump(meta, open(meta_path, "w"))
    return meta
