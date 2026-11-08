#!/usr/bin/env python3
"""Writes the site-tour spec for /weight-loss (Nov 9, 2026).

Spoken facts are from the reviews in top-weight-loss (config-store.ts:173-:523,
provider-audit.ts) and match the card text the camera highlights; the capture
fails if a highlighted card text is not on the live page. The five checks are
the page's own "How to Choose a GLP-1 Telehealth Provider" list.
/weight-loss is in REVIEW_LOG (REVIEWED_2026_10_30).
"""
import json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://www.treatmentshub.com"

spec = {
    "id": "2026-11-09-weight-loss-site-tour", "mode": "site", "vertical": "weight-loss", "page": "/weight-loss",
    "title": "Best Online GLP-1 Providers (Nov 2026): How Our Top 3 Compare",
    "targets": {
        "h1": {"text": "Best GLP-1 Weight Loss Providers of 2026"},
        "byline": {"selector": "[data-review-status=reviewed]"},
        "embody": {"text": "Read full embody review", "closest": "article"},
        "embody_pts": {"text": "5-minute health qualifier", "closest": "ul"},
        "eden": {"text": "Read full Eden review", "closest": "article"},
        "eden_pts": {"text": "One all-inclusive price: no membership", "closest": "ul"},
        "altrx": {"text": "Read full altRx review", "closest": "article"},
        "altrx_pts": {"text": "Brand-name options too: Zepbound and Wegovy", "closest": "ul"},
        "choose": {"text": "How to Choose a GLP-1 Telehealth Provider"},
        "checks": {"text": "Published, all-inclusive pricing", "closest": "ul"},
    },
    "script": [
        {"say": "Hey guys! Looking for the best online GLP-1 provider? Here's how our ranking actually compares them.",
         "shot": {"target": "h1", "pad": 70, "highlight": True}},
        {"say": "This page was reviewed for medical accuracy, and the ranking was last updated this November.",
         "shot": {"target": "h1", "pad": 70, "highlight": "byline"}},
        {"say": "Number one, embody: a doctor review usually within 24 hours, free one to two day shipping, and no insurance or clinic visits needed.",
         "shot": {"target": "embody", "pad": 12, "scroll_to": "embody", "highlight": "embody_pts"}},
        {"say": "Number two, Eden: one all-inclusive price, the same at every dose, no membership, and doctor-guided care with 24/7 human support.",
         "shot": {"target": "eden", "pad": 12, "scroll_to": "eden", "highlight": "eden_pts"}},
        {"say": "Number three, alt R X: brand-name Zepbound and Wegovy options too, clinician-guided care, and free shipping in about five to seven days.",
         "shot": {"target": "altrx", "pad": 12, "scroll_to": "altrx", "highlight": "altrx_pts"}},
        {"say": "Not sure which fits you? Check five things: published all-inclusive pricing, a licensed prescriber review, pharmacy transparency, support you'll actually use, and shipping that fits the medication.",
         "shot": {"target": "choose", "pad": 16, "scroll_to": "checks", "highlight": "checks"}},
        {"say": "The full ranking and in-depth reviews are on treatments hub dot com.",
         "shot": {"target": "h1", "pad": 70}},
    ],
    "caption_replace": {"alt R X": "altRx", "treatments hub dot com": "treatmentshub.com", "24/7": "24/7"},
    "end": {"headline": "See the full GLP-1 ranking", "url": "treatmentshub.com/weight-loss"},
    "source_note": "Source: treatmentshub.com/weight-loss · page reviewed for medical accuracy by Francheska Capistrano, RMT, MPH (Oct 30, 2026)",
    "music": "bed.mp3", "category_id": "26", "synthetic_media": True,
    "tags": ["glp-1", "best glp-1 provider", "online glp-1", "embody", "eden", "altrx", "compounded semaglutide", "compounded tirzepatide",
             "zepbound", "wegovy", "online weight loss", "weight loss medication online", "semaglutide", "tirzepatide",
             "telehealth weight loss", "how to choose glp-1 provider", "treatmentshub"],
}
spec["description"] = "\n".join([
    "A quick tour of the TreatmentsHub GLP-1 ranking: how embody, Eden and altRx compare, and the five things to check before choosing any online provider.",
    "",
    "How our top 3 compare:",
    "• embody: doctor review usually within 24 hours; free 1-2 day shipping; no insurance or clinic visits needed",
    "• Eden: one all-inclusive price, the same at every dose; no membership; doctor-guided care with 24/7 human support",
    "• altRx: brand-name Zepbound and Wegovy options too; clinician-guided (physician, PA or NP); free shipping in about 5-7 days",
    "",
    "Five checks before you choose: published all-inclusive pricing, a licensed prescriber review, pharmacy transparency, support you'll actually use, and shipping that fits the medication.",
    "",
    "Provider details as listed in our reviews (updated Sep-Oct 2026); ranking updated November 2026. Confirm current terms on each provider's site.",
    "",
    f"Full ranking: {SITE}/weight-loss",
    "The page shown in this video was reviewed for medical accuracy by Francheska Capistrano, RMT, MPH (medical content reviewer) on Oct 30, 2026.",
    "",
    "Important:",
    "• The narration in this video is AI-generated.",
    "• TreatmentsHub is a comparison site, not a medical provider. This is general information, not medical advice.",
    "• Prescription treatment needs an evaluation by a licensed clinician, who decides whether it's right for you.",
    "• Compounded GLP-1 medications are not FDA-approved.",
    "• We may earn a commission from partner links. It never affects our rankings.",
    f"How we rank: {SITE}/weight-loss/how-we-rank",
    "",
    "#GLP1 #WeightLoss #Shorts",
])
assert len(spec["title"]) <= 100 and len(spec["description"]) <= 5000
folder = os.path.join(ROOT, "queue", spec["id"])
os.makedirs(folder, exist_ok=True)
json.dump(spec, open(os.path.join(folder, "spec.json"), "w"), indent=2, ensure_ascii=False)
print("wrote", folder)
