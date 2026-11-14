# Handover — haoyu-wu-academic

Updated: 2026-11-14
Writer: RELEASED
Mode: solo
From: Codex
To: next agent
Checkpoint: previous HEAD 3f090db; this commit adds NTU Scholars

## Current State

Added the user-provided verified NTU Scholars profile to homepage buttons and Person sameAs.
Existing LinkedIn, ORCID and fixed white/blue theme are preserved.
Google Scholar URL supplied by the user is a signup URL, not a public profile. No logged-in
browser integration is available, and the signup fetch returned HTTP 429. No form was submitted.
Prepared build/google-scholar-setup.txt locally (ignored) with fields and five known journal
articles. User must log in, verify institutional email, check authorship and create the profile.
Add the final citations?user= URL when provided; never publish the signup URL as a profile.

## Verification

Baseline and final scripts/verify.sh PASS. Inspect final diff and browser-check the new button.
The current push deploys through GitHub Actions; check its result and live button before reporting.
No private source data or credentials added. Original working tree was clean and aligned with origin/main.

## Next Action

No further site implementation required. Await the user's public Google Scholar profile URL.
Before future edits, read the manifest, verify baseline, claim a unique writer, then verify and release.
