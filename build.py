import os, json, html, datetime, secrets, textwrap
D="https://tinydesktrend.com"; OUT="public"; TODAY="2026-10-29"
BRAND="Tiny Desk Trend"
os.makedirs(OUT,exist_ok=True)
def svg(paths,cls=""):
    c=f' class="{cls}"' if cls else ""
    return f'<svg{c} viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{paths}</svg>'
I_MIC=svg('<rect x="9" y="2.5" width="6" height="11" rx="3"/><path d="M5.5 11a6.5 6.5 0 0 0 13 0M12 17.5V21.5M8.5 21.5h7"/>')
I_UP=svg('<path d="M12 15V4M7.5 8.5 12 4l4.5 4.5"/><path d="M4 15v3.5A2.5 2.5 0 0 0 6.5 21h11a2.5 2.5 0 0 0 2.5-2.5V15"/>')
I_CHECK=svg('<path d="m5 12.5 4.5 4.5L19 7.5"/>')
I_ARROW=svg('<path d="M5 12h14M13 6l6 6-6 6"/>')
I_SOUND=svg('<path d="M4 9.5h3.5L12 5.5v13l-4.5-4H4z"/><path d="M15.5 9a4 4 0 0 1 0 6M18 6.5a7.5 7.5 0 0 1 0 11"/>')
I_PAUSE=svg('<path d="M9 5.5v13M15 5.5v13"/>','i-pause')
I_PLAY=svg('<path d="M7.5 5v14l11-7z"/>','i-play')
I_X=svg('<path d="M6 6l12 12M18 6 6 18"/>')
I_STAR=svg('<path d="M12 3.5l2.4 5 5.4.6-4 3.7 1.1 5.4L12 15.5l-4.9 2.7 1.1-5.4-4-3.7 5.4-.6z"/>')
MARK=f'<span class="logo-mark" aria-hidden="true">{I_MIC}</span>'
NAV=f"""<header class="site-header"><div class="wrap hdr">
<a class="logo" href="/" aria-label="{BRAND} home">{MARK}<span>{BRAND}</span></a>
<nav class="main-nav" id="main-nav" aria-label="Main"><a href="/#create">Create</a><a href="/#pricing">Pricing</a><a href="/#how-it-works">How it works</a><a href="/guides/">Guides</a><a href="/#faq">FAQ</a></nav>
<div class="hdr-right">
 <div class="auth-out" id="hdr-out"><button type="button" class="btn ghost sm" data-auth="login">Sign in</button><button type="button" class="btn sm hide-xs" data-auth="signup">Sign up</button></div>
 <div class="auth-in" id="hdr-in" hidden><a class="credit-pill" href="/#pricing" title="Your credits"><b id="hdr-credits">0</b> credits</a>
  <div class="acct"><button type="button" class="acct-btn" id="acct-btn" aria-haspopup="true" aria-expanded="false" aria-label="Account menu"><span id="acct-initial">?</span></button>
   <div class="acct-menu" id="acct-menu" hidden><p class="acct-email" id="hdr-email"></p><a href="/#videos" data-menu="videos">My videos</a><a href="/#pricing">Buy credits</a><button type="button" id="hdr-logout">Sign out</button></div></div></div>
 <button type="button" class="burger" id="burger" aria-label="Menu" aria-controls="main-nav" aria-expanded="false"><span></span><span></span><span></span></button>
</div></div></header>
<dialog class="modal" id="auth-modal" aria-labelledby="auth-title"><form method="dialog" class="modal-x"><button aria-label="Close">{I_X}</button></form>
<h2 id="auth-title">Sign in</h2><p class="muted small" id="auth-sub">Use your email and a password. No email verification needed.</p>
<div class="tabs" role="tablist"><button type="button" role="tab" data-tab="login" class="on">Sign in</button><button type="button" role="tab" data-tab="signup">Create account</button></div>
<form id="auth-form" class="auth-form"><label>Email <input id="email" type="email" autocomplete="email" required></label>
<label>Password <span class="muted small">(8+ characters)</span> <input id="password" type="password" autocomplete="current-password" minlength="8" required></label>
<button type="submit" class="btn full" id="auth-submit">Sign in</button><p id="auth-msg" class="msg small"></p>
<p class="small muted">By continuing you agree to the <a href="/terms/">Terms</a> and <a href="/privacy/">Privacy Policy</a>.</p></form></dialog>"""
DISC=f'<p class="disc"><strong>Unofficial fan tool.</strong> {BRAND} is not affiliated with, endorsed by, or connected to NPR, NPR Music, or Tiny Desk Concerts. No NPR or Tiny Desk logos or official assets are used on this site.</p>'
FOOT=f"""<footer class="site-footer"><div class="wrap">
<div class="foot-grid"><div><a class="logo" href="/">{MARK}<span>{BRAND}</span></a><p class="small">An unofficial Tiny Desk AI photo-to-video tool for the "Outstanding" meme.</p></div>
<div><h3>Product</h3><a href="/#create">Create a video</a><a href="/#pricing">Pricing</a><a href="/#how-it-works">How it works</a><a href="/faq/">FAQ</a><a href="/about/">About</a></div>
<div><h3>Guides</h3><a href="/guides/what-is-the-tiny-desk-ai-trend/">Trend origin</a><a href="/guides/outstanding-tiny-desk-song/">The song</a><a href="/guides/outstanding-tiny-desk-ai-template/">The template</a><a href="/guides/">All guides</a></div>
<div><h3>Legal</h3><a href="/privacy/">Privacy</a><a href="/terms/">Terms</a><a href="mailto:privacy@tinydesktrend.com">Contact</a></div></div>
{DISC}<p class="small">© 2026 tinydesktrend.com</p></div></footer>"""

ORG={"@type":"Organization","@id":D+"/#org","name":BRAND,"alternateName":"Tiny Desk AI","url":D+"/","logo":D+"/logo.png","email":"privacy@tinydesktrend.com",
     "description":"Unofficial fan site and photo-to-video generator for the \"Outstanding\" Tiny Desk AI meme. Not affiliated with NPR."}
AUTHOR={"@type":"Organization","name":f"{BRAND} team","url":D+"/about/"}
PUBLISHER={"@type":"Organization","@id":D+"/#org","name":BRAND,"logo":{"@type":"ImageObject","url":D+"/logo.png"}}

pages=[]; OG_JOBS=[]
def crumbs_for(path,title):
    if path=="/": return None
    items=[("Home","/")]
    if path.startswith("/guides/") and path!="/guides/": items.append(("Guides","/guides/"))
    items.append((title,path))
    return items
def page(path,title,desc,body,ld=None,extra_head="",cls="",index=True,og=None,crumb=None):
    url=D+path
    rob="" if index else '<meta name="robots" content="noindex">'; bcls=cls or "prose"; mcls="" if cls else "wrap narrow"
    ld=list(ld or [])
    cr=crumbs_for(path,crumb or title) if index else None
    nav=""
    if cr:
        ld.append({"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[{"@type":"ListItem","position":i+1,"name":n,"item":D+p} for i,(n,p) in enumerate(cr)]})
        nav='<nav class="crumbs" aria-label="Breadcrumb">'+" / ".join(f'<a href="{p}">{html.escape(n)}</a>' if i<len(cr)-1 else f'<span aria-current="page">{html.escape(n)}</span>' for i,(n,p) in enumerate(cr))+'</nav>'
    ogimg=D+(og or "/og.png")
    lds="".join(f'<script type="application/ld+json">{json.dumps(x)}</script>' for x in ld)
    h=f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title><meta name="description" content="{html.escape(desc)}"><link rel="canonical" href="{url}">{rob}
<link rel="icon" href="/favicon.ico" sizes="any"><link rel="icon" href="/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="/style.css">
<meta property="og:type" content="{'website' if path=='/' else 'article' if path.startswith('/guides/') and path!='/guides/' else 'website'}"><meta property="og:site_name" content="{BRAND}"><meta property="og:title" content="{html.escape(title)}"><meta property="og:description" content="{html.escape(desc)}"><meta property="og:url" content="{url}"><meta property="og:image" content="{ogimg}"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{html.escape(title)}"><meta name="twitter:description" content="{html.escape(desc)}"><meta name="twitter:image" content="{ogimg}">{lds}<script type="module" src="/site.js"></script>{extra_head}</head>
<body class="{bcls}">{NAV}<main class="{mcls}">{nav}{body}</main>{FOOT}</body></html>"""
    d=OUT+path; os.makedirs(d,exist_ok=True); open(d+"index.html","w").write(h)
    if index: pages.append(path)

SRC_NPR="https://www.npr.org/2023/06/05/1179416602/charlie-wilson-tiny-desk-concert"
SRC_RS="https://www.rollingstone.com/music/music-news/charlie-wilson-gap-band-tiny-desk-1234759558/"
SRC_HF="https://huggingface.co/blog/trendrecast/how-to-make-outstanding-tiny-desk-ai-video"
SRC_WIKI="https://en.wikipedia.org/wiki/Outstanding"
SRC_WS="https://www.whosampled.com/The-Gap-Band/"
SRC_JUT="https://jutsustudio.com/video-api-pricing/seedance-2-0-mini/"
SRC_WAVE="https://wavespeed.ai/models/bytedance/seedance-2.0-mini/video-edit"
SRC_OT="https://outstandingtinydesk.com/blog/outstanding-tiny-desk-ai-trend"

g1="/guides/what-is-the-tiny-desk-ai-trend/"; g2="/guides/how-to-make-outstanding-tiny-desk-ai-video/"; g3="/guides/outstanding-tiny-desk-song/"
g4="/guides/tiny-desk-ai-video-generator/"; g5="/guides/outstanding-tiny-desk-ai-template/"; g6="/guides/outstanding-tiny-desk-meme-ideas/"; g7="/guides/outstanding-gap-band-song-facts/"

# (question, answer, optional follow-up link)
faq=[
("What is the Tiny Desk AI trend?","It is an AI parody meme: people re-cast the closing moment of Charlie Wilson's 2023 NPR Tiny Desk concert, where he sings \"Outstanding\", with new faces swapped in by an AI video model. It took off on TikTok in October 2026 after a clip put college football coaches whose teams had just lost into the band.",(g1,"Where the trend came from")),
("What do I get?","A 13-second vertical (9:16) 480p clip of the lead-singer part of the meme with your face on the lead singer, in two versions: one with the original song and one silent copy for apps that mute music.",(g2,"How our generator makes it")),
("How much does it cost?","Each video uses 100 credits. Credit packs: $9.99 for 300 credits (3 videos), $19.99 for 700 credits (7 videos) and $49.99 for 1,800 credits (18 videos). One-time payments, no subscription.",("/#pricing","See the credit packs")),
("What photo works best?","A clear, front-facing photo of one person, well lit, JPEG, PNG or WebP up to 10 MB. Your browser checks for a face before anything is uploaded.",(g6,"Photo tips for whoever is on lead")),
("Whose photo can I use?","Only your own photo or a photo of someone who has agreed to it. No minors, no impersonation, no using other people's faces without consent. You must confirm this before generating.",("/terms/","Read the terms")),
("What happens if a video fails?","If the video service fails or rejects the request, the credits for that video are returned to your account automatically.",(g4,"What to check in any generator")),
("Is the result perfect?","No. It is an AI recast, so details can differ from the original clip: the cap may disappear, shots can be re-cut, and faces vary between takes.",(g2,"Common problems")),
("What song is in the Tiny Desk AI video?","\"Outstanding\" by The Gap Band, from their 1982 album The Gap Band IV. Charlie Wilson, The Gap Band's lead singer, closed his June 2023 Tiny Desk concert with it.",(g3,"More about the song")),
("Is the Tiny Desk AI video real?","No. These are AI edits of real concert footage. Label yours as AI when you post it.",(g1,"How the meme started")),
("Is this site official?",f"No. {BRAND} is an unofficial fan tool and is not affiliated with NPR, NPR Music or Tiny Desk Concerts.",("/about/","About this site")),
]
faq_ld={"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a,_ in faq]}
web_ld={"@context":"https://schema.org","@type":"WebSite","name":BRAND,"alternateName":"Tiny Desk AI","url":D+"/","publisher":{"@id":D+"/#org"}}
org_ld={"@context":"https://schema.org",**ORG}

# Guide registry: path -> (short title, one-line summary). Drives the index, related links and llms.txt.
GUIDES=[(g1,"Where the Tiny Desk AI trend came from","From Charlie Wilson's 2023 Tiny Desk concert to the October 2026 TikTok parody, with a dated timeline."),
(g2,"How the Outstanding Tiny Desk AI video is made","The general method, and exactly what our generator does with your photo."),
(g3,"What is the song?","\"Outstanding\" by The Gap Band, and the part of it the meme uses."),
(g4,"Tiny Desk AI video generator: what to check","Why free tools are rare, what the model costs, and a checklist for any generator."),
(g5,"The Outstanding template: shots and roles","The five shots, their timings and which roles you can recast."),
(g6,"Meme meaning and casting ideas","Why the joke works, who to put on lead, photo tips and caption ideas."),
(g7,"\"Outstanding\" by The Gap Band: facts","Release date, writer, chart peaks, covers and samples.")]
GUIDES_LIST=[(u,t) for u,t,_ in GUIDES]
BYLINE=f'<p class="byline">By the <a href="/about/">{BRAND} team</a> · Updated {TODAY}</p>'
def guide_end(path):
    i=[u for u,_,_ in GUIDES].index(path)
    rel=[GUIDES[(i+k)%len(GUIDES)] for k in (1,2,3)]
    return (f'<aside class="guide-end"><div class="guide-cta"><h2>Make your own</h2><p>Upload one photo and get the 13-second lead-singer clip with you in it, with the song and a silent copy.</p>'
            f'<a class="btn" href="/#create">Put your face on lead</a></div><h2>Related guides</h2><ul class="related">'
            +"".join(f'<li><a href="{u}">{html.escape(t)}</a><span>{html.escape(s)}</span></li>' for u,t,s in rel)+'</ul></aside>')
def art(t,d,p,slug):
    return {"@context":"https://schema.org","@type":"Article","headline":t,"description":d,"datePublished":"2026-10-28","dateModified":TODAY,
            "mainEntityOfPage":D+p,"image":D+f"/og/{slug}.png","author":AUTHOR,"publisher":PUBLISHER,"inLanguage":"en"}
def guide(path,slug,t,d,body,extra_ld=None,og_sub=""):
    OG_JOBS.append((f"og/{slug}.png",t,og_sub or "Tiny Desk AI guide"))
    page(path,t,d,f"<h1>{t}</h1>{BYLINE}{body}{guide_end(path)}",[art(t,d,path,slug)]+(extra_ld or []),og=f"/og/{slug}.png",crumb=t)

CASTING=[("Your team after a loss","Where the trend started: coaches of teams that just lost, belting a song called “Outstanding”."),
("The coworker who missed the deadline","Put them front and centre for the big laugh."),
("Last place in the fantasy league","Losers sing lead. League rules."),
("The group chat’s worst week","Whoever had it gets the close-up."),
("You","Your own outstanding week, on lead.")]
MARQUEE=["Put your face on lead","One photo","13 seconds","Vertical 9:16","Song + silent copy","Credits back if it fails","Unofficial fan tool"]
def pack(key,name,price,credits,videos,pop=False):
    badge='<span class="badge">Most popular</span>' if pop else ""
    cls="pack pop" if pop else "pack"
    btn="btn full buy" if pop else "btn ghost full buy"
    feats="".join(f"<li>{I_CHECK}{t}</li>" for t in ("13 s lead-singer clip","Song + silent versions","480p, vertical 9:16"))
    return (f'<div class="{cls}">{badge}<div class="ticket"><div class="pack-face"><h3>{name}</h3><p class="price">{price}</p></div>'
            f'<div class="pack-stub"><p class="credits">{credits} credits <span>= {videos} videos</span></p><ul>{feats}</ul>'
            f'<button type="button" class="{btn}" data-pack="{key}">Buy {name}</button></div></div></div>')
HOME=f"""
<section class="hero" id="create"><div class="wrap">
 <div class="hero-head">
  <h1 class="hero-title">Put your face in the <span class="hl">“Outstanding”</span> Tiny Desk video</h1>
  <p class="lead">Upload one photo and get the 13-second lead-singer clip, recast with you. Vertical 9:16, with the song and a silent copy.</p>
  <div class="hero-facts"><span class="pill sun">13 s · 9:16 · 480p</span><span class="pill">Song + silent copy</span><span class="pill mint">Credits back if it fails</span></div>
 </div>
</div>
 <div class="stage"><div class="wrap stage-inner">
  <div class="card gen" id="account">
   <h2>Cast yourself on lead</h2>
   <label class="drop" id="drop"><input id="photo" class="vh" type="file" accept="image/jpeg,image/png,image/webp">
    <span class="preview-wrap"><img id="preview" alt="Your photo preview" hidden><span class="preview-tag">Now on lead</span></span><span class="drop-icon">{I_UP}</span>
    <span class="drop-text" id="drop-text"><b>Choose a photo</b><span class="small muted">JPEG, PNG or WebP, up to 10 MB. One clear, front-facing face.</span></span></label>
   <p id="photo-msg" class="msg small"></p>
   <a href="#sample" class="see-sample small" id="see-sample" hidden>See yourself on the sample</a>
   <label class="consent"><input id="consent" type="checkbox"> This photo is of me, or of someone who has given me permission to use it. No minors.</label>
   <p id="sold-out" class="msg error" hidden>Sold out for now. Please check back soon.</p>
   <button type="button" id="generate" class="btn big full" disabled>Generate · 100 credits</button>
   <p id="gen-hint" class="small muted center"></p>
   <p id="gen-status" class="msg"></p>
   <div id="result" hidden>
    <video id="result-video" controls playsinline></video>
    <div class="row"><a id="dl-song" class="btn" download="tiny-desk-ai-with-song.mp4" hidden>Download with song</a><a id="dl-silent" class="btn ghost" download="tiny-desk-ai-silent.mp4" hidden>Download silent</a><a id="dl-raw" class="link small" download="tiny-desk-ai-original.mp4">Original file</a></div>
   </div>
   <ul class="gen-facts"><li>1 photo</li><li>About 2 minutes</li><li>From $9.99</li><li><a href="#pricing">See pricing</a></li></ul>
   <details id="videos" class="history" hidden><summary>My videos <span class="muted small">(kept 7 days)</span></summary><ul id="history"></ul></details>
  </div>
  <figure class="sample" id="sample">
   <div class="phone">
    <video src="/media/sample.mp4" poster="/media/sample.jpg" muted playsinline loop preload="none" aria-label="Sample output video"></video>
    <div class="phone-ctrl"><button type="button" class="sound" id="sample-play" aria-pressed="false" aria-label="Pause sample">{I_PAUSE}{I_PLAY}</button><button type="button" class="sound" id="sample-sound" aria-pressed="false">{I_SOUND}<span>Sound on</span></button></div>
    <span class="sticker" id="lead-tag">{I_STAR}Your face goes here</span>
    <span class="cast" id="cast"><img id="cast-img" alt="Your photo, cast on lead"></span><span class="cast-label">Now on lead</span>
   </div>
   <figcaption>Sample output · 13 s · 480p · AI results vary<br>Unofficial fan tool, not affiliated with NPR</figcaption>
  </figure>
 </div></div>
</section>
<div class="marquee" aria-hidden="true"><div class="marquee-track">{"".join(f"<span>{t}</span>" for t in MARQUEE*2)}</div></div>
<section id="ideas"><div class="wrap">
<div class="sec-head"><h2>Who’s singing lead this week?</h2><p>One photo puts one person on lead. The joke is who you pick.</p></div>
<ul class="casting">{"".join(f"<li><b>{html.escape(a)}</b><span>{html.escape(b)}</span></li>" for a,b in CASTING)}</ul>
<p class="casting-more"><a href="{g6}">More casting ideas and how the meme works</a></p>
</div></section>
<section id="how-it-works" class="band"><div class="wrap setlist-wrap">
<div><h2>Tonight’s set list</h2><p class="lead">Three steps from photo to post. Most videos are ready in about two minutes.</p><p><a class="btn" href="#create">Add your photo</a></p><p class="small"><a href="{g2}">What happens to your photo, step by step</a></p></div>
<ol class="setlist">
<li><b>Upload a clear portrait</b><span>Your browser checks for a face before anything is uploaded. Confirm the photo is yours or that you have permission.</span></li>
<li><b>Generate</b><span>100 credits are used and the AI recasts the lead singer. If it fails, the credits come back.</span></li>
<li><b>Download</b><span>Your browser trims the clip to 13 seconds and hands you a version with the song and a silent copy.</span></li></ol>
</div></section>
<section id="pricing"><div class="wrap">
<div class="sec-head center"><h2 class="center">Credit packs</h2><p class="center">One-time payments, no subscription. 100 credits make one 13-second 480p video. Secure checkout by Stripe.</p></div>
<div class="packs">{pack("starter","Starter","$9.99","300",3)}{pack("plus","Plus","$19.99","700",7,True)}{pack("pro","Pro","$49.99","1,800",18)}</div>
<p id="buy-msg" class="msg center"></p><p class="pack-note center">Credits are returned automatically if a video fails.</p></div></section>
<section id="about" class="band"><div class="wrap about-grid">
<div><h2>What is Tiny Desk AI?</h2>
<p>The <strong>Tiny Desk AI trend</strong> takes the end of Charlie Wilson’s 2023 NPR Tiny Desk concert, where he closes with The Gap Band’s “Outstanding”, and uses AI to put new people in it. It went viral on TikTok in October 2026 with a parody starring college football coaches whose teams had just lost.</p>
<p><a href="/about/">About {BRAND}</a></p>
{DISC}</div>
<ul class="guide-links">{"".join(f'<li><a href="{u}"><span>{html.escape(t)}</span>{I_ARROW}</a></li>' for u,t in GUIDES_LIST)}</ul>
</div></section>
<section id="faq"><div class="wrap faq-grid"><div><h2>Questions, answered</h2><p class="muted">More in the <a href="/faq/">full FAQ</a>.</p></div>
<div class="faq-list">{"".join(f"<details><summary>{html.escape(q)}</summary><p>{html.escape(a)}</p></details>" for q,a,_ in faq)}</div></div></section>
<section class="cta"><div class="wrap"><h2>Your lead-singer moment starts here</h2><p>One photo, about two minutes.</p><a class="btn big" href="#create">Add your photo</a></div></section>
"""
app_ld={"@context":"https://schema.org","@type":"WebApplication","name":BRAND,"alternateName":"Tiny Desk AI video generator","url":D+"/","applicationCategory":"MultimediaApplication","operatingSystem":"Web",
        "description":"Unofficial photo-to-video tool for the Outstanding Tiny Desk AI meme: one photo in, a 13-second 480p vertical clip out.","publisher":{"@id":D+"/#org"},
        "screenshot":D+"/media/sample.jpg",
        "offers":[{"@type":"Offer","price":p,"priceCurrency":"USD","name":n} for n,p in [("Starter 300 credits","9.99"),("Plus 700 credits","19.99"),("Pro 1800 credits","49.99")]]}
video_ld={"@context":"https://schema.org","@type":"VideoObject","name":"Tiny Desk AI sample output","description":"A 13-second 480p vertical sample made with the Tiny Desk Trend generator: the lead singer of the Outstanding Tiny Desk clip recast from one photo.",
          "thumbnailUrl":D+"/media/sample.jpg","contentUrl":D+"/media/sample.mp4","uploadDate":"2026-10-28","duration":"PT13S","publisher":{"@id":D+"/#org"}}
OG_JOBS.append(("og.png","Put your face in the “Outstanding” Tiny Desk video","One photo · 13 seconds · song + silent copy"))
page("/","Tiny Desk AI – Make Your Own Outstanding Tiny Desk AI Video",
"Upload one photo and get the Outstanding Tiny Desk AI clip with you as the lead singer: 13 s, 9:16, with the song and a silent copy. Unofficial fan tool.",
HOME,[web_ld,org_ld,app_ld,video_ld],extra_head='<script type="module" src="/app.js"></script>', cls="home")

FAQ_BODY="<h1>Tiny Desk AI FAQ</h1>"+"".join(f'<h2>{html.escape(q)}</h2><p>{html.escape(a)}</p><p class="more"><a href="{l[0]}">{html.escape(l[1])} →</a></p>' for q,a,l in faq)
OG_JOBS.append(("og/faq.png","Tiny Desk AI FAQ","The song, the length, the price and how it’s made"))
page("/faq/","Tiny Desk AI FAQ – Song, Length, How It's Made","Answers to common questions about the Tiny Desk AI trend: the song, whether it is real, clip length, price and how to make your own.",
     FAQ_BODY,[faq_ld],og="/og/faq.png",crumb="FAQ")

# ---- guides ----
guide(g1,"origin","Where the Tiny Desk AI Trend Came From",
"The origin of the Outstanding Tiny Desk AI meme: Charlie Wilson's 2023 NPR Tiny Desk concert and the October 2026 TikTok parody that started it.",f"""
<p><strong>Short answer:</strong> the Tiny Desk AI meme recasts the last seconds of Charlie Wilson's 2023 NPR Tiny Desk concert, where he sings The Gap Band's "Outstanding". The AI version took off on TikTok in October 2026, starting with a parody that put the coaches of losing college football teams in the band.</p>
<h2>The source: Charlie Wilson's Tiny Desk concert (2023)</h2>
<p>NPR Music published Charlie Wilson's Tiny Desk Concert on June 5, 2023, as part of its Black Music Month series. His set ended with "Outstanding", the Gap Band song from 1982's <em>The Gap Band IV</em>. (<a href="{SRC_NPR}" rel="nofollow">NPR set list</a>, <a href="{SRC_RS}" rel="nofollow">Rolling Stone</a>)</p>
<h2>The meme: October 2026</h2>
<p>A tool maker's write-up dates the first AI version to October 18, 2026: TikTok creator @theburnerfromhe11 posted "College Football's Week 8 All-Loss Tiny Desk Concert", an AI edit of the end of that concert with the coaches of teams that had lost that weekend placed in the band. The caption called it an AI parody. Copies with NFL teams and other groups followed, and people started calling the format the "outstanding tiny desk" set. (Secondary sources: <a href="{SRC_HF}" rel="nofollow">Hugging Face write-up</a>, <a href="{SRC_OT}" rel="nofollow">outstandingtinydesk.com</a>. We have not found the original post's link to cite directly.)</p>
<h2>Timeline</h2>
<table><tr><th>Date</th><th>What happened</th><th>Source</th></tr>
<tr><td>Nov 1982</td><td>"Outstanding" released as a single from <em>Gap Band IV</em></td><td><a href="{SRC_WIKI}" rel="nofollow">Wikipedia</a></td></tr>
<tr><td>Feb 1983</td><td>No. 1 on Billboard's Hot Black Singles chart</td><td><a href="{SRC_WIKI}" rel="nofollow">Wikipedia</a></td></tr>
<tr><td>Jun 5, 2023</td><td>NPR publishes Charlie Wilson's Tiny Desk Concert, closing with "Outstanding"</td><td><a href="{SRC_NPR}" rel="nofollow">NPR</a></td></tr>
<tr><td>Oct 18, 2026</td><td>First AI parody: college football coaches whose teams lost in Week 8</td><td>Secondary (above)</td></tr>
<tr><td>Oct 27, 2026</td><td>"tiny desk ai" and "outstanding tiny desk ai" show as Breakout searches in Google Trends (US, past 7 days); several AI video sites add Tiny Desk AI pages</td><td>Our own trend tracking</td></tr>
<tr><td>Oct 28, 2026</td><td>"tiny desk ai video" searches up more than 3,000% week over week in Google Trends (US)</td><td>Our own trend tracking</td></tr></table>
<p>The last two rows come from the daily Google Trends and competitor-sitemap checks we run to spot trends like this one. Trends numbers are relative, not search counts.</p>
<h2>Why it works</h2><p>The joke is the casting: people having a bad week shown joyfully singing a song called "Outstanding". The close-up laugh and the sax solo are the shots everyone recasts. The format also travels: any group with a bad week (a team, an office, a fantasy league) can be dropped into the same 19 seconds.</p>
<h2>Is it real?</h2><p>No. These are AI-edited videos. If you post one, label it as AI and only use faces you have permission to use.</p>""",
og_sub="Origin and timeline of the meme")

steps=[("Get the vertical clip","The viral version is a vertical, roughly 19-second cut (720x1280, 24 fps) with five shots. Working from that vertical version keeps the framing right; widescreen footage tends to get re-framed by the model."),
("Pick one clear photo per person","Use a sharp, front-facing photo of one person. Only use photos of yourself or people who agreed. A face close-up crop plus the full photo helps the model keep both the face and the clothes."),
("Use a video edit mode, not text-to-video","A video-edit model takes the clip as reference and keeps its motion, camera and timing while swapping the person. A short prompt that says to keep everything else the same works best; one public write-up found that mentioning the mouth or lip sync made results worse."),
("Split at the 13-second hard cut","These models cap a single generation at about 15 seconds, so split the clip at the hard cut at 13.0 seconds: one 13-second part and one ~6-second part. A seam on a hard cut is invisible."),
("One face per role","Assign each person to a single role. Mapping the same face to two roles caused the swap to fail in published tests."),
("Check the faces before sharing","A failed swap can still come back marked as successful. Look through the output (or run an automatic face check) to make sure the original people are gone."),
("Join the parts and add the song back","The model returns silent video. Join the two parts and lay the original audio underneath; keep a silent copy for apps that mute music. Label the post as AI.")]
howto={"@context":"https://schema.org","@type":"HowTo","name":"How to Make an Outstanding Tiny Desk AI Video","step":[{"@type":"HowToStep","name":a,"text":b} for a,b in steps]}
guide(g2,"how-to","How to Make an Outstanding Tiny Desk AI Video",
"How the Outstanding Tiny Desk AI video is made: the general method, and exactly what our generator does with your photo, from face check to the 13-second cut.",f"""
<p><strong>Short answer:</strong> take the vertical "Outstanding" clip as a reference video, give a video-edit AI model one clear photo per person you want to recast, generate in parts no longer than about 15 seconds, check the faces, then put the song back. Below is the general method, followed by exactly what our generator does.</p>
<h2>The general method</h2>
<p>These steps summarise a public technical write-up by another tool maker (<a href="{SRC_HF}" rel="nofollow">Hugging Face blog</a>) and match what we saw building our own generator.</p>
<ol>{"".join(f"<li><strong>{a}.</strong> {b}</li>" for a,b in steps)}</ol>
<h2>What our generator does</h2>
<p>Our generator on the <a href="/#create">homepage</a> makes the first 13 seconds of the clip, with one person on lead. Step by step:</p>
<ol>
<li><strong>Face check in your browser.</strong> Before anything is uploaded, your browser runs a face detector (Google's MediaPipe face detection model) on the photo. If it finds no face, nothing is uploaded and no credits are used.</li>
<li><strong>Reference clip.</strong> We send the first 13.0 seconds of the vertical clip (shots 1 to 3, ending exactly on the hard cut) as the reference video, so there is no seam to hide.</li>
<li><strong>The model.</strong> The recast is made by the MiniMax H3 video model through MetaSo, in reference-video mode, at 480p and 13 seconds.</li>
<li><strong>The instruction.</strong> The model is told to keep everything from the reference: the room, the shelves, the red mixing desk, every other person, the camera moves, the cuts and the lead singer's gestures and lip movement. Only the lead singer's face, hair, skin tone and build change to match your photo. His outfit, a red cap and a black hoodie, stays the same.</li>
<li><strong>Trim and sound, also in your browser.</strong> When the video is ready, your browser trims it to exactly 13.000 seconds (312 frames at 24 fps) and lays the first 13 seconds of the song underneath. You get a version with the song, a silent copy and the untouched original file.</li>
<li><strong>Refunds.</strong> If the video service fails or rejects the photo, the 100 credits go straight back to your account. A job that is still unfinished after 20 minutes is refunded too.</li>
</ol>
<p>What it does not do: recast the band or the sax player, make the full 19-second version, or render above 480p.</p>
<h2>Common problems</h2>
<ul><li><strong>The face looks a bit different between shots.</strong> The model regenerates every frame, so faces vary between takes. A sharp, well-lit, front-facing photo helps most.</li>
<li><strong>Small details change.</strong> Hands, the cap or the cut timing can drift from the original. That is normal for AI recasts.</li>
<li><strong>"No face found".</strong> Use a photo where one face is clearly visible and not too small in the frame.</li>
<li><strong>The song is muted after posting.</strong> Use the silent copy and add the sound from the app's own library.</li></ul>
<h2>Shot list of the viral clip</h2><table><tr><th>Shot</th><th>Time (s)</th><th>What's in it</th></tr>
<tr><td>1</td><td>0–1.375</td><td>Lead singer, side-on</td></tr><tr><td>2</td><td>1.375–6.708</td><td>The band</td></tr><tr><td>3</td><td>6.708–13.0</td><td>Lead's big laugh close-up</td></tr><tr><td>4</td><td>13.0–16.375</td><td>Sax solo</td></tr><tr><td>5</td><td>16.375–19.06</td><td>The band again</td></tr></table>
<p>Timings from the <a href="{SRC_HF}" rel="nofollow">same write-up</a>; our generator covers shots 1 to 3.</p>""",[howto],og_sub="The method, and what our generator does")

guide(g3,"song","What Is the Song in the Tiny Desk AI Video?",
"The Tiny Desk AI trend song is \"Outstanding\" by The Gap Band (1982), sung by Charlie Wilson at his 2023 NPR Tiny Desk concert.",f"""
<p><strong>Short answer:</strong> "Outstanding" by <strong>The Gap Band</strong>, from the 1982 album <em>The Gap Band IV</em>. The meme uses Charlie Wilson's live version, the closing song of his NPR Tiny Desk concert published June 5, 2023.</p>
<h2>Who is Charlie Wilson?</h2><p>Charlie Wilson was the lead singer of The Gap Band, which he formed with his brothers Robert and Ronnie; the group's hits ran from the 1970s through the '80s. He later became a frequent hip-hop collaborator, nicknamed "Uncle Charlie" by Snoop Dogg. (<a href="{SRC_NPR}" rel="nofollow">NPR</a>)</p>
<h2>Full Tiny Desk set list</h2><ol><li>Charlie, Last Name Wilson</li><li>Computer Love</li><li>There Goes My Baby</li><li>I'm Blessed</li><li>Yearning For Your Love</li><li>Sweet Yamz</li><li>Outstanding</li></ol><p>Source: <a href="{SRC_NPR}" rel="nofollow">NPR</a>, <a href="{SRC_RS}" rel="nofollow">Rolling Stone</a>.</p>
<h2>Which part of the song the meme uses</h2><p>The meme uses about the last 19 seconds of that live performance, ending on the sax solo and the band. The 13-second clip our generator makes uses the first 13 seconds of that segment, up to the hard cut before the sax; the version you download with sound carries those same 13 seconds of the song. More detail in the <a href="{g5}">template breakdown</a>.</p>
<h2>Using the song in your post</h2><p>The song is copyrighted. Platforms such as TikTok may mute or restrict uploads that contain it; using the platform's own sound library or a silent copy is the usual workaround. For the release date, writer, chart peaks and samples, see <a href="{g7}">"Outstanding" by The Gap Band: facts</a>.</p>""",
og_sub="“Outstanding” by The Gap Band")

guide(g4,"generator","Tiny Desk AI Video Generator: Free and Paid Options Explained",
"Is there a free Tiny Desk AI video generator? What a Tiny Desk AI maker needs, what the AI model behind it costs, and what to check before you upload a photo.",f"""{DISC}
<p><strong>Short answer:</strong> free Tiny Desk AI generators are rare because every clip runs a paid video-edit model. Before you pay for any of them, check the length and resolution, whether you get a silent copy, what happens when a swap fails and how your photo is handled.</p>
<h2>Is there a free Tiny Desk AI generator?</h2><p>Not really. The tools making this trend run a paid video-edit model on every clip. Public price lists put one of the common models, Seedance 2.0 mini, at roughly $0.02 to $0.07 per second of 480p video, depending on the provider and whether a reference video is used (<a href="{SRC_JUT}" rel="nofollow">price comparison, checked Oct 27, 2026</a>). A full clip needs about 19 seconds of output, plus retries when a face swap fails, so a "free" tool is either a limited trial or paying for it some other way.</p>
<h2>What a Tiny Desk AI maker has to do</h2><ul>
<li>Take the vertical ~19-second "Outstanding" clip as the reference video.</li>
<li>Replace the lead singer (and optionally the band) with the people in your photos using a video edit mode.</li>
<li>Split the job at the 13-second hard cut, because one generation is capped at about 15 seconds (<a href="{SRC_WAVE}" rel="nofollow">model limits</a>).</li>
<li>Check the faces in the result, join the parts and add the song back.</li></ul>
<h2>What to check before you pay for one</h2><ul>
<li><strong>Resolution and length:</strong> 480p or 720p, and whether you get the full ~19 seconds.</li>
<li><strong>Song and silent copy:</strong> platforms sometimes mute the original song, so a silent copy is useful.</li>
<li><strong>Refund on a bad swap:</strong> AI swaps sometimes leave an original face in place.</li>
<li><strong>Photo handling:</strong> how long your photo is kept, and whether it is used for anything else.</li>
<li><strong>Consent:</strong> only upload photos of yourself or people who agreed.</li></ul>
<h2>How our generator answers that checklist</h2>
<table><tr><th>Check</th><th>{BRAND}</th></tr>
<tr><td>Length and resolution</td><td>13 seconds (shots 1 to 3, lead singer only), 480p, vertical 9:16. Not the full 19 seconds.</td></tr>
<tr><td>Model</td><td>MiniMax H3 through MetaSo, reference-video mode</td></tr>
<tr><td>Song and silent copy</td><td>Both, plus the untouched original file</td></tr>
<tr><td>Failed or rejected jobs</td><td>Credits returned automatically, including jobs still unfinished after 20 minutes. If a finished video looks wrong, <a href="mailto:privacy@tinydesktrend.com">email us</a> and we will look at a refund.</td></tr>
<tr><td>Photo handling</td><td>The face check runs in your browser. The photo goes from our server to the video service and is not stored on our servers; finished videos are deleted after 7 days. See the <a href="/privacy/">privacy policy</a>.</td></tr>
<tr><td>Consent</td><td>You must confirm the photo is yours or that you have permission; no minors.</td></tr>
<tr><td>Price</td><td>$9.99 for 3 videos (about $3.33 each) up to $49.99 for 18 (about $2.78 each). One-time packs, no subscription.</td></tr></table>
<p>The <a href="{g2}">how-to guide</a> walks through each step our generator takes.</p>""",
og_sub="Free vs paid, and what to check")

roles=[("Lead singer","Shots 1 and 3, including the big laugh close-up. This is the role almost every version recasts."),("Keys player","Front and centre in the band shots (2 and 5). Easy to mistake for the lead at first glance."),("Two backing singers","Behind the keys in the band shots."),("Sax player","Gets the solo in shot 4, right after the 13-second cut, so it often goes to the surprise cast member.")]
guide(g5,"template","Outstanding Tiny Desk AI Template: Shots, Timing and Who Goes Where",
"The Outstanding Tiny Desk AI template broken down: 9:16 format, 19.06 seconds, five shots, and which roles (lead, keys, backing singers, sax) you can recast.",f"""
<p><strong>Short answer:</strong> the template is a vertical 9:16, 24 fps, 19.06-second cut of the end of Charlie Wilson's Tiny Desk performance of "Outstanding". It has five shots with a hard cut at exactly 13.0 seconds, and five people you can recast: the lead, the keys player, two backing singers and the sax player.</p>
<p>Specs below come from a <a href="{SRC_HF}" rel="nofollow">frame-by-frame breakdown</a> by another tool maker and match the clip we use.</p>
<h2>Format</h2><ul><li>Vertical 9:16, 720×1280</li><li>24 fps</li><li>19.06 seconds</li><li>Five shots, with a hard cut at exactly 13.0 seconds</li></ul>
<h2>The five shots</h2><table><tr><th>Shot</th><th>Time (s)</th><th>What's in it</th></tr>
<tr><td>1</td><td>0–1.375</td><td>Lead singer's opening line, side-on</td></tr><tr><td>2</td><td>1.375–6.708</td><td>Band: keys in front, two singers behind</td></tr><tr><td>3</td><td>6.708–13.0</td><td>The big laugh close-up of the lead</td></tr><tr><td>4</td><td>13.0–16.375</td><td>Sax solo</td></tr><tr><td>5</td><td>16.375–19.06</td><td>The band again</td></tr></table>
<h2>Roles you can recast</h2><ul>{"".join(f"<li><strong>{a}:</strong> {b}</li>" for a,b in roles)}</ul>
<h2>What our generator covers</h2><p>Our generator makes shots 1 to 3 (0 to 13.0 seconds) and recasts only the lead singer, from one photo. The band and the sax player stay as they are, and the lead keeps the red cap and black hoodie. Stopping on the hard cut at 13.0 seconds means there is no join to hide. Details in <a href="{g2}">how the video is made</a>.</p>
<h2>Tips</h2><ul><li>Use one person per role. Putting the same face in two roles made swaps fail in published tests.</li><li>Use the vertical cut, not the widescreen original, so the framing matches.</li><li>Keep the song timing intact so the audio lines up.</li></ul>""",
og_sub="Five shots, 19.06 seconds, five roles")

guide(g6,"ideas","Outstanding Tiny Desk Meme: What It Means and Casting Ideas",
"What the Outstanding Tiny Desk meme means, how fans cast it (losing teams, coworkers, group chats), photo tips for the lead and caption ideas.",f"""
<p><strong>Short answer:</strong> the meme puts people who just had a bad week into a joyful band singing a song called "Outstanding". The funniest versions cast one person the joke is about on lead and name the bad week in the caption.</p>
<h2>What the meme means</h2><p>The joke is contrast. The first version, posted October 18, 2026 according to a tool maker's write-up, cast the coaches of college football teams that had lost that weekend and called itself an AI parody (<a href="{SRC_HF}" rel="nofollow">source</a>). Fan versions for NFL teams followed within days (<a href="{SRC_OT}" rel="nofollow">source</a>). The origin story is in <a href="{g1}">where the trend came from</a>.</p>
<h2>Casting ideas</h2><ul>
<li><strong>Your team after a loss:</strong> the format the trend started with.</li>
<li><strong>The office:</strong> the teammate who just missed a deadline.</li>
<li><strong>Fantasy league:</strong> last place sings lead.</li>
<li><strong>Family or group chat:</strong> whoever had the worst week gets the close-up.</li>
<li><strong>Yourself:</strong> one photo, you on lead, for your own "outstanding" week.</li></ul>
<p>Our generator recasts the lead singer only, so pick the one person the joke is about. Versions that recast the whole band, sax solo included, need a tool that handles several roles; see the <a href="{g5}">template breakdown</a>.</p>
<h2>Photo tips for whoever is on lead</h2><ul>
<li>One person in the photo, facing the camera, face clearly visible.</li>
<li>Good light and a sharp image; blurry or very small faces give weaker results.</li>
<li>A photo that shows the face without heavy shadows or anything covering it.</li>
<li>Only use a photo of someone who is in on the joke, and never a minor.</li></ul>
<h2>Caption ideas</h2><ul>
<li>"Week 8, all losses, all smiles"</li>
<li>"Me after the deadline I missed"</li>
<li>"Last place in the league, first place in the band"</li>
<li>"How I'm walking into Monday"</li></ul>
<h2>Rules good versions follow</h2><ol>
<li>The close-up goes to the person the joke is about.</li>
<li>The caption names the bad week.</li>
<li>Label it as AI, in the caption and with your app's AI label.</li>
<li>Only use faces of people who are in on the joke, and never minors.</li></ol>""",
og_sub="Who to put on lead, and how")

guide(g7,"song-facts","\"Outstanding\" by The Gap Band: Release Date, Writer, Charts and Samples",
"Facts about \"Outstanding\" by The Gap Band, the Tiny Desk AI trend song: released November 1982, written by Raymond Calhoun, R&B No. 1, covers, samples.",f"""
<p><strong>Short answer:</strong> "Outstanding" was written by Raymond Calhoun, released as a single in November 1982 from <em>Gap Band IV</em>, and reached No. 1 on Billboard's Hot Black Singles chart in February 1983.</p>
<table><tr><th>Artist</th><td>The Gap Band</td></tr><tr><th>Album</th><td><em>Gap Band IV</em> (1982)</td></tr><tr><th>Released as a single</th><td>November 1982 (Total Experience)</td></tr><tr><th>Songwriter</th><td>Raymond Calhoun</td></tr><tr><th>Length</th><td>3:19 album version, 6:13 extended version</td></tr><tr><th>Peak charts</th><td>No. 1 US Billboard Hot Black Singles (February 1983), No. 51 Billboard Hot 100, No. 68 UK</td></tr></table>
<p>Source: <a href="{SRC_WIKI}" rel="nofollow">Wikipedia</a>.</p>
<h2>Covers</h2><p>British singer Kenny Thomas covered it in 1990; his version reached No. 12 on the UK Singles Chart (<a href="{SRC_WIKI}" rel="nofollow">Wikipedia</a>).</p>
<h2>Songs that sample it</h2><ul><li>Da Brat, "Da B Side" (1994)</li><li>Ashanti feat. Ja Rule, "Happy" (2002)</li><li>Tyler, The Creator, "911 / Mr. Lonely" (2017)</li></ul><p>Source: <a href="{SRC_WS}" rel="nofollow">WhoSampled</a>.</p>
<h2>Lyrics</h2><p>We don't reproduce the lyrics here because they are copyrighted; licensed lyric sites and streaming apps carry them.</p>
<h2>Why it's in the Tiny Desk AI trend</h2><p>Charlie Wilson, The Gap Band's lead singer, closed his 2023 NPR Tiny Desk concert with it, and the meme recasts the last ~19 seconds of that performance. More in <a href="{g3}">what is the song in the Tiny Desk AI video?</a></p>""",
og_sub="Release, writer, charts, samples")

GUIDE_INDEX=('<h1>Tiny Desk AI guides</h1><p class="lead">Seven short guides to the "Outstanding" Tiny Desk AI meme: where it came from, the song, the template, how the video is made and what to check in a generator.</p>'
             '<ul class="guide-index">'+"".join(f'<li><a href="{u}">{html.escape(t)}</a><span>{html.escape(s)}</span></li>' for u,t,s in GUIDES)+'</ul>'
             '<p>Ready to make one? <a href="/#create">Put your face on lead</a>.</p>')
itemlist={"@context":"https://schema.org","@type":"ItemList","name":"Tiny Desk AI guides","itemListElement":[{"@type":"ListItem","position":i+1,"url":D+u,"name":t} for i,(u,t,_) in enumerate(GUIDES)]}
OG_JOBS.append(("og/guides.png","Tiny Desk AI guides","Origin · the song · the template · how it’s made"))
page("/guides/","Tiny Desk AI Guides – Origin, Song, Template and How It's Made",
     "Seven guides to the Outstanding Tiny Desk AI meme: where it came from, the song, the five-shot template, how the video is made and how to pick a generator.",
     GUIDE_INDEX,[itemlist,{"@context":"https://schema.org","@type":"CollectionPage","name":"Tiny Desk AI guides","url":D+"/guides/","publisher":{"@id":D+"/#org"}}],og="/og/guides.png",crumb="Guides")

ABOUT=f"""<h1>About {BRAND}</h1>
<p><strong>{BRAND}</strong> (also shown as Tiny Desk AI) is an unofficial fan site for one meme: the AI recasts of Charlie Wilson singing "Outstanding" at his 2023 NPR Tiny Desk concert. It has a paid generator that puts your face on the lead singer, and free guides about the trend.</p>
{DISC}
<h2>Who runs it</h2><p>A small independent team that builds single-purpose tools for viral AI video trends. We spot trends by tracking Google Trends, TikTok and new pages on AI video sites every day, then build one focused site per trend. We are not connected to NPR, Charlie Wilson or The Gap Band.</p>
<h2>What the generator does</h2><ul>
<li>One photo in, a 13-second, 480p, vertical clip out, with your face on the lead singer.</li>
<li>Made with the MiniMax H3 video model through MetaSo, using the first 13 seconds of the vertical clip as the reference.</li>
<li>Your browser checks the photo for a face before upload, then trims the result and adds the song.</li>
<li>Credits are returned automatically when a job fails, is rejected or runs past 20 minutes.</li></ul>
<p>The full step-by-step is in <a href="{g2}">how the video is made</a>.</p>
<h2>What it does not do</h2><ul><li>Recast the band or the sax player.</li><li>Make the full 19-second version or anything above 480p.</li><li>Accept photos of minors or of people who have not agreed.</li></ul>
<h2>How we write the guides</h2><p>Guides state facts with a source next to them: NPR and Rolling Stone for the concert, Wikipedia and WhoSampled for the song, and public write-ups from other tool makers for the technical method, labelled as such. Statements about our own generator come from how it is built. Each guide shows the date it was last updated.</p>
<h2>Contact</h2><p><a href="mailto:privacy@tinydesktrend.com">privacy@tinydesktrend.com</a> for questions, refunds and data requests. Policies: <a href="/privacy/">privacy</a>, <a href="/terms/">terms</a>.</p>"""
OG_JOBS.append(("og/about.png",f"About {BRAND}","An unofficial fan tool for the Outstanding meme"))
page("/about/",f"About {BRAND} – Unofficial Tiny Desk AI Generator",
     f"Who runs {BRAND}, what its Tiny Desk AI generator does and does not do, how the guides are sourced and how to reach us. Not affiliated with NPR.",
     ABOUT,[{"@context":"https://schema.org","@type":"AboutPage","name":f"About {BRAND}","url":D+"/about/","mainEntity":{"@id":D+"/#org"}},org_ld],og="/og/about.png",crumb="About")

page("/privacy/",f"Privacy Policy – {BRAND}","What tinydesktrend.com collects (email, login cookie, photos, videos kept 7 days, Stripe orders), who processes it and how to delete your data.",f"""<h1>Privacy Policy</h1><p><em>Last updated 2026-10-28</em></p>
<p>This policy covers tinydesktrend.com, an unofficial fan tool. It is not affiliated with NPR or Tiny Desk Concerts.</p>
<h2>What we collect</h2><ul>
<li><strong>Account:</strong> your email address and a salted hash of your password (never the password itself). We do not verify emails or send marketing.</li>
<li><strong>Login cookie:</strong> one essential cookie (<code>td_session</code>, HttpOnly, 30 days) that keeps you signed in. No advertising or analytics cookies.</li>
<li><strong>Photos you upload:</strong> sent from our server straight to the video service to make your video. We do not store your photo on our own servers. The face check before upload runs entirely in your browser.</li>
<li><strong>Generated videos:</strong> stored for 7 days so you can download them, then deleted automatically.</li>
<li><strong>Purchases and credits:</strong> order records (pack, amount, status) and your credit balance. Payments are handled by Stripe on its hosted checkout page; we never see or store card numbers. Stripe receives your account email, an order ID and an internal user ID.</li>
<li><strong>Usage records:</strong> sign-up, generation, checkout and payment events, and short-lived rate-limit counters keyed by IP address, used to run the service and prevent abuse.</li></ul>
<h2>Who processes your data</h2><ul>
<li><strong>Cloudflare</strong> hosts the site, database and video storage, and processes request logs (IP address, browser, URL).</li>
<li><strong>MetaSo (metaso.cn), using the MiniMax H3 video model,</strong> receives your photo and makes the video. Its own retention rules apply to the files it receives.</li>
<li><strong>Stripe</strong> processes payments.</li>
<li><strong>jsDelivr</strong> serves the video-processing component your browser downloads; it receives your IP address like any web request.</li></ul>
<h2>Deleting your data</h2><p>Videos are deleted after 7 days. To delete your account and records, email privacy@tinydesktrend.com from your account email. Order records may be kept where the law requires it.</p>
<h2>Contact</h2><p>privacy@tinydesktrend.com</p>""",crumb="Privacy Policy")
page("/terms/",f"Terms of Use – {BRAND}","Terms for tinydesktrend.com: whose photos you may use, how credits and refunds work, generator availability, and the site's unofficial status.",f"""<h1>Terms of Use</h1><p><em>Last updated 2026-10-28</em></p>
<p>By using tinydesktrend.com you agree to these terms.</p>
<h2>Unofficial site</h2><p>This is an unofficial fan tool. It is not affiliated with, endorsed by or connected to NPR, NPR Music or Tiny Desk Concerts. All trademarks belong to their owners.</p>
<h2>Your photos</h2><p>Only upload photos of yourself or of people who have given you permission. Do not upload photos of minors. Do not use the service to impersonate, harass or deceive anyone, or to make sexual, hateful or illegal content. You are responsible for what you upload and post. Label AI videos as AI when you share them, and follow each platform's rules, including music rules.</p>
<h2>Credits and payments</h2><p>Credits are sold in one-time packs through Stripe. Each 13-second 480p video uses 100 credits. If a generation fails, its credits are returned automatically. Credits have no cash value and cannot be transferred. AI results vary and will not match the original clip exactly. If something goes wrong, contact us and we will look at a refund.</p>
<h2>Availability</h2><p>Generation depends on a third-party video service and limited capacity; it may be sold out or unavailable at times. Videos are kept for 7 days.</p>
<h2>No warranty</h2><p>The service is provided as is, without warranties, to the extent the law allows.</p>
<h2>Contact</h2><p>privacy@tinydesktrend.com</p>""",crumb="Terms of Use")
import shutil
for root,dirs,files in os.walk("static"):
    for f in files:
        src=os.path.join(root,f); dst=os.path.join(OUT,os.path.relpath(src,"static")); os.makedirs(os.path.dirname(dst),exist_ok=True); shutil.copy(src,dst)
page("/login/",f"Sign in – {BRAND}","Sign in or create an account on tinydesktrend.com.",'<h1>Sign in</h1><p>Sign in or create a free account to make your Tiny Desk AI video.</p><p class="row"><button type="button" class="btn" data-auth="login">Sign in</button><button type="button" class="btn ghost" data-auth="signup">Create account</button></p><p><a href="/#create">Back to the generator</a></p>',index=False)
# 404
open(f"{OUT}/404.html","w").write(f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Not found</title><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex"><link rel="stylesheet" href="/style.css"><script type="module" src="/site.js"></script></head><body class="prose">{NAV}<main class="wrap narrow"><h1>Page not found</h1><p><a href="/">Go home</a> or browse the <a href="/guides/">guides</a>.</p></main>{FOOT}</body></html>')
# sitemap/robots/llms
open(f"{OUT}/sitemap.xml","w").write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+"".join(f"<url><loc>{D}{p}</loc><lastmod>{'2026-10-28' if p in ('/privacy/','/terms/') else TODAY}</lastmod></url>\n" for p in pages)+"</urlset>\n")
bots=["GPTBot","OAI-SearchBot","ClaudeBot","Claude-SearchBot","PerplexityBot","Google-Extended"]
open(f"{OUT}/robots.txt","w").write("".join(f"User-agent: {b}\nAllow: /\n\n" for b in bots)+"User-agent: *\nAllow: /\nDisallow: /api/\n\nSitemap: https://tinydesktrend.com/sitemap.xml\n")
open(f"{OUT}/llms.txt","w").write(f"""# {BRAND} (tinydesktrend.com)

> Unofficial fan site about the "Outstanding" Tiny Desk AI video trend (October 2026), also shown as Tiny Desk AI. Not affiliated with NPR or Tiny Desk Concerts. The homepage has a paid photo-to-video generator.

## Key facts
- Generator: one photo in, a 13-second 480p vertical (9:16) clip out with your face on the lead singer, plus a version with the song and a silent copy.
- Model: MiniMax H3 through MetaSo, reference-video mode, using the first 13.0 seconds (shots 1 to 3) of the vertical clip. Only the lead singer is recast.
- Price: $9.99 for 300 credits (3 videos), $19.99 for 700 (7), $49.99 for 1,800 (18). 100 credits per video. One-time payments.
- Credits are refunded automatically when a job fails, is rejected or runs past 20 minutes. Videos are kept 7 days.
- The song is "Outstanding" by The Gap Band (1982); the meme recasts Charlie Wilson's June 5, 2023 NPR Tiny Desk performance.

## Guides
"""+"".join(f"- [{t}]({D}{u}): {s}\n" for u,t,s in GUIDES)+f"""- [FAQ]({D}/faq/)

## About and policies
- [About]({D}/about/)
- [Privacy]({D}/privacy/)
- [Terms]({D}/terms/)
""")
# IndexNow key (kept outside the repo; secrets/ is gitignored)
kp=os.environ.get("INDEXNOW_KEY_FILE") or ("/workspace/secrets/indexnow-tinydesktrend.txt" if os.path.isdir("/workspace/secrets") else "secrets/indexnow-tinydesktrend.txt")
if not os.path.exists(kp):
    os.makedirs(os.path.dirname(kp),exist_ok=True); open(kp,"w").write(secrets.token_hex(16)); os.chmod(kp,0o600)
key=open(kp).read().strip(); open(f"{OUT}/{key}.txt","w").write(key)

# ---- images: share cards in the site's style, logo and favicon ----
from PIL import Image, ImageDraw, ImageFont
PAPER=(255,245,229); INK=(42,30,22); SUN=(250,214,72); TOMATO=(206,64,36); SEA=(38,104,168); CARD=(255,252,246)
FD=lambda n,s: ImageFont.truetype(os.path.join("assets","fonts",n),s)
def mic(d,x,y,s,w):
    # microphone glyph inside an s-sized square at (x,y), stroke w
    d.rounded_rectangle([x+s*.39,y+s*.2,x+s*.61,y+s*.58],int(s*.11),outline=INK,width=w)
    d.arc([x+s*.27,y+s*.34,x+s*.73,y+s*.72],0,180,fill=INK,width=w)
    d.line([x+s*.5,y+s*.72,x+s*.5,y+s*.82],fill=INK,width=w); d.line([x+s*.38,y+s*.82,x+s*.62,y+s*.82],fill=INK,width=w)
def tile(d,x,y,s,w):
    d.rounded_rectangle([x,y,x+s,y+s],int(s*.22),fill=SUN,outline=INK,width=w); mic(d,x,y,s,max(2,int(w*1.1)))
def og_card(rel,title,sub):
    W,H=1200,630; im=Image.new("RGB",(W,H),PAPER); d=ImageDraw.Draw(im)
    d.rectangle([0,0,W-1,H-1],outline=INK,width=6)
    d.rectangle([0,H-96,W,H],fill=SEA); d.line([0,H-96,W,H-96],fill=INK,width=6)
    tile(d,64,56,72,5); d.text((156,70),BRAND,font=FD("Fraunces-900.ttf",44),fill=INK)
    size=84; lines=[]
    while size>=52:
        f=FD("Fraunces-900.ttf",size); chars=max(8,int(1060/(size*0.52)))
        lines=textwrap.wrap(title,chars)
        if len(lines)<=3 and all(d.textlength(l,font=f)<=1060 for l in lines): break
        size-=6
    f=FD("Fraunces-900.ttf",size); y=180
    for l in lines: d.text((64,y),l,font=f,fill=INK); y+=int(size*1.08)
    d.text((64,y+18),sub,font=FD("BricolageGrotesque-600.ttf",36),fill=(90,70,56))
    d.text((64,H-70),"tinydesktrend.com  ·  Unofficial fan tool",font=FD("BricolageGrotesque-800.ttf",32),fill=(250,246,240))
    d.rounded_rectangle([W-300,H-150,W-64,H-86],32,fill=SUN,outline=INK,width=4)
    d.text((W-182,H-118),"Now on lead",font=FD("BricolageGrotesque-800.ttf",28),fill=INK,anchor="mm")
    os.makedirs(os.path.dirname(os.path.join(OUT,rel)) or OUT,exist_ok=True); im.save(os.path.join(OUT,rel),optimize=True)
for rel,title,sub in OG_JOBS: og_card(rel,title,sub)
lg=Image.new("RGBA",(512,512),(0,0,0,0)); tile(ImageDraw.Draw(lg),16,16,480,24); lg.save(f"{OUT}/logo.png")
fi=Image.new("RGBA",(256,256),(0,0,0,0)); tile(ImageDraw.Draw(fi),8,8,240,16)
fi.save(f"{OUT}/favicon.ico",sizes=[(16,16),(32,32),(48,48),(64,64)])
open(f"{OUT}/favicon.svg","w").write('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect x="2" y="2" width="60" height="60" rx="14" fill="#fad648" stroke="#2a1e16" stroke-width="4"/><g fill="none" stroke="#2a1e16" stroke-width="4.5" stroke-linecap="round"><rect x="25" y="13" width="14" height="24" rx="7"/><path d="M18 30a14 14 0 0 0 28 0M32 44v7M25 51h14"/></g></svg>')
print(pages)
