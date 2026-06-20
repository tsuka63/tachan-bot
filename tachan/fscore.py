"""
Piotroski F-Score — a 0–9 fundamental-health score.

Designed to separate genuine recoveries from value traps, so it pairs
perfectly with たーちゃん's contrarian "2年連続赤字を買う" approach: a beaten-down
stock with a HIGH F-Score is far more likely to be a real turnaround than one
with a low score.

9 checks (1 point each), comparing the latest fiscal year to the prior one:

  収益性 (4): ① ROA>0  ② 営業CF>0  ③ ROA改善  ④ 営業CF>純利益（質）
  安全性 (3): ⑤ 負債比率↓  ⑥ 流動比率↑  ⑦ 株式の非希薄化
  効率性 (2): ⑧ 粗利率↑  ⑨ 総資産回転率↑

≥7 = 良好、≤2 = 危険（罠の可能性）。
"""

from __future__ import annotations


def _base_offset(df, key) -> int:
    """First column index whose `key` value is not NaN (skips empty latest cols)."""
    try:
        for i, v in enumerate(df.loc[key].tolist()):
            if v == v:           # not NaN
                return i
    except Exception:
        pass
    return 0


def _at(df, key, i, base=0):
    """Value of `key` row at column index base+i, or None."""
    try:
        if df is None or key not in df.index:
            return None
        v = float(df.loc[key].iloc[base + i])
        return v if v == v else None
    except Exception:
        return None


def compute(ticker) -> dict:
    """Return {score, max, labels{name:0/1}, reliable}."""
    try:
        inc = ticker.income_stmt
        bal = ticker.balance_sheet
        cf  = ticker.cashflow
    except Exception:
        return {"score": None, "max": 9, "labels": {}, "reliable": False}

    # yfinance sometimes prepends an empty latest column; align each statement
    # to its first column that actually has data so the years line up.
    bi = _base_offset(inc, "Net Income")          if inc is not None else 0
    bb = _base_offset(bal, "Total Assets")        if bal is not None else 0
    bc = _base_offset(cf,  "Operating Cash Flow") if cf  is not None else 0

    # latest (0) and prior (1) fiscal year
    ni0,  ni1  = _at(inc, "Net Income", 0, bi),         _at(inc, "Net Income", 1, bi)
    ta0,  ta1  = _at(bal, "Total Assets", 0, bb),       _at(bal, "Total Assets", 1, bb)
    cfo0       = _at(cf,  "Operating Cash Flow", 0, bc)
    rev0, rev1 = _at(inc, "Total Revenue", 0, bi),      _at(inc, "Total Revenue", 1, bi)
    gp0,  gp1  = _at(inc, "Gross Profit", 0, bi),       _at(inc, "Gross Profit", 1, bi)
    ca0,  ca1  = _at(bal, "Current Assets", 0, bb),     _at(bal, "Current Assets", 1, bb)
    cl0,  cl1  = _at(bal, "Current Liabilities", 0, bb), _at(bal, "Current Liabilities", 1, bb)
    ltd0, ltd1 = _at(bal, "Long Term Debt", 0, bb),     _at(bal, "Long Term Debt", 1, bb)
    sh0,  sh1  = _at(bal, "Ordinary Shares Number", 0, bb), _at(bal, "Ordinary Shares Number", 1, bb)

    def ratio(a, b):
        return (a / b) if (a is not None and b not in (None, 0)) else None

    roa0, roa1 = ratio(ni0, ta0), ratio(ni1, ta1)
    ltdr0, ltdr1 = ratio(ltd0, ta0), ratio(ltd1, ta1)
    cur0, cur1 = ratio(ca0, cl0), ratio(ca1, cl1)
    gm0, gm1   = ratio(gp0, rev0), ratio(gp1, rev1)
    at0, at1   = ratio(rev0, ta0), ratio(rev1, ta1)

    # each test: (points, had_enough_data)
    checks: dict[str, tuple[int, bool]] = {}

    def gt(a, b):     # a > b with data present
        ok = a is not None and b is not None
        return (1 if (ok and a > b) else 0), ok
    def lt(a, b):
        ok = a is not None and b is not None
        return (1 if (ok and a < b) else 0), ok
    def pos(a):
        return (1 if (a is not None and a > 0) else 0), (a is not None)
    def le(a, b):
        ok = a is not None and b is not None
        return (1 if (ok and a <= b) else 0), ok

    checks["ROA>0"]       = pos(roa0)
    checks["営業CF>0"]    = pos(cfo0)
    checks["ROA改善"]     = gt(roa0, roa1)
    checks["CF>純利益"]   = gt(cfo0, ni0)
    checks["負債↓"]       = lt(ltdr0, ltdr1)
    checks["流動比率↑"]   = gt(cur0, cur1)
    checks["非希薄化"]    = le(sh0, sh1)
    checks["粗利率↑"]     = gt(gm0, gm1)
    checks["資産回転↑"]   = gt(at0, at1)

    labels  = {k: v[0] for k, v in checks.items()}
    n_data  = sum(1 for v in checks.values() if v[1])
    score   = sum(labels.values())
    return {"score": score, "max": 9, "labels": labels, "reliable": n_data >= 6}
