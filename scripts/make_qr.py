#!/usr/bin/env python3
"""Regenerate the QR codes for the site URL (needs `pip install segno`; local only).

assets/qr.svg is shown on the page; qr-print.png / qr-print.svg are for posters and slides.
The URL never changes, so printed codes keep working after every content update.
"""
import json
from pathlib import Path

import segno

ROOT = Path(__file__).resolve().parents[1]
url = json.loads((ROOT / "data" / "profile.json").read_text(encoding="utf-8"))["site_url"]
qr = segno.make(url, error="q")
qr.save(ROOT / "assets" / "qr.svg", scale=6, border=2, dark="#1d5a47")
qr.save(ROOT / "qr-print.svg", scale=10, border=4)
qr.save(ROOT / "qr-print.png", scale=24, border=4)
print(f"QR -> {url}")
