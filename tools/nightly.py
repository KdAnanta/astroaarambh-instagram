"""Nightly creative build for @astroaarambhstore.

Usage:  python3 tools/nightly.py data/toppicks.json [--no-push]

toppicks.json is the live "Top picks" list from astroaarambh.store, written by
the nightly run:  [{"slug","name","price","mrp","url","rating","reviews"}, ...]

Steps: pick 5 Story products + 1 Post product (least recently used first,
never two Stories of one product in a night), render JPEGs with the approved
designs, write data/latest.json (public raw URLs + product facts), update
data/history.json, then commit, push and wait until every URL is live.

Product photos in photos/ are used whole and unedited.

Ready-made Stories: images the owner uploads to stories/ are posted exactly as
uploaded (only converted to JPEG, never cropped or redesigned), each one once,
in file-name order, up to 5 a night. Any Story slots left over are filled with
Top Picks renders.

Ready-made Posts: images in posts/ need an entry in data/post_images.json.
Files without one are listed in the manifest as "unregistered_posts".
"""
import datetime as dt, json, pathlib, random, re, subprocess, sys, time, unicodedata, urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import designs  # noqa: E402

RAW = "https://raw.githubusercontent.com/KdAnanta/astroaarambh-instagram/main"
STORIES = 5

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
    today = (dt.datetime.now(dt.timezone.utc).replace(tzinfo=None) + dt.timedelta(hours=5, minutes=30)).date().isoformat()
    copies = json.loads((ROOT / "data/products.json").read_text())
    hist_path = ROOT / "data/history.json"
    history = json.loads(hist_path.read_text()) if hist_path.exists() else []

    ready, missing = [], []
    for p in picks:
        c = {**auto_copy(p), **copies.get(p["slug"], {})}
        ph = find_photo(p, c)
        (ready if ph else missing).append({**p, "copy": c, "photo": ph})
    IMG = (".png", ".jpg", ".jpeg", ".webp")
    done_st = {f for h in history for f in (h.get("story_images") or [])}
    sdir = ROOT / "stories"
    ready_st = sorted([f.name for f in sdir.iterdir() if f.suffix.lower() in IMG and f.name not in done_st]
                      if sdir.exists() else [], key=str.lower)[:STORIES]
    if len(ready) < 2 and len(ready_st) < STORIES:
        sys.exit(f"Not enough products with photos. Missing photos for: {[m['name'] for m in missing]}")

    def last(slug, kind):
        ds = [h["date"] for h in history if slug in (h.get("stories", []) if kind == "story" else [h.get("post")])]
        return max(ds) if ds else ""
    rnd = random.Random(today)
    order = sorted(ready, key=lambda p: (last(p["slug"], "story"), rnd.random()))
    story_ps = order[:min(STORIES - len(ready_st), len(order))]
    post_pool = sorted(ready, key=lambda p: (last(p["slug"], "post"), p in story_ps, rnd.random()))
    post_p = post_pool[0]

    # Ready-made post designs uploaded by the owner (posts/ + data/post_images.json) are
    # posted as they are, one per night, least recently posted first, then in planned order.
    pi_path = ROOT / "data/post_images.json"
    pi_all = json.loads(pi_path.read_text()) if pi_path.exists() else []
    post_imgs = [x for x in pi_all if (ROOT / "posts" / x["file"]).exists()]
    known = {x["file"] for x in pi_all}
    unregistered = sorted(f.name for f in (ROOT / "posts").iterdir()
                          if f.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp") and f.name not in known)
    def last_img(f):
        ds = [h["date"] for h in history if h.get("post_image") == f]
        return max(ds) if ds else ""
    ready_img = sorted(post_imgs, key=lambda x: (last_img(x["file"]), x.get("order", 999)))[0] if post_imgs else None

    out = ROOT / "out" / today
    out.mkdir(parents=True, exist_ok=True)
    month = dt.date.fromisoformat(today).strftime("%B %Y").upper()
    manifest = {"date": today, "account_id": "17841422351662463", "stories": [], "post": None,
                "missing_photos": [{"name": m["name"], "url": m.get("url")} for m in missing],
                "unregistered_posts": unregistered, "ready_stories_left": 0}

    # Layout + palette rotation: least recently used layouts first, never the same
    # layout twice in one night, and the palette for each layout also rotates.
    used_l, used_c = {}, {}
    for h in history:
        for d in (h.get("story_designs") or []) + ([h["post_design"]] if h.get("post_design") else []):
            used_c[d] = max(used_c.get(d, ""), h["date"])
            k = d.split(":")[0] + ":" + d.split(":")[1]
            used_l[k] = max(used_l.get(k, ""), h["date"])
    def choose(kind, lib, n, avoid=()):
        lays = sorted(lib, key=lambda l: (used_l.get(f"{kind}:{l}", ""), l in avoid, rnd.random()))[:n]
        res = []
        for l in lays:
            pals = range(len(lib[l]["palettes"]))
            res.append((l, sorted(pals, key=lambda i: (used_c.get(f"{kind}:{l}:{i}", ""), rnd.random()))[0]))
        return res
    story_ds = choose("story", designs.STORY, len(story_ps))
    rnd.shuffle(story_ds)
    post_d = choose("post", designs.POST, 1, avoid={l for l, _ in story_ds})[0]

    from PIL import Image
    from playwright.sync_api import sync_playwright
    def art(p):
        png = to_png(p["photo"])
        w, h = Image.open(png).size
        return {**p["copy"], "price": p["price"], "mrp": p["mrp"]}, png.resolve().as_uri(), w / h
    with sync_playwright() as pw:
        import shutil
        br = pw.chromium.launch(executable_path=shutil.which("google-chrome") or shutil.which("chromium") or None)
        page = br.new_page()
        for i, f in enumerate(ready_st):
            name = f"story-{i+1}-ready-" + re.sub(r"[^a-z0-9]+", "-", f.rsplit(".", 1)[0].lower()).strip("-")[:50] + ".jpg"
            Image.open(sdir / f).convert("RGB").save(out / name, "JPEG", quality=95, subsampling=0)
            manifest["stories"].append({"image_url": f"{RAW}/out/{today}/{name}", "source": "ready-made",
                                        "file": f, "design": "ready"})
        for i, (p, (lay, pal)) in enumerate(zip(story_ps, story_ds), start=len(ready_st)):
            spec, uri, a = art(p)
            name = f"story-{i+1}-{lay}-{p['slug'][:50]}.jpg"
            designs.shoot(page, designs.build("story", lay, pal, spec, uri, a, month), out / name, "story")
            manifest["stories"].append({"image_url": f"{RAW}/out/{today}/{name}", "slug": p["slug"], "name": p["name"],
                                        "price": p["price"], "mrp": p["mrp"], "url": p.get("url"),
                                        "design": f"{lay}:{pal}"})
        if ready_img:
            from PIL import Image as _I
            name = "post-" + re.sub(r"[^a-z0-9]+", "-", ready_img["file"].rsplit(".", 1)[0].lower()).strip("-") + ".jpg"
            _I.open(ROOT / "posts" / ready_img["file"]).convert("RGB").save(out / name, "JPEG", quality=95, subsampling=0)
            br.close()
    if not ready_img:
      with sync_playwright() as pw:
        import shutil
        br = pw.chromium.launch(executable_path=shutil.which("google-chrome") or shutil.which("chromium") or None)
        page = br.new_page()
        spec, uri, a = art(post_p)
        lay, pal = post_d
        name = f"post-{lay}-{post_p['slug'][:50]}.jpg"
        designs.shoot(page, designs.build("post", lay, pal, spec, uri, a, month), out / name, "post")
        br.close()
    if ready_img:
        x = ready_img
        manifest["post"] = {"image_url": f"{RAW}/out/{today}/{name}", "source": "ready-made", "file": x["file"],
                            "slug": x["slug"], "name": x["name"], "price": x["price"], "mrp": x["mrp"], "url": x["url"],
                            "rating": x.get("rating"), "reviews": x.get("reviews"), "category": x.get("category"),
                            "benefits": x.get("benefits", []), "stones": x.get("stones", []),
                            "keywords": x.get("keywords", []), "hashtags": x.get("hashtags", [])}
        lay, pal = "ready", x["file"]
    c = post_p["copy"]
    if not ready_img:
      manifest["post"] = {"image_url": f"{RAW}/out/{today}/{name}", "slug": post_p["slug"], "name": post_p["name"],
                        "price": post_p["price"], "mrp": post_p["mrp"], "url": post_p.get("url"),
                        "rating": post_p.get("rating"), "reviews": post_p.get("reviews"),
                        "hashtags": c.get("hashtags", []), "design": f"{lay}:{pal}"}

    (ROOT / "data/latest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False))
    history = [h for h in history if h["date"] != today]
    if sdir.exists():
        manifest["ready_stories_left"] = len([f for f in sdir.iterdir() if f.suffix.lower() in IMG
                                              and f.name not in done_st and f.name not in ready_st])
    (ROOT / "data/latest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False))
    history.append({"date": today, "stories": [p["slug"] for p in story_ps], "story_images": ready_st,
                    "post": manifest["post"]["slug"], "post_image": ready_img["file"] if ready_img else None,
                    "story_designs": [f"story:{l}:{i}" for l, i in story_ds], "post_design": None if ready_img else f"post:{lay}:{pal}",
                    "published": False})
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
