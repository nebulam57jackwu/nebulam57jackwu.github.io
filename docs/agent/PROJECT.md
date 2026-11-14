# Project — academic profile

Public academic website for Hao-Yu Wu, MD, deployed to GitHub Pages.

## Architecture

- `data/profile.json`: public biography, talks, awards and external profiles.
- `data/research.json`: allowlisted export from the private research knowledge base.
- `data/pubmed_review.json`: same-name author exclusions and pending decisions.
- `scripts/build.py`: Python standard-library static renderer; output in ignored `build/site/`.
- `scripts/enrich.py`: OpenAlex citation refresh and PubMed candidate detection.
- `assets/`: stylesheet, portrait, favicon and permanent site QR code.
- GitHub Actions builds and deploys on main pushes and Monday 09:00 Asia/Taipei.

## Verification and invariants

Run `./scripts/verify.sh` for build, privacy patterns, assets and anchor checks.
Browser-check narrow/mobile and desktop layouts, both system color schemes, and both languages.
Keep the page white and blue regardless of system theme. Conference abstracts are publications;
only evidenced presentations belong in Talks. Exclude company/vendor talks as requested.
Only publish public academic metadata; never copy source CVs, clinical slides, private Drive URLs,
phone numbers, birth dates, addresses, licence numbers, credentials or grant budgets.
Preserve the fixed site URL so existing QR codes remain valid.

Single writer per tree. Current work belongs in `HANDOVER.md`; durable policy decisions belong in
`docs/agent/DECISIONS.md`. Verify and release ownership before transfer.
