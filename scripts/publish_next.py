#!/usr/bin/env python3
"""Daily job: build and upload the oldest video waiting in queue/.

queue/<YYYY-MM-DD-slug>/ holds spec.json + images. Folders are taken in name
order, and only once their date prefix is today or earlier, so videos can be
queued ahead. After upload the folder moves to published/ with result.json.
"""
import datetime, json, os, shutil, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import build, upload  # noqa: E402

today = datetime.date.today().isoformat()
queue = os.path.join(ROOT, "queue")
ready = sorted(d for d in os.listdir(queue) if os.path.isfile(os.path.join(queue, d, "spec.json")) and d[:10] <= today)
if not ready:
    print("Nothing due in queue/.")
    sys.exit(0)
name = ready[0]
folder = os.path.join(queue, name)
spec = json.load(open(os.path.join(folder, "spec.json")))
video = os.path.join(folder, "video.mp4")
build.build(folder, video)
vid = upload.upload(video, spec)
dest = os.path.join(ROOT, "published", name)
shutil.move(folder, dest)
os.remove(os.path.join(dest, "video.mp4"))  # keep the repo small; YouTube has the file
json.dump({"youtube_id": vid, "url": f"https://youtube.com/shorts/{vid}", "uploaded": datetime.datetime.utcnow().isoformat() + "Z",
           "privacy_requested": os.environ.get("YT_PRIVACY", "private")}, open(os.path.join(dest, "result.json"), "w"), indent=2)
print(f"Uploaded {name} -> https://youtube.com/shorts/{vid}")
