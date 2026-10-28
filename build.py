import os, json, html, datetime, secrets
from PIL import Image, ImageDraw, ImageFont
D="https://tinydesktrend.com"; OUT="public"; TODAY="2026-10-28"
os.makedirs(OUT,exist_ok=True)
NAV='<nav><a href="/">Tiny Desk AI</a> <a href="/guides/">Guides</a> <a href="/faq/">FAQ</a></nav>'
DISC='<p class="disc"><strong>Unofficial fan tool.</strong> Tiny Desk Trend is not affiliated with, endorsed by, or connected to NPR, NPR Music, or Tiny Desk Concerts. No NPR or Tiny Desk logos or official assets are used on this site.</p>'
FOOT=f'<footer>{DISC}<p><a href="/privacy/">Privacy</a> · <a href="/terms/">Terms</a> · <a href="/guides/">Guides</a> · <a href="/faq/">FAQ</a></p><p>© 2026 tinydesktrend.com</p></footer>'
CSS="""body{font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif;max-width:760px;margin:0 auto;padding:16px 20px;line-height:1.6;color:#1f1b16;background:#fbf7f0}nav a{margin-right:14px;font-weight:600;color:#7a3e12;text-decoration:none}h1{font-size:2rem;line-height:1.2}h2{margin-top:2rem}.disc{background:#fff3d6;border:1px solid #e8c77a;padding:10px 14px;border-radius:8px;font-size:.95rem}.soon{border:2px dashed #b07a3a;border-radius:12px;padding:20px;text-align:center;background:#fff}.soon b{font-size:1.3rem}footer{margin-top:3rem;border-top:1px solid #ddd;padding-top:1rem;font-size:.9rem}a{color:#7a3e12}table{border-collapse:collapse}td,th{border:1px solid #ccc;padding:4px 8px}"""
open(f"{OUT}/style.css","w").write(CSS)
pages=[]
def page(path,title,desc,body,ld=None):
    url=D+path
    lds="".join(f'<script type="application/ld+json">{json.dumps(x)}</script>' for x in (ld or []))
    h=f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title><meta name="description" content="{html.escape(desc)}"><link rel="canonical" href="{url}">
<link rel="icon" href="/favicon.ico" sizes="any"><link rel="icon" href="/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="/style.css">
<meta property="og:type" content="website"><meta property="og:site_name" content="Tiny Desk Trend"><meta property="og:title" content="{html.escape(title)}"><meta property="og:description" content="{html.escape(desc)}"><meta property="og:url" content="{url}"><meta property="og:image" content="{D}/og.png"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{html.escape(title)}"><meta name="twitter:description" content="{html.escape(desc)}"><meta name="twitter:image" content="{D}/og.png">{lds}</head>
<body>{NAV}<main>{body}</main>{FOOT}</body></html>"""
    d=OUT+path; os.makedirs(d,exist_ok=True); open(d+"index.html","w").write(h); pages.append(path)

SRC_NPR="https://www.npr.org/2023/06/05/1179416602/charlie-wilson-tiny-desk-concert"
SRC_RS="https://www.rollingstone.com/music/music-news/charlie-wilson-gap-band-tiny-desk-1234759558/"
SRC_HF="https://huggingface.co/blog/trendrecast/how-to-make-outstanding-tiny-desk-ai-video"

faq=[
("What is the Tiny Desk AI trend?","It is an AI parody meme: people re-cast the closing moment of Charlie Wilson's 2023 NPR Tiny Desk concert, where he sings \"Outstanding\", with new faces swapped in by an AI video model. It took off on TikTok in October 2026 after a clip put college football coaches whose teams had just lost into the band."),
("What song is in the Tiny Desk AI video?","\"Outstanding\" by The Gap Band, from their 1982 album The Gap Band IV. Charlie Wilson, The Gap Band's lead singer, closed his June 2023 Tiny Desk concert with it."),
("Is the Tiny Desk AI video real?","No. The viral versions are AI edits of real concert footage. The first creator labelled it \"an AI parody\" in the caption, and you should label yours as AI too."),
("How long is the clip?","The viral vertical version is about 19 seconds long (720x1280, 24 fps) and keeps five shots from the end of the concert."),
("Can I make one with my own photo?","Yes. AI video-edit models can replace the lead singer using a reference photo. Our generator is not live yet; the guide explains the general method. Only use photos of yourself or of people who have given you permission."),
("Is this site official?","No. Tiny Desk Trend is an unofficial fan tool and is not affiliated with NPR, NPR Music or Tiny Desk Concerts."),
("Will the generator include the song?","The plan is to deliver one copy with the original song and one silent copy, for platforms that mute music. Check your platform's music rules before posting."),
("When does the generator launch?","It is not available yet. This page will be updated when it launches. We do not take sign-ups or payments today."),
]
faq_html="".join(f"<h3>{html.escape(q)}</h3><p>{html.escape(a)}</p>" for q,a in faq)
faq_ld={"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in faq]}
SOON='<section class="soon" id="generator"><b>Generator launching soon</b><p>Upload one photo, get the ~19-second vertical "Outstanding" clip with you on lead vocals, plus a silent copy. Not available yet: nothing to upload, nothing to buy.</p><p style="font-size:.9rem">When it launches you will have to confirm that the photo is of you or of someone who gave you permission. No photos of other people without consent, no minors, no impersonation.</p></section>'
web_ld={"@context":"https://schema.org","@type":"WebSite","name":"Tiny Desk Trend","url":D+"/"}
page("/","Tiny Desk AI – The Outstanding Tiny Desk AI Video Trend, Explained",
"Tiny Desk AI trend explained: the Outstanding Tiny Desk AI video, the song, how it is made, and a photo-to-video generator coming soon. Unofficial fan site.",
f"""<h1>Tiny Desk AI: the "Outstanding" Tiny Desk AI video trend</h1>{DISC}
<p>The <strong>Tiny Desk AI trend</strong> takes the last ~19 seconds of Charlie Wilson's 2023 NPR Tiny Desk concert, where he closes with The Gap Band's "Outstanding", and uses an AI video model to put new people in the band. It went viral on TikTok in October 2026 with a parody starring college football coaches whose teams had just lost.</p>
<p>The effect: the original shots, cuts and song stay the same, but the lead singer laughing in the close-up (and sometimes the keys player, the sax solo and the backing singers) are replaced by someone else.</p>
{SOON}
<h2>Guides</h2><ul>
<li><a href="/guides/what-is-the-tiny-desk-ai-trend/">Where the Tiny Desk AI trend came from</a></li>
<li><a href="/guides/how-to-make-outstanding-tiny-desk-ai-video/">How to make an Outstanding Tiny Desk AI video</a></li>
<li><a href="/guides/outstanding-tiny-desk-song/">What is the song in the Tiny Desk AI video?</a></li>
<li><a href="/guides/tiny-desk-ai-video-generator/">Tiny Desk AI video generator: free and paid options</a></li>
<li><a href="/guides/outstanding-tiny-desk-ai-template/">Outstanding Tiny Desk AI template</a></li>
<li><a href="/guides/outstanding-tiny-desk-meme-ideas/">Outstanding Tiny Desk meme ideas</a></li>
<li><a href="/guides/outstanding-gap-band-song-facts/">"Outstanding" by The Gap Band: facts</a></li></ul>
<h2>Quick answers</h2>{"".join(f"<h3>{html.escape(q)}</h3><p>{html.escape(a)}</p>" for q,a in faq[:4])}<p><a href="/faq/">All FAQs →</a></p>""",
[web_ld,{"@context":"https://schema.org","@type":"WebApplication","name":"Tiny Desk AI (coming soon)","url":D+"/","applicationCategory":"MultimediaApplication","operatingSystem":"Web","description":"Unofficial photo-to-video tool for the Outstanding Tiny Desk AI trend. Launching soon."}])
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
page(g2,t2,d2,f"""<h1>{t2}</h1><p><em>Updated {TODAY}</em></p><p>This is a plain-English summary of a public technical write-up (<a href="{SRC_HF}" rel="nofollow">Hugging Face blog</a>) by another tool maker. Our own generator is <a href="/#generator">launching soon</a>.</p>
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
<h2>Our generator</h2><p>Tiny Desk Trend's own generator is <a href="/#generator">launching soon</a>. Until then, the <a href="/guides/how-to-make-outstanding-tiny-desk-ai-video/">how-to guide</a> covers the method.</p>""",[art(t4,d4,g4)])
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
page("/privacy/","Privacy Policy – Tiny Desk Trend","What tinydesktrend.com collects (almost nothing).",f"""<h1>Privacy Policy</h1><p><em>Last updated {TODAY}</em></p>
<p>tinydesktrend.com is currently a static information site. It has no accounts, no forms, no uploads, no payments, no cookies and no analytics or advertising scripts.</p>
<h2>Hosting logs</h2><p>The site is served by Cloudflare. Like any web host, Cloudflare processes technical request data (such as IP address, user agent and requested URL) to deliver the site and protect it from abuse. See Cloudflare's privacy policy at https://www.cloudflare.com/privacypolicy/.</p>
<h2>Future generator</h2><p>The photo-to-video generator is not live. Before it launches this policy will be updated to describe exactly what it collects.</p>
<h2>Contact</h2><p>privacy@tinydesktrend.com</p>""")
page("/terms/","Terms of Use – Tiny Desk Trend","Terms of use for tinydesktrend.com.",f"""<h1>Terms of Use</h1><p><em>Last updated {TODAY}</em></p>
<p>By using tinydesktrend.com you agree to these terms.</p>
<h2>Unofficial site</h2><p>This is an unofficial fan site. It is not affiliated with, endorsed by or connected to NPR, NPR Music or Tiny Desk Concerts. All trademarks belong to their owners.</p>
<h2>Content</h2><p>The guides are provided for information only, as is, without warranties. We link to third-party sources we do not control.</p>
<h2>Your use of AI video</h2><p>If you make AI videos, only use images of yourself or people who have given permission, do not depict minors, do not impersonate or deceive, label AI content, and follow the rules of the platforms you post on, including music rights.</p>
<h2>Changes</h2><p>No paid service is offered today. These terms will be updated before any generator or payment launches.</p>
<h2>Contact</h2><p>privacy@tinydesktrend.com</p>""")
# 404
open(f"{OUT}/404.html","w").write(f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Not found</title><link rel="stylesheet" href="/style.css"></head><body>{NAV}<h1>Page not found</h1><p><a href="/">Go home</a></p></body></html>')
# sitemap/robots/llms
open(f"{OUT}/sitemap.xml","w").write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+"".join(f"<url><loc>{D}{p}</loc><lastmod>{TODAY}</lastmod></url>\n" for p in pages)+"</urlset>\n")
bots=["GPTBot","OAI-SearchBot","ClaudeBot","Claude-SearchBot","PerplexityBot","Google-Extended"]
open(f"{OUT}/robots.txt","w").write("".join(f"User-agent: {b}\nAllow: /\n\n" for b in bots)+"User-agent: *\nAllow: /\n\nSitemap: https://tinydesktrend.com/sitemap.xml\n")
open(f"{OUT}/llms.txt","w").write(f"""# Tiny Desk Trend (tinydesktrend.com)

> Unofficial fan site about the "Outstanding" Tiny Desk AI video trend (October 2026). Not affiliated with NPR or Tiny Desk Concerts. A photo-to-video generator is planned but not live.

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
