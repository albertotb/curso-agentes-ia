# `data/` — course data

`data/raw/` is versioned in git. Both files can be rebuilt with the scripts in [`scripts/`](../scripts/), which run standalone with `uv run --script`.

## `bank.db` — Demo Bank (synthetic)

SQLite database of a fictional bank. Every value is generated with a fixed seed by [`scripts/build_bank_db.py`](../scripts/build_bank_db.py); names come from Faker and do not refer to real people or companies.

| Table | Rows | Content |
|---|---|---|
| `customers` | 120 | Segment (retail / sme / corporate), country, sector, internal rating (1 best .. 8 default), KYC risk |
| `loans` | 182 | Product, principal and outstanding amount, interest rate, dates, IFRS 9 stage, days past due, collateral |
| `transactions` | 2,700 | Jan–Oct 2026: date, amount (+ in / − out), type, counterparty country, channel |
| `capital_position` | 4 | Quarter ends Dec 2025 – Sep 2026: CET1, AT1, Tier 2, RWA by risk type, leverage exposure, HQLA, net outflows (EUR m) |

The data contains a few patterns on purpose: CET1 falls over 2026, and some high-KYC-risk customers make repeated cash operations just below 10,000 EUR.

## `crr_articles.jsonl` — Capital Requirements Regulation

Regulation (EU) No 575/2013 (CRR), consolidated text of 26 June 2026 (CELEX `02013R0575-20260626`), English. One JSON record per article (737), built by [`scripts/build_crr.py`](../scripts/build_crr.py) from the EU Publications Office:

```json
{"id": "CRR-art-92", "regulation": "CRR (Regulation (EU) No 575/2013)", "article": "92",
 "article_title": "Own funds requirements", "part": "PART THREE — CAPITAL REQUIREMENTS",
 "title": "TITLE I — ...", "chapter": "CHAPTER 1 — ...", "section": "Section 1 — ...",
 "text": "1. Subject to Articles 93 and 94, ...", "url": "https://eur-lex.europa.eu/...#art_92"}
```

Annexes are not included. The consolidated text is a documentation tool with no legal effect; the authentic version is the one published in the Official Journal.
