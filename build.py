import os, json, html, datetime, secrets
from PIL import Image, ImageDraw, ImageFont
D="https://tinydesktrend.com"; OUT="public"; TODAY="2026-10-28"
os.makedirs(OUT,exist_ok=True)
NAV='<nav><a href="/">Tiny Desk AI</a> <a href="/guides/">Guides</a> <a href="/faq/">FAQ</a></nav>'
DISC='<p class="disc"><strong>Unofficial fan tool.</strong> Tiny Desk Trend is not affiliated with, endorsed by, or connected to NPR, NPR Music, or Tiny Desk Concerts. No NPR or Tiny Desk logos or official assets are used on this site.</p>'
FOOT=f'<footer>{DISC}<p><a href="/privacy/">Privacy</a> · <a href="/terms/">Terms</a> · <a href="/guides/">Guides</a> · <a href="/faq/">FAQ</a></p><p>© 2026 tinydesktrend.com</p></footer>'
CSS="""body{font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif;max-width:760px;margin:0 auto;padding:16px 20px;line-height:1.6;color:#1f1b16;background:#fbf7f0}nav a{margin-right:14px;font-weight:600;color:#7a3e12;text-decoration:none}h1{font-size:2rem;line-height:1.2}h2{margin-top:2rem}.disc{background:#fff3d6;border:1px solid #e8c77a;padding:10px 14px;border-radius:8px;font-size:.95rem}.soon{border:2px dashed #b07a3a;border-radius:12px;padding:20px;text-align:center;background:#fff}.soon b{font-size:1.3rem}footer{margin-top:3rem;border-top:1px solid #ddd;padding-top:1rem;font-size:.9rem}a{color:#7a3e12}table{border-collapse:collapse}.home{max-width:1100px}.hero{display:grid;grid-template-columns:minmax(0,1.4fr) minmax(0,1fr);gap:28px;align-items:start}.hero-side video{width:100%;max-width:360px;border-radius:14px;background:#000;display:block}.lead{font-size:1.1rem}.card{background:#fff;border:1px solid #e3d6c3;border-radius:14px;padding:18px}.card h2{font-size:1.1rem;margin:.8rem 0 .4rem}.card label{display:block;margin:.4rem 0}.card input[type=email],.card input[type=password]{width:100%;padding:8px;border:1px solid #ccc;border-radius:8px;box-sizing:border-box}.row{display:flex;gap:10px;flex-wrap:wrap;align-items:center;margin:.5rem 0}.btn{background:#b0652a;color:#fff;border:0;border-radius:10px;padding:10px 16px;font-weight:700;cursor:pointer;text-decoration:none;display:inline-block}.btn.ghost{background:#fff;color:#7a3e12;border:1px solid #b0652a}.btn.big{font-size:1.05rem;padding:12px 20px;margin-top:.5rem}.btn:disabled{opacity:.45;cursor:not-allowed}.link{background:none;border:0;color:#7a3e12;text-decoration:underline;cursor:pointer;padding:0;font:inherit}#preview{max-width:160px;max-height:160px;border-radius:8px;display:block;margin:.5rem 0}#result video{width:100%;max-width:320px;border-radius:10px;background:#000}.consent{font-size:.95rem}.msg{min-height:1.2em}.msg.error{color:#a3201b}.msg.ok{color:#1d6b2f}.small{font-size:.9rem}.muted{color:#6b5e50}.packs{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}.pack{border:2px solid #e3d6c3;border-radius:12px;padding:14px;display:flex;flex-direction:column;gap:4px;background:#fff;cursor:pointer}.pack:has(input:checked){border-color:#b0652a}.price{font-size:1.6rem;font-weight:800}.steps li{margin:.5rem 0}details{border-bottom:1px solid #e3d6c3;padding:.6rem 0}summary{font-weight:600;cursor:pointer}.cta{text-align:center;padding:2rem 0}@media(max-width:760px){.hero,.packs{grid-template-columns:1fr}}td,th{border:1px solid #ccc;padding:4px 8px}"""
open(f"{OUT}/style.css","w").write(CSS)
pages=[]
def page(path,title,desc,body,ld=None,extra_head="",cls=""):
    url=D+path
    lds="".join(f'<script type="application/ld+json">{json.dumps(x)}</script>' for x in (ld or []))
    h=f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title><meta name="description" content="{html.escape(desc)}"><link rel="canonical" href="{url}">
<link rel="icon" href="/favicon.ico" sizes="any"><link rel="icon" href="/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="/style.css">
<meta property="og:type" content="website"><meta property="og:site_name" content="Tiny Desk Trend"><meta property="og:title" content="{html.escape(title)}"><meta property="og:description" content="{html.escape(desc)}"><meta property="og:url" content="{url}"><meta property="og:image" content="{D}/og.png"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{html.escape(title)}"><meta name="twitter:description" content="{html.escape(desc)}"><meta name="twitter:image" content="{D}/og.png">{lds}{extra_head}</head>
<body class="{cls}">{NAV}<main>{body}</main>{FOOT}</body></html>"""
    d=OUT+path; os.makedirs(d,exist_ok=True); open(d+"index.html","w").write(h); pages.append(path)

SRC_NPR="https://www.npr.org/2023/06/05/1179416602/charlie-wilson-tiny-desk-concert"
SRC_RS="https://www.rollingstone.com/music/music-news/charlie-wilson-gap-band-tiny-desk-1234759558/"
SRC_HF="https://huggingface.co/blog/trendrecast/how-to-make-outstanding-tiny-desk-ai-video"

faq=[
("What is the Tiny Desk AI trend?","It is an AI parody meme: people re-cast the closing moment of Charlie Wilson's 2023 NPR Tiny Desk concert, where he sings \"Outstanding\", with new faces swapped in by an AI video model. It took off on TikTok in October 2026 after a clip put college football coaches whose teams had just lost into the band."),
("What do I get?","A 13-second vertical (9:16) 480p clip of the lead-singer part of the meme with your face on the lead singer, in two versions: one with the original song and one silent copy for apps that mute music."),
("How much does it cost?","Each video uses 100 credits. Credit packs: $9.99 for 300 credits (3 videos), $19.99 for 700 credits (7 videos) and $49.99 for 1,800 credits (18 videos). One-time payments, no subscription."),
("What photo works best?","A clear, front-facing photo of one person, well lit, JPEG, PNG or WebP up to 10 MB. Your browser checks for a face before anything is uploaded."),
("Whose photo can I use?","Only your own photo or a photo of someone who has agreed to it. No minors, no impersonation, no using other people's faces without consent. You must confirm this before generating."),
("What happens if a video fails?","If the video service fails or rejects the request, the credits for that video are returned to your account automatically."),
("Is the result perfect?","No. It is an AI recast, so details can differ from the original clip: the cap may disappear, shots can be re-cut, and faces vary between takes."),
("What song is in the Tiny Desk AI video?","\"Outstanding\" by The Gap Band, from their 1982 album The Gap Band IV. Charlie Wilson, The Gap Band's lead singer, closed his June 2023 Tiny Desk concert with it."),
("Is the Tiny Desk AI video real?","No. These are AI edits of real concert footage. Label yours as AI when you post it."),
("Is this site official?","No. Tiny Desk Trend is an unofficial fan tool and is not affiliated with NPR, NPR Music or Tiny Desk Concerts."),
]
faq_html="".join(f"<h3>{html.escape(q)}</h3><p>{html.escape(a)}</p>" for q,a in faq)
faq_ld={"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in faq]}
web_ld={"@context":"https://schema.org","@type":"WebSite","name":"Tiny Desk Trend","url":D+"/"}
GUIDES_LIST=[("/guides/what-is-the-tiny-desk-ai-trend/","Where the Tiny Desk AI trend came from"),("/guides/how-to-make-outstanding-tiny-desk-ai-video/","How the Outstanding Tiny Desk AI video is made"),("/guides/outstanding-tiny-desk-song/","What is the song?"),("/guides/tiny-desk-ai-video-generator/","Tiny Desk AI video generator: what to check"),("/guides/outstanding-tiny-desk-ai-template/","The Outstanding template: shots and roles"),("/guides/outstanding-tiny-desk-meme-ideas/","Meme meaning and casting ideas"),("/guides/outstanding-gap-band-song-facts/","\"Outstanding\" by The Gap Band: facts")]
HOME=f"""
<section class="hero" id="create">
 <div class="hero-main">
  <h1>Tiny Desk AI: put your face in the "Outstanding" Tiny Desk video</h1>
  <p class="lead">Upload one photo and get the 13-second lead-singer clip of the Outstanding Tiny Desk AI trend, recast with you. Vertical 9:16, with the song and a silent copy.</p>
  <div class="card gen" id="account">
   <div id="auth-forms" hidden>
    <h2>1. Create a free account or log in</h2>
    <label>Email <input id="email" type="email" autocomplete="email" required></label>
    <label>Password (8+ characters) <input id="password" type="password" autocomplete="current-password" minlength="8" required></label>
    <div class="row"><button type="button" id="signup" class="btn">Create account</button><button type="button" id="login" class="btn ghost">Log in</button></div>
    <p id="auth-msg" class="msg"></p>
   </div>
   <div id="signed-in" hidden><p class="small">Signed in as <b id="who"></b> · <b id="credits">0</b> credits · <button type="button" id="logout" class="link">Log out</button></p></div>
   <h2>2. Add your photo</h2>
   <input id="photo" type="file" accept="image/jpeg,image/png,image/webp">
   <img id="preview" alt="Your photo preview" hidden>
   <p id="photo-msg" class="msg small">JPEG, PNG or WebP, up to 10 MB. One clear, front-facing face.</p>
   <label class="consent"><input id="consent" type="checkbox"> This photo is of me, or of someone who has given me permission to use it. No minors.</label>
   <p id="sold-out" class="msg error" hidden>Sold out for now. Please check back soon.</p>
   <button type="button" id="generate" class="btn big" disabled>Generate my video</button>
   <p id="gen-hint" class="small muted"></p>
   <p id="gen-status" class="msg"></p>
   <div id="result" hidden>
    <video id="result-video" controls playsinline></video>
    <div class="row"><a id="dl-song" class="btn" download="tiny-desk-ai-with-song.mp4" hidden>Download with song</a><a id="dl-silent" class="btn ghost" download="tiny-desk-ai-silent.mp4" hidden>Download silent</a><a id="dl-raw" class="link" download="tiny-desk-ai-original.mp4">Original file</a></div>
   </div>
   <div id="history-wrap" hidden><h3>Your videos (kept 7 days)</h3><ul id="history"></ul></div>
  </div>
 </div>
 <aside class="hero-side">
  <video src="/media/sample.mp4" poster="/media/sample.jpg" controls muted playsinline loop preload="none"></video>
  <p class="small muted">Sample output (13 s, 480p). AI results vary.</p>
 </aside>
</section>
{DISC}
<section id="pricing"><h2>Pricing</h2><p class="muted">One-time credit packs. 100 credits = one 13-second 480p video. Secure checkout by Stripe.</p>
<div class="packs">
<label class="pack"><input type="radio" name="pack" value="starter" checked><b>Starter</b><span class="price">$9.99</span><span>300 credits · 3 videos</span><span class="small muted">480p</span></label>
<label class="pack"><input type="radio" name="pack" value="plus"><b>Plus</b><span class="price">$19.99</span><span>700 credits · 7 videos</span><span class="small muted">480p</span></label>
<label class="pack"><input type="radio" name="pack" value="pro"><b>Pro</b><span class="price">$49.99</span><span>1,800 credits · 18 videos</span><span class="small muted">480p</span></label>
</div><button type="button" id="buy" class="btn big">Buy credits</button><p id="buy-msg" class="msg"></p></section>
<section id="how-it-works"><h2>How it works</h2><ol class="steps">
<li><b>Upload a clear portrait.</b> Your browser checks for a face first. Confirm the photo is yours or that you have permission.</li>
<li><b>Generate.</b> 100 credits are used and the AI recasts the lead singer. It usually takes about 2 minutes. If it fails, the credits come back.</li>
<li><b>Download.</b> Your browser trims the clip to 13 seconds and gives you a version with the song and a silent copy.</li></ol></section>
<section id="about"><h2>What is Tiny Desk AI?</h2>
<p>The <strong>Tiny Desk AI trend</strong> takes the end of Charlie Wilson's 2023 NPR Tiny Desk concert, where he closes with The Gap Band's "Outstanding", and uses AI to put new people in it. It went viral on TikTok in October 2026 with a parody starring college football coaches whose teams had just lost.</p>
<ul>{"".join(f'<li><a href="{u}">{html.escape(t)}</a></li>' for u,t in GUIDES_LIST)}</ul></section>
<section id="faq"><h2>FAQ</h2>{"".join(f"<details><summary>{html.escape(q)}</summary><p>{html.escape(a)}</p></details>" for q,a in faq)}<p><a href="/faq/">All FAQs</a></p></section>
<section class="cta"><h2>Your lead-singer moment starts here</h2><a class="btn big" href="#create">Add your photo</a></section>
"""
page("/","Tiny Desk AI – Make Your Own Outstanding Tiny Desk AI Video",
"Tiny Desk AI video generator: upload one photo and get the Outstanding Tiny Desk AI clip with you as the lead singer, with the song and a silent copy. Unofficial fan tool.",
HOME,
[web_ld,faq_ld,{"@context":"https://schema.org","@type":"WebApplication","name":"Tiny Desk AI","url":D+"/","applicationCategory":"MultimediaApplication","operatingSystem":"Web","description":"Unofficial photo-to-video tool for the Outstanding Tiny Desk AI trend.","offers":[{"@type":"Offer","price":p,"priceCurrency":"USD","name":n} for n,p in [("Starter 300 credits","9.99"),("Plus 700 credits","19.99"),("Pro 1800 credits","49.99")]]}],
extra_head='<script type="module" src="/app.js"></script>', cls="home")
page("/faq/","Tiny Desk AI FAQ – Song, Length, How It's Made","Answers to common questions about the Tiny Desk AI trend: the song, whether it is real, clip length and how to make your own.",f"<h1>Tiny Desk AI FAQ</h1>{faq_html}",[faq_ld])

art=lambda t,d,p: {"@context":"https://schema.org","@type":"Article","headline":t,"description":d,"datePublished":TODAY,"dateModified":TODAY,"mainEntityOfPage":D+p,"publisher":{"@type":"Organization","name":"Tiny Desk Trend"}}
g1="/guides/what-is-the-tiny-desk-ai-trend/"
t1="Where the Tiny Desk AI Trend Came From"; d1="The origin of the Outstanding Tiny Desk AI meme: Charlie Wilson's 2023 NPR Tiny Desk concert and the October 2026 TikTok parody that started it."
page(g1,t1,d1,f"""<h1>{t1}</h1><p><em>Updated {TODAY}</em></p>
<h2>The source: Charlie Wilson's Tiny Desk concert (2023)</h2>
<p>NPR Music published Charlie Wilson's Tiny Desk Concert on June 5, 2023, as part of its Black Music Month series. His set ended with "Outstanding", the Gap Band song from 1982's <em>The Gap Band IV</em>. (<a href="{SRC_NPR}" rel="nofollow">NPR set list</a>, <a href="{SRC_RS}" rel="nofollow">Rolling Stone</a>)</p>
<h2>The meme: October 2026</h2>
<p>On October 18, 2026, TikTok creator @theburnerfromhe11 posted "College Football's Week 8 All-Loss Tiny Desk Concert": an AI edit of the end of that concert with the coaches of teams that had lost that weekend placed in the band. The caption called it an AI parody. Copies with NFL teams and other groups followed, and people started calling the format the "outstanding tiny desk" set. (<a href="{SRC_HF}" rel="nofollow">source</a>)</p>
<h2>Why it works</h2><p>The joke is the casting: people having a bad week shown joyfully singing a song called "Outstanding". The close-up laugh and the sax solo are the shots everyone recasts.</p>
<h2>Is it real?</h2><p>No. These are AI-edited videos. If you post one, label it as AI and only use faces you have permission to use.</p>
<p><a href="/guides/how-to-make-outstanding-tiny-desk-ai-video/">Next: how it's made →</a></p>""",[art(t1,d1,g1)])
g2="/guides/how-to-make-outstanding-tiny-desk-ai-video/"
t2="How to Make an Outstanding Tiny Desk AI Video"; d2="Plain-English steps for the Outstanding Tiny Desk AI video: the 19-second vertical clip, video edit mode, the 13-second cut, face checks and adding the song back."
steps=[("Get the vertical clip","The viral version is a vertical, roughly 19-second cut (720x1280, 24 fps) with five shots. Working from that vertical version keeps the framing right; widescreen footage tends to get re-framed by the model."),
("Pick one clear photo per person","Use a sharp, front-facing photo of one person. Only use photos of yourself or people who agreed. A face close-up crop plus the full photo helps the model keep both the face and the clothes."),
("Use a video edit mode, not text-to-video","A video-edit model (for example ByteDance's Seedance 2.0 mini in edit mode) takes the clip as reference and keeps its motion, camera and timing while swapping the person. A short prompt that says to keep everything else the same works best; one public write-up found that mentioning the mouth or lip sync made results worse."),
("Split at the 13-second hard cut","These models cap a single generation at about 15 seconds, so split the clip at the hard cut at 13.0 seconds: one 13-second part and one ~6-second part. A seam on a hard cut is invisible."),
("One face per role","Assign each person to a single role. Mapping the same face to two roles caused the swap to fail in published tests."),
("Check the faces before sharing","A failed swap can still come back marked as successful. Look through the output (or run an automatic face check) to make sure the original people are gone."),
("Join the parts and add the song back","The model returns silent video. Join the two parts and lay the original audio underneath; keep a silent copy for apps that mute music. Label the post as AI.")]
howto={"@context":"https://schema.org","@type":"HowTo","name":t2,"description":d2,"step":[{"@type":"HowToStep","name":a,"text":b} for a,b in steps]}
page(g2,t2,d2,f"""<h1>{t2}</h1><p><em>Updated {TODAY}</em></p><p>This is a plain-English summary of a public technical write-up (<a href="{SRC_HF}" rel="nofollow">Hugging Face blog</a>) by another tool maker. Our own generator is <a href="/#create">on the homepage</a>.</p>
<ol>{"".join(f"<li><strong>{a}.</strong> {b}</li>" for a,b in steps)}</ol>
<h2>Shot list of the viral clip</h2><table><tr><th>Shot</th><th>Time (s)</th><th>What's in it</th></tr>
<tr><td>1</td><td>0–1.375</td><td>Lead singer, side-on</td></tr><tr><td>2</td><td>1.375–6.708</td><td>The band</td></tr><tr><td>3</td><td>6.708–13.0</td><td>Lead's big laugh close-up</td></tr><tr><td>4</td><td>13.0–16.375</td><td>Sax solo</td></tr><tr><td>5</td><td>16.375–19.06</td><td>The band again</td></tr></table>
<p>Timings from the <a href="{SRC_HF}" rel="nofollow">same write-up</a>.</p>""",[art(t2,d2,g2),howto])
g3="/guides/outstanding-tiny-desk-song/"
t3="What Is the Song in the Tiny Desk AI Video?"; d3="The Tiny Desk AI trend song is \"Outstanding\" by The Gap Band (1982), sung by Charlie Wilson at his 2023 NPR Tiny Desk concert."
page(g3,t3,d3,f"""<h1>{t3}</h1><p><em>Updated {TODAY}</em></p>
<p><strong>Short answer:</strong> "Outstanding" by <strong>The Gap Band</strong>, from the 1982 album <em>The Gap Band IV</em>. The meme uses Charlie Wilson's live version, the closing song of his NPR Tiny Desk concert published June 5, 2023.</p>
<h2>Who is Charlie Wilson?</h2><p>Charlie Wilson was the lead singer of The Gap Band, which he formed with his brothers Robert and Ronnie; the group's hits ran from the 1970s through the '80s. He later became a frequent hip-hop collaborator, nicknamed "Uncle Charlie" by Snoop Dogg. (<a href="{SRC_NPR}" rel="nofollow">NPR</a>)</p>
<h2>Full Tiny Desk set list</h2><ol><li>Charlie, Last Name Wilson</li><li>Computer Love</li><li>There Goes My Baby</li><li>I'm Blessed</li><li>Yearning For Your Love</li><li>Sweet Yamz</li><li>Outstanding</li></ol><p>Source: <a href="{SRC_NPR}" rel="nofollow">NPR</a>, <a href="{SRC_RS}" rel="nofollow">Rolling Stone</a>.</p>
<h2>Using the song in your post</h2><p>The song is copyrighted. Platforms such as TikTok may mute or restrict uploads that contain it; using the platform's own sound library or a silent copy is the usual workaround.</p>""",[art(t3,d3,g3)])
SRC_WIKI="https://en.wikipedia.org/wiki/Outstanding"
SRC_WS="https://www.whosampled.com/The-Gap-Band/"
SRC_SEA="https://seadanse.com/blog/tiny-desk-ai-for-your-team"
SRC_JUT="https://jutsustudio.com/video-api-pricing/seedance-2-0-mini/"
SRC_WAVE="https://wavespeed.ai/models/bytedance/seedance-2.0-mini/video-edit"
SRC_OT="https://outstandingtinydesk.com/blog/outstanding-tiny-desk-ai-trend"
g4="/guides/tiny-desk-ai-video-generator/"
t4="Tiny Desk AI Video Generator: Free and Paid Options Explained"; d4="Is there a free Tiny Desk AI video generator? What a Tiny Desk AI maker needs, what the AI model behind it costs, and what to check before you upload a photo."
page(g4,t4,d4,f"""<h1>{t4}</h1><p><em>Updated {TODAY}</em></p>{DISC}
<h2>Is there a free Tiny Desk AI generator?</h2><p>Not really. The tools making this trend run a paid video-edit model on every clip. Public price lists put the Seedance 2.0 mini model at roughly $0.02 to $0.07 per second of 480p video, depending on the provider and whether a reference video is used (<a href="{SRC_JUT}" rel="nofollow">price comparison, checked Oct 27, 2026</a>). A full clip needs about 19 seconds of output, plus retries when a face swap fails, so a "free" tool is either a limited trial or paying for it some other way.</p>
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
<h2>Our generator</h2><p>Tiny Desk Trend's own generator is <a href="/#create">on the homepage</a>: one photo in, a 13-second 480p vertical clip out (with the song and a silent copy), from $9.99 for 3 videos. The <a href="/guides/how-to-make-outstanding-tiny-desk-ai-video/">how-to guide</a> covers the method.</p>""",[art(t4,d4,g4)])
g5="/guides/outstanding-tiny-desk-ai-template/"
t5="Outstanding Tiny Desk AI Template: Shots, Timing and Who Goes Where"; d5="The Outstanding Tiny Desk AI template broken down: 9:16 format, 19.06 seconds, five shots, and which roles (lead, keys, backing singers, sax) you can recast."
roles=[("Lead singer","Shots 1 and 3, including the big laugh close-up. This is the role almost every version recasts."),("Keys player","Front and centre in the band shots (2 and 5). Easy to mistake for the lead at first glance."),("Two backing singers","Behind the keys in the band shots."),("Sax player","Gets the solo in shot 4, right after the 13-second cut, so it often goes to the surprise cast member.")]
page(g5,t5,d5,f"""<h1>{t5}</h1><p><em>Updated {TODAY}</em></p>
<p>The "template" everyone recasts is the vertical cut of the last ~19 seconds of Charlie Wilson's 2023 Tiny Desk performance of "Outstanding". Specs below come from a <a href="{SRC_HF}" rel="nofollow">frame-by-frame breakdown</a>.</p>
<h2>Format</h2><ul><li>Vertical 9:16, 720×1280</li><li>24 fps</li><li>19.06 seconds</li><li>Five shots, with a hard cut at exactly 13.0 seconds</li></ul>
<h2>The five shots</h2><table><tr><th>Shot</th><th>Time (s)</th><th>What's in it</th></tr>
<tr><td>1</td><td>0–1.375</td><td>Lead singer's opening line, side-on</td></tr><tr><td>2</td><td>1.375–6.708</td><td>Band: keys in front, two singers behind</td></tr><tr><td>3</td><td>6.708–13.0</td><td>The big laugh close-up of the lead</td></tr><tr><td>4</td><td>13.0–16.375</td><td>Sax solo</td></tr><tr><td>5</td><td>16.375–19.06</td><td>The band again</td></tr></table>
<h2>Roles you can recast</h2><ul>{"".join(f"<li><strong>{a}:</strong> {b}</li>" for a,b in roles)}</ul>
<h2>Tips</h2><ul><li>Use one person per role. Putting the same face in two roles made swaps fail in published tests.</li><li>Use the vertical cut, not the widescreen original, so the framing matches.</li><li>Keep the song timing intact so the audio lines up.</li></ul>
<p>Next: <a href="/guides/outstanding-tiny-desk-meme-ideas/">casting ideas</a> · <a href="/guides/how-to-make-outstanding-tiny-desk-ai-video/">how to make it</a></p>""",[art(t5,d5,g5)])
g6="/guides/outstanding-tiny-desk-meme-ideas/"
t6="Outstanding Tiny Desk Meme: What It Means and Casting Ideas"; d6="What the Outstanding Tiny Desk meme means, how fans cast it (losing teams, coworkers, group chats) and the simple rules good versions follow."
page(g6,t6,d6,f"""<h1>{t6}</h1><p><em>Updated {TODAY}</em></p>
<h2>What the meme means</h2><p>The joke is contrast: people who just had a bad week appear as a joyful band singing a song literally called "Outstanding". The first version, posted October 18, 2026, cast the coaches of college football teams that had lost that weekend and called itself an AI parody (<a href="{SRC_HF}" rel="nofollow">source</a>). Fan versions for NFL teams followed within days (<a href="{SRC_OT}" rel="nofollow">source</a>).</p>
<h2>Casting ideas</h2><ul>
<li><strong>Your team after a loss:</strong> the format the trend started with.</li>
<li><strong>The office:</strong> the team that just missed a deadline, with the manager on sax.</li>
<li><strong>Fantasy league:</strong> last place sings lead.</li>
<li><strong>Family or group chat:</strong> whoever had the worst week gets the close-up.</li>
<li><strong>Yourself:</strong> one photo, you on lead, for your own "outstanding" week.</li></ul>
<h2>Rules good versions follow</h2><ol>
<li>The close-up goes to the person the joke is about.</li>
<li>The sax solo is the punchline, so save it for the surprise.</li>
<li>The caption names the bad week.</li>
<li>Label it as AI, in the caption and with your app's AI label.</li>
<li>Only use faces of people who are in on the joke, and never minors.</li></ol>
<p>See the <a href="/guides/outstanding-tiny-desk-ai-template/">template breakdown</a> for which roles exist.</p>""",[art(t6,d6,g6)])
g7="/guides/outstanding-gap-band-song-facts/"
t7="\"Outstanding\" by The Gap Band: Release Date, Writer, Charts and Samples"; d7="Facts about \"Outstanding\" by The Gap Band, the song in the Tiny Desk AI trend: released November 1982, written by Raymond Calhoun, R&B No. 1, covers and samples."
page(g7,t7,d7,f"""<h1>{t7}</h1><p><em>Updated {TODAY}</em></p>
<table><tr><th>Artist</th><td>The Gap Band</td></tr><tr><th>Album</th><td><em>Gap Band IV</em> (1982)</td></tr><tr><th>Released as a single</th><td>November 1982 (Total Experience)</td></tr><tr><th>Songwriter</th><td>Raymond Calhoun</td></tr><tr><th>Length</th><td>3:19 album version, 6:13 extended version</td></tr><tr><th>Peak charts</th><td>No. 1 US Billboard Hot Black Singles (February 1983), No. 51 Billboard Hot 100, No. 68 UK</td></tr></table>
<p>Source: <a href="{SRC_WIKI}" rel="nofollow">Wikipedia</a>.</p>
<h2>Covers</h2><p>British singer Kenny Thomas covered it in 1990; his version reached No. 12 on the UK Singles Chart (<a href="{SRC_WIKI}" rel="nofollow">Wikipedia</a>).</p>
<h2>Songs that sample it</h2><ul><li>Da Brat, "Da B Side" (1994)</li><li>Ashanti feat. Ja Rule, "Happy" (2002)</li><li>Tyler, The Creator, "911 / Mr. Lonely" (2017)</li></ul><p>Source: <a href="{SRC_WS}" rel="nofollow">WhoSampled</a>.</p>
<h2>Lyrics</h2><p>We don't reproduce the lyrics here because they are copyrighted; licensed lyric sites and streaming apps carry them.</p>
<h2>Why it's in the Tiny Desk AI trend</h2><p>Charlie Wilson, The Gap Band's lead singer, closed his 2023 NPR Tiny Desk concert with it, and the meme recasts the last ~19 seconds of that performance. More in <a href="/guides/outstanding-tiny-desk-song/">What is the song in the Tiny Desk AI video?</a></p>""",[art(t7,d7,g7)])
page("/guides/","Tiny Desk AI Guides","Guides to the Tiny Desk AI trend: origin, how to make one, and the song.",
'<h1>Tiny Desk AI guides</h1><ul>'+"".join(f'<li><a href="{g}">{t}</a></li>' for g,t in [(g1,t1),(g2,t2),(g3,t3),(g4,t4),(g5,t5),(g6,t6),(g7,t7)])+'</ul>')
page("/privacy/","Privacy Policy – Tiny Desk Trend","What tinydesktrend.com collects and why.",f"""<h1>Privacy Policy</h1><p><em>Last updated {TODAY}</em></p>
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
<h2>Contact</h2><p>privacy@tinydesktrend.com</p>""")
page("/terms/","Terms of Use – Tiny Desk Trend","Terms of use for tinydesktrend.com.",f"""<h1>Terms of Use</h1><p><em>Last updated {TODAY}</em></p>
<p>By using tinydesktrend.com you agree to these terms.</p>
<h2>Unofficial site</h2><p>This is an unofficial fan tool. It is not affiliated with, endorsed by or connected to NPR, NPR Music or Tiny Desk Concerts. All trademarks belong to their owners.</p>
<h2>Your photos</h2><p>Only upload photos of yourself or of people who have given you permission. Do not upload photos of minors. Do not use the service to impersonate, harass or deceive anyone, or to make sexual, hateful or illegal content. You are responsible for what you upload and post. Label AI videos as AI when you share them, and follow each platform's rules, including music rules.</p>
<h2>Credits and payments</h2><p>Credits are sold in one-time packs through Stripe. Each 13-second 480p video uses 100 credits. If a generation fails, its credits are returned automatically. Credits have no cash value and cannot be transferred. AI results vary and will not match the original clip exactly. If something goes wrong, contact us and we will look at a refund.</p>
<h2>Availability</h2><p>Generation depends on a third-party video service and limited capacity; it may be sold out or unavailable at times. Videos are kept for 7 days.</p>
<h2>No warranty</h2><p>The service is provided as is, without warranties, to the extent the law allows.</p>
<h2>Contact</h2><p>privacy@tinydesktrend.com</p>""")
import shutil
for root,dirs,files in os.walk("static"):
    for f in files:
        src=os.path.join(root,f); dst=os.path.join(OUT,os.path.relpath(src,"static")); os.makedirs(os.path.dirname(dst),exist_ok=True); shutil.copy(src,dst)
# 404
open(f"{OUT}/404.html","w").write(f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Not found</title><link rel="stylesheet" href="/style.css"></head><body>{NAV}<h1>Page not found</h1><p><a href="/">Go home</a></p></body></html>')
# sitemap/robots/llms
open(f"{OUT}/sitemap.xml","w").write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+"".join(f"<url><loc>{D}{p}</loc><lastmod>{TODAY}</lastmod></url>\n" for p in pages)+"</urlset>\n")
bots=["GPTBot","OAI-SearchBot","ClaudeBot","Claude-SearchBot","PerplexityBot","Google-Extended"]
open(f"{OUT}/robots.txt","w").write("".join(f"User-agent: {b}\nAllow: /\n\n" for b in bots)+"User-agent: *\nAllow: /\n\nSitemap: https://tinydesktrend.com/sitemap.xml\n")
open(f"{OUT}/llms.txt","w").write(f"""# Tiny Desk Trend (tinydesktrend.com)

> Unofficial fan site about the "Outstanding" Tiny Desk AI video trend (October 2026). Not affiliated with NPR or Tiny Desk Concerts. The homepage has a paid photo-to-video generator (13-second 480p vertical clip, credit packs from $9.99).

## Guides
- [{t1}]({D}{g1}): origin of the meme
- [{t2}]({D}{g2}): how the video is made
- [{t3}]({D}{g3}): the song ("Outstanding" by The Gap Band, 1982)
- [{t4}]({D}{g4})
- [{t5}]({D}{g5})
- [{t6}]({D}{g6})
- [{t7}]({D}{g7})
- [FAQ]({D}/faq/)

## Policies
- [Privacy]({D}/privacy/)
- [Terms]({D}/terms/)
""")
# IndexNow key
kp="/workspace/secrets/indexnow-tinydesktrend.txt"
if not os.path.exists(kp):
    open(kp,"w").write(secrets.token_hex(16)); os.chmod(kp,0o600)
key=open(kp).read().strip(); open(f"{OUT}/{key}.txt","w").write(key)
# images
B="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"; R="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
im=Image.new("RGB",(1200,630),"#2a1a10"); d=ImageDraw.Draw(im)
d.rectangle([0,560,1200,630],fill="#b0652a")
d.text((80,150),"Tiny Desk AI",font=ImageFont.truetype(B,110),fill="#ffd27a")
d.text((80,300),"The \u201cOutstanding\u201d Tiny Desk AI video trend",font=ImageFont.truetype(R,46),fill="#fbf7f0")
d.text((80,380),"Origin \u00b7 the song \u00b7 how it's made",font=ImageFont.truetype(R,40),fill="#e6d2b5")
d.text((80,575),"tinydesktrend.com  \u00b7  unofficial fan site",font=ImageFont.truetype(R,32),fill="#fff")
im.save(f"{OUT}/og.png")
fi=Image.new("RGBA",(64,64),(0,0,0,0)); fd=ImageDraw.Draw(fi); fd.rounded_rectangle([0,0,63,63],12,fill="#b0652a"); fd.text((10,8),"TD",font=ImageFont.truetype(B,34),fill="#fff")
fi.save(f"{OUT}/favicon.ico",sizes=[(16,16),(32,32),(48,48),(64,64)])
open(f"{OUT}/favicon.svg","w").write('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="12" fill="#b0652a"/><text x="32" y="43" font-family="Arial,sans-serif" font-weight="bold" font-size="30" fill="#fff" text-anchor="middle">TD</text></svg>')
print(pages)
