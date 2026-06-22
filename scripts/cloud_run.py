"""
Cloud daily run (GitHub Actions) for tachan-bot.

Screens the curated cyclical/value universe and writes the report to
docs/index.html, which GitHub Pages serves — no local machine needed.
"""

from __future__ import annotations

import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

PROJECT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_DIR))

from tachan.fundamentals import fetch_many
from tachan.strategy     import screen
from tachan.universe     import UNIVERSES
from tachan.report       import save

JST   = timezone(timedelta(hours=9))
TODAY = datetime.now(JST).strftime("%Y-%m-%d")
OUT   = str(PROJECT_DIR / "docs" / "index.html")


def main() -> int:
    Path(OUT).parent.mkdir(parents=True, exist_ok=True)
    codes = UNIVERSES["all"]
    print(f"[{TODAY}] Screening {len(codes)} stocks (たーちゃん流) …")
    rows = screen(fetch_many(codes))

    # Health check: if most stocks have no price, yfinance likely broke.
    # Fail (GitHub alerts) and keep the last good page.
    priced = sum(1 for m in rows if m.get("price") is not None)
    if priced < len(codes) * 0.5:
        print(f"  [ERROR] only {priced}/{len(codes)} priced — data source degraded. "
              "Keeping last good page.")
        return 1

    save(rows, OUT, title="たーちゃん流 バリュー・スクリーナー")
    n_cyc = sum(1 for m in rows if m.get("strategy") == "cyclical")
    print(f"  Report → {OUT}  (シクリカル本命 {n_cyc}件 ／ {priced}/{len(codes)}銘柄に価格)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
