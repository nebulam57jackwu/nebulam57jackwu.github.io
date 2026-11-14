# Handover — haoyu-wu-academic

Updated: 2026-11-14
Writer: RELEASED
Mode: solo
From: Codex
To: next agent
Checkpoint: publication commit containing this handoff; previous HEAD fa2e0a3

## 1. Current State

Objective: fix the live academic site to always use a white/blue design, curate non-vendor talks,
exclude user-rejected same-name papers, and recover previously saved academic profile links.
Implementation complete: fixed light theme, cache-versioned CSS, seven added dated talks plus the
existing workshop role, LinkedIn and ORCID links, and two newly confirmed PubMed exclusions.
Abstracts remain in Publications and are no longer automatically duplicated as talks.
Single-writer workflow initialized because the site repository previously had no manifest/handoff.
The existing project-specific verification script was intentionally preserved during initialization.

## 2. Next Steps

Publish this change on origin/main, observe the GitHub Pages deployment, and verify the live page.
After deployment no implementation remains. Future additions require evidence of speaker, date and
venue; Google Scholar remains unverified. Do not add uncertain draft talks or company sessions.
Scope is the academic website; the private research-kb working tree is untouched.

## 3. Key Decisions and Contracts

See docs/agent/DECISIONS.md for theme, evidence, date precision and attribution decisions.
Private Drive documents were read only; their contents and clinical slides are not in Git.
Source CVs corroborate LinkedIn; a manuscript title page corroborates ORCID.

## 4. Verification Evidence

Baseline and final scripts/verify.sh: PASS (build, privacy patterns, assets, anchors).
Chromium: eight combinations covering 320/390/1440 px, light/dark preference and English/Chinese;
white background, no horizontal overflow, language switching, profile links and eight talk rows PASS.
Mobile and desktop screenshots reviewed. WebKit is not installed; no physical iPhone test claimed.
Git diff checked; origin/main initially aligned with HEAD; no pre-existing changes or ahead commits.
Use agent-workflow.py verify after staging/committing to refresh the local receipt.

## 5. Working Tree and Recovery

Only task changes and workflow initialization are included. Generated site/metrics remain ignored.
No source documents, credentials or private clinical information are submitted.

## 6. Direct Command for the Next Agent

Read the manifest and this handoff, inspect Git, run baseline verification, and claim a unique owner
before edits. Verify, refresh handoff, release the same owner and run ./scripts/agent-handoff.sh.
