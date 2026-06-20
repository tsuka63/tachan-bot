# tachan-bot — たーちゃん流 バリュー・スクリーナー

個人投資家・たーちゃん氏の投資手法をコード化した、**stock-bot とは独立した**
スクリーニングツール。日本株のファンダメンタルズから、4つの戦略タイプに分類する。

利益配分の目安は **資産バリュー1 : 収益バリュー1 : シクリカルバリュー8**
（シクリカルが本命）。

## 4戦略の判定条件（動画準拠）

| 戦略 | 条件 |
|------|------|
| 🔄 **シクリカルV（本命）** | 景気循環業種（鉄鋼/海運/造船/非鉄/化学…）で **2年連続赤字→黒字転換** を底値で仕込む逆張り |
| 💎 資産バリュー | PBR ≤ 0.5 かつ 自己資本比率 ≥ 60%（含み資産狙い） |
| 🪙 収益バリュー | PER ≤ 15・営業利益率 ≥ 10%・ROA ≥ 7%・時価総額 ≤ 300億・売上成長 < 20% |
| 🚀 グロース（避ける） | 売上が年率20%以上の高成長 → 高値掴みリスクで対象外 |

## 売り時の3ルール
1. シナリオが崩れたとき（業績悪化／経営方針変更）
2. もっと良い銘柄を見つけたとき（※主観・自動判定なし）
3. 短期間で急騰したとき（利確を検討）

## 使い方

```bash
pip install -r requirements.txt

# 景気循環株を一括スクリーニング（本命）
python scripts/screen.py --universe cyclical --report

# 業種別
python scripts/screen.py --universe steel        # 鉄鋼
python scripts/screen.py --universe shipping     # 海運

# 個別指定
python scripts/screen.py --symbols 5401,9101,7014
```

`--report` を付けると `data/screen.html` を生成（ブラウザで閲覧）。

## 構成

```
tachan-bot/
├── tachan/
│   ├── fundamentals.py   yfinance から PER/PBR/ROA/自己資本比率/純利益履歴/業種 を取得
│   ├── strategy.py       4戦略の判定ロジック + 売り時ルール
│   ├── universe.py       景気循環/資産バリュー候補の銘柄リスト
│   └── report.py         HTMLレポート生成
└── scripts/
    └── screen.py         CLI
```

## データソース
Yahoo Finance（yfinance）。財務データは遅延・欠損があり得るため、
最終判断は決算短信・有価証券報告書で確認すること。これは投資助言ではない。
