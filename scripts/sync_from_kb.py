#!/usr/bin/env python3
"""Copy the public subset of research-kb into data/research.json.

research-kb (private) is the single source for publications, conference
abstracts and grants. This script reads it locally and writes only public
fields: titles, authors, venues, DOIs, grant titles/funders/periods/roles.
It never copies research-kb's PI block (phone, birth date, address) or grant
amounts/terms.

    python3 scripts/sync_from_kb.py [--kb ~/projects/research-kb]
"""
from __future__ import annotations

import argparse
from datetime import date
import importlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "research.json"

# research-kb stores most grant titles in Chinese only; these are our English renderings.
GRANT_TITLE_EN = {
    "G1": "An AI endoscopic image model to predict malignancy risk and submucosal invasion depth "
          "of colorectal laterally spreading tumors: a multicentre study",
    "G3": "LLM-based structured analysis of colonoscopy and pathology reports to optimise "
          "surveillance intervals: clinical implementation and long-term impact",
    "G4": "A retrieval-augmented LLM chatbot for bowel-preparation education and a stool-image "
          "recognition system: development and prospective feasibility study",
}
FUNDER_EN = {
    "國家科學及技術委員會": "National Science and Technology Council (NSTC), Taiwan",
    "國立臺灣大學醫學院附設醫院癌醫中心分院": "National Taiwan University Cancer Center",
    "國立臺灣大學醫學院附設醫院癌醫中心分院、國立臺灣科技大學":
        "NTU Cancer Center – National Taiwan University of Science and Technology Joint Research Program",
}
ROLE_EN = {"主持人": "Principal Investigator"}
TALK_KIND = {"invited_lecture": "Invited lecture", "conference_oral": "Oral presentation",
             "conference_poster": "Poster", "grand_round": "Grand Round", "workshop_teaching": "Teaching",
             "public_education": "Public education", "other": "Talk"}


def _clean_venue(text: str) -> str:
    # "DDW 2025（Gastroenterology 169(1):S-1027-S-1028）" -> "DDW 2025 (Gastroenterology 169(1):S-1027-S-1028)"
    return text.replace("（", " (").replace("）", ")").strip()


def build(kb: Path) -> dict:
    sys.path.insert(0, str(kb))
    profile = importlib.import_module("data.profile")
    grants = importlib.import_module("data.grants")
    journals = [{
        "id": p["id"], "title": p["title"], "authors": p["authors_en"],
        "journal": p["journal_full"], "journal_abbr": p["journal_abbr"], "year": str(p["year"]),
        "doi": p["doi"], "pubmed": p.get("pubmed", ""),
        "first_author": p["authors_en"].startswith(profile.WU_EN),
        "selected": bool(p["is_representative"]),
    } for p in profile.JOURNAL_PUBS]
    journals.sort(key=lambda j: (j["year"], j["id"]), reverse=True)
    abstracts = [{
        "id": a["md_id"], "title": a["title"], "authors": a["authors_en"],
        "venue": _clean_venue(a["conference_detail"]), "year": str(a["year"]),
    } for a in profile.ABSTRACT_PUBS]
    abstracts.sort(key=lambda a: a["year"], reverse=True)
    in_prep = [{"title": i["title"].split("（")[0].strip()} for i in profile.IN_PREP]
    out_grants = []
    for g in grants.GRANTS:
        start, end = (x.split("/")[0] for x in g["period_ad"].split("–"))
        out_grants.append({
            "id": g["id"],
            "title_en": g["title_en"] or GRANT_TITLE_EN.get(g["id"], ""),
            "title_zh": g["title_zh"],
            "number": g["number"],
            "funder": FUNDER_EN.get(g["funder"], g["funder"]),
            "years": start if start == end else f"{start}–{end}",
            "start": g["period_ad"].split("–")[0],
            "role": ROLE_EN.get(g["role"], g["role"]),
        })
    out_grants.sort(key=lambda g: g["start"], reverse=True)
    missing = [g["id"] for g in out_grants if not g["title_en"]]
    if missing:
        raise SystemExit(f"Add an English title to GRANT_TITLE_EN for: {missing}")
    talks_path = kb / "data" / "talks.json"
    talks = []
    if talks_path.exists():
        for t in json.loads(talks_path.read_text(encoding="utf-8"))["talks"]:
            if not t.get("public") or t.get("hidden") or not t.get("date") or t["date"] > date.today().isoformat():
                continue
            talks.append({  # public fields only; no Drive IDs or file names
                "date": t["date"], "kind": TALK_KIND.get(t["type"], "Talk"),
                "title": t["title_en"], "title_zh": t.get("title_zh", ""),
                "venue": ", ".join(x for x in (t.get("event"), t.get("location")) if x),
                "venue_zh": t.get("event_zh", ""),
                "slides": t.get("public_slides", ""), "video": t.get("public_video", ""),
            })
    return {"source": "research-kb", "journals": journals, "abstracts": abstracts,
            "in_prep": in_prep, "grants": out_grants, "talks": talks}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--kb", type=Path, default=Path.home() / "projects" / "research-kb")
    args = ap.parse_args()
    text = json.dumps(build(args.kb.resolve()), ensure_ascii=False, indent=2) + "\n"
    changed = not OUT.exists() or OUT.read_text(encoding="utf-8") != text
    OUT.write_text(text, encoding="utf-8")
    # Explicitly allowlisted scholarship metadata; preserve manually curated profile entries.
    sys.path.insert(0, str(args.kb.resolve()))
    kb_profile = importlib.import_module("data.profile")
    path = ROOT / "data" / "profile.json"
    current_text = path.read_text(encoding="utf-8")
    public_profile = json.loads(current_text)
    for award in kb_profile.SCHOLARSHIPS:
        item = {"id": award["id"], "year": str(award["year"]),
                "en": award["title_en"], "zh": award["title_zh"],
                "venue": award["institution_en"],
                "venue_zh": award["institution_zh"] + f" · {award['academic_year_roc']}學年度"}
        public_profile["awards"] = [a for a in public_profile["awards"] if a.get("id") != award["id"]]
        public_profile["awards"].append(item)
    for award in kb_profile.INSTITUTIONAL_AWARDS:
        item = {"id": award["id"], "year": str(award["year"]),
                "en": award["title_en"], "zh": award["title_zh"], "highlight": True,
                "venue": award["team_en"] or award["institution_en"],
                "venue_zh": award["team_zh"] or award["institution_zh"]}
        public_profile["awards"] = [a for a in public_profile["awards"] if a.get("id") != award["id"]]
        public_profile["awards"].append(item)
    public_profile["awards"].sort(key=lambda a: str(a["year"]), reverse=True)
    # Keep unrelated hand-edited JSON formatting stable.
    awards_json = json.dumps(public_profile["awards"], ensure_ascii=False, indent=2).replace("\n", "\n  ")
    updated_profile, replacements = re.subn(r'("awards": )\[[\s\S]*?\](?=,\n)',
                          lambda match: match[1] + awards_json, current_text, count=1)
    if replacements != 1:
        raise SystemExit("Expected one awards array in data/profile.json")
    path.write_text(updated_profile, encoding="utf-8")
    print(f"{'updated' if updated_profile != current_text else 'unchanged'}: data/profile.json")

    print(f"{'updated' if changed else 'unchanged'}: {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
