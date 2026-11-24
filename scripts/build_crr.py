# /// script
# requires-python = ">=3.11"
# dependencies = ["beautifulsoup4", "lxml", "requests"]
# ///
"""Download the consolidated CRR (Regulation (EU) No 575/2013) and split it into one record per article.

Usage: uv run --script build_crr.py [--celex 02013R0575-20260626] [--out ../data/raw/crr_articles.jsonl]

The text comes from the EU Publications Office (Cellar), because eur-lex.europa.eu answers automated clients with a bot challenge.
"""

import argparse
import json
import re
import warnings
from pathlib import Path

import requests
from bs4 import BeautifulSoup, Tag, XMLParsedAsHTMLWarning

CELLAR = "http://publications.europa.eu/resource/celex/{celex}"
EURLEX = "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:{celex}"
LEVELS = {"prt": "part", "tis": "title", "cpt": "chapter", "sct": "section", "sbs": "subsection"}


def clean(text: str) -> str:
    text = text.replace("\xa0", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r" *\n *", "\n", text)
    return re.sub(r"\n{2,}", "\n", text).strip()


def heading(div: Tag) -> str:
    """'PART THREE — CAPITAL REQUIREMENTS' from the two title paragraphs of a division div."""
    parts = [
        p.get_text(" ", strip=True)
        for p in div.find_all("p", class_=["title-division-1", "title-division-2"], recursive=False)
    ]
    return " — ".join(parts)


def article_text(art: Tag) -> str:
    for junk in art.select("p.modref, p.title-article-norm, div.eli-title, p.arrow"):
        junk.decompose()
    # Lists are rendered as two-column grids: put "(a) " and its text on one line.
    for grid in art.select("div.grid-container"):
        grid.replace_with("\n" + grid.get_text(" ", strip=True) + "\n")
    for p in art.find_all(["p", "div", "tr"]):
        p.insert_after("\n")
    # Paragraph numbers ("1.", "2a.") end up alone on their line; join them with the text that follows.
    return re.sub(r"^(\d+[a-z]*\.)\n", r"\1 ", clean(art.get_text("")), flags=re.MULTILINE)


def parse(html: bytes, celex: str) -> list[dict]:
    warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)
    soup = BeautifulSoup(html, "lxml")
    records = []
    for art in soup.select("div.eli-subdivision[id^=art_]"):
        number = (
            art.select_one("p.title-article-norm")
            .get_text(strip=True)
            .removeprefix("Article ")
            .strip()
        )
        stitle = art.select_one("p.stitle-article-norm")
        rec = {
            "id": f"CRR-art-{number}",
            "regulation": "CRR (Regulation (EU) No 575/2013)",
            "article": number,
            "article_title": stitle.get_text(" ", strip=True) if stitle else "",
        }
        for anc in reversed(list(art.parents)):
            m = re.fullmatch(
                r".*?(prt|tis|cpt|sct|sbs)_([^.]+)",
                anc.get("id", "") if isinstance(anc, Tag) else "",
            )
            if m:
                rec[LEVELS[m.group(1)]] = heading(anc)
        rec["text"] = article_text(art)
        rec["url"] = EURLEX.format(celex=celex) + f"#art_{number}"
        records.append(rec)
    return records


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--celex", default="02013R0575-20260626")
    ap.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).parent.parent / "data" / "raw" / "crr_articles.jsonl",
    )
    args = ap.parse_args()

    resp = requests.get(
        CELLAR.format(celex=args.celex),
        headers={"Accept": "application/xhtml+xml", "Accept-Language": "eng"},
        timeout=120,
    )
    resp.raise_for_status()
    records = parse(resp.content, args.celex)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"{len(records)} articles -> {args.out}")


if __name__ == "__main__":
    main()
