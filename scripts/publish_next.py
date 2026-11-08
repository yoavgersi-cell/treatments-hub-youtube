#!/usr/bin/env python3
"""Daily job: build and upload the oldest video waiting in queue/.

queue/<YYYY-MM-DD-slug>/ holds spec.json (+ images). Folders are taken in name
order, and only once their date prefix is today or earlier, so videos can be
queued ahead. After upload the folder moves to published/ with result.json.

Specs with a "script" use the HeyGen presenter (needs HEYGEN_API_KEY);
specs with "slides" are image-only. --preview NAME builds one folder (due or
not) to video.mp4 without uploading, for the workflow's preview artifact.
"""
import argparse, datetime, json, os, shutil, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import build  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--preview", help="queue folder name to build without uploading")
a = ap.parse_args()

queue = os.path.join(ROOT, "queue")
if a.preview:
    name = a.preview
else:
    today = datetime.date.today().isoformat()
    ready = sorted(d for d in os.listdir(queue) if os.path.isfile(os.path.join(queue, d, "spec.json")) and d[:10] <= today)
    if not ready:
        print("Nothing due in queue/.")
        sys.exit(0)
    name = ready[0]
folder = os.path.join(queue, name)
spec = json.load(open(os.path.join(folder, "spec.json")))
presenter = "script" in spec

# Check every credential before spending HeyGen credits on a render.
need = ([] if a.preview else ["YT_CLIENT_ID", "YT_CLIENT_SECRET", "YT_REFRESH_TOKEN"]) + (["HEYGEN_API_KEY"] if presenter else [])
missing = [k for k in need if not os.environ.get(k)]
if missing:
    print(f"Not configured yet, skipping {name}: missing secrets {', '.join(missing)} (see README).")
    sys.exit(0)

video = os.path.join(folder, "video.mp4")
(build.build_presenter if presenter else build.build)(folder, video)
if a.preview:
    print(f"Preview built: {video}")
    sys.exit(0)

import upload  # noqa: E402
vid = upload.upload(video, spec)
dest = os.path.join(ROOT, "published", name)
shutil.move(folder, dest)
for big in ("video.mp4", "presenter.mp4"):  # keep the repo small; YouTube and HeyGen have the files
    p = os.path.join(dest, big)
    if os.path.exists(p):
        os.remove(p)
json.dump({"youtube_id": vid, "url": f"https://youtube.com/shorts/{vid}", "uploaded": datetime.datetime.utcnow().isoformat() + "Z",
           "privacy_requested": os.environ.get("YT_PRIVACY", "private")}, open(os.path.join(dest, "result.json"), "w"), indent=2)
print(f"Uploaded {name} -> https://youtube.com/shorts/{vid}")
