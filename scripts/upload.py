#!/usr/bin/env python3
"""Upload one built Short to YouTube with the Data API v3 (resumable upload).

Credentials come only from environment variables (GitHub Actions secrets):
  YT_CLIENT_ID, YT_CLIENT_SECRET, YT_REFRESH_TOKEN
Optional: YT_PRIVACY = private | unlisted | public   (default: private)

Until Google completes the API compliance audit for this project, YouTube
keeps every API upload private regardless of YT_PRIVACY; switch the video
to Public in YouTube Studio.
Usage: upload.py <video.mp4> <spec.json>   -> prints the video id
"""
import json, os, sys, urllib.parse, urllib.request

TOKEN_URL = "https://oauth2.googleapis.com/token"
UPLOAD_URL = "https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status"


def access_token():
    body = urllib.parse.urlencode({
        "client_id": os.environ["YT_CLIENT_ID"],
        "client_secret": os.environ["YT_CLIENT_SECRET"],
        "refresh_token": os.environ["YT_REFRESH_TOKEN"],
        "grant_type": "refresh_token",
    }).encode()
    with urllib.request.urlopen(urllib.request.Request(TOKEN_URL, data=body)) as r:
        return json.load(r)["access_token"]


def upload(video, spec):
    token = access_token()
    meta = {
        "snippet": {
            "title": spec["title"][:100],
            "description": spec["description"][:5000],
            "tags": spec.get("tags", []),
            "categoryId": spec.get("category_id", "26"),
            "defaultLanguage": "en",
            "defaultAudioLanguage": "en",
        },
        "status": {
            "privacyStatus": os.environ.get("YT_PRIVACY", "private"),
            "selfDeclaredMadeForKids": False,
            "containsSyntheticMedia": bool(spec.get("synthetic_media", False)),
        },
    }
    size = os.path.getsize(video)
    req = urllib.request.Request(UPLOAD_URL, data=json.dumps(meta).encode(), method="POST", headers={
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=UTF-8",
        "X-Upload-Content-Type": "video/mp4",
        "X-Upload-Content-Length": str(size),
    })
    with urllib.request.urlopen(req) as r:
        location = r.headers["Location"]
    with open(video, "rb") as f:
        put = urllib.request.Request(location, data=f.read(), method="PUT", headers={
            "Authorization": f"Bearer {token}", "Content-Type": "video/mp4", "Content-Length": str(size)})
    with urllib.request.urlopen(put) as r:
        return json.load(r)["id"]


if __name__ == "__main__":
    vid = upload(sys.argv[1], json.load(open(sys.argv[2])))
    print(vid)
