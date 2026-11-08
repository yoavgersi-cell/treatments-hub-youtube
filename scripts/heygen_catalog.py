#!/usr/bin/env python3
"""List HeyGen presenters and voices into catalog/*.md so one can be picked.

Writes catalog/avatars.md (public studio avatars plus your own, with preview
images) and catalog/voices.md (English public voices plus your own, with
preview audio links). Preview links are presigned and expire; rerun the
workflow for fresh ones. Prints the account's plan line from /v3/users/me so
the run log shows the key works. Needs HEYGEN_API_KEY.
"""
import os, sys
from heygen import _req, ROOT

OUT = os.path.join(ROOT, "catalog")


def pages(path, params, max_pages=20):
    token = None
    for _ in range(max_pages):
        q = "&".join(f"{k}={v}" for k, v in params.items()) + (f"&token={token}" if token else "")
        res = _req("GET", f"{path}?{q}")
        yield from res.get("data", [])
        token = res.get("next_token")
        if not res.get("has_more") or not token:
            break


def main():
    os.makedirs(OUT, exist_ok=True)
    me = _req("GET", "/v3/users/me").get("data", {})
    safe = {k: v for k, v in me.items() if k not in ("email", "username", "user_id", "id")}
    print("heygen account:", safe)

    looks = list(pages("/v3/avatars/looks", {"ownership": "private", "limit": 50}, 5))
    looks += list(pages("/v3/avatars/looks", {"ownership": "public", "avatar_type": "studio_avatar", "limit": 50}))
    portrait = [l for l in looks if l.get("preferred_orientation") == "portrait"]
    rest = [l for l in looks if l.get("preferred_orientation") != "portrait"]
    with open(os.path.join(OUT, "avatars.md"), "w") as f:
        f.write("# HeyGen presenters\n\nPortrait looks first (best for Shorts). Copy an `avatar_id` into presenter.json.\n"
                "Preview links expire; rerun the catalog workflow for fresh ones.\n\n")
        f.write("| Preview | Name | avatar_id | Gender | Engines | Default voice |\n|---|---|---|---|---|---|\n")
        for l in portrait + rest:
            img = l.get("preview_image_url") or ""
            prev = f"<img src=\"{img}\" width=\"110\">" if img else ""
            f.write(f"| {prev} | {l.get('name','')} ({l.get('preferred_orientation') or '?'}) | `{l['id']}` | "
                    f"{l.get('gender') or ''} | {', '.join(l.get('supported_api_engines') or [])} | `{l.get('default_voice_id') or ''}` |\n")
    print(f"avatars: {len(looks)} ({len(portrait)} portrait)")

    voices = list(pages("/v3/models/audio/voices", {"type": "private", "limit": 100}, 3))
    voices += [v for v in pages("/v3/models/audio/voices", {"type": "public", "limit": 100})
               if (v.get("language") or "").lower().startswith("en")]
    with open(os.path.join(OUT, "voices.md"), "w") as f:
        f.write("# HeyGen voices\n\nEnglish public voices plus your own. Copy a `voice_id` into presenter.json.\n\n")
        f.write("| Name | voice_id | Language | Gender | Preview |\n|---|---|---|---|---|\n")
        for v in voices:
            a = v.get("preview_audio_url")
            f.write(f"| {v.get('name','')} | `{v['voice_id']}` | {v.get('language') or ''} | {v.get('gender') or ''} | "
                    f"{'[listen](' + a + ')' if a else ''} |\n")
    print(f"voices: {len(voices)}")


if __name__ == "__main__":
    sys.exit(main())
