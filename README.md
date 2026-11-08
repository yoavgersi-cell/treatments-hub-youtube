# Treatments HUB - YouTube Shorts

Daily YouTube Shorts for the **Treatments HUB** channel, covering every category on
[treatmentshub.com](https://www.treatmentshub.com): weight loss, hair loss, ED, TRT, HRT and online therapy.

## How it works
1. Each video is a folder in `queue/<YYYY-MM-DD-slug>/` with a `spec.json`: the spoken
   script (split into segments), title, description, tags, and optional images.
2. Every day at 15:17 UTC, `.github/workflows/daily-upload.yml` takes the oldest folder whose
   date has arrived:
   - `scripts/heygen.py` renders the AI presenter speaking the whole script (HeyGen, 9:16,
     1080p) and downloads the video and its subtitle file;
   - `scripts/build.py` adds captions timed from the subtitles, the comparison cards, the
     on-screen disclaimer while it is spoken, and the end card (TH monogram logo);
   - `scripts/upload.py` uploads it with YouTube's synthetic-content flag set.
   The folder then moves to `published/` with the YouTube link in `result.json`.
3. Images for cards go into Google Drive (yoavgersi@gmail.com): `TreatmentsHub YouTube / images - new`.

**Segment types** in `script`: `presenter` (the avatar on screen, with captions), `compare`
(one criterion, a row per provider), `points` (a title and 2-4 bullets), `card` (a photo with
a headline). A disclaimer segment is added automatically to every video.

**Preview before publishing:** Actions > Daily YouTube Short > Run workflow, and type a
queue folder name in "preview". The finished video is attached to the run as an artifact.
Nothing is uploaded to YouTube.

## One-time setup (owner)
**A. HeyGen**
1. In HeyGen, create an API key (https://developers.heygen.com/docs/api-key.md). API usage
   bills to a HeyGen API plan, separate from the web subscription.
2. Add it as the GitHub secret `HEYGEN_API_KEY`.
3. Run Actions > **HeyGen presenter catalog**. It writes `catalog/avatars.md` and
   `catalog/voices.md`. Pick one presenter and one voice, and put their ids in
   `presenter.json`. Use the same presenter every day; it is the channel's face.

**B. Google Cloud (YouTube API)**
1. Go to https://console.cloud.google.com and create a project named `treatments-hub-youtube`.
2. Under APIs & Services > Library, enable **YouTube Data API v3**.
3. Under OAuth consent screen, choose External, fill in the app name and your email, add the
   scope `.../auth/youtube.upload`, add your Google account as a test user, then click
   **Publish app** (in production). If you skip this, the sign-in expires every 7 days.
4. Under Credentials, create an OAuth client ID of type **Web application**. Add this
   redirect URI: `https://developers.google.com/oauthplayground`.

**C. Get the refresh token (no code needed)**
1. Open https://developers.google.com/oauthplayground and click the gear icon. Tick
   "Use your own OAuth credentials" and paste the client ID and secret.
2. In Step 1, enter `https://www.googleapis.com/auth/youtube.upload` and click Authorize APIs.
   Sign in with the account that owns the Treatments HUB channel (choose the channel / Brand
   Account when asked).
3. In Step 2, click "Exchange authorization code for tokens" and copy the **refresh token**.

**D. GitHub secrets** (repo Settings > Secrets and variables > Actions > New repository secret)
- `HEYGEN_API_KEY`, `YT_CLIENT_ID`, `YT_CLIENT_SECRET`, `YT_REFRESH_TOKEN`

Never paste these into a chat. Until all of them exist, the daily job skips without
rendering or uploading anything.

**Privacy:** until Google approves the API project in its compliance audit, YouTube keeps
API uploads **private**. Switch each video to Public in YouTube Studio, or request the audit at
https://support.google.com/youtube/contact/yt_api_form.

## Content rules
- Comparisons first, not prices: plan structure, medication options, support, shipping, who
  each provider is for. Every fact is copied from the site's verified data, with its date in
  the description. No invented numbers, ratings, quotes or testimonials.
- No Trustpilot content (Trustpilot asked us to remove its widgets).
- Positive, fair framing: say what each provider is good for; safety limits (compounded drugs
  not FDA-approved, a clinician decides) are always stated.
- The reviewer credit is only used when the source page is in the site's review log
  (`src/data/reviewers.ts` in top-weight-loss): "page reviewed for medical accuracy by
  Francheska Capistrano, RMT, MPH" with that page's review date. It never claims the video
  itself was reviewed, and never says "doctor".
- The presenter is AI-generated and says so; it is labelled on screen ("AI presenter"), in
  the spoken disclaimer, on the end card and in the description, and `synthetic_media: true`
  sets YouTube's altered/synthetic content flag. It never poses as a doctor or clinician.
- Every video says we are a comparison site, not a medical provider, that it is not medical
  advice, that a licensed clinician decides, and that we may earn a commission.
- Mental-health videos include 988.
