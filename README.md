# Treatments HUB - YouTube Shorts

Daily YouTube Shorts for the **Treatments HUB** channel, covering every category on
[treatmentshub.com](https://www.treatmentshub.com): weight loss, hair loss, TRT, HRT, ED and online therapy.

## How it works
1. Images go into Google Drive: `TreatmentsHub YouTube / images - new`.
2. Claude turns them into a video folder in `queue/<YYYY-MM-DD-slug>/`: the images, a
   `spec.json` (on-screen script, title, description, tags) and, later, a voice-over script.
3. Every day at 15:17 UTC, `.github/workflows/daily-upload.yml` builds the oldest due video
   with `scripts/build.py` and uploads it with `scripts/upload.py`. The folder then moves to
   `published/` with the YouTube link in `result.json`.

## One-time setup (owner)
**A. Google Cloud (YouTube API)**
1. Go to https://console.cloud.google.com and create a project named `treatments-hub-youtube`.
2. Under APIs & Services > Library, enable **YouTube Data API v3**.
3. Under OAuth consent screen, choose External, fill in the app name and your email, add the
   scope `.../auth/youtube.upload`, add your Google account as a test user, then click
   **Publish app** (in production). If you skip this, the sign-in expires every 7 days.
4. Under Credentials, create an OAuth client ID of type **Web application**. Add this
   redirect URI: `https://developers.google.com/oauthplayground`.

**B. Get the refresh token (no code needed)**
1. Open https://developers.google.com/oauthplayground and click the gear icon. Tick
   "Use your own OAuth credentials" and paste the client ID and secret.
2. In Step 1, enter `https://www.googleapis.com/auth/youtube.upload` and click Authorize APIs.
   Sign in with the account that owns the Treatments HUB channel (choose the channel / Brand
   Account when asked).
3. In Step 2, click "Exchange authorization code for tokens" and copy the **refresh token**.

**C. GitHub secrets** (repo Settings > Secrets and variables > Actions > New repository secret)
- `YT_CLIENT_ID`, `YT_CLIENT_SECRET`, `YT_REFRESH_TOKEN`

Never paste these into a chat.

**Privacy:** until Google approves the API project in its compliance audit, YouTube keeps
API uploads **private**. Switch each video to Public in YouTube Studio, or request the audit at
https://support.google.com/youtube/contact/yt_api_form.

## Content rules
- Facts and prices only from the site's verified data, with dates. No invented numbers,
  ratings or testimonials.
- Every video says we are a comparison site, not a medical provider, and that it is not
  medical advice. The disclaimer is on screen and in the description.
- Compounded medications are always named as not FDA-approved.
- AI-generated people or voices are disclosed (`synthetic_media: true`, which sets YouTube's
  altered/synthetic content flag).
