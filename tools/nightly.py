"""Nightly creative build for @astroaarambhstore.

Usage:  python3 tools/nightly.py data/toppicks.json [--no-push]

toppicks.json is the live "Top picks" list from astroaarambh.store, written by
the nightly run:  [{"slug","name","price","mrp","url","rating","reviews"}, ...]

Steps: pick 5 Story products + 1 Post product (least recently used first,
never two Stories of one product in a night), render JPEGs with the approved
designs, write data/latest.json (public raw URLs + product facts), update
data/history.json, then commit, push and wait until every URL is live.

Product photos in photos/ are used whole and unedited.
"""
import datetime as dt, json, pathlib, random, re, subprocess, sys, time, unicodedata, urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import render  # noqa: E402

RAW = "https://raw.githubusercontent.com/KdAnanta/astroaarambh-instagram/main"
STORIES = 5
THEMES = list(render.THEMES)  # emerald, maroon, royal, earth, plum

AUTO_BENEFITS = [
    (r"wallet|purse|bag|money|wealth|pyrite|zibu|kuber", [["wealth", "Attracts Wealth"], ["coins", "Brings Abundance"], ["shield", "Protects Savings"]]),
    (r"horse|career|success|sun|surya", [["career", "Career Growth"], ["wealth", "Success &amp; Speed"], ["home", "Vastu Positive"]]),
    (r"love|rose quartz|venus", [["peace", "Attracts Love"], ["star", "Harmony"], ["shield", "Positive Energy"]]),
    (r"karungali|evil eye|protection|rahu|ketu|shani", [["shield", "Protection"], ["peace", "Calm Mind"], ["star", "Removes Negativity"]]),
    (r"rudraksha|mala|siddh", [["peace", "Inner Peace"], ["star", "Spiritual Power"], ["shield", "Divine Protection"]]),
    (r"zodiac|rashi", [["star", "Made for Your Rashi"], ["peace", "Balance &amp; Healing"], ["shield", "Positive Energy"]]),
    (r"vastu|yantra|tree|pyramid|frame|murti", [["home", "Vastu Harmony"], ["wealth", "Prosperity"], ["peace", "Peaceful Home"]]),
]

def norm(s):
    s = unicodedata.normalize("NFKC", s).lower()
    return re.sub(r"[^a-z0-9]+", " ", s).strip()

def find_photo(p, copy):
    if copy.get("photo") and (ROOT / "photos" / copy["photo"]).exists():
        return ROOT / "photos" / copy["photo"]
    want = set(norm(p["name"]).split())
    best, score = None, 0.0
    for f in (ROOT / "photos").iterdir():
        if f.suffix.lower() not in (".png", ".jpg", ".jpeg", ".webp"):
            continue
        have = set(norm(f.stem).split())
        s = len(want & have) / max(1, len(want | have))
        if norm(f.stem) == norm(p["slug"]).replace(" ", " "):
            s = 1
        if s > score:
            best, score = f, s
    return best if score >= 0.5 else None

def auto_copy(p):
    clean = re.sub(r"\s*\|.*$", "", p["name"])
    clean = re.sub(r"\(.*?\)", "", clean).strip()
    extra = " ".join(p["name"].split("|")[1:]).strip()
    m = re.match(r"^(.*?)\s+(for\s+.+)$", clean, re.I)
    head = m.group(1) if m else clean
    ben = next((b for rx, b in AUTO_BENEFITS if re.search(rx, p["name"], re.I)),
               [["star", "100% Authentic"], ["peace", "Astrologer Energised"], ["shield", "Govt Lab Certified"]])
    return {"headline": head, "sub": m.group(2).upper() if m else "",
            "ribbon": extra.upper() if extra else "100% NATURAL &#8226; ENERGISED",
            "benefits": ben, "post_title": head,
            "post_sub": m.group(2) if m else "Energised by Top Astrologers", "hashtags": []}

def to_png(path):
    """Decode any format to PNG for the page (format change only, pixels untouched)."""
    from PIL import Image
    out = ROOT / ".cache" / (path.stem + ".png")
    out.parent.mkdir(exist_ok=True)
    if not out.exists():
        Image.open(path).convert("RGB").save(out)
    return out

def git(*a):
    return subprocess.run(["git", "-C", str(ROOT), *a], check=True, capture_output=True, text=True).stdout

def wait_live(urls, timeout=300):
    t0 = time.time()
    pending = list(urls)
    while pending and time.time() - t0 < timeout:
        still = []
        for u in pending:
            try:
                with urllib.request.urlopen(urllib.request.Request(u, method="HEAD"), timeout=20) as r:
                    ok = r.status == 200 and "image/jpeg" in r.headers.get("Content-Type", "")
            except Exception:
                ok = False
            if not ok:
                still.append(u)
        pending = still
        if pending:
            time.sleep(10)
    return pending

def main():
    picks = json.loads(pathlib.Path(sys.argv[1]).read_text())
    push = "--no-push" not in sys.argv
    today = (dt.datetime.utcnow() + dt.timedelta(hours=5, minutes=30)).date().isoformat()
    copies = json.loads((ROOT / "data/products.json").read_text())
    hist_path = ROOT / "data/history.json"
    history = json.loads(hist_path.read_text()) if hist_path.exists() else []

    ready, missing = [], []
    for p in picks:
        c = {**auto_copy(p), **copies.get(p["slug"], {})}
        ph = find_photo(p, c)
        (ready if ph else missing).append({**p, "copy": c, "photo": ph})
    if len(ready) < 2:
        sys.exit(f"Not enough products with photos. Missing photos for: {[m['name'] for m in missing]}")

    def last(slug, kind):
        ds = [h["date"] for h in history if slug in (h.get("stories", []) if kind == "story" else [h.get("post")])]
        return max(ds) if ds else ""
    rnd = random.Random(today)
    order = sorted(ready, key=lambda p: (last(p["slug"], "story"), rnd.random()))
    story_ps = order[:min(STORIES, len(order))]
    post_pool = sorted(ready, key=lambda p: (last(p["slug"], "post"), p in story_ps, rnd.random()))
    post_p = post_pool[0]

    out = ROOT / "out" / today
    out.mkdir(parents=True, exist_ok=True)
    day = dt.date.fromisoformat(today).toordinal()
    manifest = {"date": today, "account_id": "17841422351662463", "stories": [], "post": None,
                "missing_photos": [{"name": m["name"], "url": m.get("url")} for m in missing]}

    for i, p in enumerate(story_ps):
        c = p["copy"]
        spec = {**c, "image": str(to_png(p["photo"])), "price": p["price"], "mrp": p["mrp"]}
        name = f"story-{i+1}-{p['slug'][:60]}.jpg"
        render.shoot(render.story_html(spec, THEMES[(day + i) % len(THEMES)]), str(out / name), 1080, 1920)
        manifest["stories"].append({"image_url": f"{RAW}/out/{today}/{name}", "slug": p["slug"], "name": p["name"],
                                    "price": p["price"], "mrp": p["mrp"], "url": p.get("url")})

    c = post_p["copy"]
    spec = {**c, "image": str(to_png(post_p["photo"])), "price": post_p["price"], "mrp": post_p["mrp"]}
    name = f"post-{post_p['slug'][:60]}.jpg"
    render.shoot(render.post_html(spec), str(out / name), 1080, 1350)
    manifest["post"] = {"image_url": f"{RAW}/out/{today}/{name}", "slug": post_p["slug"], "name": post_p["name"],
                        "price": post_p["price"], "mrp": post_p["mrp"], "url": post_p.get("url"),
                        "rating": post_p.get("rating"), "reviews": post_p.get("reviews"),
                        "hashtags": c.get("hashtags", [])}

    (ROOT / "data/latest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False))
    history = [h for h in history if h["date"] != today]
    history.append({"date": today, "stories": [p["slug"] for p in story_ps], "post": post_p["slug"], "published": False})
    hist_path.write_text(json.dumps(history[-400:], indent=1))

    if push:
        git("add", "-A", "out", "data")
        git("commit", "-q", "-m", f"Creatives for {today}\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>")
        git("push", "-q", "origin", "main")
        urls = [s["image_url"] for s in manifest["stories"]] + [manifest["post"]["image_url"]]
        dead = wait_live(urls)
        if dead:
            sys.exit(f"Images not live yet: {dead}")
    print(json.dumps(manifest, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
