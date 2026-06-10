# 📦 note-archive

[`writing-style.md`](../writing-style.md) を作るために、note [@mink_freelife](https://note.com/mink_freelife)
「30代パパフリーランスの朝日記」の実記事を自動取得・プレーンテキスト化したアーカイブ。

- [`note-corpus.txt`](note-corpus.txt) … 取得した記事18本の本文（計約3万字）。文体分析の元データ。

## 取得方法（再取得したい時）

note.com が環境のネットワークポリシーで許可されている前提（roadmap.md「✍️ 発信の型」の状況メモ参照）。

```bash
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"

# 1. 記事一覧（key=nXXXX を集める）
curl -s -A "$UA" "https://note.com/api/v2/creators/mink_freelife/contents?kind=note&page=1"

# 2. 各記事の本文（JSON内 body がHTML）
curl -s -A "$UA" "https://note.com/api/v3/notes/<key>"
```

取得日: 2026-06-10 / 取得本数: 18本
