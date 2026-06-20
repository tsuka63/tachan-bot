"""
たーちゃん流バリュー投資の4戦略スクリーニング。

利益配分は 資産バリュー1 : 収益バリュー1 : シクリカルバリュー8 で、
シクリカル（景気循環）が本命。各戦略の判定条件は動画準拠。

  ① 資産バリュー   PBR ≤ 0.5 かつ 自己資本比率 ≥ 60%
  ② 収益バリュー   PER ≤ 15・営業利益率 ≥ 10%・ROA ≥ 7%・
                   時価総額 ≤ 300億・売上成長 < 20%
  ③ シクリカルV★  景気循環業種で 2年連続赤字 → 黒字転換 を狙う逆張り
  ④ グロース(避)   売上が年率20%以上の高成長 → 高値掴みリスクで対象外

売り時の3ルール（②は主観のため自動化せず参考表示）:
  1. シナリオが崩れたとき（業績悪化）
  2. もっと良い銘柄を見つけたとき
  3. 短期間で急騰したとき
"""

from __future__ import annotations

# ── ① 資産バリュー ──
ASSET_PBR_MAX    = 0.5
ASSET_EQUITY_MIN = 0.60
# ── ② 収益バリュー ──
EARN_PER_MAX     = 15.0
EARN_OPM_MIN     = 0.10
EARN_ROA_MIN     = 0.07
EARN_MKTCAP_MAX  = 30_000_000_000   # 300億円
EARN_REVGROW_MAX = 0.20
# ── ④ グロース（避ける）──
GROWTH_REVGROW   = 0.20

# 景気循環業種（鉄鋼/非鉄/造船/海運/化学 …）
_CYCLICAL_KEYWORDS = (
    "steel", "marine", "shipping", "chemical", "metal", "mining",
    "aerospace", "copper", "aluminum", "nonferrous", "paper", "oil", "gas",
)

# strategy key → (label, emoji, sort-rank)
STRATEGIES = {
    "cyclical": ("シクリカルV（本命）", "🔄", 0),
    "asset":    ("資産バリュー",        "💎", 1),
    "earnings": ("収益バリュー",        "🪙", 2),
    "growth":   ("グロース（避ける）",   "🚀", 3),
    "none":     ("該当なし",            "・", 4),
}

# 4-quadrant cycle (matches たーちゃん's "株の4タイプ" diagram):
# 縦 = 高PBR/PER↔低PBR/PER, 横 = 低成長↔高成長.
# Cycle flow: どん底 → 回復期 → 天井 → 後退期 → どん底 …
QUADRANTS = {
    "ceiling":   ("天井",   "高PBR/PER・高成長"),   # top-right
    "recession": ("後退期", "高PBR/PER・低成長"),   # top-left
    "bottom":    ("どん底", "低PBR/PER・低成長"),   # bottom-left
    "recovery":  ("回復期", "低PBR/PER・高成長"),   # bottom-right
    "unknown":   ("判定不可", "データ不足"),
}

# valuation / growth cut-offs for placing a stock on the matrix
VAL_PBR_HIGH = 1.5
VAL_PER_HIGH = 20.0
GROWTH_HIGH  = 0.10


def quadrant(m: dict) -> str:
    """Place a stock on the 4-type matrix by valuation × growth."""
    per, pbr = m.get("per"), m.get("pbr")
    g        = m.get("rev_growth")
    if per is None and pbr is None:
        return "unknown"
    expensive   = (pbr is not None and pbr >= VAL_PBR_HIGH) or (per is not None and per >= VAL_PER_HIGH)
    high_growth = g is not None and g >= GROWTH_HIGH
    if expensive and high_growth:
        return "ceiling"
    if expensive:
        return "recession"
    if high_growth:
        return "recovery"
    return "bottom"


def is_cyclical(sector: str | None, industry: str | None) -> bool:
    blob = f"{sector or ''} {industry or ''}".lower()
    return any(k in blob for k in _CYCLICAL_KEYWORDS)


def classify(m: dict) -> str:
    """Return the best-matching strategy key (cyclical has top priority)."""
    per, pbr = m.get("per"), m.get("pbr")
    eqr, opm = m.get("equity_ratio"), m.get("op_margin")
    roa, cap = m.get("roa"), m.get("market_cap")
    rev      = m.get("rev_growth")
    es       = m.get("earnings", {})
    cyc      = is_cyclical(m.get("sector"), m.get("industry"))

    # ③ シクリカルV（本命）: 循環業種 × 底値サイン
    if cyc and (es.get("two_year_loss") or es.get("turnaround") or es.get("loss_streak", 0) >= 1):
        return "cyclical"
    # ① 資産バリュー
    if pbr is not None and pbr <= ASSET_PBR_MAX and eqr is not None and eqr >= ASSET_EQUITY_MIN:
        return "asset"
    # ② 収益バリュー
    if (per is not None and 0 < per <= EARN_PER_MAX
            and opm is not None and opm >= EARN_OPM_MIN
            and roa is not None and roa >= EARN_ROA_MIN
            and cap is not None and cap <= EARN_MKTCAP_MAX
            and (rev is None or rev < EARN_REVGROW_MAX)):
        return "earnings"
    # ④ グロース（避ける）— 売上の高成長
    if rev is not None and rev >= GROWTH_REVGROW:
        return "growth"
    return "none"


def reasons(m: dict, key: str) -> list[str]:
    """Human-readable reasons why a stock matched (or didn't) its strategy."""
    es = m.get("earnings", {})
    out: list[str] = []
    if key == "cyclical":
        out.append(es.get("label", "—"))
        if m.get("industry"):
            out.append(str(m["industry"]))
    elif key == "asset":
        if m.get("pbr") is not None:
            out.append(f"PBR {m['pbr']:.2f}")
        if m.get("equity_ratio") is not None:
            out.append(f"自己資本比率 {m['equity_ratio']*100:.0f}%")
    elif key == "earnings":
        if m.get("per") is not None:
            out.append(f"PER {m['per']:.1f}")
        if m.get("op_margin") is not None:
            out.append(f"営利 {m['op_margin']*100:.0f}%")
        if m.get("roa") is not None:
            out.append(f"ROA {m['roa']*100:.0f}%")
    elif key == "growth":
        if m.get("rev_growth") is not None:
            out.append(f"売上成長 {m['rev_growth']*100:+.0f}%（高値掴み注意）")
    return out


def screen(rows: list[dict]) -> list[dict]:
    """Classify each fundamentals dict; attach 'strategy', 'reasons', 'quadrant'."""
    for m in rows:
        key = classify(m)
        m["strategy"] = key
        m["reasons"]  = reasons(m, key)
        m["quadrant"] = quadrant(m)
    rank = {k: v[2] for k, v in STRATEGIES.items()}
    return sorted(rows, key=lambda m: rank.get(m["strategy"], 9))


# ── 売り時の3ルール ──────────────────────────────────────────────────────
SELL_RULES = (
    "① シナリオが崩れたとき（業績が想定より悪化／経営方針の変更）",
    "② もっと良い銘柄を見つけたとき（※主観のため自動判定なし）",
    "③ 短期間で急騰したとき（利益が一気に乗ったら利確を検討）",
)


def spike_alert(returns_60d: float | None, threshold: float = 0.50) -> bool:
    """Sell-rule ③: flag a rapid run-up (default +50% over ~60 trading days)."""
    return returns_60d is not None and returns_60d >= threshold
