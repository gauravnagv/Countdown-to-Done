"""Builds an upload-friendly folder (JPGs + one PDF) next to the project."""
import subprocess
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SHOTS = ROOT / "screenshots"
OUT = ROOT.parent / "Countdown_Lock_Screen_Upload"
OUT.mkdir(exist_ok=True)
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

# 1. compressed JPGs
picks = {
    "1_phone_lock_screen_sage.jpg": "phone_sage.png",
    "2_laptop_lock_screen_sage.jpg": "laptop_sage.png",
    "3_phone_lock_screen_dusk.jpg": "phone_dusk.png",
    "4_laptop_lock_screen_dusk.jpg": "laptop_dusk.png",
    "5_phone_lock_screen_clay.jpg": "phone_clay.png",
    "6_laptop_lock_screen_clay.jpg": "laptop_clay.png",
}
for dst, src in picks.items():
    Image.open(SHOTS / src).convert("RGB").save(OUT / dst, "JPEG", quality=88, optimize=True)

# 2. PDF: description + images
DESC = """
<p>November is a crowded month for me, with coursework, project work, interviews and this challenge all competing for time. Instead of trying to track everything at once, I picked the one deadline I can't move, my <b>Final Project Submission on November 22</b>, and built a system around it.</p>
<h2>Planning backward</h2>
<p>I started at the deadline and worked back. I split the last 14 days into five T-minus checkpoints, each with a clear definition of "done":</p>
<ul>
<li><b>T-14 (Nov 8): Scope locked.</b> The deliverable, success criteria and full task list are written down.</li>
<li><b>T-7 (Nov 15): First full draft.</b> A rough version of every part exists, with nothing left blank.</li>
<li><b>T-3 (Nov 19): Feedback &amp; polish.</b> A reviewer has seen it and I'm fixing the top issues.</li>
<li><b>T-1 (Nov 21): Final QA + buffer.</b> Proofread, tested, exported and backed up.</li>
<li><b>T-0 (Nov 22): Submit.</b> Early in the day, with 11:59 PM kept as an emergency buffer.</li>
</ul>
<p>Each day in the final week also gets one main focus, so I know exactly what matters when I sit down. I listed the main risks too, like a reviewer replying late or upload problems, and planned a buffer for each.</p>
<h2>Designing the lock screen</h2>
<p>A plan only helps if I see it, so I turned it into a lock screen I notice every time I pick up my phone. I wanted it to feel natural and modern, calm rather than stressful. It uses a sage green and warm sand gradient, a terracotta accent, a line-drawn leaf sprig and a light paper texture. Big serif numbers show the days left, inside a progress ring that fills as the 14-day window passes. Below it, a checkpoint track shows what's done and what's next, with a short motivation line that changes each day ("Hardest part first," "Ask for feedback early," "Ship it.").</p>
<p>I kept the top quarter of the phone screen clear so the phone's clock never covers anything. I made two formats, <b>9:16 for phone</b> and <b>16:9 for laptop</b>, in three color themes (Sage, Dusk and Clay). I also made a daily wallpaper pack from T-6 to T-0, so the screen updates as the deadline gets closer.</p>
<h2>Staying on track</h2>
<p>To make the plan stick, I set up a <b>daily 9 AM reminder</b> that tells me that day's task and reminds me to swap in the new wallpaper. There is also a final alert two hours before the deadline.</p>
<h2>What I learned</h2>
<p>Working backward from a fixed date turns a vague goal into concrete steps. Seeing the countdown every time I unlock my phone keeps the deadline in view without effort.</p>
"""

def img(name, cls):
    return f'<img class="{cls}" src="{(OUT / name).as_uri()}">'

html = f"""<!doctype html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400&family=Inter:wght@400;600&display=swap" rel="stylesheet">
<style>
@page {{ size: A4; margin: 16mm; }}
body {{ font-family: Inter, sans-serif; color:#2C372B; font-size:10.5pt; line-height:1.5; }}
h1 {{ font-family: Fraunces, Georgia, serif; font-weight:400; font-size:24pt; margin:0 0 4pt; }}
h2 {{ font-family: Fraunces, Georgia, serif; font-weight:400; font-size:14pt; margin:14pt 0 4pt; color:#6F8A5E; }}
.sub {{ color:#66705F; margin-bottom:12pt; }}
ul {{ padding-left:16pt; }} li {{ margin:2pt 0; }}
.page {{ page-break-before: always; text-align:center; }}
.row {{ display:flex; gap:8mm; justify-content:center; }}
.phone {{ height:225mm; border-radius:6mm; }}
.phone3 {{ width:56mm; border-radius:4mm; }}
.laptop {{ width:100%; border-radius:3mm; margin-bottom:6mm; }}
.cap {{ color:#66705F; font-size:9pt; margin-top:4pt; }}
</style></head><body>
<h1>Countdown to Done</h1>
<div class="sub">A calm lock screen for my November 22 deadline</div>
{DESC}
<div class="page">{img("1_phone_lock_screen_sage.jpg","phone")}<div class="cap">Phone lock screen (9:16) · Sage</div></div>
<div class="page">{img("2_laptop_lock_screen_sage.jpg","laptop")}{img("4_laptop_lock_screen_dusk.jpg","laptop")}<div class="cap">Laptop lock screen (16:9) · Sage and Dusk</div></div>
<div class="page"><div class="row">{img("1_phone_lock_screen_sage.jpg","phone3")}{img("3_phone_lock_screen_dusk.jpg","phone3")}{img("5_phone_lock_screen_clay.jpg","phone3")}</div>
<div class="cap">Three themes: Sage · Dusk · Clay</div></div>
</body></html>"""

tmp = OUT / "_print.html"
tmp.write_text(html, encoding="utf-8")
pdf = OUT / "Countdown_to_Done.pdf"
subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                "--virtual-time-budget=4000", "--allow-file-access-from-files",
                f"--print-to-pdf={pdf}", tmp.as_uri()], check=True, capture_output=True)
tmp.unlink()

for f in sorted(OUT.iterdir()):
    print(f"{f.name:40s} {f.stat().st_size/1024:8.0f} KB")
