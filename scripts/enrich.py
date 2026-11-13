#!/usr/bin/env python3
"""Scheduled refresh, run by GitHub Actions before each build.

1. Citation counts for every journal DOI from OpenAlex  -> build/metrics.json
2. PubMed search for "Wu, Hao-Yu" + Taiwan; any PMID that is neither a known
   paper (matched by DOI) nor listed in data/pubmed_review.json is written to
   build/new_pubmed.json so the workflow can open a review issue. Name matches
   are ambiguous, so nothing is published automatically.

Network failures never fail the build: the page simply omits the counts.
"""
from __future__ import annotations

import json
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / "build"
PUBMED_TERM = '"Wu, Hao-Yu"[Author - Full] AND Taiwan[Affiliation]'
UA = {"User-Agent": "haoyu-wu-academic-site (GitHub Pages build)"}


def _get(url: str) -> dict:
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=20) as r:
        return json.load(r)


def citations(dois: list[str]) -> dict[str, int]:
    out = {}
    for doi in dois:
        try:
            data = _get(f"https://api.openalex.org/works/doi:{urllib.parse.quote(doi)}?select=cited_by_count")
            out[doi] = int(data.get("cited_by_count") or 0)
        except Exception as exc:  # noqa: BLE001 - best effort
            print(f"  openalex {doi}: {exc}", file=sys.stderr)
    return out


def new_pubmed(known_dois: set[str], reviewed: set[str]) -> list[dict]:
    base = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
    ids = _get(base + "esearch.fcgi?db=pubmed&retmode=json&retmax=200&term="
               + urllib.parse.quote(PUBMED_TERM))["esearchresult"]["idlist"]
    ids = [i for i in ids if i not in reviewed]
    if not ids:
        return []
    res = _get(base + "esummary.fcgi?db=pubmed&retmode=json&id=" + ",".join(ids))["result"]
    found = []
    for uid in res["uids"]:
        r = res[uid]
        doi = next((a["value"] for a in r.get("articleids", []) if a["idtype"] == "doi"), "")
        if doi.lower() in known_dois:
            continue
        found.append({"pmid": uid, "title": r.get("title", ""), "journal": r.get("source", ""),
                      "date": r.get("pubdate", ""), "doi": doi})
    return found


def main() -> int:
    BUILD.mkdir(exist_ok=True)
    research = json.loads((ROOT / "data" / "research.json").read_text(encoding="utf-8"))
    review = json.loads((ROOT / "data" / "pubmed_review.json").read_text(encoding="utf-8"))
    dois = [j["doi"] for j in research["journals"]]
    metrics = {"updated": datetime.now(timezone.utc).strftime("%Y-%m-%d"), "citations": citations(dois)}
    (BUILD / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    print(f"citations: {metrics['citations']}")
    try:
        found = new_pubmed({d.lower() for d in dois}, {str(p) for p in review["not_mine"]}
                           | {str(p) for p in review["pending"]})
    except Exception as exc:  # noqa: BLE001
        print(f"  pubmed: {exc}", file=sys.stderr)
        found = []
    (BUILD / "new_pubmed.json").write_text(json.dumps(found, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"new PubMed candidates: {len(found)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
