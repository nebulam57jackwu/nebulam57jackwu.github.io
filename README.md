# Hao-Yu Wu, MD — academic profile

Public site: https://nebulam57jackwu.github.io/ (QR code: `qr-print.png` / `qr-print.svg`).

Static, stdlib-only Python build, deployed by GitHub Actions to GitHub Pages on every push
and every Monday 09:00 (Taiwan), when it also refreshes citation counts (OpenAlex) and opens
an issue if PubMed lists a new paper under "Wu, Hao-Yu" + Taiwan.

## 更新方式

| 要更新的內容 | 改哪裡 | 之後 |
|---|---|---|
| 論文、研討會摘要、計畫 | research-kb `data/profile.py`、`data/grants.py` | `python3 scripts/sync_from_kb.py` |
| 簡介、經歷、獎項、演講、近期會議（Meet me at） | `data/profile.json` | — |
| 新 PubMed 同名論文（Action 開的 issue） | 是自己的 → 加入 research-kb；不是 → `data/pubmed_review.json` 的 `not_mine` | — |

然後 `./scripts/verify.sh`（建置＋個資檢查），commit、push，約 1 分鐘後網站更新。QR code 網址固定，不需重印。

本機預覽：`python3 scripts/enrich.py && python3 scripts/build.py && python3 -m http.server -d build/site 8799`。

## 隱私

只放公開學術資訊。不得放手機、生日、住址、證照字號或計畫金額；`scripts/verify.sh` 會擋下常見樣式。
research-kb 是私有 repo，`sync_from_kb.py` 只複製公開欄位。

## 外觀與演講維護

網站固定白底藍色，不隨系統深色模式變更；樣式網址含內容雜湊以避免舊版快取。
演講僅列已核對議程或簡報的學術／教學活動，排除廠商演講。
研討會摘要保留在著作區，不自動列為演講。`title_zh`、`venue_zh` 可提供中文版本。
不要公開未經審查的原始臨床投影片或私人雲端資料夾連結。

獎學金以 research-kb `data/profile.py` 的 `SCHOLARSHIPS` 為來源；執行 `python3 scripts/sync_from_kb.py` 會依 ID 同步公開中英文名稱、年度及頒發日期，保留其他手動維護獎項。
