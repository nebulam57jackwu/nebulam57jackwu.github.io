# Handover — haoyu-wu-academic

Updated: 2026-11-14
Writer: RELEASED
Mode: solo
From: Codex
To: next agent
Checkpoint: previous HEAD b430986; this commit adds the 2025 NTU scholarship

## Current State

User requested hiding the in-preparation LST manuscript. The public page now omits drafts
unless profile.show_in_preparation is explicitly enabled. Private KB records and published
conference abstracts remain unchanged. Baseline/build verification PASS.


Added the user-certified 2025 NTU Hou Yong-Xiong scholarship, with official English/Chinese
names, academic year 114 and award date 2025-12-10. No student or certificate identifiers.
Scholarships now sync by ID from research-kb SCHOLARSHIPS through an explicit public allowlist;
other manually maintained awards remain intact. Award title and venue support both languages.


Added the user-provided verified NTU Scholars profile to homepage buttons and Person sameAs.
Existing LinkedIn, ORCID and fixed white/blue theme are preserved.
Added the user's newly created Google Scholar profile (user ID jyqa29EAAAAJ) to homepage
buttons and Person sameAs. Stored the canonical user/hl URL only; omitted the supplied gmla and
view_op parameters. The profile itself was not readable through the web tool; authorship is based
on the user's explicit identification. No claim of checking its publication list or visibility.

Talks now come from research-kb data/talks.json (auto-scanned daily from the Drive talks folder by
research-kb/scripts/talks_autoupdate.sh, systemd timer research-kb-talks.timer 04:30). sync_from_kb.py
copies only public, dated, past talks; industry-sponsored seminars are never published (user decision
2026-11-14). The 7 hand-verified talks moved from profile.json into research-kb as reviewed entries;
profile.json keeps only the Drive-less workshop entry. build.py renders profile talks + research talks.

## Verification

Baseline and final scripts/verify.sh PASS. Inspect final diff and browser-check the new button.
The current push deploys through GitHub Actions; check its result and live button before reporting.
No private source data or credentials added. Original working tree was clean and aligned with origin/main.

## Next Action

No further site implementation required. Sync scholarships from research-kb when updated.
Before future edits, read the manifest, verify baseline, claim a unique writer, then verify and release.
