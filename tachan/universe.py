"""
Stock universes to screen — たーちゃん's hunting grounds.

A full ~3,800-name TSE sweep isn't feasible daily via yfinance (rate limits +
3 financial statements per stock), so this is a deliberately broad *curated*
list (~150 names) spanning every cyclical / low-PBR sector where 2年連続赤字→
黒字転換 turnarounds and 資産バリュー hidden-asset plays appear.

⚠️ It is still a subset — opportunities outside this list won't be found.
Add your own watchlist under "custom".
"""

UNIVERSES: dict[str, list[str]] = {
    # 鉄鋼
    "steel": ["5401", "5411", "5406", "5410", "5440", "5444", "5445", "5631",
              "5463", "5471", "5481", "5482", "5408"],
    # 海運
    "shipping": ["9101", "9104", "9107", "9110", "9115", "9119", "9069", "9101"],
    # 造船・重機・機械
    "machinery": ["7014", "7003", "7012", "7011", "7013", "6013", "6301", "6305",
                  "6326", "6361", "6367", "6471", "6472", "6473", "6113", "6103",
                  "6136", "6201", "6326", "6473"],
    # 非鉄金属・電線
    "nonferrous": ["5713", "5711", "5714", "5801", "5802", "5803", "5706", "5707",
                   "5715", "5727", "5938"],
    # 化学
    "chemical": ["4005", "4183", "4188", "4204", "3407", "4063", "4208", "4612",
                 "4021", "4042", "4045", "4061", "4088", "4091", "4118", "4203",
                 "4205", "3405", "3402", "3401"],
    # 紙・パルプ
    "paper": ["3861", "3863", "3880", "3865"],
    # 石油・エネルギー
    "energy": ["5020", "5019", "5021", "1605", "1662"],
    # 商社
    "trading": ["8001", "8002", "8015", "8031", "8053", "8058", "2768", "8020"],
    # 自動車・部品・タイヤ
    "auto": ["7203", "7201", "7267", "7269", "7270", "7211", "7202", "7261",
             "6902", "7259", "5108", "5101", "5110", "7282"],
    # 建設・不動産
    "construction": ["1801", "1802", "1803", "1808", "1812", "1925", "1928",
                     "8801", "8802", "8830", "8804", "3289"],
    # 繊維・資産バリュー候補
    "asset": ["3201", "3101", "3103", "3105", "3110", "3023", "3107", "8016",
              "2768", "3201"],
    # ガラス・土石・セラミック
    "ceramic": ["5201", "5202", "5232", "5233", "5301", "5333", "5334"],
    # 半導体・電機（景気敏感）
    "semicon": ["8035", "6857", "6146", "6976", "3436", "6963", "6967"],
}

# Cyclical sweep = all cyclical sectors combined (deduped, drop junk codes)
def _clean(codes):
    return sorted({c for c in codes if c.isdigit() and len(c) == 4})

UNIVERSES["cyclical"] = _clean(
    c for k in ("steel", "shipping", "machinery", "nonferrous", "chemical",
                "paper", "energy", "ceramic", "semicon")
    for c in UNIVERSES[k]
)

# Everything (deduped)
UNIVERSES["all"] = _clean(c for v in UNIVERSES.values() for c in v)
