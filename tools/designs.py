"""Design library for @astroaarambhstore Stories (1080x1920) and Posts (1080x1350).

Each layout is a different composition (not just a colour swap), and each has
several palettes. nightly.py rotates layouts and palettes so the feed keeps
changing. The product photo is always shown whole: its box has the photo's own
aspect ratio and the image is drawn with background-size: contain.
Text-heavy areas stay out of the top ~210px and bottom ~230px of Stories,
where Instagram draws its own UI.
"""
import base64, pathlib, re

ROOT = pathlib.Path(__file__).resolve().parent.parent
FONT_DIR = ROOT / "fonts"

FACES = [
    ("Cinzel", "cinzel-latin-700-normal", 700, "normal"),
    ("Playfair", "playfair-display-latin-700-normal", 700, "normal"),
    ("Mont", "montserrat-latin-500-normal", 500, "normal"),
    ("Corm", "cormorant-garamond-latin-500-normal", 500, "normal"),
    ("Corm", "cormorant-garamond-latin-700-normal", 700, "normal"),
    ("Corm", "cormorant-garamond-latin-500-italic", 500, "italic"),
    ("Marcellus", "marcellus-latin-400-normal", 400, "normal"),
    ("Italiana", "italiana-latin-400-normal", 400, "normal"),
    ("Bebas", "bebas-neue-latin-400-normal", 400, "normal"),
    ("Poppins", "poppins-latin-300-normal", 300, "normal"),
    ("Poppins", "poppins-latin-400-normal", 400, "normal"),
    ("Poppins", "poppins-latin-500-normal", 500, "normal"),
    ("Poppins", "poppins-latin-600-normal", 600, "normal"),
    ("Poppins", "poppins-latin-700-normal", 700, "normal"),
    ("Caveat", "caveat-latin-700-normal", 700, "normal"),
    ("DMSerif", "dm-serif-display-latin-400-normal", 400, "normal"),
    ("DMSerif", "dm-serif-display-latin-400-italic", 400, "italic"),
    ("Josefin", "josefin-sans-latin-300-normal", 300, "normal"),
    ("Josefin", "josefin-sans-latin-400-normal", 400, "normal"),
    ("Josefin", "josefin-sans-latin-600-normal", 600, "normal"),
    ("Tiro", "tiro-devanagari-hindi-devanagari-400-normal", 400, "normal"),
    ("Abril", "abril-fatface-latin-400-normal", 400, "normal"),
]
_FONT_CSS = None
def font_css():
    global _FONT_CSS
    if _FONT_CSS is None:
        _FONT_CSS = "".join(
            "@font-face{font-family:'%s';font-weight:%d;font-style:%s;src:url(data:font/woff2;base64,%s)}"
            % (fam, w, st, base64.b64encode((FONT_DIR / f"{file}.woff2").read_bytes()).decode())
            for fam, file, w, st in FACES)
    return _FONT_CSS

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
    return ('<svg viewBox="0 0 40 40" fill="none" stroke="currentColor" stroke-width="2.4" '
            f'stroke-linecap="round" stroke-linejoin="round">{ICONS.get(k, ICONS["star"])}</svg>')
CHECK = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" '
         'stroke-linecap="round" stroke-linejoin="round"><path d="M5 12.5l4.5 4.5L19 7"/></svg>')

BASE_CSS = """*{margin:0;padding:0;box-sizing:border-box}
:root{--img:url('{{img}}')}
body{width:{{W}}px;height:{{H}}px;overflow:hidden;position:relative;-webkit-font-smoothing:antialiased}
.ph{position:relative;overflow:hidden;width:{{ph_w}}px;height:{{ph_h}}px;flex:none}
.ph .im{position:absolute;inset:0;background:var(--img) center/contain no-repeat}
s{text-decoration-thickness:3px}
"""
FIT_JS = """<script>document.fonts.ready.then(function(){
document.querySelectorAll('[data-fit]').forEach(function(el){
 var f=parseFloat(getComputedStyle(el).fontSize),min=+el.dataset.fit,mh=+(el.dataset.maxh||1e9);
 while((el.offsetHeight>mh||el.scrollWidth>el.clientWidth+1)&&f>min){f-=2;el.style.fontSize=f+'px'}});
document.body.dataset.ready=1})</script>"""

def fit_box(aspect, w, maxh):
    h = w / aspect
    if h > maxh:
        h, w = maxh, maxh * aspect
    return round(w), round(h)

# ---------------------------------------------------------------------------
# STORY LAYOUTS  (1080 x 1920)
# ---------------------------------------------------------------------------
STORY = {}

STORY["editorial"] = dict(box=(1080, 1060), palettes=[
  dict(bg="#f3ede2", fg="#1f2a22", accent="#2f5d46", chipfg="#f3ede2"),
  dict(bg="#dfe5d6", fg="#26302a", accent="#8a5a2b", chipfg="#f6f1e6"),
  dict(bg="#f2dcd3", fg="#3d1a1d", accent="#8e2c3a", chipfg="#fbeee9"),
], html=r"""<style>
body{background:{{bg}};color:{{fg}};font-family:Josefin;display:flex;flex-direction:column}
.panel{flex:1;padding:56px 90px 240px;display:flex;flex-direction:column;justify-content:center;gap:26px}
.eb{font-weight:600;font-size:26px;letter-spacing:8px;color:{{accent}}}
h1{font-family:DMSerif;font-weight:400;font-size:112px;line-height:1;width:900px}
.sub{font-family:Corm;font-style:italic;font-weight:500;font-size:50px;opacity:.85}
.pr{display:flex;align-items:center;gap:28px;margin-top:6px}
.now{font-family:DMSerif;font-size:110px;line-height:1}
.was{font-size:36px;opacity:.6}
.chip{background:{{accent}};color:{{chipfg}};font-weight:600;font-size:30px;padding:14px 26px 10px;border-radius:40px}
.ft{border-top:2px solid {{fg}}33;padding-top:24px;font-size:30px;letter-spacing:3px;display:flex;justify-content:space-between}
</style>
<div class="ph"><i class="im"></i></div>
<div class="panel">
 <div class="eb">TOP PICK &nbsp;&#183;&nbsp; ASTRO AARAMBH</div>
 <h1 data-fit="64" data-maxh="230">{{headline}}</h1>
 <div class="sub">{{sub_lc}}</div>
 <div class="pr"><span class="now">&#8377;{{price}}</span><span class="was">MRP <s>&#8377;{{mrp}}</s></span><span class="chip">{{off}}% OFF</span></div>
 <div class="ft"><span>Shop at astroaarambh.store</span><span>&#8594;</span></div>
</div>""")

STORY["polaroid"] = dict(box=(760, 820), palettes=[
  dict(bg="#c9a77c", fg="#3b2a1a", accent="#a3281f"),
  dict(bg="#cdd9e2", fg="#22313d", accent="#1f4f7a"),
  dict(bg="#e6cbc0", fg="#4a2423", accent="#7a2e3b"),
], html=r"""<style>
body{font-family:Josefin;color:{{fg}};display:flex;flex-direction:column;align-items:center;justify-content:space-between;padding:215px 90px 250px;
 background:radial-gradient(ellipse at 50% 40%,transparent 40%,rgba(0,0,0,.18)),
 repeating-linear-gradient(83deg,rgba(255,255,255,.05) 0 2px,transparent 2px 7px),
 repeating-linear-gradient(-12deg,rgba(0,0,0,.035) 0 1px,transparent 1px 5px),{{bg}}}
.eb{font-family:Caveat;font-weight:700;font-size:70px;transform:rotate(-2deg)}
.pol{position:relative;background:#fffdf8;padding:30px 30px 34px;transform:rotate(-3deg);box-shadow:0 30px 60px rgba(0,0,0,.28),0 2px 6px rgba(0,0,0,.15)}
.cap{font-family:Caveat;font-weight:700;font-size:72px;line-height:1.05;color:#2b2b2b;text-align:left;width:{{ph_w}}px;padding-right:230px;margin-top:22px;min-height:150px}
.tape{position:absolute;width:210px;height:58px;background:rgba(255,248,220,.72);box-shadow:0 2px 4px rgba(0,0,0,.08)}
.t1{top:-26px;left:-50px;transform:rotate(-32deg)} .t2{top:-26px;right:-50px;transform:rotate(30deg)}
.stamp{position:absolute;right:-70px;bottom:-90px;width:290px;height:290px;border-radius:50%;background:{{accent}};color:#fff;
 transform:rotate(12deg);display:grid;place-items:center;text-align:center;box-shadow:0 14px 30px rgba(0,0,0,.3)}
.stamp:before{content:"";position:absolute;inset:14px;border:3px dashed rgba(255,255,255,.7);border-radius:50%}
.stamp b{display:block;font-family:Abril;font-weight:400;font-size:84px;line-height:1}
.stamp span{font-size:26px;letter-spacing:2px}
.list{align-self:flex-start;font-family:Caveat;font-weight:700;font-size:54px;line-height:1.3}
.list i{font-style:normal;color:{{accent}}}
.ft{font-weight:600;font-size:28px;letter-spacing:7px}
</style>
<div class="eb">today's lucky pick &#10022;</div>
<div class="pol"><i class="tape t1"></i><i class="tape t2"></i>
 <div class="ph"><i class="im"></i></div>
 <div class="cap" data-fit="44" data-maxh="170">{{headline}}</div>
 <div class="stamp"><div><span>NOW</span><b>&#8377;{{price}}</b><span>MRP <s>&#8377;{{mrp}}</s></span></div></div>
</div>
<div class="list"><i>&#10003;</i> {{b1}}<br><i>&#10003;</i> {{b2}}<br><i>&#10003;</i> {{b3}}</div>
<div class="ft">SHOP NOW &#183; LINK IN BIO</div>""")

STORY["arch"] = dict(box=(640, 600), palettes=[
  dict(bg1="#f6a641", bg2="#c4442a", fg="#fff7ea", gold="#ffe1a1", deep="#6f1b10"),
  dict(bg1="#13636a", bg2="#062a2f", fg="#f5ead2", gold="#e4c171", deep="#031a1d"),
  dict(bg1="#c25b6e", bg2="#5e1a2c", fg="#fff0ec", gold="#f6cf9a", deep="#3a0d1a"),
], html=r"""<style>
body{background:linear-gradient(170deg,{{bg1}},{{bg2}});color:{{fg}};font-family:Marcellus;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:34px;padding:215px 80px 245px}
.md{position:absolute;left:50%;top:50%;width:1500px;height:1500px;margin:-820px 0 0 -750px;border-radius:50%;opacity:.16;
 background:repeating-conic-gradient({{gold}} 0 1.2deg,transparent 1.2deg 10deg);-webkit-mask-image:radial-gradient(circle,transparent 26%,#000 27%,#000 50%,transparent 51%,transparent 56%,#000 57%,transparent 70%)}
.dev{font-family:Tiro;font-size:44px;color:{{gold}};letter-spacing:4px}
.brand{font-size:28px;letter-spacing:12px;margin-top:-18px}
.arch{position:relative;width:{{arch_w}}px;height:{{arch_h}}px;border-radius:{{arch_r}}px {{arch_r}}px 18px 18px;overflow:hidden;
 box-shadow:0 0 0 6px {{gold}},0 0 0 16px rgba(255,255,255,.12),0 40px 80px rgba(0,0,0,.45)}
.arch .bl{position:absolute;inset:-40px;background:var(--img) center/cover;filter:blur(26px) brightness(.95)}
.arch .ph{position:absolute;left:0;bottom:0}
h1{font-weight:400;font-size:84px;line-height:1.05;text-align:center;letter-spacing:2px;width:920px}
.sub{font-family:Corm;font-style:italic;font-size:44px;margin-top:-18px;color:{{gold}}}
.pill{display:flex;align-items:baseline;gap:22px;border:3px solid {{gold}};border-radius:80px;padding:12px 50px 16px;background:{{deep}}66}
.pill b{font-weight:400;font-size:76px}
.pill span{font-family:Josefin;font-size:30px;opacity:.8}
</style>
<i class="md"></i>
<div class="dev">&#2405; &#2358;&#2369;&#2349; &#2354;&#2366;&#2349; &#2405;</div>
<div class="brand">ASTRO AARAMBH</div>
<div class="arch"><i class="bl"></i><div class="ph"><i class="im"></i></div></div>
<h1 data-fit="48" data-maxh="190">{{headline_uc}}</h1>
<div class="sub">{{sub_lc}}</div>
<div class="pill"><b>&#8377;{{price}}</b><span>MRP <s>&#8377;{{mrp}}</s> &#183; {{off}}% off</span></div>""")

STORY["boldsale"] = dict(box=(720, 640), palettes=[
  dict(c1="#ff6b4a", c2="#14213d", t1="#14213d", t2="#ffd166"),
  dict(c1="#f4b400", c2="#141414", t1="#141414", t2="#f4b400"),
  dict(c1="#2ec4b6", c2="#0b2b33", t1="#0b2b33", t2="#cbf3f0"),
], html=r"""<style>
body{background:linear-gradient(180deg,{{c1}} 0 47%,{{c2}} 47%);font-family:Bebas;display:flex;flex-direction:column;align-items:center;justify-content:space-between;padding:200px 70px 240px}
.big{display:flex;align-items:center;color:{{t1}};line-height:.8;height:400px}
.big b{font-weight:400;font-size:460px;letter-spacing:-6px}
.big span{font-size:150px;writing-mode:vertical-rl;transform:rotate(180deg);margin-left:16px}
.card{background:#fff;padding:16px;box-shadow:0 30px 70px rgba(0,0,0,.4);transform:rotate(2deg)}
h1{font-weight:400;font-size:132px;line-height:.92;color:{{t2}};text-align:center;width:940px;letter-spacing:1px}
.pr{display:flex;align-items:baseline;gap:30px;color:#fff}
.pr b{font-weight:400;font-size:120px;color:{{t2}}}
.pr span{font-family:Josefin;font-size:38px;opacity:.75}
.ft{font-family:Josefin;font-weight:600;font-size:28px;letter-spacing:8px;color:#fff;opacity:.85}
</style>
<div class="big"><b>{{off}}%</b><span>OFF</span></div>
<div class="card"><div class="ph"><i class="im"></i></div></div>
<h1 data-fit="70" data-maxh="250">{{headline}}</h1>
<div class="pr"><b>NOW &#8377;{{price}}</b><span>MRP <s>&#8377;{{mrp}}</s></span></div>
<div class="ft">LINK IN BIO &#8594;</div>""")

STORY["minimal"] = dict(box=(840, 820), palettes=[
  dict(bg="#f4f1ec", fg="#2b2b2b", line="#2b2b2b33", acc="#9a7b4f"),
  dict(bg="#121212", fg="#ece6da", line="#ece6da33", acc="#c8a96a"),
  dict(bg="#e3ded2", fg="#3a4436", line="#3a443633", acc="#7a5c3a"),
], html=r"""<style>
body{background:{{bg}};color:{{fg}};font-family:Josefin;font-weight:300;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:46px;padding:230px 110px 260px}
body:before{content:"";position:absolute;inset:56px;border:1.5px solid {{line}}}
.brand{font-family:Italiana;font-size:34px;letter-spacing:14px}
.rule{width:80px;height:1.5px;background:{{acc}}}
.ph{box-shadow:0 30px 60px rgba(0,0,0,.18)}
h1{font-family:Italiana;font-weight:400;font-size:100px;line-height:1.02;text-align:center;width:860px}
.sub{font-size:28px;letter-spacing:9px;text-transform:uppercase;margin-top:-22px;color:{{acc}}}
.pr{font-size:64px;letter-spacing:2px}
.pr small{display:block;text-align:center;font-size:26px;letter-spacing:4px;opacity:.6;margin-top:8px}
</style>
<div class="brand">ASTRO AARAMBH</div><div class="rule"></div>
<div class="ph"><i class="im"></i></div>
<h1 data-fit="56" data-maxh="215">{{headline}}</h1>
<div class="sub">{{sub_or_ribbon}}</div>
<div class="pr">&#8377; {{price}}<small>MRP <s>&#8377;{{mrp}}</s> &#183; {{off}}% OFF</small></div>""")

STORY["cosmic"] = dict(box=(780, 700), palettes=[
  dict(bg1="#1b2363", bg2="#03050f", gold="#e9c46a", fg="#eef0ff"),
  dict(bg1="#44175c", bg2="#0c0412", gold="#f1c27d", fg="#fbefff"),
  dict(bg1="#0b4d55", bg2="#011316", gold="#e7d39a", fg="#eafbf7"),
], html=r"""<style>
body{color:{{fg}};font-family:Josefin;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:36px;padding:210px 70px 240px;
 background:radial-gradient(circle,rgba(255,255,255,.9) 1.2px,transparent 1.8px) 0 0/137px 151px,
 radial-gradient(circle,rgba(255,255,255,.6) 1px,transparent 1.5px) 40px 70px/89px 97px,
 radial-gradient(ellipse at 50% 35%,{{bg1}},{{bg2}} 75%)}
.wheel{position:absolute;left:50%;top:50%;width:1000px;height:1000px;margin:-560px 0 0 -500px;border-radius:50%;opacity:.35;
 border:2px solid {{gold}};box-shadow:inset 0 0 0 70px transparent,inset 0 0 0 72px {{gold}};
 background:repeating-conic-gradient(from 15deg,{{gold}} 0 .35deg,transparent .35deg 30deg);
 -webkit-mask-image:radial-gradient(circle,transparent 60%,#000 61%)}
.eb{font-family:Corm;font-style:italic;font-weight:500;font-size:52px;color:{{gold}}}
h1{font-family:Corm;font-weight:700;font-size:96px;line-height:1;text-align:center;letter-spacing:3px;text-transform:uppercase;width:940px}
.ph{border-radius:28px;box-shadow:0 0 0 3px {{gold}},0 0 80px {{gold}}55,0 30px 60px rgba(0,0,0,.6)}
.pills{display:flex;gap:16px;flex-wrap:wrap;justify-content:center;width:960px}
.pills span{border:2px solid {{gold}}99;border-radius:40px;padding:12px 24px 8px;font-size:27px}
.pills span:before{content:"\2726  ";color:{{gold}}}
.pr{display:flex;align-items:baseline;gap:24px}
.pr b{font-family:Corm;font-size:112px;color:{{gold}}}
.pr span{font-size:32px;opacity:.75}
</style>
<i class="wheel"></i>
<div class="eb">&#10022; your lucky charm &#10022;</div>
<h1 data-fit="54" data-maxh="200">{{headline}}</h1>
<div class="ph"><i class="im"></i></div>
<div class="pills"><span>{{b1}}</span><span>{{b2}}</span><span>{{b3}}</span></div>
<div class="pr"><b>&#8377;{{price}}</b><span>MRP <s>&#8377;{{mrp}}</s> &#183; {{off}}% off</span></div>""")

STORY["magazine"] = dict(box=(1080, 880), palettes=[
  dict(c1="#c1121f", c2="#ffffff", rest="#fdf0d5", fg="#1d1d1d", badge="#ffd60a", bfg="#1d1d1d"),
  dict(c1="#141414", c2="#ffd60a", rest="#f5f0e6", fg="#141414", badge="#ffd60a", bfg="#141414"),
  dict(c1="#1d3557", c2="#f1faee", rest="#f1faee", fg="#1d3557", badge="#e63946", bfg="#ffffff"),
], html=r"""<style>
body{background:{{rest}};color:{{fg}};font-family:Josefin;display:flex;flex-direction:column}
.mast{background:{{c1}};color:{{c2}};padding:205px 50px 30px;text-align:center}
.mast h2{font-family:Abril;font-weight:400;font-size:132px;line-height:1;white-space:nowrap;width:980px}
.mast div{font-weight:600;font-size:25px;letter-spacing:7px;margin-top:14px;display:flex;justify-content:space-between}
.mid{position:relative;display:flex;justify-content:center;background:{{c1}}}
.badge{position:absolute;right:46px;top:36px;width:250px;height:250px;border-radius:50%;background:{{badge}};color:{{bfg}};display:grid;place-items:center;text-align:center;
 box-shadow:0 12px 30px rgba(0,0,0,.35);transform:rotate(10deg);z-index:2}
.badge b{display:block;font-family:Abril;font-weight:400;font-size:68px;line-height:1}
.badge span{font-weight:600;font-size:26px;letter-spacing:2px}
.rest{position:relative;flex:1;padding:44px 70px 240px;display:flex;flex-direction:column;justify-content:center;gap:22px}
h1{font-family:Abril;font-weight:400;font-size:92px;line-height:1.02;width:940px}
.rest h1{width:680px}
.lines{width:940px;font-weight:600;font-size:27px;letter-spacing:2px;text-transform:uppercase}
.lines i{font-style:normal;color:{{c1}};margin:0 10px}
.ft{font-size:28px;letter-spacing:6px;font-weight:600}
</style>
<div class="mast"><h2 data-fit="60">ASTRO AARAMBH</h2><div><span>TOP PICKS EDITION</span><span>{{month}}</span></div></div>
<div class="mid"><div class="ph"><i class="im"></i></div></div>
<div class="rest"><div class="badge"><div><b>&#8377;{{price}}</b><span>{{off}}% OFF</span></div></div>
 <h1 data-fit="52" data-maxh="200">{{headline}}</h1>
 <div class="lines">{{b1}}<i>&#9679;</i>{{b2}}<i>&#9679;</i>{{b3}}</div>
 <div class="ft">MRP <s>&#8377;{{mrp}}</s> &nbsp;&#183;&nbsp; SHOP NOW &#8594; LINK IN BIO</div>
</div>""")

STORY["glass"] = dict(box=(840, 700), palettes=[
  dict(m1="#e5ccff", m2="#ffd2bd", m3="#c4ecff", fg="#2a1f3d", btn="#2a1f3d"),
  dict(m1="#bff2da", m2="#cfe3ff", m3="#fff0bd", fg="#173b33", btn="#173b33"),
  dict(m1="#ffc9d6", m2="#ffe5c2", m3="#e2ccff", fg="#4a1d2c", btn="#4a1d2c"),
], html=r"""<style>
body{color:{{fg}};font-family:Poppins;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:34px;padding:215px 70px 245px;
 background:radial-gradient(circle at 15% 20%,{{m1}},transparent 45%),radial-gradient(circle at 90% 35%,{{m2}},transparent 50%),
 radial-gradient(circle at 30% 85%,{{m3}},transparent 50%),linear-gradient({{m2}},{{m1}})}
.blob{position:absolute;border-radius:50%;filter:blur(40px);opacity:.8}
.b1{width:420px;height:420px;background:{{m3}};left:-120px;top:260px} .b2{width:520px;height:520px;background:{{m1}};right:-160px;bottom:220px}
.brand{font-weight:500;font-size:28px;letter-spacing:5px;position:relative}
.card{position:relative;width:940px;padding:40px 40px 44px;border-radius:52px;background:rgba(255,255,255,.38);border:2px solid rgba(255,255,255,.7);
 backdrop-filter:blur(22px);box-shadow:0 30px 70px rgba(60,30,80,.18);display:flex;flex-direction:column;align-items:center;gap:26px}
.ph{border-radius:32px}
h1{font-weight:600;font-size:66px;line-height:1.1;text-align:center;width:840px}
.pills{display:flex;gap:14px;flex-wrap:wrap;justify-content:center}
.pills span{background:rgba(255,255,255,.7);border-radius:40px;padding:12px 24px;font-weight:500;font-size:25px}
.row{display:flex;align-items:center;justify-content:space-between;width:840px}
.row b{font-weight:700;font-size:84px;line-height:1}
.row small{font-size:28px;opacity:.6;margin-left:14px}
.btn{background:{{btn}};color:#fff;border-radius:50px;padding:20px 36px;font-weight:600;font-size:28px}
</style>
<i class="blob b1"></i><i class="blob b2"></i>
<div class="brand">astroaarambh.store</div>
<div class="card">
 <div class="ph"><i class="im"></i></div>
 <h1 data-fit="40" data-maxh="160">{{headline}}</h1>
 <div class="pills"><span>{{b1}}</span><span>{{b2}}</span><span>{{b3}}</span></div>
 <div class="row"><div><b>&#8377;{{price}}</b><small><s>&#8377;{{mrp}}</s></small></div><div class="btn">Shop now &#8594;</div></div>
</div>""")

STORY["checklist"] = dict(box=(900, 640), palettes=[
  dict(bg="#1e1e1e", fg="#f3eee3", acc="#d4af37", afg="#1e1e1e"),
  dict(bg="#163a2e", fg="#f4ecd8", acc="#e9d8a6", afg="#163a2e"),
  dict(bg="#4a1020", fg="#fbeee6", acc="#f2c57c", afg="#4a1020"),
], html=r"""<style>
body{background:radial-gradient(ellipse at 50% 0%,rgba(255,255,255,.08),transparent 60%),{{bg}};color:{{fg}};font-family:Poppins;
 display:flex;flex-direction:column;justify-content:center;gap:34px;padding:215px 90px 245px}
.eb{font-family:Josefin;font-weight:600;font-size:28px;letter-spacing:9px;color:{{acc}}}
h1{font-family:Playfair;font-weight:700;font-size:86px;line-height:1.05;width:900px;margin-top:-14px}
.ph{border-radius:26px}
ul{list-style:none;display:flex;flex-direction:column;gap:22px}
li{display:flex;align-items:center;gap:26px;font-weight:500;font-size:42px}
li i{width:68px;height:68px;border-radius:50%;background:{{acc}};color:{{afg}};display:grid;place-items:center;flex:none}
li i svg{width:38px}
.bar{display:flex;align-items:center;justify-content:space-between;background:{{acc}};color:{{afg}};border-radius:22px;padding:20px 36px}
.bar b{font-family:Playfair;font-size:84px;line-height:1}
.bar span{font-weight:600;font-size:28px;text-align:right;line-height:1.35}
</style>
<div class="eb">WHY YOU'LL LOVE IT</div>
<h1 data-fit="50" data-maxh="190">{{headline}}</h1>
<div class="ph"><i class="im"></i></div>
<ul><li><i>{{check}}</i>{{b1}}</li><li><i>{{check}}</i>{{b2}}</li><li><i>{{check}}</i>{{b3}}</li></ul>
<div class="bar"><b>&#8377;{{price}}</b><span>MRP <s>&#8377;{{mrp}}</s><br>{{off}}% OFF &#183; LINK IN BIO</span></div>""")

# ---------------------------------------------------------------------------
# POST LAYOUTS  (1080 x 1350)
# ---------------------------------------------------------------------------
POST = {}

POST["band"] = dict(box=(1080, 940), palettes=[
  dict(bg="#1f3b2d", fg="#f3ead7", acc="#d9b26a", afg="#1f3b2d"),
  dict(bg="#f3ede2", fg="#2a1c10", acc="#8e2c3a", afg="#f3ede2"),
  dict(bg="#14213d", fg="#f6efe2", acc="#e9c46a", afg="#14213d"),
], html=r"""<style>
body{background:{{bg}};color:{{fg}};font-family:Josefin;display:flex;flex-direction:column}
.mid{display:flex;justify-content:center;background:{{bg}}}
.band{flex:1;display:flex;align-items:center;justify-content:space-between;gap:40px;padding:30px 80px}
.l{min-width:0;flex:1}
.eb{font-weight:600;font-size:22px;letter-spacing:7px;color:{{acc}}}
h1{font-family:DMSerif;font-weight:400;font-size:76px;line-height:1.02;margin-top:10px}
.sub{font-family:Corm;font-style:italic;font-size:38px;opacity:.85;margin-top:6px}
.r{text-align:right;flex:none}
.r b{font-family:DMSerif;font-weight:400;font-size:92px;line-height:1;display:block}
.r span{display:inline-block;margin-top:10px;background:{{acc}};color:{{afg}};font-weight:600;font-size:24px;padding:10px 20px 6px;border-radius:30px}
</style>
<div class="mid"><div class="ph"><i class="im"></i></div></div>
<div class="band"><div class="l"><div class="eb">ASTRO AARAMBH</div><h1 data-fit="42" data-maxh="165">{{post_title}}</h1><div class="sub">{{post_sub}}</div></div>
<div class="r"><b>&#8377;{{price}}</b><span>{{off}}% OFF</span></div></div>""")

POST["gallery"] = dict(box=(620, 640), palettes=[
  dict(wall="#8fa58a", fg="#1f2a1d", f1="#e7c873", f2="#9b7428"),
  dict(wall="#1f3a5f", fg="#f2ead8", f1="#e7c873", f2="#9b7428"),
  dict(wall="#b9583b", fg="#2a1208", f1="#5a3a22", f2="#2c1a0e"),
], html=r"""<style>
body{color:{{fg}};font-family:Josefin;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:44px;padding:70px 80px;
 background:radial-gradient(ellipse 60% 45% at 50% 18%,rgba(255,255,255,.28),transparent 70%),repeating-linear-gradient(90deg,rgba(0,0,0,.025) 0 2px,transparent 2px 9px),{{wall}}}
.brand{position:absolute;top:56px;left:80px;font-weight:600;font-size:22px;letter-spacing:7px}
.frame{padding:30px;background:linear-gradient(135deg,{{f1}},{{f2}} 40%,{{f1}} 70%,{{f2}});box-shadow:0 30px 60px rgba(0,0,0,.4)}
.mat{padding:46px;background:#fbf8f2;box-shadow:inset 0 2px 8px rgba(0,0,0,.25)}
.label{align-self:flex-end;background:#fbf8f2;color:#2a2018;padding:22px 30px;width:470px;box-shadow:0 8px 18px rgba(0,0,0,.2);margin-top:-6px}
.label h1{font-family:Corm;font-weight:700;font-size:38px;line-height:1.1}
.label em{font-family:Corm;font-style:italic;font-size:28px;display:block;margin-top:2px}
.label div{border-top:1px solid #2a201833;margin-top:12px;padding-top:10px;font-size:24px;letter-spacing:1px}
</style>
<div class="brand">ASTRO AARAMBH</div>
<div class="frame"><div class="mat"><div class="ph"><i class="im"></i></div></div></div>
<div class="label"><h1 data-fit="26" data-maxh="90">{{post_title}}</h1><em>{{post_sub}}</em><div>&#8377;{{price}} &nbsp;&#183;&nbsp; MRP <s>&#8377;{{mrp}}</s></div></div>""")

POST["typo"] = dict(box=(640, 600), palettes=[
  dict(c1="#0f5132", c2="#f8e9c4"),
  dict(c1="#5a1029", c2="#ffd8a8"),
  dict(c1="#1b3b8f", c2="#ffe066"),
], html=r"""<style>
body{background:{{c1}};color:{{c2}};font-family:Bebas;display:flex;flex-direction:column;align-items:center;justify-content:flex-end;gap:26px;padding:60px 70px 70px}
.words{position:absolute;top:40px;left:0;right:0;text-align:center;font-size:330px;line-height:.82;color:transparent;-webkit-text-stroke:3px {{c2}};opacity:.55;white-space:nowrap}
.card{position:relative;background:#fff;padding:14px;box-shadow:0 30px 60px rgba(0,0,0,.45)}
h1{font-weight:400;font-size:96px;line-height:.95;text-align:center;width:940px;position:relative}
.pr{display:flex;align-items:baseline;gap:26px;position:relative}
.pr b{font-weight:400;font-size:84px}
.pr span{font-family:Josefin;font-size:32px;opacity:.8}
</style>
<div class="words">{{w1}}<br>{{w2}}</div>
<div class="card"><div class="ph"><i class="im"></i></div></div>
<h1 data-fit="54" data-maxh="190">{{post_title}}</h1>
<div class="pr"><b>&#8377;{{price}}</b><span>MRP <s>&#8377;{{mrp}}</s> &#183; {{off}}% OFF</span></div>""")

POST["arch"] = dict(box=(560, 520), palettes=STORY["arch"]["palettes"], html=r"""<style>
body{background:linear-gradient(170deg,{{bg1}},{{bg2}});color:{{fg}};font-family:Marcellus;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:26px;padding:50px 70px}
.md{position:absolute;left:50%;top:50%;width:1300px;height:1300px;margin:-700px 0 0 -650px;border-radius:50%;opacity:.15;
 background:repeating-conic-gradient({{gold}} 0 1.2deg,transparent 1.2deg 10deg);-webkit-mask-image:radial-gradient(circle,transparent 30%,#000 31%,#000 50%,transparent 51%)}
.dev{font-family:Tiro;font-size:34px;color:{{gold}};letter-spacing:4px}
.arch{position:relative;width:{{arch_w}}px;height:{{arch_h}}px;border-radius:{{arch_r}}px {{arch_r}}px 16px 16px;overflow:hidden;
 box-shadow:0 0 0 5px {{gold}},0 0 0 14px rgba(255,255,255,.12),0 30px 60px rgba(0,0,0,.4)}
.arch .bl{position:absolute;inset:-40px;background:var(--img) center/cover;filter:blur(26px) brightness(.95)}
.arch .ph{position:absolute;left:0;bottom:0}
h1{font-weight:400;font-size:58px;line-height:1.05;text-align:center;letter-spacing:2px;width:940px}
.pill{display:flex;align-items:baseline;gap:18px;border:3px solid {{gold}};border-radius:60px;padding:8px 40px 12px;background:{{deep}}66}
.pill b{font-weight:400;font-size:56px}
.pill span{font-family:Josefin;font-size:26px;opacity:.85}
</style>
<i class="md"></i>
<div class="dev">&#2405; &#2358;&#2369;&#2349; &#2354;&#2366;&#2349; &#2405;</div>
<div class="arch"><i class="bl"></i><div class="ph"><i class="im"></i></div></div>
<h1 data-fit="36" data-maxh="130">{{post_title_uc}}</h1>
<div class="pill"><b>&#8377;{{price}}</b><span>MRP <s>&#8377;{{mrp}}</s> &#183; {{off}}% off</span></div>""")

POST["minimal"] = dict(box=(860, 900), palettes=STORY["minimal"]["palettes"], html=r"""<style>
body{background:{{bg}};color:{{fg}};font-family:Josefin;font-weight:300;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:34px;padding:110px 80px 70px}
.top{position:absolute;top:50px;left:80px;right:80px;display:flex;justify-content:space-between;font-size:24px;letter-spacing:6px}
.top b{font-family:Italiana;font-weight:400;font-size:28px;letter-spacing:10px}
.ph{box-shadow:0 26px 50px rgba(0,0,0,.16)}
h1{font-family:Italiana;font-weight:400;font-size:70px;line-height:1.05;text-align:center;width:940px}
.sub{font-size:24px;letter-spacing:8px;text-transform:uppercase;color:{{acc}};margin-top:-18px}
</style>
<div class="top"><b>ASTRO AARAMBH</b><span>&#8377;{{price}} &#183; <s>&#8377;{{mrp}}</s></span></div>
<div class="ph"><i class="im"></i></div>
<h1 data-fit="40" data-maxh="150">{{post_title}}</h1>
<div class="sub">{{post_sub}}</div>""")

POST["split"] = dict(box=(600, 1150), palettes=[
  dict(c1="#4b5a2a", c2="#efe8d6", fg="#f6f0dc", acc="#e3c77a"),
  dict(c1="#6e1a2c", c2="#f5e1dc", fg="#fdeee9", acc="#f2c57c"),
  dict(c1="#1d2b4a", c2="#ece3d2", fg="#f3ecdf", acc="#e0b968"),
], html=r"""<style>
body{display:flex;font-family:Josefin;color:{{fg}}}
.l{width:440px;flex:none;background:{{c1}};padding:70px 46px 64px;display:flex;flex-direction:column;gap:26px}
.brand{font-weight:600;font-size:20px;letter-spacing:7px;color:{{acc}}}
h1{font-family:DMSerif;font-weight:400;font-size:72px;line-height:1.02;margin-top:20px}
.sub{font-family:Corm;font-style:italic;font-size:34px;color:{{acc}}}
ul{list-style:none;display:flex;flex-direction:column;gap:18px;margin-top:10px}
li{display:flex;align-items:center;gap:16px;font-size:27px}
li i{width:48px;height:48px;flex:none;color:{{acc}}}
.pr{margin-top:auto}
.pr b{font-family:DMSerif;font-weight:400;font-size:96px;line-height:1;display:block}
.pr span{font-size:26px;opacity:.8}
.r{flex:1;background:{{c2}};display:grid;place-items:center}
</style>
<div class="l"><div class="brand">ASTRO AARAMBH</div><h1 data-fit="40" data-maxh="300">{{post_title}}</h1><div class="sub">{{post_sub}}</div>
<ul><li><i>{{i1}}</i>{{b1}}</li><li><i>{{i2}}</i>{{b2}}</li><li><i>{{i3}}</i>{{b3}}</li></ul>
<div class="pr"><b>&#8377;{{price}}</b><span>MRP <s>&#8377;{{mrp}}</s> &#183; {{off}}% OFF</span></div></div>
<div class="r"><div class="ph"><i class="im"></i></div></div>""")

POST["cosmic"] = dict(box=(700, 640), palettes=STORY["cosmic"]["palettes"], html=r"""<style>
body{color:{{fg}};font-family:Josefin;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:28px;padding:60px 70px;
 background:radial-gradient(circle,rgba(255,255,255,.9) 1.2px,transparent 1.8px) 0 0/137px 151px,
 radial-gradient(circle,rgba(255,255,255,.6) 1px,transparent 1.5px) 40px 70px/89px 97px,
 radial-gradient(ellipse at 50% 40%,{{bg1}},{{bg2}} 75%)}
.wheel{position:absolute;left:50%;top:50%;width:960px;height:960px;margin:-520px 0 0 -480px;border-radius:50%;opacity:.35;border:2px solid {{gold}};
 background:repeating-conic-gradient(from 15deg,{{gold}} 0 .35deg,transparent .35deg 30deg);-webkit-mask-image:radial-gradient(circle,transparent 60%,#000 61%)}
.eb{font-family:Corm;font-style:italic;font-size:40px;color:{{gold}}}
.ph{border-radius:24px;box-shadow:0 0 0 3px {{gold}},0 0 70px {{gold}}55,0 30px 60px rgba(0,0,0,.6)}
h1{font-family:Corm;font-weight:700;font-size:66px;line-height:1.05;text-align:center;letter-spacing:2px;text-transform:uppercase;width:940px}
.pr{display:flex;align-items:baseline;gap:20px}
.pr b{font-family:Corm;font-size:80px;color:{{gold}}}
.pr span{font-size:28px;opacity:.75}
</style>
<i class="wheel"></i>
<div class="eb">&#10022; astroaarambh.store &#10022;</div>
<div class="ph"><i class="im"></i></div>
<h1 data-fit="38" data-maxh="150">{{post_title}}</h1>
<div class="pr"><b>&#8377;{{price}}</b><span>MRP <s>&#8377;{{mrp}}</s> &#183; {{off}}% off</span></div>""")

POST["tag"] = dict(box=(860, 860), palettes=[
  dict(bg="#efe4d2", fg="#2c1d12", tag="#8e2c3a"),
  dict(bg="#dcefe6", fg="#15342a", tag="#1f5f4a"),
  dict(bg="#e7e0f3", fg="#2b1a47", tag="#4b2a7b"),
], html=r"""<style>
body{color:{{fg}};font-family:Poppins;display:flex;flex-direction:column;align-items:center;gap:36px;padding:70px 80px;
 background:repeating-linear-gradient(135deg,rgba(0,0,0,.025) 0 2px,transparent 2px 22px),{{bg}}}
.ph{border-radius:24px;box-shadow:0 20px 44px rgba(0,0,0,.18)}
.row{display:flex;align-items:center;justify-content:space-between;width:920px;flex:1;gap:30px}
.t{min-width:0;flex:1}
.t small{font-weight:600;font-size:20px;letter-spacing:6px;opacity:.7}
h1{font-family:Playfair;font-weight:700;font-size:58px;line-height:1.08;margin-top:6px}
.tag{position:relative;flex:none;width:250px;padding:34px 20px 24px 40px;background:{{tag}};color:#fff;transform:rotate(-6deg);
 clip-path:polygon(16% 0,100% 0,100% 100%,16% 100%,0 50%);box-shadow:0 10px 20px rgba(0,0,0,.25)}
.tag:before{content:"";position:absolute;left:30px;top:50%;width:18px;height:18px;margin-top:-9px;border-radius:50%;background:{{bg}}}
.tag b{display:block;font-weight:700;font-size:58px;line-height:1;margin-left:24px}
.tag span{display:block;font-size:22px;margin-left:24px;opacity:.85}
</style>
<div class="ph"><i class="im"></i></div>
<div class="row"><div class="t"><small>ASTRO AARAMBH &#183; TOP PICK</small><h1 data-fit="36" data-maxh="140">{{post_title}}</h1></div>
<div class="tag"><b>&#8377;{{price}}</b><span><s>&#8377;{{mrp}}</s> &#183; {{off}}% off</span></div></div>""")

# ---------------------------------------------------------------------------
def tokens(p, aspect, month):
    words = [w for w in re.sub(r"&\w+;", " ", p["headline"]).split() if w]
    if words and words[0].isdigit() and len(words) > 1:
        words = [words[0] + " " + words[1]] + words[2:]
    sub = p.get("sub") or ""
    b = [l for _, l in p["benefits"][:3]] + ["", "", ""]
    ic = [k for k, _ in p["benefits"][:3]] + ["star"] * 3
    return dict(
        headline=p["headline"], headline_uc=p["headline"].upper(),
        sub=sub, sub_lc=sub.lower().capitalize() if sub else p.get("post_sub", ""),
        sub_or_ribbon=sub or p.get("ribbon", ""), ribbon=p.get("ribbon", ""),
        post_title=p["post_title"], post_title_uc=p["post_title"].upper(), post_sub=p["post_sub"],
        price=f"{int(p['price']):,}", mrp=f"{int(p['mrp']):,}",
        off=round(100 - p["price"] * 100 / p["mrp"]),
        b1=b[0], b2=b[1], b3=b[2], i1=icon(ic[0]), i2=icon(ic[1]), i3=icon(ic[2]), check=CHECK,
        w1=(words[0] if words else "").upper(), w2=(words[1] if len(words) > 1 else "").upper(),
        month=month)

def build(kind, layout, pal_idx, p, img_uri, aspect, month):
    lib = STORY if kind == "story" else POST
    L = lib[layout]
    W, H = (1080, 1920) if kind == "story" else (1080, 1350)
    pw, ph = fit_box(aspect, *L["box"])
    t = dict(tokens(p, aspect, month), **L["palettes"][pal_idx % len(L["palettes"])],
             W=W, H=H, ph_w=pw, ph_h=ph, img=img_uri,
             arch_w=pw, arch_h=ph + pw // 2, arch_r=pw // 2)
    body = re.sub(r"\{\{(\w+)\}\}", lambda m: str(t[m.group(1)]), L["html"])
    css = re.sub(r"\{\{(\w+)\}\}", lambda m: str(t[m.group(1)]), BASE_CSS)
    return f"<!doctype html><html><head><meta charset='utf-8'><style>{font_css()}{css}</style></head><body>{body}{FIT_JS}</body></html>"

def shoot(page, html, out, kind):
    """img in build() must be a file:// URI (pathlib.Path.as_uri()); the page is loaded from a file
    so large photos are not squeezed through a data: URL."""
    W, H = (1080, 1920) if kind == "story" else (1080, 1350)
    page.set_viewport_size({"width": W, "height": H})
    tmp = ROOT / ".cache" / "_page.html"
    tmp.parent.mkdir(exist_ok=True)
    tmp.write_text(html, encoding="utf-8")
    page.goto(tmp.as_uri())
    page.wait_for_function("document.body.dataset.ready == '1'", timeout=30000)
    page.wait_for_timeout(250)
    page.screenshot(path=str(out), type="jpeg", quality=92)
