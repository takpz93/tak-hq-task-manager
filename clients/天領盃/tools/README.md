# 天領盃「加登仙一の日本酒大学」週次レポート

`yt_weekly_report.py` が Analytics API / Data API / Reporting API から毎週同じ指標を取り、
`clients/天領盃/output/週次レポート_YYYYMMDD.md`（表のみ）と `維持率_YYYYMMDD/*.csv` を出します。
解釈・考察は書きません。

## 初回セットアップ（手元のPCで1回だけ）

1. Google Cloud Console で新規プロジェクト → 「APIとサービス」で次を有効化
   - YouTube Analytics API
   - YouTube Data API v3
   - YouTube Reporting API
2. 「認証情報」→ OAuth クライアントID（アプリの種類: デスクトップ）を作成し、JSON をダウンロード
   → `clients/天領盃/credentials/client_secret.json` に保存
3. OAuth 同意画面のテストユーザーに、チャンネルの管理者権限を持つ Google アカウントを追加
4. 依存インストール: `pip install -r clients/天領盃/tools/requirements.txt`
5. 初回実行: `python3 clients/天領盃/tools/yt_weekly_report.py`
   ブラウザが開くので、管理者権限のアカウントで許可 → `credentials/token.json` が保存され、以降は無人で動きます。

## 毎週の実行

```
python3 clients/天領盃/tools/yt_weekly_report.py            # 実行日＝今日、期間は前日まで7日
python3 clients/天領盃/tools/yt_weekly_report.py --date 2026-09-28
python3 clients/天領盃/tools/yt_weekly_report.py --public-only   # 認証なし。動画一覧と企画タイプだけ
```

日曜に cron / launchd で回す場合の例（毎週日曜 09:00）:

```
0 9 * * 0 cd /path/to/repo && python3 clients/天領盃/tools/yt_weekly_report.py >> clients/天領盃/output/run.log 2>&1
```

## 出力

- タスク1 週次サマリー: 直近7日／前週／2週前／3週前／直近28日／前28日。登録増・減は分離、分/視聴 列あり
- タスク2 動画別: 直近12本の横動画（180秒以下と #shorts 除外）。企画タイプ、登録/1000h、流入元TOP3
- タスク3 維持率: 対象5本（東京の酒屋／純米大吟醸／2026秋／中国地方編／関西、見つからない分は最新で補完）。
  1%刻みCSV、30秒/1分/3分/5分/10分/中央/終盤の表、直前比3pt以上の落ち込みを mm:ss で列挙、字幕があれば発話を添付
- タスク4 流入元: 直近28日・前28日の流入元別、YouTube検索の検索語TOP20
- 末尾にターミナルへ「会話に貼る用」要約（各表上位4行、2000字以内）

## 既知の制約

- **インプレッション・CTR**: Analytics API には無い指標です。スクリプトは Reporting API の
  `channel_reach_basic_a1` ジョブを自動作成し、レポートにインプレッション系の列があれば集計、無ければ空欄にします。
  ジョブ作成後、レポート生成まで 1〜2 日かかります（初回実行時は空欄になります）。
  公開ドキュメント上、この帳票にサムネイル・インプレッションの列は含まれていない可能性が高く、
  その場合は Studio からの手動転記が必要です。
- Analytics API の集計は 2〜3 日遅れます。「直近7日」の末尾 2 日は翌週に増えることがあります。
- 視聴回数は 2026-08-27 以降、YouTube 側の問題で水増しの可能性があるため各表に注記を入れています。
- 字幕は `youtube-transcript-api` で取得します。取れない動画は `clients/天領盃/scripts/{動画ID}.srt` を置くと使われます。
