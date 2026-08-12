# note 予約投稿ワークフロー

note には公開 API がないため、**ログイン済みセッションを使ったブラウザ自動操作
（Playwright）** で「下書き作成 → 本文流し込み → サムネ設定 → ハッシュタグ →
マガジン追加 → 予約公開」までを行う。

## セットアップ（初回のみ）

```bash
pip install -r requirements.txt
python -m playwright install chromium   # 通常環境のみ。既に chromium がある環境は不要
```

## 1. note にログイン（Cookie を保存）

```bash
secretary note-login
```

ブラウザが開くので **自分の note アカウントでログイン**し、完了したらターミナルで
Enter。`note_cookies.json`（.gitignore 済み）にセッションが保存される。
環境変数 `NOTE_COOKIES`（storage_state JSON）でも渡せる。

## 2. 投稿設定を用意する

1 投稿 = 1 YAML。本文は Markdown で別ファイル。例:
[`2026-08-14-china-semiconductor.yaml`](2026-08-14-china-semiconductor.yaml)

重要なガード（**問題があれば予約せず停止**する）:

| 項目 | ルール |
|------|--------|
| `thumbnail` | 未設定 or ファイル不在なら停止（発注書の⚠️ルール） |
| `links.<key>.url` | 本文の `{{link:key}}` に対して URL が空/プレースホルダなら停止 |
| `publish_at` | 未設定なら停止 |
| `title` / 本文 | 空なら停止 |

本文中の note 誘導リンクは、Markdown で
`[アンカー文言]({{link:キー}})` と書き、YAML の `links.キー.url` に実 URL を入れる。
**URL を入れ忘れると予約は実行されない**（＝リンクが文字だけになる事故を防ぐ）。

## 3. まず検証（ブラウザは開かない）

```bash
secretary note-schedule -c note_posts/2026-08-14-china-semiconductor.yaml --dry-run
```

エラーが出たら潰す。よくあるのは「サムネ未設定」「誘導URL未差し込み」。

## 4. 予約を実行

```bash
secretary note-schedule -c note_posts/2026-08-14-china-semiconductor.yaml --x-stock
# 動作を目視したいとき: --show --slow-mo 300
```

`--x-stock` を付けると、予約完了後に X 告知文を
[`x_stock.md`](x_stock.md) へ発行済み記事URL入りで積む。

## 5. X 告知（手貼り）

X も API を使わない運用。`x_stock.md` に時刻付きで文面が積まれるので、
投稿時刻（例 19:00）にそこからコピペする。設定だけ先に積むなら:

```bash
secretary x-stock -c note_posts/2026-08-14-china-semiconductor.yaml --note-url <記事URL>
```

## 注意：DOM セレクタについて

note のエディタは SPA で、DOM は予告なく変わる。セレクタは
`secretary/note_ops.py` の `NoteBrowser` クラス上部に定数として集約してあるので、
壊れたらそこだけ直す。**初回は必ず `--show --slow-mo` で目視しながら**流し、
各ステップ（`[note] ...` ログ）が想定通り進むか確認すること。
