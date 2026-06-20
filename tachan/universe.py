"""
Stock universes to screen — focused on たーちゃん's hunting grounds:
景気循環業種（鉄鋼・海運・造船・非鉄・化学・紙・石油）where 2年連続赤字→
黒字転換 turnarounds and 資産バリュー hidden-asset plays tend to appear.

Add your own watchlist under "custom".
"""

UNIVERSES: dict[str, list[str]] = {
    # 鉄鋼
    "steel": ["5401", "5411", "5406", "5410", "5440", "5444", "5631"],
    # 海運
    "shipping": ["9101", "9104", "9107", "9110", "9115"],
    # 造船・重機
    "shipbuilding": ["7014", "7003", "7012", "7011", "6013"],
    # 非鉄金属
    "nonferrous": ["5713", "5711", "5714", "5801", "5802", "5803", "5706"],
    # 化学
    "chemical": ["4005", "4183", "4188", "4204", "3407", "4063", "4208", "4612"],
    # 紙・パルプ
    "paper": ["3861", "3863", "3880"],
    # 石油・エネルギー
    "energy": ["5020", "5019", "5021", "1605"],
    # 資産バリュー候補（低PBR・含み資産で知られる例）
    "asset": ["3201", "8016", "3023", "8002", "2768", "3107"],
}

# Broad cyclical sweep = all of the cyclical sectors combined
UNIVERSES["cyclical"] = sorted({
    c for k in ("steel", "shipping", "shipbuilding", "nonferrous", "chemical", "paper", "energy")
    for c in UNIVERSES[k]
})

# Everything
UNIVERSES["all"] = sorted({c for v in UNIVERSES.values() for c in v})
