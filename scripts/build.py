#!/usr/bin/env python3
"""Render the static site into build/site/ (stdlib only).

Inputs : data/profile.json, data/research.json, optional build/metrics.json
Outputs: build/site/index.html, contact.vcf, assets/*, .nojekyll
"""
from __future__ import annotations

import hashlib
import html
import json
import re
import shutil
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "build" / "site"
SELF = "Hao-Yu Wu"


def e(value) -> str:
    return html.escape(str(value or ""), quote=True)


def bi(en: str, zh: str = "", tag: str = "span") -> str:
    """Bilingual text: both are in the page, CSS shows the active language."""
    if not zh:
        return e(en)
    return f'<{tag} class="en">{e(en)}</{tag}><{tag} class="zh" lang="zh-Hant">{e(zh)}</{tag}>'


def authors(text: str) -> str:
    return e(text).replace(e(SELF), f"<strong>{e(SELF)}</strong>")


def venue(text: str) -> str:
    text = re.sub(r"^TDDW\b", "Taiwan Digestive Disease Week (TDDW)", text)
    return re.sub(r"^DDW\b", "Digestive Disease Week (DDW)", text)


def section(sid: str, en: str, zh: str, body: str, extra: str = "") -> str:
    return (f'<section id="{sid}" class="section {extra}"><h2>{bi(en, zh)}</h2>{body}</section>')


def pub_item(j: dict, cites: dict) -> str:
    links = [f'<a href="https://doi.org/{e(j["doi"])}" target="_blank" rel="noopener">DOI</a>']
    if j.get("pubmed"):
        links.append(f'<a href="{e(j["pubmed"])}" target="_blank" rel="noopener">PubMed</a>')
    n = cites.get(j["doi"])
    if n:
        links.append(f'<span class="cite">Cited by {n}</span>')
    tag = '<span class="tag">First author</span>' if j["first_author"] else ""
    return (f'<li class="pub"><p class="pub-title">{e(j["title"])}{tag}</p>'
            f'<p class="pub-authors">{authors(j["authors"])}</p>'
            f'<p class="pub-venue"><em>{e(j["journal"])}</em> · {e(j["year"])}</p>'
            f'<p class="pub-links">{" ".join(links)}</p></li>')


def render(profile: dict, research: dict, metrics: dict) -> str:
    cites = metrics.get("citations", {})
    p = profile
    jsonld = {
        "@context": "https://schema.org", "@type": "Person", "name": "Hao-Yu Wu",
        "alternateName": "吳浩宇", "honorificSuffix": "MD", "jobTitle": "Attending Physician, Gastroenterology",
        "affiliation": {"@type": "Organization", "name": p["org_en"]},
        "alumniOf": "National Taiwan University", "url": p["site_url"],
        "email": f"mailto:{p['email']}" if p.get("email") else None,
        "knowsAbout": p["keywords"], "sameAs": [l["url"] for l in p.get("links", [])] or None,
    }
    jsonld = {k: v for k, v in jsonld.items() if v}

    links = "".join(f'<a class="btn ghost" href="{e(l["url"])}" target="_blank" rel="noopener">{e(l["label"])}</a>'
                    for l in p.get("links", []))
    email_btn = (f'<a class="btn" href="mailto:{e(p["email"])}">{bi("Email me", "寫信給我")}</a>'
                 if p.get("email") else "")
    hero = f'''<header class="hero">
<img class="portrait" src="assets/portrait.jpg" width="240" height="320" alt="Portrait of Dr. Hao-Yu Wu in a white coat">
<div class="hero-text">
<p class="eyebrow">{bi(p["headline_en"], p["headline_zh"])}</p>
<h1><span class="en">{e(p["name_en"])}</span><span class="zh" lang="zh-Hant">{e(p["name_zh"])}</span></h1>
<p class="affil">{bi(p["affiliation_en"], p["affiliation_zh"])}</p>
<ul class="chips">{"".join(f"<li>{e(k)}</li>" for k in p["keywords"])}</ul>
<div class="actions">{email_btn}<a class="btn ghost" href="contact.vcf" download>{bi("Save contact", "存入聯絡人")}</a>{links}</div>
</div></header>'''

    upcoming = ""
    if p.get("upcoming"):
        items = "".join(f'<li><strong>{e(u["date"])}</strong> {e(u["event"])}'
                        f'{" — " + e(u["note"]) if u.get("note") else ""}</li>' for u in p["upcoming"])
        upcoming = section("meet", "Meet me at", "近期會議行程", f'<ul class="plain">{items}</ul>', "callout")

    about = section("about", "About", "簡介",
                    "".join(f'<p class="en">{e(t)}</p>' for t in p["bio_en"])
                    + "".join(f'<p class="zh" lang="zh-Hant">{e(t)}</p>' for t in p["bio_zh"]))

    themes = "".join(f'<article class="card"><h3>{bi(t["title_en"], t["title_zh"])}</h3>'
                     f'<p>{bi(t["text_en"], t["text_zh"])}</p></article>' for t in p["themes"])
    research_sec = section("research", "Research focus", "研究主題", f'<div class="grid">{themes}</div>')

    journals = research["journals"]
    total_cites = sum(cites.get(j["doi"], 0) for j in journals)
    stats = (f'<div class="stats"><div><strong>{len(journals)}</strong><span>{bi("journal articles", "期刊論文")}</span></div>'
             f'<div><strong>{len(research["abstracts"])}</strong><span>{bi("conference abstracts", "研討會摘要")}</span></div>'
             f'<div><strong>{len(research["grants"])}</strong><span>{bi("funded grants as PI", "主持計畫")}</span></div>'
             + (f'<div><strong>{total_cites}</strong><span>{bi("citations (OpenAlex)", "引用次數（OpenAlex）")}</span></div>'
                if cites else "") + '</div>')
    abstracts = "".join(
        f'<li class="pub"><p class="pub-title">{e(a["title"])}</p><p class="pub-authors">{authors(a["authors"])}</p>'
        f'<p class="pub-venue"><em>{e(venue(a["venue"]))}</em></p></li>' for a in research["abstracts"])
    prep = "".join(f'<li class="pub"><p class="pub-title">{e(i["title"])}</p></li>' for i in research["in_prep"])
    pubs = section("publications", "Publications", "著作", stats
                   + f'<h3>{bi("Journal articles", "期刊論文")}</h3><ol class="pubs">{"".join(pub_item(j, cites) for j in journals)}</ol>'
                   + f'<h3>{bi("Conference abstracts", "研討會論文摘要")}</h3><ol class="pubs">{abstracts}</ol>'
                   + (f'<h3>{bi("In preparation", "撰寫中")}</h3><ul class="pubs">{prep}</ul>' if prep else ""))

    grants = "".join(
        f'<li><span class="when">{e(g["years"])}</span><div><p class="pub-title">{bi(g["title_en"], g["title_zh"])}</p>'
        f'<p class="muted">{e(g["funder"])} · {e(g["number"])} · {e(g["role"])}</p></div></li>'
        for g in research["grants"])
    grants_sec = section("grants", "Research grants", "研究計畫", f'<ul class="timeline">{grants}</ul>')

    awards = "".join(
        f'<li class="{"hl" if a.get("highlight") else ""}"><span class="when">{e(a["year"])}</span>'
        f'<div><p class="pub-title">{e(a["en"])}</p><p class="muted">{e(a["venue"])}</p></div></li>'
        for a in p["awards"])
    awards_sec = section("awards", "Honours & awards", "獲獎", f'<ul class="timeline">{awards}</ul>')

    talk_items = [(t["date"], t["kind"], bi(t["title"], t.get("title_zh", "")), bi(t["venue"], t.get("venue_zh", "")), t.get("slides"), t.get("video")) for t in p["talks"]]
    talk_items.sort(key=lambda t: (t[0] == "Ongoing", t[0]), reverse=True)
    talks = "".join(
        f'<li><span class="when">{e(d)}</span><div><p class="pub-title">{title} <span class="tag">{e(kind)}</span></p>'
        f'<p class="muted">{where}'
        + (f' · <a href="{e(s)}" target="_blank" rel="noopener">Slides</a>' if s else "")
        + (f' · <a href="{e(v)}" target="_blank" rel="noopener">Video</a>' if v else "")
        + '</p></div></li>' for d, kind, title, where, s, v in talk_items)
    talks_sec = section("talks", "Talks & presentations", "演講與學術報告", f'<ul class="timeline">{talks}</ul>')

    def rows(items, fmt):
        return "".join(fmt(x) for x in items)
    exp = (f'<div class="two"><div><h3>{bi("Positions", "經歷")}</h3><ul class="timeline">'
           + rows(p["positions"], lambda x: f'<li><span class="when">{e(x["period"])}</span><div><p class="pub-title">{bi(x["role_en"], x["role_zh"])}</p><p class="muted">{bi(x["org_en"], x["org_zh"])}</p></div></li>')
           + f'</ul></div><div><h3>{bi("Education", "學歷")}</h3><ul class="timeline">'
           + rows(p["education"], lambda x: f'<li><span class="when">{e(x["period"])}</span><div><p class="pub-title">{bi(x["degree_en"], x["degree_zh"])}</p><p class="muted">{bi(x["org_en"], x["org_zh"])}</p></div></li>')
           + f'</ul><h3>{bi("Board certification", "專科資格")}</h3><ul class="timeline">'
           + rows(p["certifications"], lambda x: f'<li><span class="when">{e(x["year"])}</span><div><p>{bi(x["en"], x["zh"])}</p></div></li>')
           + f'</ul><h3>{bi("Memberships", "學會")}</h3><ul class="plain">'
           + rows(p["memberships"], lambda m: f"<li>{e(m)}</li>") + '</ul></div></div>')
    exp_sec = section("experience", "Experience", "經歷與學歷", exp)

    contact = section("contact", "Let's collaborate", "合作與聯絡", f'''<div class="contact">
<div><p>{bi(p["collaborate_en"], p["collaborate_zh"])}</p><div class="actions">{email_btn}
<a class="btn ghost" href="contact.vcf" download>{bi("Save contact", "存入聯絡人")}</a></div></div>
<figure class="qr"><img src="assets/qr.svg" width="180" height="180" alt="QR code linking to this page">
<figcaption>{e(p["site_url"].replace("https://", "").rstrip("/"))}</figcaption></figure></div>''', "callout")

    nav = "".join(f'<a href="#{sid}">{bi(en, zh)}</a>' for sid, en, zh in (
        ("research", "Research", "研究"), ("publications", "Publications", "著作"),
        ("grants", "Grants", "計畫"), ("awards", "Awards", "獲獎"), ("talks", "Talks", "演講"),
        ("experience", "Experience", "經歷"), ("contact", "Contact", "聯絡")))
    css_version = hashlib.sha256((ROOT / "assets" / "style.css").read_bytes()).hexdigest()[:12]
    updated = metrics.get("updated") or date.today().isoformat()
    desc = f'{p["name_en"]} — {p["headline_en"]}, {p["org_en"]}. Research, publications, grants, awards and talks.'
    return f'''<!doctype html>
<html lang="en" data-lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Hao-Yu Wu, MD · Gastroenterology & Clinical AI</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{e(p["site_url"])}">
<meta property="og:type" content="profile">
<meta property="og:title" content="Hao-Yu Wu, MD · 吳浩宇">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{e(p["site_url"])}">
<meta property="og:image" content="{e(p["site_url"])}assets/portrait.jpg">
<meta name="theme-color" content="#ffffff">
<meta name="color-scheme" content="only light">
<link rel="icon" href="assets/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="assets/style.css?v={css_version}">
<script type="application/ld+json">{json.dumps(jsonld, ensure_ascii=False)}</script>
</head>
<body>
<nav class="top"><a class="brand" href="#">H.-Y. Wu</a><div class="navlinks">{nav}</div>
<button class="lang" type="button" aria-label="Switch language / 切換語言">中文</button></nav>
<main>
{hero}
{upcoming}
{about}
{research_sec}
{pubs}
{grants_sec}
{awards_sec}
{talks_sec}
{exp_sec}
{contact}
</main>
<footer><p>{bi("Last updated", "最後更新")} {e(updated)} · {bi("Citation counts from OpenAlex, refreshed weekly.", "引用數取自 OpenAlex，每週自動更新。")}</p></footer>
<script>
(function () {{
  var root = document.documentElement, btn = document.querySelector('.lang');
  function set(l) {{
    root.dataset.lang = l; root.lang = l === 'zh' ? 'zh-Hant' : 'en';
    btn.textContent = l === 'zh' ? 'English' : '中文';
    try {{ localStorage.setItem('lang', l); }} catch (err) {{}}
  }}
  var saved = null;
  try {{ saved = localStorage.getItem('lang'); }} catch (err) {{}}
  if (location.hash === '#zh') saved = 'zh';
  set(saved || ((navigator.language || '').indexOf('zh') === 0 ? 'zh' : 'en'));
  btn.addEventListener('click', function () {{ set(root.dataset.lang === 'zh' ? 'en' : 'zh'); }});
}})();
</script>
</body>
</html>
'''


def vcard(p: dict) -> str:
    lines = ["BEGIN:VCARD", "VERSION:3.0", "N:Wu;Hao-Yu;;Dr.;MD", "FN:Hao-Yu Wu, MD",
             f"ORG:{p['org_en']};Division of Gastroenterology & Hepatology",
             "TITLE:Attending Physician, Gastroenterology"]
    if p.get("email"):
        lines.append(f"EMAIL;TYPE=INTERNET:{p['email']}")
    lines += [f"URL:{p['site_url']}", "END:VCARD"]
    return "\r\n".join(lines) + "\r\n"


def main() -> int:
    profile = json.loads((ROOT / "data" / "profile.json").read_text(encoding="utf-8"))
    research = json.loads((ROOT / "data" / "research.json").read_text(encoding="utf-8"))
    metrics_path = ROOT / "build" / "metrics.json"
    metrics = json.loads(metrics_path.read_text(encoding="utf-8")) if metrics_path.exists() else {}
    if OUT.exists():
        shutil.rmtree(OUT)
    shutil.copytree(ROOT / "assets", OUT / "assets")
    (OUT / "index.html").write_text(render(profile, research, metrics), encoding="utf-8")
    (OUT / "contact.vcf").write_text(vcard(profile), encoding="utf-8", newline="")
    (OUT / ".nojekyll").write_text("", encoding="utf-8")
    print(f"built {OUT.relative_to(ROOT)}/index.html")
    return 0


if __name__ == "__main__":
    sys.exit(main())
