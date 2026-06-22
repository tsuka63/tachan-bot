"""Smoke tests (no network) — run: python tests/test_smoke.py"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from tachan.strategy import classify, quadrant, is_cyclical
from tachan.fscore   import compute  # noqa: F401  (ensure module imports)


def test_quadrant():
    # 低PBR・高成長 → 回復期(recovery)
    assert quadrant({"per": 8, "pbr": 0.9, "rev_growth": 0.20}) == "recovery"
    # 高PBR・高成長 → 天井(ceiling)
    assert quadrant({"per": 40, "pbr": 5.0, "rev_growth": 0.30}) == "ceiling"
    # 低PBR・低成長 → どん底(bottom)
    assert quadrant({"per": 7, "pbr": 0.5, "rev_growth": 0.0}) == "bottom"
    # データなし → unknown
    assert quadrant({"per": None, "pbr": None, "rev_growth": None}) == "unknown"


def test_is_cyclical():
    assert is_cyclical("Basic Materials", "Steel")
    assert is_cyclical(None, "Marine Shipping")
    assert not is_cyclical("Technology", "Software")


def test_classify_cyclical_priority():
    # 循環業種 × 2年連続赤字 → 本命(cyclical)
    m = {"sector": "Basic Materials", "industry": "Steel",
         "earnings": {"two_year_loss": True, "turnaround": False, "loss_streak": 2}}
    assert classify(m) == "cyclical"


def test_classify_asset():
    m = {"pbr": 0.4, "equity_ratio": 0.7, "earnings": {}, "sector": "Real Estate"}
    assert classify(m) == "asset"


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for fn in fns:
        fn()
        print(f"  ✓ {fn.__name__}")
    print(f"OK — {len(fns)} tests passed")
