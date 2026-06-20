"""
たーちゃん流バリュー・スクリーナー — CLI entry point.

Usage:
  python scripts/screen.py --universe cyclical --report
  python scripts/screen.py --symbols 5401,9101,7014
  python scripts/screen.py --universe steel
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from tachan.fundamentals import fetch_many
from tachan.strategy     import screen, STRATEGIES, SELL_RULES
from tachan.universe     import UNIVERSES
from tachan.report       import save


def _fmt(v, pct=False, nd=1):
    if v is None:
        return "—"
    return f"{v*100:+.0f}%" if pct else f"{v:.{nd}f}"


def main() -> int:
    ap = argparse.ArgumentParser(description="たーちゃん流バリュー・スクリーナー")
    ap.add_argument("--symbols",  help="カンマ区切りの銘柄コード（例: 5401,9101）")
    ap.add_argument("--universe", help=f"ユニバース: {', '.join(UNIVERSES)}")
    ap.add_argument("--report",   action="store_true", help="HTMLレポートも出力")
    ap.add_argument("--out",      default="data/screen.html", help="HTML出力先")
    args = ap.parse_args()

    if args.symbols:
        codes = [s.strip() for s in args.symbols.split(",") if s.strip()]
    elif args.universe:
        if args.universe not in UNIVERSES:
            print(f"不明なユニバース '{args.universe}'。選択肢: {list(UNIVERSES)}")
            return 1
        codes = UNIVERSES[args.universe]
    else:
        codes = UNIVERSES["cyclical"]

    print(f"判定中: {len(codes)} 銘柄 …")
    rows = screen(fetch_many(codes))

    cur = None
    for m in rows:
        if m["strategy"] != cur:
            cur = m["strategy"]
            label, emoji, _ = STRATEGIES[cur]
            print(f"\n=== {emoji} {label} ===")
        reasons = " / ".join(m.get("reasons", [])) or "—"
        print(f"  {m['code']:6} {str(m['name'])[:18]:18} "
              f"PER{_fmt(m.get('per')):>6} PBR{_fmt(m.get('pbr'),nd=2):>6} "
              f"営利{_fmt(m.get('op_margin'),pct=True):>5} "
              f"自己{_fmt(m.get('equity_ratio'),pct=True):>5}  {reasons}")

    print("\n🔔 売り時の3ルール:")
    for r in SELL_RULES:
        print("  " + r)

    if args.report:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        out = save(rows, args.out)
        print(f"\nHTML → {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
