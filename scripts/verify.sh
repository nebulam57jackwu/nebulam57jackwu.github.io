#!/usr/bin/env bash
# Build the site and fail if private data or broken structure would be published.
set -euo pipefail
cd "$(dirname "$0")/.."
python3 scripts/build.py >/dev/null
python3 - <<'PY'
import json, re, sys
from html.parser import HTMLParser
from pathlib import Path
site = Path("build/site")
text = "\n".join(p.read_text(encoding="utf-8") for p in [*Path("data").glob("*.json"), site / "index.html", site / "contact.vcf"])
# Phone numbers, Taiwanese ID / licence numbers, birth dates, home address fragments.
banned = [r"09\d{2}-?\d{3}-?\d{3}", r"\+886", r"醫字", r"專醫字", r"1991", r"和平東路", r"基隆路", r"[A-Z][12]\d{8}"]
hits = [b for b in banned if re.search(b, text)]
if hits:
    sys.exit(f"FAIL private data pattern found: {hits}")
class P(HTMLParser):
    ids = set(); hrefs = []
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "id" in a: self.ids.add(a["id"])
        if tag == "a" and a.get("href", "").startswith("#") and len(a["href"]) > 1: self.hrefs.append(a["href"][1:])
p = P(); p.feed((site / "index.html").read_text(encoding="utf-8"))
missing = [h for h in p.hrefs if h not in p.ids]
if missing:
    sys.exit(f"FAIL broken in-page links: {missing}")
for f in ("assets/portrait.jpg", "assets/qr.svg", "assets/style.css", "assets/favicon.svg"):
    if not (site / f).exists(): sys.exit(f"FAIL missing {f}")
json.loads(json.dumps(json.load(open("data/profile.json"))))
print("verify PASS")
PY
