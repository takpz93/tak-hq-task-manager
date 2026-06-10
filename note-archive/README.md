# 📦 note-archive

[`writing-style.md`](../writing-style.md) を作るために、note [@mink_freelife](https://note.com/mink_freelife)
「30代パパフリーランスの朝日記」の実記事を自動取得・プレーンテキスト化したアーカイブ。

- [`note-corpus.txt`](note-corpus.txt) … 取得した直近**100本**の本文（計約18万字）。文体分析の元データ。
- [`all-note-keys.json`](all-note-keys.json) … アカウント全**381本**の (key, タイトル, 公開日) 一覧（2023-06〜2026-05）。さらに遡って取得したい時の元リスト。

## 取得方法（再取得したい時）

note.com が環境のネットワークポリシーで許可されている前提（roadmap.md「✍️ 発信の型」の状況メモ参照）。

```bash
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"

# 1. 記事一覧（key=nXXXX を集める）
curl -s -A "$UA" "https://note.com/api/v2/creators/mink_freelife/contents?kind=note&page=1"

# 2. 各記事の本文（JSON内 body がHTML）
curl -s -A "$UA" "https://note.com/api/v3/notes/<key>"
```

`all-note-keys.json` の key を使えば残り281本も同手順で取得可能（必要なら全381本まで拡張）。

取得日: 2026-06-10 / 取得本数: 100本（全381本中・直近）
