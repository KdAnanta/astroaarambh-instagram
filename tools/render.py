"""Render Astro Aarambh Instagram Story (1080x1920) and Post (1080x1350) JPEGs.

The product photo is placed exactly as supplied (no cut-out, recolour or redraw):
it sits inside a gold-edged card, scaled with object-fit: contain.
"""
import base64, json, sys, pathlib
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).parent
import shutil
CHROME = shutil.which("google-chrome") or shutil.which("chromium") or None
F = ROOT.parent / "fonts"

def font(face, path, weight):
    return f"@font-face{{font-family:'{face}';src:url(data:font/woff2;base64,{base64.b64encode((F/path).read_bytes()).decode()});font-weight:{weight}}}"

FONTS = "".join([
    font("Cinzel", "cinzel-latin-600-normal.woff2", 600),
    font("Cinzel", "cinzel-latin-700-normal.woff2", 700),
    font("Playfair", "playfair-display-latin-600-normal.woff2", 600),
    font("Playfair", "playfair-display-latin-700-normal.woff2", 700),
    font("Mont", "montserrat-latin-400-normal.woff2", 400),
    font("Mont", "montserrat-latin-500-normal.woff2", 500),
    font("Mont", "montserrat-latin-600-normal.woff2", 600),
])

ICONS = {
 "wealth": '<path d="M6 30h28M10 26v-6m7 6V16m7 10V12m7 14V8M8 18l8-7 6 4 10-9m0 0h-6m6 0v6"/>',
 "coins": '<ellipse cx="20" cy="10" rx="11" ry="4"/><path d="M9 10v6c0 2.2 4.9 4 11 4s11-1.8 11-4v-6M9 16v6c0 2.2 4.9 4 11 4s11-1.8 11-4v-6M9 22v6c0 2.2 4.9 4 11 4s11-1.8 11-4v-6"/>',
 "shield": '<path d="M20 5l12 4v9c0 8-5.5 13.5-12 16C13.5 31.5 8 26 8 18V9z"/><path d="M14 19l4.5 4.5L27 15"/>',
 "career": '<path d="M8 14h24v16H8zM15 14v-4h10v4M8 21h24"/>',
 "peace": '<path d="M20 30c-6-3-11-8-11-14a6 6 0 0 1 11-3 6 6 0 0 1 11 3c0 6-5 11-11 14z"/>',
 "star": '<path d="M20 6l4.2 8.6 9.5 1.4-6.9 6.7 1.6 9.4L20 27.6l-8.5 4.5 1.6-9.4-6.9-6.7 9.5-1.4z"/>',
 "home": '<path d="M7 19L20 8l13 11M11 16v15h18V16M17 31v-8h6v8"/>',
}
def icon(k):
    return f'<svg viewBox="0 0 40 40" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">{ICONS[k]}</svg>'

LOTUS = '<svg viewBox="0 0 60 30" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M30 26C26 20 26 10 30 3c4 7 4 17 0 23zM30 26c-6-1-12-7-13-15 7 1 12 7 13 15zM30 26c6-1 12-7 13-15-7 1-12 7-13 15zM30 26c-8 1-16-2-21-8 7-2 15 1 21 8zM30 26c8 1 16-2 21-8-7-2-15 1-21 8z"/></svg>'

def img_uri(path):
    data = pathlib.Path(path).read_bytes()
    mime = "image/png" if str(path).endswith("png") else "image/jpeg"
    return f"data:{mime};base64,{base64.b64encode(data).decode()}"

def rupee(n):
    return f"&#8377;{n:,}"

THEMES = {  # rotate so consecutive Stories don't look identical
 "emerald": dict(bg1="#0d2a20", bg2="#04110c", glow="rgba(212,175,55,.22)"),
 "maroon":  dict(bg1="#3a0f14", bg2="#160407", glow="rgba(230,170,80,.22)"),
 "royal":   dict(bg1="#141a3d", bg2="#060818", glow="rgba(212,175,55,.20)"),
 "earth":   dict(bg1="#3a2614", bg2="#140b04", glow="rgba(240,190,90,.22)"),
 "plum":    dict(bg1="#2c1236", bg2="#0f0514", glow="rgba(220,180,90,.20)"),
}

def story_html(p, theme):
    t = THEMES[theme]
    off = round(100 - p["price"] * 100 / p["mrp"])
    u = img_uri(p["image"])
    benefits = "".join(
        f'<div class="b"><div class="ic"><div class="in">{icon(k)}</div></div><span>{label}</span></div>'
        for k, label in p["benefits"][:3])
    return f"""<html><head><style>{FONTS}
*{{margin:0;box-sizing:border-box}}
body{{width:1080px;height:1920px;overflow:hidden;font-family:Mont;color:#f6e7c1;position:relative;
 background:radial-gradient(ellipse 75% 40% at 50% 62%,{t['glow']},transparent 70%),
 radial-gradient(ellipse at 50% 25%,{t['bg1']},{t['bg2']} 78%)}}
.rays{{position:absolute;left:50%;top:1200px;width:1800px;height:1800px;margin:-900px 0 0 -900px;opacity:.16;
 background:repeating-conic-gradient(from 0deg,rgba(255,220,140,.9) 0 3deg,transparent 3deg 15deg);
 -webkit-mask-image:radial-gradient(circle,#000 10%,transparent 55%)}}
.spark{{position:absolute;inset:0;opacity:.6;
 background-image:radial-gradient(circle,rgba(255,225,150,.8) 1.5px,transparent 2.2px),radial-gradient(circle,rgba(255,215,120,.45) 1px,transparent 1.6px);
 background-size:173px 211px,97px 131px;background-position:31px 47px,11px 3px;
 -webkit-mask-image:linear-gradient(#000 0,transparent 28%,transparent 75%,#000)}}
.gold{{background:linear-gradient(180deg,#fffbe6 0%,#f6d77f 30%,#c8952a 62%,#f9e7a8 100%);
 -webkit-background-clip:text;color:transparent;filter:drop-shadow(0 4px 8px rgba(0,0,0,.55))}}
.top{{position:absolute;top:78px;width:100%;text-align:center}}
.site{{display:flex;align-items:center;justify-content:center;gap:26px;font-size:33px;letter-spacing:2px;color:#f3e2b4}}
.site:before,.site:after{{content:"";width:160px;height:2px;background:linear-gradient(90deg,transparent,#e0bb55)}}
.site:after{{transform:scaleX(-1)}}
.lotus{{width:66px;color:#e0bb55;margin:8px auto 0}}
h1{{font-family:Cinzel;font-weight:700;font-size:{p.get('title_size',118)}px;line-height:1;margin-top:20px;padding:0 50px;letter-spacing:1px}}
h2{{display:flex;align-items:center;justify-content:center;gap:24px;font-family:Cinzel;font-weight:600;font-size:52px;letter-spacing:3px;margin-top:14px;color:#fbf0d6}}
h2:before,h2:after{{content:"";width:90px;height:2px;background:#e0bb55}}
.ribbon{{display:inline-block;margin-top:22px;padding:14px 60px;font-family:Cinzel;font-weight:700;font-size:33px;color:#2a1c05;
 background:linear-gradient(180deg,#fbe9ad,#d9ad42 60%,#f1d27e);clip-path:polygon(4% 0,96% 0,100% 50%,96% 100%,4% 100%,0 50%)}}
.bens{{position:absolute;top:{p.get('bens_top',648)}px;width:100%;display:flex;justify-content:center;gap:64px}}
.b{{width:236px;text-align:center;font-size:30px;font-weight:600;line-height:1.2;color:#fbf0d6}}
.ic{{width:124px;height:124px;margin:0 auto 14px;border-radius:50%;padding:4px;
 background:linear-gradient(160deg,#fff1b8,#c8952a 45%,#f6d77f 70%,#9c6f1c);box-shadow:0 8px 20px rgba(0,0,0,.5)}}
.in{{width:100%;height:100%;border-radius:50%;display:grid;place-items:center;color:#f3cf6c;
 background:radial-gradient(circle at 50% 35%,rgba(40,30,10,.7),rgba(0,0,0,.92))}}
.in svg{{width:62px}}
.frame{{position:absolute;left:84px;right:84px;top:{p.get('card_top',905)}px;height:610px;border-radius:30px;padding:6px;
 background:linear-gradient(150deg,#fff1b8,#c8952a 30%,#f6d77f 55%,#9c6f1c 80%,#f1d27e);
 box-shadow:0 0 60px rgba(240,200,110,.25),0 45px 90px rgba(0,0,0,.7);
 -webkit-box-reflect:below 14px linear-gradient(transparent 82%,rgba(255,255,255,.18))}}
.card{{position:relative;width:100%;height:100%;border-radius:25px;overflow:hidden;background:#fff}}
.card img{{position:relative;width:100%;height:100%;object-fit:contain}}
.bl{{position:absolute;inset:-40px;background-size:cover;background-position:center;filter:blur(30px) brightness(.9)}}
.corner{{position:absolute;width:70px;height:70px;border:3px solid #f1d27e;z-index:2}}
.c1{{top:-18px;left:-18px;border-right:0;border-bottom:0;border-radius:18px 0 0 0}}
.c2{{top:-18px;right:-18px;border-left:0;border-bottom:0;border-radius:0 18px 0 0}}
.c3{{bottom:-18px;left:-18px;border-right:0;border-top:0;border-radius:0 0 0 18px}}
.c4{{bottom:-18px;right:-18px;border-left:0;border-top:0;border-radius:0 0 18px 0}}
.off{{position:absolute;top:{p.get('card_top',905)-62}px;right:46px;width:190px;height:190px;z-index:3;transform:rotate(-12deg);
 background:linear-gradient(160deg,#fff1b8,#c8952a 50%,#f6d77f);
 clip-path:polygon(50% 0,61% 13%,77% 6%,80% 23%,96% 26%,90% 42%,100% 55%,86% 65%,90% 82%,73% 82%,65% 97%,50% 88%,35% 97%,27% 82%,10% 82%,14% 65%,0 55%,10% 42%,4% 26%,20% 23%,23% 6%,39% 13%)}}
.off div{{position:absolute;inset:11px;display:grid;place-items:center;text-align:center;color:#fff;font-weight:600;font-size:25px;line-height:1;
 background:radial-gradient(circle at 40% 30%,#e8432a,#9d1208);clip-path:inherit}}
.off b{{font-size:54px;display:block}}
.price{{position:absolute;top:1572px;width:100%;text-align:center}}
.plate{{display:inline-block;padding:5px;background:linear-gradient(160deg,#fff1b8,#c8952a 45%,#f6d77f 70%,#9c6f1c);
 clip-path:polygon(7% 0,93% 0,100% 22%,100% 78%,93% 100%,7% 100%,0 78%,0 22%)}}
.pin{{padding:6px 96px 12px;background:radial-gradient(ellipse at 50% 20%,rgba(50,38,12,.95),#050403);
 clip-path:polygon(7% 0,93% 0,100% 22%,100% 78%,93% 100%,7% 100%,0 78%,0 22%)}}
.now{{font-family:Playfair;font-weight:700;font-size:104px;line-height:1.05;font-variant-numeric:lining-nums}}
.was{{font-size:36px;color:#d8c9a3}}
.was s{{text-decoration-color:#e0352b;text-decoration-thickness:4px}}
.cta{{display:inline-block;margin-top:20px;padding:15px 54px;border-radius:50px;font-size:29px;letter-spacing:4px;font-weight:600;color:#2a1c05;
 background:linear-gradient(180deg,#fbe9ad,#d9ad42);box-shadow:0 8px 22px rgba(0,0,0,.5)}}
</style></head><body>
<div class="rays"></div><div class="spark"></div>
<div class="top">
 <div class="site">astroaarambh.store</div><div class="lotus">{LOTUS}</div>
 <h1 class="gold">{p['headline']}</h1>
 {f'<h2>{p["sub"]}</h2>' if p.get('sub') else ''}
 {f'<div class="ribbon">{p["ribbon"]}</div>' if p.get('ribbon') else ''}
</div>
<div class="bens">{benefits}</div>
<div class="frame"><i class="corner c1"></i><i class="corner c2"></i><i class="corner c3"></i><i class="corner c4"></i>
 <div class="card"><div class="bl" style="background-image:url({u})"></div><img src="{u}"></div></div>
<div class="off"><div><span><b>{off}%</b>OFF</span></div></div>
<div class="price"><div class="plate"><div class="pin"><div class="now gold">{rupee(p['price'])}</div>
<div class="was">MRP <s>{rupee(p['mrp'])}</s></div></div></div><br>
<div class="cta">SHOP NOW &#10140; LINK IN BIO</div></div>
<script>document.fonts.ready.then(function(){{const top=document.querySelector('.top'),h=top.querySelector('h1'),
lim=document.querySelector('.bens').offsetTop-24,fits=()=>top.offsetTop+top.offsetHeight<=lim;
let f=parseFloat(getComputedStyle(h).fontSize);
while(!fits()&&f>62){{f-=4;h.style.fontSize=f+'px'}}
const r=top.querySelector('.ribbon');if(!fits()&&r)r.remove();
const h2=top.querySelector('h2');let g=h2?parseFloat(getComputedStyle(h2).fontSize):0;
while(!fits()&&h2&&g>30){{g-=3;h2.style.fontSize=g+'px'}}
while(!fits()&&f>48){{f-=3;h.style.fontSize=f+'px'}}}})</script>
</body></html>"""

def post_html(p):
    u = img_uri(p["image"])
    return f"""<html><head><style>{FONTS}
*{{margin:0;box-sizing:border-box}}
body{{width:1080px;height:1350px;overflow:hidden;font-family:Mont;color:#3b2412;position:relative;
 background:linear-gradient(180deg,#f7efe2 0%,#efe2cc 66%,#e6d6bd 66.2%,#f3eadc 100%);display:flex;flex-direction:column;align-items:center;padding:64px 110px 52px}}
.light{{position:absolute;inset:0;background:
 linear-gradient(115deg,transparent 30%,rgba(255,255,255,.55) 38%,transparent 46%,transparent 52%,rgba(255,255,255,.4) 58%,transparent 66%);
 -webkit-mask-image:linear-gradient(#000 60%,transparent)}}
.glow{{position:absolute;left:50%;top:700px;width:1100px;height:900px;margin:-450px 0 0 -550px;
 background:radial-gradient(ellipse,rgba(255,250,235,.95),transparent 60%)}}
.title{{position:relative;text-align:center;width:960px}}
h1{{font-family:Playfair;font-weight:700;font-size:{p.get('post_title_size',72 if len(p['post_title'])<=26 else 64)}px;line-height:1.08;
 background:linear-gradient(180deg,#5a2f12,#2c1306);-webkit-background-clip:text;color:transparent}}
.rule{{display:flex;align-items:center;justify-content:center;gap:16px;margin:22px auto 18px;color:#b8893a}}
.rule:before,.rule:after{{content:"";width:270px;height:2px;background:linear-gradient(90deg,transparent,#b8893a)}}
.rule:after{{transform:scaleX(-1)}}
.rule svg{{width:46px}}
h2{{font-size:42px;font-weight:500;letter-spacing:4px;color:#4a3322}}
.shadow{{position:absolute;left:160px;right:160px;top:1120px;height:70px;border-radius:50%;
 background:radial-gradient(ellipse,rgba(60,35,10,.45),transparent 70%);filter:blur(8px)}}
.frame{{position:relative;width:100%;flex:1;margin:34px 0 40px;border-radius:26px;padding:4px;
 background:linear-gradient(150deg,#f3dc9c,#b8893a 40%,#e9cd85 70%,#a27629);box-shadow:0 26px 50px rgba(80,50,20,.3)}}
.card{{position:relative;width:100%;height:100%;border-radius:22px;overflow:hidden;background:#fff}}
.card img{{position:relative;width:100%;height:100%;object-fit:contain}}
.bl{{position:absolute;inset:-40px;background-size:cover;background-position:center;filter:blur(30px) brightness(1.05)}}
.pill{{position:relative;padding:18px 58px;border-radius:60px;
 background:linear-gradient(180deg,#5a3418,#2d170a);color:#f6e7c8;font-family:Playfair;font-weight:600;font-size:40px;letter-spacing:1px;
 box-shadow:0 10px 24px rgba(0,0,0,.25),inset 0 0 0 2px #c9a04a;white-space:nowrap}}
</style></head><body>
<div class="light"></div><div class="glow"></div>
<div class="title"><h1>{p['post_title']}</h1><div class="rule">{LOTUS}</div><h2>{p['post_sub']}</h2></div>
<div class="frame"><div class="card"><div class="bl" style="background-image:url({u})"></div><img src="{u}"></div></div>
<div class="pill">astroaarambh.store</div>
</body></html>"""

def shoot(html, out, w, h):
    with sync_playwright() as pw:
        b = pw.chromium.launch(executable_path=CHROME)
        pg = b.new_page(viewport={"width": w, "height": h})
        pg.set_content(html, wait_until="networkidle")
        pg.evaluate("document.fonts.ready.then(()=>1)")
        pg.wait_for_timeout(500)
        pg.screenshot(path=out, type="jpeg", quality=92)
        b.close()

if __name__ == "__main__":
    spec = json.loads(pathlib.Path(sys.argv[1]).read_text())
    outdir = pathlib.Path(sys.argv[2]); outdir.mkdir(parents=True, exist_ok=True)
    for i, p in enumerate(spec):
        slug = p["slug"]
        shoot(story_html(p, p.get("theme", list(THEMES)[i % 5])), str(outdir / f"story_{slug}.jpg"), 1080, 1920)
        if p.get("post_title"):
            shoot(post_html(p), str(outdir / f"post_{slug}.jpg"), 1080, 1350)
        print("rendered", slug)
