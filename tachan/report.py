"""
HTML report for the たーちゃん value screener.

Leads with the "株の4タイプ" matrix (シクリカルバリュー株の循環サイクル) so
each stock's position in the cycle is visible at a glance, then a compact
detail table grouped by strategy, then the sell-rule reminder.
"""

from __future__ import annotations

from datetime import datetime, timezone, timedelta
from html import escape

from tachan.strategy import STRATEGIES, QUADRANTS, SELL_RULES

# strategy → emoji (for marking 本命 candidates inside the matrix)
_STRAT_EMOJI = {k: v[1] for k, v in STRATEGIES.items()}

# quadrant accent colours (matching the diagram's purple cycle)
_QCOLOR = {
    "ceiling":   "#c084fc",
    "recession": "#c084fc",
    "bottom":    "#c084fc",
    "recovery":  "#c084fc",
}


def _num(v, pct=False, nd=2):
    if v is None:
        return "—"
    return f"{v*100:+.0f}%" if pct else f"{v:.{nd}f}"


def _yen_oku(v):
    return "—" if v is None else f"{v/1e8:,.0f}億"


def _chip(m: dict) -> str:
    """One stock chip inside a quadrant. 本命 strategies get an emoji."""
    strat = m.get("strategy", "none")
    badge = _STRAT_EMOJI.get(strat, "") if strat in ("cyclical", "asset", "earnings") else ""
    es    = m.get("earnings", {}).get("label", "")
    extra = ""
    if es in ("黒字転換✨", "2年連続赤字"):
        extra = f'<span class="chip-es">{escape(es)}</span>'
    return (
        f'<div class="chip">{badge}<b>{escape(m["code"])}</b> '
        f'{escape(str(m["name"])[:10])}{extra}</div>'
    )


def _quad_cell(key: str, rows: list[dict]) -> str:
    label, sub = QUADRANTS[key]
    color = _QCOLOR.get(key, "#c084fc")
    chips = "".join(_chip(m) for m in rows) or '<div class="chip empty">—</div>'
    return (
        f'<div class="quad" style="border-color:{color}">'
        f'<div class="quad-h">シクリカルバリュー株の<b style="color:{color}">{label}</b>'
        f'<span class="quad-sub">{sub}</span></div>'
        f'<div class="chips">{chips}</div></div>'
    )


def render(rows: list[dict], title: str = "たーちゃん流 バリュー・スクリーナー") -> str:
    jst       = timezone(timedelta(hours=9))
    generated = datetime.now(jst).strftime("%Y-%m-%d %H:%M")

    by_q: dict[str, list[dict]] = {}
    for m in rows:
        by_q.setdefault(m.get("quadrant", "unknown"), []).append(m)

    # ── detail table, grouped by strategy ──
    groups: dict[str, list[dict]] = {}
    for m in rows:
        groups.setdefault(m.get("strategy", "none"), []).append(m)
    sections = []
    for key, (label, emoji, _) in STRATEGIES.items():
        items = groups.get(key, [])
        if not items:
            continue
        trows = "".join(
            "<tr>"
            f'<td class="code">{escape(m["code"])}</td>'
            f'<td class="name">{escape(str(m["name"])[:20])}</td>'
            f'<td>{_num(m.get("per"), nd=1)}</td>'
            f'<td>{_num(m.get("pbr"))}</td>'
            f'<td>{_num(m.get("op_margin"), pct=True)}</td>'
            f'<td>{_num(m.get("roa"), pct=True)}</td>'
            f'<td>{_num(m.get("equity_ratio"), pct=True)}</td>'
            f'<td>{_yen_oku(m.get("market_cap"))}</td>'
            f'<td>{escape(m.get("earnings", {}).get("label","—"))}</td>'
            "</tr>"
            for m in items
        )
        sections.append(
            f'<h3>{emoji} {escape(label)} <span class="count">{len(items)}件</span></h3>'
            '<table><thead><tr><th>コード</th><th>銘柄</th><th>PER</th><th>PBR</th>'
            '<th>営利率</th><th>ROA</th><th>自己資本</th><th>時価総額</th><th>業績</th>'
            f'</tr></thead><tbody>{trows}</tbody></table>'
        )

    sell = "".join(f"<li>{escape(r)}</li>" for r in SELL_RULES)

    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(title)} — {generated}</title>
<style>
  body {{ font-family:-apple-system,"Hiragino Sans",sans-serif; background:#0f1115;
         color:#e6e6e6; padding:24px; max-width:1040px; margin:0 auto; }}
  h1 {{ font-size:20px; margin:0 0 4px; }}
  h2 {{ font-size:16px; margin:26px 0 8px; }}
  h3 {{ font-size:14px; margin:18px 0 4px; }}
  .count {{ color:#8a93a2; font-size:12px; font-weight:400; }}
  .meta {{ color:#8a93a2; font-size:13px; margin-bottom:18px; }}

  /* ── 4-type matrix ── */
  .matrix-title {{ text-align:center; font-weight:700; color:#9ec5ff; margin:6px 0; }}
  .matrix {{ display:grid; grid-template-columns:30px 1fr 1fr 30px;
             grid-template-rows:26px 1fr 1fr 26px; gap:7px; }}
  .ax {{ display:flex; align-items:center; justify-content:center; color:#9ec5ff;
         font-size:12px; font-weight:700; }}
  .ax.v {{ writing-mode:vertical-rl; }}
  .ax.tag {{ color:#8a93a2; font-weight:400; font-size:11px; }}
  .quad {{ background:#1a1430; border:1.5px solid; border-radius:12px; padding:10px 12px;
           min-height:118px; }}
  .quad-h {{ font-size:13px; font-weight:700; margin-bottom:8px; }}
  .quad-sub {{ display:block; color:#8a93a2; font-weight:400; font-size:10px; margin-top:2px; }}
  .chips {{ display:flex; flex-wrap:wrap; gap:5px; }}
  .chip {{ background:#0f1115; border:1px solid #3a3550; border-radius:7px;
           padding:2px 7px; font-size:12px; }}
  .chip b {{ color:#d8b4fe; }}
  .chip-es {{ color:#34d399; font-size:10px; margin-left:4px; }}
  .chip.empty {{ color:#555; border-style:dashed; }}
  .corner {{ font-size:10px; color:#8a93a2; }}

  table {{ border-collapse:collapse; width:100%; font-size:13px; margin-bottom:4px; }}
  th,td {{ padding:6px 9px; border-bottom:1px solid #232733; text-align:right; white-space:nowrap; }}
  th {{ color:#b8c0cc; background:#161a22; }}
  td.code {{ text-align:left; font-weight:700; color:#6db3f2; }}
  td.name {{ text-align:left; }}
  .note {{ background:#161a22; border:1px solid #232733; border-radius:10px;
           padding:14px 18px; margin-top:24px; font-size:13px; line-height:1.7; }}
  .note ul {{ margin:6px 0 0; padding-left:20px; color:#cdd3dc; }}
</style>
</head>
<body>
  <h1>💹 {escape(title)}</h1>
  <div class="meta">🕒 最終更新: {generated}（JST） ／ {len(rows)}銘柄を判定</div>

  <h2>📊 株の4タイプ（シクリカルバリュー株の循環サイクル）</h2>
  <div class="matrix-title">高PBR・高PER ↑</div>
  <div class="matrix">
    <div class="ax"></div><div class="ax tag"></div>
    <div class="ax tag" style="text-align:right">グロース株投資 ▶</div><div class="ax"></div>

    <div class="ax v">低成長</div>
    {_quad_cell("recession", by_q.get("recession", []))}
    {_quad_cell("ceiling",   by_q.get("ceiling", []))}
    <div class="ax v">高成長</div>

    <div class="ax v" style="color:#8a93a2;font-weight:400">資産バリュー</div>
    {_quad_cell("bottom",    by_q.get("bottom", []))}
    {_quad_cell("recovery",  by_q.get("recovery", []))}
    <div class="ax"></div>

    <div class="ax"></div><div class="ax tag">◀ 収益バリュー株投資（中央）</div>
    <div class="ax tag"></div><div class="ax"></div>
  </div>
  <div class="matrix-title">低PBR・低PER ↓</div>
  <div class="meta">🔄💎🪙=たーちゃん本命候補（マークつき）／<span style="color:#34d399">黒字転換✨・2年連続赤字</span>は底値サイン。
    循環は <b>どん底→回復期→天井→後退期</b> の順に回る。</div>

  <h2>📋 戦略別の詳細</h2>
  {"".join(sections) or "<p>該当銘柄なし。</p>"}

  <div class="note">
    <b>利益配分</b> = 資産バリュー1 : 収益バリュー1 : <b>シクリカルバリュー8（本命）</b>。
    景気循環業種で<b>2年連続赤字→黒字転換</b>を底値で仕込み、回復で大きく取る逆張り。
    <h3 style="margin-top:10px;">🔔 売り時の3ルール</h3>
    <ul>{sell}</ul>
  </div>
</body>
</html>"""


def save(rows: list[dict], out_path: str, title: str = "たーちゃん流 バリュー・スクリーナー") -> str:
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(render(rows, title))
    return out_path
