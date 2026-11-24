# /// script
# requires-python = ">=3.11"
# dependencies = ["faker"]
# ///
"""Build a small synthetic SQLite database for a fictional bank ("Demo Bank").

Usage: uv run --script build_bank_db.py [--out ../data/raw/bank.db]

All data is synthetic and generated with a fixed seed, so every run produces the same file.
"""

import argparse
import random
import sqlite3
from datetime import date, timedelta
from pathlib import Path

from faker import Faker

SEED = 42
N_CUSTOMERS = 120

SCHEMA = """
CREATE TABLE customers (
    customer_id   TEXT PRIMARY KEY,   -- C-0001
    name          TEXT NOT NULL,
    segment       TEXT NOT NULL,      -- retail | sme | corporate
    country       TEXT NOT NULL,      -- ISO 3166-1 alpha-2
    sector        TEXT,               -- NACE-like sector for sme/corporate, NULL for retail
    internal_rating TEXT NOT NULL,    -- 1 (best) .. 8 (default)
    kyc_risk      TEXT NOT NULL,      -- low | medium | high
    onboarding_date TEXT NOT NULL
);
CREATE TABLE loans (
    loan_id       TEXT PRIMARY KEY,   -- L-00001
    customer_id   TEXT NOT NULL REFERENCES customers(customer_id),
    product       TEXT NOT NULL,      -- mortgage | consumer | credit_line | term_loan
    principal_eur REAL NOT NULL,
    outstanding_eur REAL NOT NULL,
    interest_rate REAL NOT NULL,      -- annual, in %
    start_date    TEXT NOT NULL,
    maturity_date TEXT NOT NULL,
    ifrs9_stage   INTEGER NOT NULL,   -- 1 | 2 | 3
    days_past_due INTEGER NOT NULL,
    collateral    TEXT                -- residential_property | commercial_property | guarantee | none
);
CREATE TABLE transactions (
    tx_id         TEXT PRIMARY KEY,   -- T-000001
    customer_id   TEXT NOT NULL REFERENCES customers(customer_id),
    tx_date       TEXT NOT NULL,
    amount_eur    REAL NOT NULL,      -- positive = incoming, negative = outgoing
    tx_type       TEXT NOT NULL,      -- transfer | card | cash | direct_debit
    counterparty_country TEXT NOT NULL,
    channel       TEXT NOT NULL       -- online | branch | atm | mobile
);
CREATE TABLE capital_position (
    reference_date TEXT PRIMARY KEY,  -- quarter end
    cet1_capital_eur_m REAL NOT NULL,
    at1_capital_eur_m  REAL NOT NULL,
    tier2_capital_eur_m REAL NOT NULL,
    rwa_credit_eur_m   REAL NOT NULL,
    rwa_market_eur_m   REAL NOT NULL,
    rwa_operational_eur_m REAL NOT NULL,
    leverage_exposure_eur_m REAL NOT NULL,
    hqla_eur_m         REAL NOT NULL,
    net_outflows_30d_eur_m REAL NOT NULL
);
"""

SECTORS = [
    "Real estate",
    "Construction",
    "Manufacturing",
    "Retail trade",
    "Hospitality",
    "Transport",
    "Energy",
    "Agriculture",
    "IT services",
]
COUNTRIES = ["ES"] * 14 + ["PT", "FR", "DE", "IT", "NL", "GB", "US", "MX", "AE", "PA"]
HIGH_RISK_COUNTRIES = ["PA", "AE", "KY", "VG", "RU"]


def rdate(rng: random.Random, start: date, end: date) -> date:
    return start + timedelta(days=rng.randrange((end - start).days))


def build(out: Path) -> None:
    rng = random.Random(SEED)
    fake = Faker("es_ES")
    Faker.seed(SEED)
    out.unlink(missing_ok=True)
    con = sqlite3.connect(out)
    con.executescript(SCHEMA)

    customers = []
    for i in range(1, N_CUSTOMERS + 1):
        segment = rng.choices(["retail", "sme", "corporate"], weights=[60, 30, 10])[0]
        name = fake.name() if segment == "retail" else fake.company()
        rating = str(min(8, max(1, round(rng.gauss(4, 1.5)))))
        kyc = rng.choices(["low", "medium", "high"], weights=[70, 22, 8])[0]
        customers.append(
            (
                f"C-{i:04d}",
                name,
                segment,
                rng.choice(COUNTRIES),
                None if segment == "retail" else rng.choice(SECTORS),
                rating,
                kyc,
                rdate(rng, date(2012, 1, 1), date(2025, 12, 31)).isoformat(),
            )
        )
    con.executemany("INSERT INTO customers VALUES (?,?,?,?,?,?,?,?)", customers)

    loans, n = [], 0
    for c in customers:
        cid, segment, rating = c[0], c[2], int(c[5])
        products = {
            "retail": ["mortgage", "consumer"],
            "sme": ["credit_line", "term_loan"],
            "corporate": ["term_loan", "credit_line"],
        }[segment]
        size = {
            "retail": (5_000, 350_000),
            "sme": (50_000, 2_000_000),
            "corporate": (1_000_000, 40_000_000),
        }[segment]
        for _ in range(rng.choice([0, 1, 1, 2, 3])):
            n += 1
            product = rng.choice(products)
            principal = round(rng.uniform(*size), -2)
            start = rdate(rng, date(2016, 1, 1), date(2026, 6, 30))
            years = {"mortgage": 25, "consumer": 5, "credit_line": 1, "term_loan": 7}[product]
            stage = (
                3
                if rating == 8 or (rating == 7 and rng.random() < 0.5)
                else 2
                if rating >= 6 and rng.random() < 0.6
                else 1
            )
            dpd = (
                rng.randint(91, 400)
                if stage == 3
                else rng.randint(31, 89)
                if stage == 2 and rng.random() < 0.5
                else rng.choice([0] * 9 + [rng.randint(1, 29)])
            )
            collateral = (
                "residential_property"
                if product == "mortgage"
                else rng.choice(["commercial_property", "guarantee", "none"])
                if segment != "retail"
                else "none"
            )
            loans.append(
                (
                    f"L-{n:05d}",
                    cid,
                    product,
                    principal,
                    round(principal * rng.uniform(0.2, 1.0), 2),
                    round(
                        rng.uniform(1.5, 4.5) + rating * 0.4 + (3 if product == "consumer" else 0),
                        2,
                    ),
                    start.isoformat(),
                    (start + timedelta(days=365 * years)).isoformat(),
                    stage,
                    dpd,
                    collateral,
                )
            )
    con.executemany("INSERT INTO loans VALUES (?,?,?,?,?,?,?,?,?,?,?)", loans)

    txs, n = [], 0
    for c in customers:
        cid, kyc = c[0], c[6]
        for _ in range(rng.randint(5, 40)):
            n += 1
            suspicious = kyc == "high" and rng.random() < 0.3
            amount = rng.uniform(9_000, 9_990) if suspicious else rng.lognormvariate(6, 1.4)
            country = (
                rng.choice(HIGH_RISK_COUNTRIES)
                if suspicious and rng.random() < 0.5
                else rng.choice(COUNTRIES)
            )
            txs.append(
                (
                    f"T-{n:06d}",
                    cid,
                    rdate(rng, date(2026, 1, 1), date(2026, 10, 31)).isoformat(),
                    round(amount * rng.choice([1, -1]), 2),
                    "cash"
                    if suspicious and rng.random() < 0.5
                    else rng.choice(["transfer", "card", "direct_debit", "transfer"]),
                    country,
                    rng.choice(["online", "branch", "atm", "mobile"]),
                )
            )
    con.executemany("INSERT INTO transactions VALUES (?,?,?,?,?,?,?)", txs)

    # Quarterly capital figures (EUR m). 2026-09-30 deliberately sits close to the combined buffer requirement.
    capital = [
        ("2025-12-31", 1480.0, 210.0, 300.0, 9100.0, 650.0, 1150.0, 31500.0, 4200.0, 3100.0),
        ("2026-03-31", 1455.0, 210.0, 300.0, 9350.0, 700.0, 1150.0, 32100.0, 4050.0, 3200.0),
        ("2026-06-30", 1420.0, 210.0, 290.0, 9700.0, 720.0, 1180.0, 33000.0, 3900.0, 3300.0),
        ("2026-09-30", 1390.0, 200.0, 290.0, 10050.0, 760.0, 1180.0, 33900.0, 3600.0, 3350.0),
    ]
    con.executemany("INSERT INTO capital_position VALUES (?,?,?,?,?,?,?,?,?,?)", capital)
    con.commit()
    con.close()
    print(
        f"{len(customers)} customers, {len(loans)} loans, {len(txs)} transactions, {len(capital)} capital snapshots -> {out}"
    )


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--out", type=Path, default=Path(__file__).parent.parent / "data" / "raw" / "bank.db"
    )
    build(ap.parse_args().out)


if __name__ == "__main__":
    main()
