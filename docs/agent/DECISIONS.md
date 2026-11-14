# Decision log — haoyu-wu-academic

Add dated entries with context, decision, and consequences. Keep this append-oriented so future agents
do not reverse choices without understanding the tradeoffs.

## 2026-11-14 12:37 CST — Multi-agent single-writer relay

Context: The project may move among Claude Code, Codex, and a research model, or use parallel worktrees.

Decision: Claude Code reads `CLAUDE.md`; Codex reads `AGENTS.md`; both use `docs/agent/PROJECT.md`,
`HANDOVER.md`, and this decision log. Research lanes are read-only by default. Only one agent writes
to a working tree at a time.

Consequences: Every transfer refreshes `HANDOVER.md`. Parallel work uses separate branches/worktrees.
Verification and diff review are required. Checkpoint commits remain user-controlled.

## 2026-11-14 — Fixed light theme and evidence-based academic content

The user requests a consistently white/blue professional design, including devices in dark mode.
Remove system dark-theme overrides, declare `color-scheme: only light`, use a system sans font,
and fingerprint the stylesheet URL to avoid stale cached styling.

Talk entries are selected from agendas and presentation title slides. Add seven dated academic,
teaching and public-education entries; retain the existing workshop instructor entry. Do not infer
oral presentations from publication abstracts. Do not publish source slide files or private Drive URLs.
Use July 24 for the 2026 Grand Round (the final slide date overrides its July 23 folder name).
Keep the Bei-Hu lecture at month precision because its filename has a malformed day.
The July 2023 symposium agenda explicitly lists the author as a case presenter.
Company/product sessions, including the company-branded Colon Chat webinar, are excluded.
Undated or unclear draft presentations are not treated as confirmed speaking engagements.

LinkedIn is corroborated by two existing CVs; ORCID by a manuscript title page. Google Scholar
has not been verified and is omitted. The user explicitly rejected PMIDs 23830375 and 22107733;
move them to `not_mine` so scheduled discovery does not raise them again.
