"""
Fundamental data for Japanese stocks (Yahoo Finance via yfinance).

Pulls everything たーちゃん's screens need: valuation (PER/PBR), profitability
(営業利益率/ROA), balance-sheet strength (自己資本比率), size (時価総額),
growth (売上成長), sector, and the net-income history used to spot
2年連続赤字 → 黒字転換 turnarounds.
"""

from __future__ import annotations


def _f(x) -> float | None:
    try:
        v = float(x)
        return v if v == v else None      # drop NaN
    except (TypeError, ValueError):
        return None


def _yahoo_symbol(code: str) -> str:
    return f"{code}.T" if (code.isdigit() and len(code) == 4) else code


def earnings_history(ticker) -> dict:
    """
    Net-income history → loss streak and 黒字転換 flag.

    Returns {net_income[], loss_streak, two_year_loss, turnaround, label}.
    `net_income` is newest-first (億円).
    """
    out = {"net_income": [], "loss_streak": 0, "two_year_loss": False,
           "turnaround": False, "label": "—"}
    try:
        stmt = ticker.income_stmt
        if stmt is None or "Net Income" not in stmt.index:
            return out
        ni = [float(v) for v in stmt.loc["Net Income"].tolist() if v == v]  # newest first
    except Exception:
        return out
    if not ni:
        return out

    out["net_income"] = [round(v / 1e8, 0) for v in ni]      # 億円
    streak = 0
    for v in ni:
        if v < 0:
            streak += 1
        else:
            break
    out["loss_streak"]   = streak
    out["two_year_loss"] = len(ni) >= 2 and ni[0] < 0 and ni[1] < 0
    out["turnaround"]    = len(ni) >= 2 and ni[0] > 0 and ni[1] < 0

    if out["turnaround"]:
        out["label"] = "黒字転換✨"
    elif out["two_year_loss"]:
        out["label"] = "2年連続赤字"
    elif streak == 1:
        out["label"] = "今期赤字"
    else:
        out["label"] = "黒字"
    return out


def fetch(code: str) -> dict:
    """Return a full fundamentals snapshot for one stock code."""
    import yfinance as yf

    tk = yf.Ticker(_yahoo_symbol(code))
    try:
        info = tk.info or {}
    except Exception:
        info = {}

    # 自己資本比率 = 株主資本 / 総資産
    equity_ratio = None
    try:
        bs = tk.balance_sheet
        if bs is not None and "Total Assets" in bs.index and "Stockholders Equity" in bs.index:
            ta = float(bs.loc["Total Assets"].iloc[0])
            eq = float(bs.loc["Stockholders Equity"].iloc[0])
            if ta:
                equity_ratio = eq / ta
    except Exception:
        pass

    price   = _f(info.get("currentPrice"))
    div     = _f(info.get("dividendRate"))
    hi52    = _f(info.get("fiftyTwoWeekHigh"))
    lo52    = _f(info.get("fiftyTwoWeekLow"))

    # 配当利回り = 配当 / 株価（曖昧さを避けて自前計算）
    div_yield = (div / price) if (div is not None and price) else _f(info.get("dividendYield"))
    # 52週レンジ内の位置（0%=安値圏／100%=高値圏）
    pos52 = None
    if price is not None and hi52 is not None and lo52 is not None and hi52 > lo52:
        pos52 = (price - lo52) / (hi52 - lo52) * 100

    return {
        "code":         str(code),
        "name":         info.get("shortName") or info.get("longName") or str(code),
        "price":        price,
        "eps":          _f(info.get("trailingEps")),
        "bps":          _f(info.get("bookValue")),
        "dividend":     div,
        "div_yield":    div_yield,
        "week52_high":  hi52,
        "week52_low":   lo52,
        "pos52":        pos52,
        "roe":          _f(info.get("returnOnEquity")),
        "per":          _f(info.get("trailingPE")),
        "pbr":          _f(info.get("priceToBook")),
        "op_margin":    _f(info.get("operatingMargins")),
        "roa":          _f(info.get("returnOnAssets")),
        "market_cap":   _f(info.get("marketCap")),
        "rev_growth":   _f(info.get("revenueGrowth")),
        "equity_ratio": equity_ratio,
        "sector":       info.get("sector"),
        "industry":     info.get("industry"),
        "earnings":     earnings_history(tk),
    }


def fetch_many(codes: list[str]) -> list[dict]:
    return [fetch(c) for c in codes]
