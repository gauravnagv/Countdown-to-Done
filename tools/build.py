"""
Rebuilds every generated asset in the project:
  - screenshots/            showcase PNGs (phone 1080x1920, laptop 1920x1080, 3 themes)
  - screenshots/daily/      one wallpaper per day from T-6 to T-0 (swap it each morning)
  - 03_Reminders/countdown_reminders.ics   daily calendar reminders

Change TITLE / DEADLINE below, then run:  python tools/build.py
Needs Google Chrome or Microsoft Edge installed.
"""
import os
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import urlencode

TITLE = "Countdown to Done"
DEADLINE = datetime(2026, 11, 22, 23, 59)
TODAY = datetime(2026, 11, 16, 9, 0)          # "now" used for the showcase screenshots

ROOT = Path(__file__).resolve().parent.parent
HTML = ROOT / "02_Lock_Screen" / "lockscreen.html"
SHOTS = ROOT / "screenshots"
DAILY = SHOTS / "daily"

BROWSERS = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
]
BROWSER = next(b for b in BROWSERS if os.path.exists(b))

SIZES = {"phone": (1080, 1920), "laptop": (1920, 1080)}


def render(out: Path, mode: str, theme: str, now: datetime, static: bool = True):
    params = {
        "title": TITLE,
        "deadline": DEADLINE.strftime("%Y-%m-%dT%H:%M"),
        "mode": mode,
        "theme": theme,
        "now": now.strftime("%Y-%m-%dT%H:%M"),
    }
    if static:
        params["static"] = "1"
    url = HTML.as_uri() + "?" + urlencode(params)
    w, h = SIZES[mode]
    out.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run([
        BROWSER, "--headless=new", "--disable-gpu", "--hide-scrollbars",
        "--force-device-scale-factor=1", f"--window-size={w},{h}",
        "--virtual-time-budget=4000", f"--screenshot={out}", url,
    ], check=True, capture_output=True)
    print("rendered", out.relative_to(ROOT))


# ---- daily plan (also used for the reminders) ----
DAILY_PLAN = [
    (6, "Close the gaps in the first draft; write the open-issues list."),
    (5, "Tackle the hardest remaining piece first thing."),
    (4, "Full self-review with fresh eyes; line up a reviewer for tomorrow."),
    (3, "CHECKPOINT T-3: send to reviewer, start polishing."),
    (2, "Apply feedback - top 3 issues only."),
    (1, "CHECKPOINT T-1: final QA, export, back up, prep submission."),
    (0, "DEADLINE: submit before noon (11:59 PM is the hard stop)."),
]


def build_ics():
    def esc(s):
        return s.replace("\\", "\\\\").replace(",", "\\,").replace(";", "\\;")

    stamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    lines = [
        "BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//Countdown Lock Screen//EN",
        "CALSCALE:GREGORIAN", "METHOD:PUBLISH", f"X-WR-CALNAME:{esc(TITLE)} countdown",
    ]
    dl_day = DEADLINE.replace(hour=0, minute=0)
    for t, task in DAILY_PLAN:
        day = dl_day - timedelta(days=t)
        start = day.replace(hour=9, minute=0)
        end = start + timedelta(minutes=15)
        summary = f"T-{t} | {TITLE}: {task.split(':')[0] if 'CHECKPOINT' in task or 'DEADLINE' in task else 'Daily focus'}"
        lines += [
            "BEGIN:VEVENT",
            f"UID:countdown-t{t}-{DEADLINE:%Y%m%d}@lockscreen",
            f"DTSTAMP:{stamp}",
            f"DTSTART:{start:%Y%m%dT%H%M%S}",
            f"DTEND:{end:%Y%m%dT%H%M%S}",
            f"SUMMARY:{esc(summary)}",
            f"DESCRIPTION:{esc(f'{t} day(s) to go. Today: {task} Swap your lock screen to screenshots/daily/phone_T-{t}.png')}",
            "BEGIN:VALARM", "ACTION:DISPLAY", f"DESCRIPTION:{esc(f'T-{t}: {task}')}",
            "TRIGGER:PT0M", "END:VALARM",
            "END:VEVENT",
        ]
    # hard deadline event
    lines += [
        "BEGIN:VEVENT",
        f"UID:countdown-deadline-{DEADLINE:%Y%m%d}@lockscreen",
        f"DTSTAMP:{stamp}",
        f"DTSTART:{DEADLINE - timedelta(hours=2):%Y%m%dT%H%M%S}",
        f"DTEND:{DEADLINE:%Y%m%dT%H%M%S}",
        f"SUMMARY:{esc('HARD DEADLINE - ' + TITLE)}",
        "BEGIN:VALARM", "ACTION:DISPLAY", "DESCRIPTION:2 hours to the hard deadline", "TRIGGER:PT0M", "END:VALARM",
        "END:VEVENT",
        "END:VCALENDAR",
    ]
    out = ROOT / "03_Reminders" / "countdown_reminders.ics"
    out.write_bytes(("\r\n".join(lines) + "\r\n").encode("utf-8"))
    print("wrote", out.relative_to(ROOT))


if __name__ == "__main__":
    # showcase screenshots
    for theme in ("sage", "dusk", "clay"):
        for mode in ("phone", "laptop"):
            render(SHOTS / f"{mode}_{theme}.png", mode, theme, TODAY)
    # daily wallpaper pack T-6 .. T-0
    dl_day = DEADLINE.replace(hour=9, minute=0)
    for t, _ in DAILY_PLAN:
        for mode in ("phone", "laptop"):
            render(DAILY / f"{mode}_T-{t}.png", mode, "sage", dl_day - timedelta(days=t))
    build_ics()
