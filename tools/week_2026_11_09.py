#!/usr/bin/env python3
"""Writes the queue specs for Nov 9-15, 2026 (presenter format).

Every provider fact below is copied from the top-weight-loss repo as it stood
on Nov 8, 2026 (file:line noted per video). No Trustpilot content: Trustpilot
asked us to take its widgets down. No prices as the hook: comparisons first.
The reviewer line appears only where the source page is in REVIEW_LOG
(src/data/reviewers.ts, REVIEWED_2026_10_30).
"""
import json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://www.treatmentshub.com"
REVIEWED = ("The comparison page this video is based on was reviewed for medical accuracy by "
            "Francheska Capistrano, RMT, MPH (medical content reviewer) on Oct 30, 2026.")


def footer(extra=()):
    lines = ["", "Important:", "• The presenter in this video is AI-generated.",
             "• TreatmentsHub is a comparison site, not a medical provider. This is general information, not medical advice.",
             "• Prescription treatment needs an evaluation by a licensed clinician, who decides whether it's right for you."]
    lines += [f"• {x}" for x in extra]
    lines += ["• We may earn a commission from partner links. It never affects our rankings.",
              f"How we rank: {SITE}/weight-loss/how-we-rank"]
    return "\n".join(lines)


def note(path, reviewed, label=None):
    return f"Source: {label or 'treatmentshub.com' + path}" + (" · page reviewed for medical accuracy by Francheska Capistrano, RMT, MPH (Oct 30, 2026)" if reviewed else "")


V = []

# ── Mon: weight loss — embody, Eden, altRx (config-store.ts:4135 order; facts :173-:523, provider-audit.ts:28,:60)
V.append(dict(
    id="2026-11-09-weight-loss-top3-compared", vertical="weight-loss", path="/weight-loss", reviewed=True,
    title="embody vs Eden vs altRx: Online GLP-1 Providers Compared (Not Just Price)",
    script=[
        {"say": "Hey guys! Choosing an online GLP-1 provider? Don't just compare prices. Here's how our top three actually differ.", "show": "presenter"},
        {"say": "First, commitment. embody is month to month, Eden has one all-inclusive price with no membership, and alt R X is monthly with no contract.",
         "show": "compare", "title": "No long contracts", "label": "Plan & commitment",
         "rows": [["embody", "Month-to-month, no contract"], ["Eden", "One all-inclusive price, no membership"], ["altRx", "Monthly, no contract; pause or cancel anytime"]]},
        {"say": "Second, medication. embody and Eden offer compounded options only. alt R X also offers brand-name Zepbound and Wegovy.",
         "show": "compare", "title": "Brand-name or compounded?", "label": "Medication options",
         "rows": [["embody", "Compounded medications only"], ["Eden", "Compounded only"], ["altRx", "Brand-name options too: Zepbound and Wegovy"]]},
        {"say": "Third, support. embody has a dedicated nursing team, Eden offers 24/7 human support, and alt R X is clinician-guided.",
         "show": "compare", "title": "Who's in your corner", "label": "Support",
         "rows": [["embody", "Dedicated nursing team, 1:1 medical support"], ["Eden", "Doctor-guided care, 24/7 human support"], ["altRx", "Physician, PA or nurse practitioner"]]},
        {"say": "Shipping? embody ships free in one to two days. alt R X takes about five to seven.", "show": "presenter"},
        {"say": "The full side-by-side, reviewed for medical accuracy, is on treatments hub dot com.", "show": "presenter"},
    ],
    end={"headline": "Compare GLP-1 providers side by side", "url": "treatmentshub.com/weight-loss"},
    summary="How the top three online GLP-1 providers on TreatmentsHub compare on what matters beyond price: commitment, medication options, support and shipping.",
    facts=["embody: month-to-month, no contract; compounded medications only; dedicated nursing team and 1:1 medical support; free 1-2 day shipping",
           "Eden: one all-inclusive price, no membership or long-term plans; compounded only; doctor-guided care with 24/7 human support",
           "altRx: monthly, no contract; brand-name Zepbound and Wegovy options too; clinician-guided (physician, PA or NP); free shipping in about 5-7 days"],
    facts_date="Provider details as listed in our reviews (updated Sep-Oct 2026). Confirm current terms on each provider's site.",
    extra=["Compounded GLP-1 medications are not FDA-approved."],
    tags=["glp-1", "glp1 provider", "best online glp-1 provider", "embody", "eden", "altrx", "compounded semaglutide", "compounded tirzepatide",
          "zepbound", "wegovy", "online weight loss", "weight loss medication online", "semaglutide", "tirzepatide", "telehealth weight loss",
          "glp-1 comparison", "treatmentshub"],
    hashtags="#GLP1 #WeightLoss #Shorts"))

# ── Tue: hair loss — Maximus, Happy Head, PeterMD (hair-loss.ts:2600 order; :237-:357)
V.append(dict(
    id="2026-11-10-hair-loss-top3-compared", vertical="hair-loss", path="/hair-loss", reviewed=True,
    title="Maximus vs Happy Head vs PeterMD: Online Hair Loss Treatment Compared",
    script=[
        {"say": "Hey guys! Thinning hair and shopping online for treatment? Here's how our top three hair-loss providers compare.", "show": "presenter"},
        {"say": "Who it's for. Maximus focuses on men's regrowth. Happy Head has formulas for both men and women. PeterMD is men-focused.",
         "show": "compare", "title": "Men, women, or both?", "label": "Who it's for",
         "rows": [["Maximus", "Focused on men's hair regrowth"], ["Happy Head", "Formulas for both men and women"], ["PeterMD", "Men-focused"]]},
        {"say": "What's on the menu. Maximus offers oral finasteride, minoxidil and dutasteride. Happy Head makes personalized formulas, with topical minoxidil up to eight percent. PeterMD's Follicure spray combines three ingredients in one.",
         "show": "compare", "title": "What you can get", "label": "Treatment options",
         "rows": [["Maximus", "Oral finasteride, minoxidil and dutasteride, plus a compounded topical"], ["Happy Head", "Personalized formulas; topical minoxidil up to 8%"], ["PeterMD", "Follicure RX: minoxidil + finasteride + ketoconazole spray"]]},
        {"say": "And the process. At Maximus a board-certified doctor reviews your questionnaire. Happy Head is dermatologist-founded, with a free online consultation.",
         "show": "points", "kicker": "How it works", "title": "A doctor reviews first",
         "points": ["Maximus: board-certified doctor reviews your questionnaire", "Happy Head: dermatologist-founded, free online consultation", "Prescription treatments need a medical review"]},
        {"say": "Whatever you pick, results need ongoing use. Full comparison, reviewed for medical accuracy, at treatments hub dot com.", "show": "presenter"},
    ],
    end={"headline": "Compare hair-loss treatments", "url": "treatmentshub.com/hair-loss"},
    summary="Maximus, Happy Head and PeterMD compared on who they're for, what they prescribe and how the online visit works.",
    facts=["Maximus: focused on men's hair regrowth; oral finasteride, oral minoxidil and oral dutasteride options plus a compounded topical; a board-certified doctor reviews your questionnaire",
           "Happy Head: formulas for both men and women; personalized topical and oral formulas; topical minoxidil up to 8%; dermatologist-founded, free online consultation",
           "PeterMD: men-focused; Follicure RX topical spray with minoxidil, finasteride and ketoconazole"],
    facts_date="Provider details as listed in our reviews (updated Aug 2026). Confirm current options on each provider's site.",
    extra=["Oral minoxidil is prescribed off-label for hair loss. Finasteride and dutasteride are generally not recommended for women, especially during pregnancy."],
    tags=["hair loss treatment", "online hair loss treatment", "maximus hair", "happy head", "petermd", "finasteride", "minoxidil", "oral minoxidil",
          "dutasteride", "hair regrowth", "thinning hair", "male pattern baldness", "hair loss women", "telehealth hair loss", "treatmentshub"],
    hashtags="#HairLoss #Minoxidil #Shorts"))

# ── Wed: ED — Quad by MEDVi vs Rex MD (ed.ts:61 order; :344-:373, :435-:462)
V.append(dict(
    id="2026-11-11-ed-quad-vs-rexmd", vertical="ed", path="/ed", reviewed=True,
    title="Quad by MEDVi vs Rex MD: Two Very Different Online ED Options",
    script=[
        {"say": "Hey guys! Looking into ED treatment online? Two of the providers we rank take very different approaches. Here's the difference.", "show": "presenter"},
        {"say": "Quad by MEDVi is a compounded four-in-one formula in a single, fast-dissolving dose, so there's no pill to swallow. It's prescription only, after a licensed provider review.",
         "show": "points", "kicker": "Quad by MEDVi", "title": "One dissolvable dose",
         "points": ["Compounded 4-in-1 formula in a single dose", "Fast-dissolving: no pill to swallow", "Rx-only after a licensed-provider review"]},
        {"say": "Rex M D is the big-menu option: branded and generic Viagra and Cialis, daily tadalafil, and its own Ignite gummy, with free two-day discreet delivery.",
         "show": "points", "kicker": "Rex MD", "title": "The big menu",
         "points": ["Branded + generic Viagra & Cialis, plus daily tadalafil", "Ignite ED gummy (sildenafil + tadalafil)", "Free 2-day discreet delivery"]},
        {"say": "So: if a standard pill didn't work well for you, Quad is worth asking about. If you want an established brand with lots of options, look at Rex M D.",
         "show": "compare", "title": "Which fits you?", "label": "Best for",
         "rows": [["Quad by MEDVi", "Men for whom a single standard ED pill underperformed"], ["Rex MD", "Men who want a big, established brand with lots of options"]]},
        {"say": "Our full ED ranking, reviewed for medical accuracy, is on treatments hub dot com.", "show": "presenter"},
    ],
    end={"headline": "Compare online ED treatment", "url": "treatmentshub.com/ed"},
    summary="Quad by MEDVi and Rex MD compared: a single compounded dissolvable dose versus a wide menu of branded and generic options.",
    facts=["Quad by MEDVi: compounded 4-in-1 (\"quad-blend\") formula in a single dose; fast-dissolving, no pill to swallow; Rx-only after a licensed-provider review; prescribed and managed through MEDVi telehealth",
           "Rex MD: branded and generic Viagra and Cialis, plus daily tadalafil; Ignite ED gummy (sildenafil + tadalafil compound); US-licensed provider review; free 2-day discreet delivery"],
    facts_date="Provider details as listed in our reviews (updated Oct 9, 2026). Confirm current options on each provider's site.",
    extra=["Compounded products are not FDA-approved the way brand or generic pills are; whether one is appropriate is a provider's decision.",
           "Never combine an ED medication (PDE5 inhibitor) with nitrates. Tell the clinician about every medication you take."],
    tags=["ed treatment online", "erectile dysfunction treatment", "quad by medvi", "rex md", "sildenafil", "tadalafil", "viagra", "cialis", "daily tadalafil",
          "ed medication", "telehealth ed", "best ed treatment", "ed gummy", "treatmentshub"],
    hashtags="#ED #MensHealth #Shorts"))

# ── Thu: online therapy — Medicare (seed article does-medicare-cover-online-therapy, Nov 6/8, 2026; not in REVIEW_LOG)
V.append(dict(
    id="2026-11-12-medicare-online-therapy", vertical="online-therapy", source_label="our guide, Does Medicare Cover Online Therapy?", path="/online-therapy/articles/does-medicare-cover-online-therapy", reviewed=False,
    title="Does Medicare Cover Online Therapy? Yes, Through 2027 (Which Apps Take It)",
    script=[
        {"say": "Hey guys! Did you know Medicare covers therapy by video, from your own home? Here's what to know before open enrollment ends.", "show": "presenter"},
        {"say": "Medicare Part B covers therapy by video from home, at the same price as an in-person visit, through at least December 31st, 2027. With Original Medicare you pay twenty percent after the Part B deductible.",
         "show": "points", "kicker": "Medicare Part B", "title": "Video therapy is covered",
         "points": ["Covered by video from home through at least Dec 31, 2027", "Same price as an in-person visit", "Original Medicare: 20% after the Part B deductible ($283 in 2026)"]},
        {"say": "But the platform has to take Medicare. Talkspace and Talkiatry say they take Original Medicare. Headspace works only through some Medicare Advantage plans. BetterHelp says it doesn't accept Medicare.",
         "show": "compare", "title": "Which platforms take it?", "label": "Per each company's own help pages",
         "rows": [["Talkspace", "Original Medicare, all 50 states + DC"], ["Talkiatry", "Original Medicare; psychiatry & medication"], ["Headspace", "Select Medicare Advantage plans only"], ["BetterHelp", "Doesn't accept Medicare"]]},
        {"say": "Open enrollment ends December 7th. If you use online therapy, check your plan's network and copays before then.", "show": "presenter"},
        {"say": "If you're struggling right now, call or text 9 8 8. The full guide is on treatments hub dot com.", "show": "presenter"},
    ],
    end={"headline": "Medicare & online therapy, explained", "url": "treatmentshub.com/online-therapy"},
    summary="Medicare Part B covers therapy by video from home through at least Dec 31, 2027. What you pay, which online platforms take Medicare, and what to check before open enrollment ends Dec 7, 2026.",
    facts=["Medicare Part B covers therapy by video from home, at the same price as in person, through at least Dec 31, 2027 (Medicare.gov; Consolidated Appropriations Act, 2026)",
           "Original Medicare: 20% of the Medicare-approved amount after the Part B deductible, $283 in 2026 (CMS)",
           "Talkspace and Talkiatry say they take Original Medicare; Headspace works through select Medicare Advantage plans; BetterHelp says Medicare isn't accepted (each company's own help pages, checked Nov 2026)",
           "Open enrollment runs Oct 15 - Dec 7, 2026; changes take effect Jan 1, 2027"],
    facts_date="Sources: https://www.medicare.gov/coverage/telehealth · https://www.cms.gov/newsroom/fact-sheets/2026-medicare-parts-b-premiums-deductibles · https://www.medicare.gov/health-drug-plans/open-enrollment",
    extra=["Online therapy isn't an emergency service. In a crisis, call or text 988 (Suicide & Crisis Lifeline) or call 911.",
           "Platform policies change; confirm coverage with your plan or 1-800-MEDICARE."],
    tags=["medicare online therapy", "does medicare cover therapy", "medicare telehealth", "medicare open enrollment", "online therapy medicare",
          "talkspace medicare", "talkiatry", "headspace therapy", "betterhelp medicare", "medicare part b", "therapy for seniors", "telehealth 2027", "treatmentshub"],
    hashtags="#Medicare #OnlineTherapy #Shorts"))

# ── Fri: TRT — Hone Health, TMates, Male Excel (trt.ts:1421 order; trt-ported.ts:134-:281)
V.append(dict(
    id="2026-11-13-trt-top3-compared", vertical="trt", path="/trt", reviewed=True,
    title="Hone Health vs TMates vs Male Excel: Online TRT Compared",
    script=[
        {"say": "Hey guys! Thinking about testosterone therapy online? Here's how our top three TRT providers compare.", "show": "presenter"},
        {"say": "All three start with labs. Hone Health tests first to confirm whether your testosterone is clinically low. TMates adds a licensed clinician review. Male Excel offers comprehensive at-home testing.",
         "show": "compare", "title": "It starts with labs", "label": "Getting started",
         "rows": [["Hone Health", "Labs first, to confirm testosterone is clinically low"], ["TMates", "Lab testing plus a licensed-clinician review"], ["Male Excel", "Comprehensive at-home lab testing"]]},
        {"say": "Then ongoing care. Hone does follow-up bloodwork and dose adjustments. TMates is a membership with support built in. Male Excel includes unlimited provider follow-ups.",
         "show": "compare", "title": "What happens next", "label": "Ongoing care",
         "rows": [["Hone Health", "Follow-up bloodwork and dose adjustments"], ["TMates", "Membership model with support built in"], ["Male Excel", "Unlimited provider follow-ups"]]},
        {"say": "TRT is usually long-term, so ask about fertility and monitoring before you start. Full comparison, reviewed for medical accuracy, at treatments hub dot com.", "show": "presenter"},
    ],
    end={"headline": "Compare online TRT providers", "url": "treatmentshub.com/trt"},
    summary="Hone Health, TMates and Male Excel compared on how treatment starts and what ongoing care looks like.",
    facts=["Hone Health: begins with lab testing to confirm whether testosterone is clinically low; ongoing monitoring with follow-up bloodwork and dose adjustments",
           "TMates: TRT-first program; lab testing and a licensed-clinician review; membership model with support built in",
           "Male Excel: comprehensive at-home lab testing; TRT medication if prescribed (injections or cream); unlimited provider follow-ups"],
    facts_date="Provider details as listed in our reviews (updated Sep 14, 2026). Confirm current plans on each provider's site.",
    extra=["TRT is long-term and can affect fertility; it needs ongoing monitoring by a clinician."],
    tags=["trt", "testosterone replacement therapy", "online trt", "low testosterone", "low t", "hone health", "tmates", "male excel", "trt clinic online",
          "testosterone therapy", "mens health", "best trt provider", "treatmentshub"],
    hashtags="#TRT #Testosterone #Shorts"))

# ── Sat: HRT — Winona, Midi Health, Gala (hrt.ts:1380 order; :618-:789, hrt-guides.ts:201,:435)
V.append(dict(
    id="2026-11-14-hrt-top3-compared", vertical="hrt", path="/hrt", reviewed=True,
    title="Winona vs Midi Health vs Gala: Online Menopause HRT Compared",
    script=[
        {"say": "Hey guys! Menopause symptoms and looking at HRT online? Here's how our top three providers compare.", "show": "presenter"},
        {"say": "The visit. Winona is all online, with a free physician consultation. Midi Health has clinicians trained in midlife women's health, with video visits. Gala is a hundred percent online telehealth.",
         "show": "compare", "title": "How the visit works", "label": "The visit",
         "rows": [["Winona", "All online, no video call; free physician consultation"], ["Midi Health", "Midlife-trained clinicians; video visits"], ["Gala", "100% online telehealth visit"]]},
        {"say": "Insurance. Midi works with many major insurance plans. Winona is cash-pay. Gala needs no insurance and accepts FSA and HSA.",
         "show": "compare", "title": "Insurance or cash?", "label": "Paying for it",
         "rows": [["Winona", "Cash-pay; no insurance path"], ["Midi Health", "Works with many major insurance plans"], ["Gala", "No insurance needed; FSA/HSA accepted"]]},
        {"say": "Delivery. Winona delivers in under five days, Gala ships free in one to two days, and with Midi your medication goes through your pharmacy benefit.",
         "show": "compare", "title": "Getting your medication", "label": "Delivery",
         "rows": [["Winona", "Discreet home delivery in under 5 days"], ["Midi Health", "Through your pharmacy benefit"], ["Gala", "Free discreet 1-2 day shipping"]]},
        {"say": "HRT isn't right for everyone, and a licensed clinician decides. Full comparison, reviewed for medical accuracy, at treatments hub dot com.", "show": "presenter"},
    ],
    end={"headline": "Compare online menopause care", "url": "treatmentshub.com/hrt"},
    summary="Winona, Midi Health and Gala compared on how the visit works, insurance versus cash, and how your medication arrives.",
    facts=["Winona: dedicated to menopause and perimenopause; all-online intake with no video call; free physician consultation, pay only if prescribed; cash-pay; discreet home delivery in under 5 days",
           "Midi Health: clinicians trained in midlife women's health; video visits; hormonal and non-hormonal paths; works with many major insurance plans; medication through your pharmacy benefit",
           "Gala: 100% online telehealth visit; no insurance needed, FSA/HSA accepted, cancel anytime; free discreet 1-2 day shipping"],
    facts_date="Provider details as listed in our reviews (updated Oct 8, 2026). Insurance participation varies by state and plan.",
    extra=["HRT carries real risks, including blood clots and stroke; a licensed clinician decides whether it's appropriate for you.",
           "Compounded hormone formulations are not individually FDA-approved products."],
    tags=["hrt", "menopause hrt", "hormone replacement therapy", "online menopause treatment", "perimenopause", "winona", "midi health", "gala hrt",
          "menopause symptoms", "estradiol", "menopause telehealth", "hrt insurance", "treatmentshub"],
    hashtags="#Menopause #HRT #Shorts"))

# ── Sun: GLP-1 hair loss (seed article glp1-hair-loss, Nov 6, 2026; not in REVIEW_LOG)
V.append(dict(
    id="2026-11-15-ozempic-hair-loss-studies", vertical="hair-loss", source_label="our guide, Ozempic Hair Loss: What 2026 Studies Show", path="/hair-loss/articles/glp1-hair-loss", reviewed=False,
    title="Ozempic Hair Loss: What the 2026 Studies Actually Found (and What Helps)",
    script=[
        {"say": "Hey guys! Losing hair on Ozempic, Wegovy or Zepbound? Here's what the 2026 studies actually found.", "show": "presenter"},
        {"say": "A July 2026 BMJ study found people with type 2 diabetes on GLP-1s were between 1.37 and 1.68 times as likely to be diagnosed with hair loss. But the extra risk is small: roughly two or three cases per thousand people a year.",
         "show": "points", "kicker": "The studies", "title": "Linked, but modestly",
         "points": ["BMJ, Jul 2026: 1.37-1.68x as likely to be diagnosed", "Extra risk: about 2-3 cases per 1,000 people a year", "An association, not proof the drug causes it"]},
        {"say": "Most of it looks like telogen effluvium: a temporary shed triggered by fast weight loss and eating less. It usually grows back once your weight steadies.",
         "show": "points", "kicker": "Why it happens", "title": "Usually a temporary shed",
         "points": ["Telogen effluvium, not follicle damage", "Triggered by fast weight loss and eating less", "Usually settles once weight steadies"]},
        {"say": "What helps: eat enough protein, lose weight at a steadier pace, and check your iron. And don't stop your GLP-1 on your own.",
         "show": "points", "kicker": "What helps", "title": "Protect your hair",
         "points": ["Eat enough protein", "Lose weight at a steadier pace", "Get your iron checked", "Don't stop your GLP-1 on your own"]},
        {"say": "Receding hairline or thinning crown? That's pattern loss, and it needs its own treatment. Full breakdown on treatments hub dot com.", "show": "presenter"},
    ],
    end={"headline": "GLP-1s & hair loss, explained", "url": "treatmentshub.com/hair-loss"},
    summary="New 2026 studies link Ozempic, Wegovy and Zepbound to a modestly higher risk of hair loss. Why the shedding happens, whether it's permanent, and what helps.",
    facts=["BMJ (July 2026): adults with type 2 diabetes on GLP-1s were 1.37 to 1.68 times as likely to be diagnosed with hair loss as those on other diabetes drugs; the extra risk is about 2-3 cases per 1,000 person-years",
           "NYU Langone (Sept 2026): higher GLP-1 receptor gene activity linked to about 7% higher odds of male-pattern hair loss (genetic association only)",
           "Most cases look like telogen effluvium, a temporary shed after rapid weight loss"],
    facts_date="Sources: https://bmjgroup.com/glp-1-diabetes-drugs-linked-to-increased-risk-of-hair-loss/ · https://nyulangone.org/news/some-hair-loss-men-linked-use-weight-loss-drugs · https://www.sciencemediacentre.org/expert-reaction-to-a-target-trial-emulation-study-on-risk-of-hair-loss-associated-with-glp-1-ras-in-adults-with-type-2-diabetes/",
    extra=["Talk to your prescriber before changing or stopping any medication. See a dermatologist for patchy loss, scalp symptoms or shedding that doesn't ease."],
    tags=["ozempic hair loss", "glp-1 hair loss", "wegovy hair loss", "zepbound hair loss", "semaglutide hair loss", "tirzepatide hair loss",
          "telogen effluvium", "hair shedding", "hair loss weight loss", "ozempic side effects", "glp-1 side effects", "treatmentshub"],
    hashtags="#Ozempic #HairLoss #Shorts"))


for v in V:
    folder = os.path.join(ROOT, "queue", v["id"])
    os.makedirs(folder, exist_ok=True)
    url = SITE + v["path"]
    desc = "\n".join([v["summary"], "", "What we compared:" if v["vertical"] != "online-therapy" and "studies" not in v["id"] else "Key facts:",
                      *[f"• {f}" for f in v["facts"]], "", v["facts_date"], "", f"Full guide: {url}"]
                     + ([REVIEWED] if v["reviewed"] else []) + [footer(v["extra"]), "", v["hashtags"]])
    spec = {"id": v["id"], "vertical": v["vertical"], "title": v["title"], "description": desc, "tags": v["tags"],
            "category_id": "26", "synthetic_media": True, "script": v["script"], "end": v["end"],
            "source_note": note(v["path"], v["reviewed"], v.get("source_label")), "music": "bed.mp3"}
    assert len(spec["title"]) <= 100 and len(desc) <= 5000 and sum(len(t) + 3 for t in spec["tags"]) < 500, v["id"]
    json.dump(spec, open(os.path.join(folder, "spec.json"), "w"), indent=2, ensure_ascii=False)
    words = sum(len(s["say"].split()) for s in spec["script"]) + 38
    print(f"{v['id']}: {words} words ≈ {words / 2.6:.0f}s + 4s end card")
