#!/usr/bin/env node
// Capture a treatmentshub.com page as one tall, phone-width screenshot plus
// the page positions of the elements a video wants to show.
//
//   node scripts/capture_site.mjs <url> <out_dir> [targets.json]
//
// targets.json: {"name": {"text": "visible text", "closest": "article"} | {"selector": "css"}, ...}
// "closest" boxes the nearest matching ancestor (e.g. the whole provider card).
// Writes <out_dir>/page.png (CSS width 400 at 2.5x = 1000px wide) and
// <out_dir>/page.json {width, height, scale, targets: {name: {x, y, w, h}}}
// in CSS px. Fixed/sticky overlays (chat helper, popups, sticky bars) are
// removed so they never cover the content. Set HOST_MAP=www.treatmentshub.com=127.0.0.1:4201
// to capture a local build instead of the live site.
import { createRequire } from "node:module";
const require = createRequire(import.meta.url);
const { chromium } = require("playwright"); // CJS resolution: works with a global install too
import fs from "node:fs";
import path from "node:path";

const [url, outDir, targetsPath] = process.argv.slice(2);
if (!url || !outDir) {
  console.error("usage: capture_site.mjs <url> <out_dir> [targets.json]");
  process.exit(2);
}
fs.mkdirSync(outDir, { recursive: true });
const targets = targetsPath ? JSON.parse(fs.readFileSync(targetsPath, "utf8")) : {};
const SCALE = 2.5;
const args = [];
if (process.env.HOST_MAP) {
  const [host, to] = process.env.HOST_MAP.split("=");
  args.push(`--host-resolver-rules=MAP ${host} ${to}`, "--proxy-server=direct://");
}
const browser = await chromium.launch({ args });
const ctx = await browser.newContext({
  viewport: { width: 400, height: 760 },
  deviceScaleFactor: SCALE,
  isMobile: true,
  hasTouch: true,
  userAgent:
    "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1",
});
// Keep the chat teaser and promo popups from ever opening.
await ctx.addInitScript(() => {
  try {
    sessionStorage.setItem("th-chat-teaser-shown", "1");
  } catch {}
});
const page = await ctx.newPage();
const target = process.env.HOST_MAP ? url.replace(/^https:/, "http:") : url;
await page.goto(target, { waitUntil: "networkidle", timeout: 90000 });
// Walk the page so lazy images load, then return to the top.
const total = await page.evaluate(() => document.documentElement.scrollHeight);
for (let y = 0; y < total; y += 600) {
  await page.evaluate((v) => window.scrollTo(0, v), y);
  await page.waitForTimeout(120);
}
await page.evaluate(() => window.scrollTo(0, 0));
await page.waitForLoadState("networkidle").catch(() => {});
await page.evaluate(() => {
  for (const el of document.querySelectorAll("body *")) {
    const pos = getComputedStyle(el).position;
    if (pos === "fixed" || pos === "sticky") el.style.setProperty("display", "none", "important");
  }
  document.documentElement.style.scrollBehavior = "auto";
});
await page.waitForTimeout(400);

const boxes = {};
for (const [name, t] of Object.entries(targets)) {
  const loc = t.selector ? page.locator(t.selector) : page.getByText(t.text, { exact: t.exact ?? false });
  const el = loc.first();
  if (!(await el.count())) {
    console.error(`target not found: ${name} ${JSON.stringify(t)}`);
    process.exitCode = 3;
    continue;
  }
  const b = await el.evaluate((n, sel) => {
    const r = (sel ? n.closest(sel) || n : n).getBoundingClientRect();
    return { x: r.left + window.scrollX, y: r.top + window.scrollY, w: r.width, h: r.height };
  }, t.closest || null);
  boxes[name] = b;
}
const height = await page.evaluate(() => document.documentElement.scrollHeight);
await page.screenshot({ path: path.join(outDir, "page.png"), fullPage: true });
fs.writeFileSync(path.join(outDir, "page.json"), JSON.stringify({ url, width: 400, height, scale: SCALE, targets: boxes }, null, 2));
await browser.close();
console.log(`captured ${url}: ${height}px tall, ${Object.keys(boxes).length} targets`);
