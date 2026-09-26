# 競合6チャンネル｜直近1年（2025-09-20以降）で基準を超えた動画

## 取得条件・データソース
- YouTube Data API v3 のキー（YOUTUBE_API_KEY）が実行環境に無いため、YouTube内部API（youtubei.googleapis.com の /browse・/next）から取得。登録者数はチャンネルページ表示の概数、再生数・公開日は各動画ページの実値（2026-09-26取得）
- 倍率＝再生数÷現在の登録者数（概数）。抽出基準: 登録10万人以上→1倍以上／1万〜10万人→2倍以上／1万人未満→3倍以上
- 尺は動画タブの表示値。ショート棚（Shortsタブ）掲載動画は秒数が取得できないため尺は「—」とし、ショート棚掲載を根拠に別テーブルに分離
- サムネイルURLは YouTube 標準の hqdefault（480×360）

## 対象チャンネル

| チャンネル名 | channel_id | 登録者数（表示） | 1年以内の動画数（通常） | 1年以内のショート数 |
|---|---|---|---|---|
| センスアールのRYUYA | UCXCy0fYOsvGFDSOHXJX4JUw | 2.75万人 | 116 | 48 |
| WAX-WASH | UClwYG24hyQ2fUcCMyXNxRpg | 16万人 | 18 | 27 |
| ピットワン | UCW3rbAgw8x0brFr29v50FJg | 25.7万人 | 116 | 39 |
| チャンネル隊長 | UCEgvzVCeW2MnHV-M62CxBDQ | 21.7万人 | 189 | 127 |
| ワイズ社長のワイズチャンネル | UCr65_J7H0Lu_zJHOCuHswww | 12.5万人 | 283 | 2 |
| 僕たちの洗車旅。 | UCBHG2P_CcPLCQkFQROGxjLA | 2.3万人 | 67 | 154 |

## 通常動画（基準以上・倍率降順・120本）

| チャンネル名 | 登録者数 | タイトル | 公開日 | 再生数 | 倍率 | 尺 | 動画URL | サムネイルURL |
|---|---|---|---|---|---|---|---|---|
| 僕たちの洗車旅。 | 2.3万人 | 【洗車拒否】20代女子の放置プリウスを勝手に洗車したらヤバい事になった | 2026-05-30 | 699,245 | 30.40 | 32:31 | https://www.youtube.com/watch?v=HFtDuu5fq5s | https://i.ytimg.com/vi/HFtDuu5fq5s/hqdefault.jpg |
| センスアールのRYUYA | 2.8万人 | 【プロ直伝】9割が知らないコメリ水垢剤「赤と青」の本当の使い分け！間違えると逆効果になります | 2026-07-13 | 616,864 | 22.43 | 9:36 | https://www.youtube.com/watch?v=I_e7NkZZrwc | https://i.ytimg.com/vi/I_e7NkZZrwc/hqdefault.jpg |
| センスアールのRYUYA | 2.8万人 | 【コメリ新作】削らず“埋めて消す”傷消しポリマーが想像以上…プロが実演レビュー | 2026-06-18 | 574,902 | 20.91 | 16:54 | https://www.youtube.com/watch?v=68jpS-PJK08 | https://i.ytimg.com/vi/68jpS-PJK08/hqdefault.jpg |
| センスアールのRYUYA | 2.8万人 | 【本音レビュー】キーパーコーティングって実際どうなの？プロが正直に語ります。 | 2025-09-27 | 304,647 | 11.08 | 18:00 | https://www.youtube.com/watch?v=-PBodPFRM0Q | https://i.ytimg.com/vi/-PBodPFRM0Q/hqdefault.jpg |
| センスアールのRYUYA | 2.8万人 | 【初心者必見】そのホイールの洗い方、間違ってます！プロ直伝の手順とは | 2026-04-07 | 272,276 | 9.90 | 20:58 | https://www.youtube.com/watch?v=rB8h_2SoxgQ | https://i.ytimg.com/vi/rB8h_2SoxgQ/hqdefault.jpg |
| センスアールのRYUYA | 2.8万人 | 【洗車のプロが解説】ディーラーと専門店のコーティングの違い。Keeperって実際どうなの？ | 2025-09-24 | 235,380 | 8.56 | 16:27 | https://www.youtube.com/watch?v=usw_rUIK7jc | https://i.ytimg.com/vi/usw_rUIK7jc/hqdefault.jpg |
| センスアールのRYUYA | 2.8万人 | 【プロ直伝】9割が間違ってる！コメリ樹脂コートの正しい使い方で黒ツヤ完全復活 | 2026-06-11 | 234,358 | 8.52 | 18:07 | https://www.youtube.com/watch?v=LMPcW2qF9E0 | https://i.ytimg.com/vi/LMPcW2qF9E0/hqdefault.jpg |
| センスアールのRYUYA | 2.8万人 | 【売切れ続出】コメリの498円“純水ガラスクリーナー”は本当に凄い？プロが忖度なしレビュー | 2026-09-21 | 210,122 | 7.64 | 11:18 | https://www.youtube.com/watch?v=GmzdVBoDAQM | https://i.ytimg.com/vi/GmzdVBoDAQM/hqdefault.jpg |
| センスアールのRYUYA | 2.8万人 | 【キーパー施工体験】研磨なしでも本当にキレイになる？プロショップで実際に試してみた結果がやばかった... | 2025-11-21 | 198,444 | 7.22 | 14:08 | https://www.youtube.com/watch?v=-x1VxVsBq1A | https://i.ytimg.com/vi/-x1VxVsBq1A/hqdefault.jpg |
| センスアールのRYUYA | 2.8万人 | 【プロ直伝】9割が間違ってる！DCMヘッドライトクリーナーの正しい使い方で黄ばみが秒殺 | 2026-09-05 | 187,676 | 6.82 | 12:22 | https://www.youtube.com/watch?v=0NFlrgjCL2k | https://i.ytimg.com/vi/0NFlrgjCL2k/hqdefault.jpg |
| 僕たちの洗車旅。 | 2.3万人 | 【洗車する人全員見て】板金塗装屋が明かす 車を守るために絶対知っておくべき事実 | 2026-01-24 | 136,465 | 5.93 | 40:59 | https://www.youtube.com/watch?v=cgpUQPPWsfo | https://i.ytimg.com/vi/cgpUQPPWsfo/hqdefault.jpg |
| センスアールのRYUYA | 2.8万人 | 今すぐやめて】コーティング施工車が洗車機で選ぶと危険なメニュー｜新車RAV4で検証 | 2026-06-14 | 156,902 | 5.71 | 11:58 | https://www.youtube.com/watch?v=N8Gw60Mxciw | https://i.ytimg.com/vi/N8Gw60Mxciw/hqdefault.jpg |
| ワイズ社長のワイズチャンネル | 12.5万人 | 【これどう思いますか？】保険屋と喧嘩しました | 2026-03-03 | 665,546 | 5.32 | 13:56 | https://www.youtube.com/watch?v=Dr-2NDrqlJk | https://i.ytimg.com/vi/Dr-2NDrqlJk/hqdefault.jpg |
| センスアールのRYUYA | 2.8万人 | 【実演】研磨しないのに…なぜ傷が消える？プロだけがやってる裏技 | 2026-02-06 | 139,474 | 5.07 | 17:28 | https://www.youtube.com/watch?v=dy_RjpeT07Q | https://i.ytimg.com/vi/dy_RjpeT07Q/hqdefault.jpg |
| センスアールのRYUYA | 2.8万人 | 【速報】コメリの2026年最新展示会に潜入！アップデートされるアイテムや新商品など洗車のプロが厳選レビュー | 2026-09-07 | 138,977 | 5.05 | 39:01 | https://www.youtube.com/watch?v=1ylikDML0_w | https://i.ytimg.com/vi/1ylikDML0_w/hqdefault.jpg |
| ワイズ社長のワイズチャンネル | 12.5万人 | 返金対応したのに返ってきた車は販売した現状ではなかった【アタオカ返金トラブルパート２】 | 2026-09-12 | 606,894 | 4.86 | 9:26 | https://www.youtube.com/watch?v=aucwZb-lynY | https://i.ytimg.com/vi/aucwZb-lynY/hqdefault.jpg |
| ワイズ社長のワイズチャンネル | 12.5万人 | 【YouTube史上ナンバー１】前オーナーが数日で売却を決意した、とんでもない車を買い取っってしまいました。 | 2025-12-02 | 581,561 | 4.65 | 13:01 | https://www.youtube.com/watch?v=mihNXTcaFBE | https://i.ytimg.com/vi/mihNXTcaFBE/hqdefault.jpg |
| 僕たちの洗車旅。 | 2.3万人 | 【99％の人が知らない】グラスターゾルオートの本当の使い方【激安万能クリーナー】 | 2025-10-25 | 103,958 | 4.52 | 26:16 | https://www.youtube.com/watch?v=Y-3O-j4gUqw | https://i.ytimg.com/vi/Y-3O-j4gUqw/hqdefault.jpg |
| ワイズ社長のワイズチャンネル | 12.5万人 | １０万ｋｍ超の車を買う奴はアホの貧乏人 | 2025-10-22 | 522,795 | 4.18 | 14:08 | https://www.youtube.com/watch?v=EbKnotTIORo | https://i.ytimg.com/vi/EbKnotTIORo/hqdefault.jpg |
| センスアールのRYUYA | 2.8万人 | 【初心者必見】90分→30分！時短とキズ防止が両立する洗車術 | 2025-12-19 | 113,327 | 4.12 | 29:33 | https://www.youtube.com/watch?v=KMj-tMapqXY | https://i.ytimg.com/vi/KMj-tMapqXY/hqdefault.jpg |
| センスアールのRYUYA | 2.8万人 | 【初心者向け】水垢の正体と“最短で落とす順番”｜もう迷わない | 2026-02-18 | 111,373 | 4.05 | 15:48 | https://www.youtube.com/watch?v=0C1x0sMnRGU | https://i.ytimg.com/vi/0C1x0sMnRGU/hqdefault.jpg |
| ワイズ社長のワイズチャンネル | 12.5万人 | 【勘違いするな】またバディカ。。。 | 2026-04-09 | 484,876 | 3.88 | 10:43 | https://www.youtube.com/watch?v=lYdGpU7RTkw | https://i.ytimg.com/vi/lYdGpU7RTkw/hqdefault.jpg |
| センスアールのRYUYA | 2.8万人 | 【コメリ越え？】DCMがコスパ最強!!水アカクリーナー最強はどっち？洗車のプロがガチ比較  | 2026-08-30 | 106,311 | 3.87 | 11:09 | https://www.youtube.com/watch?v=f-XYYxMBaWY | https://i.ytimg.com/vi/f-XYYxMBaWY/hqdefault.jpg |
| ワイズ社長のワイズチャンネル | 12.5万人 | 水没車・冠水車の事を全て話します | 2026-08-18 | 473,735 | 3.79 | 20:59 | https://www.youtube.com/watch?v=McSk1yIomFI | https://i.ytimg.com/vi/McSk1yIomFI/hqdefault.jpg |
| ワイズ社長のワイズチャンネル | 12.5万人 | 【不思議】冠水した１５０００台が行方不明になりました。オートオークションなどで見てみましたがほぼ出品されていません。 | 2026-09-07 | 457,958 | 3.66 | 8:57 | https://www.youtube.com/watch?v=omw3_zFWxkA | https://i.ytimg.com/vi/omw3_zFWxkA/hqdefault.jpg |
| ワイズ社長のワイズチャンネル | 12.5万人 | 【グーニーズワン夜逃げ】スズキの副代理店でジムニーショップだった車屋がとうさんした理由を解説します | 2026-04-04 | 453,944 | 3.63 | 14:05 | https://www.youtube.com/watch?v=fBb_zd6CEC4 | https://i.ytimg.com/vi/fBb_zd6CEC4/hqdefault.jpg |
| WAX-WASH | 16.0万人 | 洗車しても報われない人の共通点3つをプロ解説 | 2026-02-15 | 570,655 | 3.57 | 15:34 | https://www.youtube.com/watch?v=fIXjeqPlgdo | https://i.ytimg.com/vi/fIXjeqPlgdo/hqdefault.jpg |
| ワイズ社長のワイズチャンネル | 12.5万人 | 日本最大のUSS東京オークションが水没したので誰が車の責任を負うのかを説明します | 2026-09-22 | 438,178 | 3.51 | 21:21 | https://www.youtube.com/watch?v=Wq9bDP4sDRw | https://i.ytimg.com/vi/Wq9bDP4sDRw/hqdefault.jpg |
| ワイズ社長のワイズチャンネル | 12.5万人 | 納車してすぐ返金対応を求める客に返金して切りました | 2026-09-10 | 433,706 | 3.47 | 11:36 | https://www.youtube.com/watch?v=xF0RZxyj-Xo | https://i.ytimg.com/vi/xF0RZxyj-Xo/hqdefault.jpg |
| WAX-WASH | 16.0万人 | 水弾きが消えたレクサスIS｜犯人はコーティングじゃない【洗車】 | 2026-06-27 | 546,735 | 3.42 | 21:29 | https://www.youtube.com/watch?v=uUgjy9gBDEA | https://i.ytimg.com/vi/uUgjy9gBDEA/hqdefault.jpg |
| ワイズ社長のワイズチャンネル | 12.5万人 | 【削除覚悟】実は今、車屋界隈で大騒ぎになってることがあり、そのことについて誰も言いませんが暴露します。皆様にとって2026は損しかないです | 2026-01-01 | 426,985 | 3.42 | 12:46 | https://www.youtube.com/watch?v=IdRXDBxLews | https://i.ytimg.com/vi/IdRXDBxLews/hqdefault.jpg |
| センスアールのRYUYA | 2.8万人 | 【要注意】そのポリッシャーの使い方、完全に間違ってます｜初心者が必ずハマる落とし穴とは？ | 2026-05-12 | 93,321 | 3.39 | 25:32 | https://www.youtube.com/watch?v=1rFJhD5oLq4 | https://i.ytimg.com/vi/1rFJhD5oLq4/hqdefault.jpg |
| センスアールのRYUYA | 2.8万人 | 【もう時代遅れ】洗車のプロが今は買わない洗車用品10選…昔は正解だったのに今使うと車がダメになります 1 | 2026-08-10 | 91,831 | 3.34 | 15:40 | https://www.youtube.com/watch?v=3bT6t-toBXY | https://i.ytimg.com/vi/3bT6t-toBXY/hqdefault.jpg |
| センスアールのRYUYA | 2.8万人 | 【中古車買ったらこれやれ】くすんだ黒いヴォクシーを甦らせる。プロが教える納車後の徹底洗車 | 2026-07-10 | 88,918 | 3.23 | 29:10 | https://www.youtube.com/watch?v=iktecEPeSTc | https://i.ytimg.com/vi/iktecEPeSTc/hqdefault.jpg |
| ワイズ社長のワイズチャンネル | 12.5万人 | 【赤字確定】最近の車にほぼ付いているコレが潰れたら数十万円の故障になります | 2026-02-21 | 393,710 | 3.15 | 13:33 | https://www.youtube.com/watch?v=SHYv_GXqW3U | https://i.ytimg.com/vi/SHYv_GXqW3U/hqdefault.jpg |
| センスアールのRYUYA | 2.8万人 | 【プロ直伝】9割が間違ってる！黒い車の正しい洗車法…キズを増やさない唯一の方法 | 2026-08-02 | 86,153 | 3.13 | 17:37 | https://www.youtube.com/watch?v=OEkn3VLQBsY | https://i.ytimg.com/vi/OEkn3VLQBsY/hqdefault.jpg |
| ワイズ社長のワイズチャンネル | 12.5万人 | 某激安専門店から業販仕入れした車、絶対に訳ありやろ | 2025-11-12 | 357,902 | 2.86 | 12:19 | https://www.youtube.com/watch?v=dhAskVNEe8Y | https://i.ytimg.com/vi/dhAskVNEe8Y/hqdefault.jpg |
| ピットワン | 25.7万人 | 軽自動車を中古で買うな！？安いのにはワケがある？買ったら後悔する中古車とは？？ | 2025-10-18 | 726,358 | 2.83 | 25:22 | https://www.youtube.com/watch?v=ZPgHkKexv6M | https://i.ytimg.com/vi/ZPgHkKexv6M/hqdefault.jpg |
| センスアールのRYUYA | 2.8万人 | 【比較検証】車の内窓拭きで一番ムラが出ないのはどれ？｜洗車のプロが全部試す | 2026-07-29 | 77,458 | 2.82 | 12:58 | https://www.youtube.com/watch?v=_uqrzUjjdC4 | https://i.ytimg.com/vi/_uqrzUjjdC4/hqdefault.jpg |
| センスアールのRYUYA | 2.8万人 | 【洗車のプロが検証】リンレイ硬化型コーティングが最強？脅威の撥水と耐久性で常識を覆しました... | 2025-11-08 | 76,657 | 2.79 | 20:54 | https://www.youtube.com/watch?v=YWRwOcaOK78 | https://i.ytimg.com/vi/YWRwOcaOK78/hqdefault.jpg |
| ワイズ社長のワイズチャンネル | 12.5万人 | 【完全終了】３年経過でアルファードハイパーリセール終了 | 2026-09-04 | 342,966 | 2.74 | 13:07 | https://www.youtube.com/watch?v=gtwwiKwaaeU | https://i.ytimg.com/vi/gtwwiKwaaeU/hqdefault.jpg |
| センスアールのRYUYA | 2.8万人 | 【徹底比較】最強のスケール除去剤はどれ？人気5種類を洗車のプロが本気検証！ | 2026-06-30 | 75,370 | 2.74 | 20:02 | https://www.youtube.com/watch?v=o7bo7o2JMKw | https://i.ytimg.com/vi/o7bo7o2JMKw/hqdefault.jpg |
| チャンネル隊長 | 21.7万人 | 【車整備】車エアコンの効きが悪い人必見！たった1本で冷房効率を劇的に上げる方法【ワコーズ パワーエアコンプラス】 | 2026-07-14 | 582,559 | 2.68 | 8:16 | https://www.youtube.com/watch?v=8ZnnYOWHd3s | https://i.ytimg.com/vi/8ZnnYOWHd3s/hqdefault.jpg |
| ワイズ社長のワイズチャンネル | 12.5万人 | 俺の思い全部話すから、バディカ中野、聞け。ガッキーもな。 | 2026-01-09 | 326,412 | 2.61 | 22:35 | https://www.youtube.com/watch?v=cJTDH80h454 | https://i.ytimg.com/vi/cJTDH80h454/hqdefault.jpg |
| 僕たちの洗車旅。 | 2.3万人 | 【ドッキリ検証】洗車プロがレンタカーを勝手に洗ったら…店長が衝撃の反応 | 2026-07-11 | 58,870 | 2.56 | 32:54 | https://www.youtube.com/watch?v=vPp4olxD-Kg | https://i.ytimg.com/vi/vPp4olxD-Kg/hqdefault.jpg |
| 僕たちの洗車旅。 | 2.3万人 | 【油汚れ・虫・鳥フン・花粉を即分解】脱脂シャンプーのシン・説明書｜ながら洗車 | 2026-03-21 | 58,804 | 2.56 | 32:38 | https://www.youtube.com/watch?v=TyhiMDjMHqM | https://i.ytimg.com/vi/TyhiMDjMHqM/hqdefault.jpg |
| センスアールのRYUYA | 2.8万人 | 【洗車のプロが比較】コメリCRUZARD洗車スポンジ&ミット4種類を使い比べてみた | 2025-10-15 | 69,907 | 2.54 | 20:02 | https://www.youtube.com/watch?v=4mwXCxUAa-Q | https://i.ytimg.com/vi/4mwXCxUAa-Q/hqdefault.jpg |
| ワイズ社長のワイズチャンネル | 12.5万人 | 今回、ご迷惑かけたお客様、本当に申し訳ございませんでした。 | 2026-09-20 | 317,372 | 2.54 | 10:19 | https://www.youtube.com/watch?v=0Rb_U8GA-WQ | https://i.ytimg.com/vi/0Rb_U8GA-WQ/hqdefault.jpg |
| センスアールのRYUYA | 2.8万人 | 【コメリ新作】CRUZARD電動フォームガンが凄い！洗車のプロも絶賛の神商品でした | 2025-12-06 | 69,078 | 2.51 | 13:37 | https://www.youtube.com/watch?v=-XBK0rVhSrE | https://i.ytimg.com/vi/-XBK0rVhSrE/hqdefault.jpg |
| ワイズ社長のワイズチャンネル | 12.5万人 | バディカ。。。 | 2026-02-14 | 313,100 | 2.50 | 20:34 | https://www.youtube.com/watch?v=eFYQvStuQLY | https://i.ytimg.com/vi/eFYQvStuQLY/hqdefault.jpg |
| センスアールのRYUYA | 2.8万人 | 【初公開】バディカ初のコーティング店をSENSE-Rが監修！オープン前の裏側を全て見せます | 2026-02-14 | 66,523 | 2.42 | 25:07 | https://www.youtube.com/watch?v=nX5LUy37dwc | https://i.ytimg.com/vi/nX5LUy37dwc/hqdefault.jpg |
| 僕たちの洗車旅。 | 2.3万人 | 【キーパーを頼む前に見て！】DIYでもKeePer以上に綺麗にできる！ | 2026-07-04 | 54,348 | 2.36 | 28:20 | https://www.youtube.com/watch?v=WWCfJf8g9Sk | https://i.ytimg.com/vi/WWCfJf8g9Sk/hqdefault.jpg |
| ワイズ社長のワイズチャンネル | 12.5万人 | オークションで落札した車、大損害故障だったので出品店に交渉しましたが・・・ | 2025-12-12 | 295,077 | 2.36 | 9:56 | https://www.youtube.com/watch?v=oCxxZF7IdbM | https://i.ytimg.com/vi/oCxxZF7IdbM/hqdefault.jpg |
| センスアールのRYUYA | 2.8万人 | 【完成報告】悪魔のS30フェアレディZの1000万円カスタム。外装も中身も全部やった！ | 2026-05-20 | 64,678 | 2.35 | 21:51 | https://www.youtube.com/watch?v=xvZdoEYSW5U | https://i.ytimg.com/vi/xvZdoEYSW5U/hqdefault.jpg |
| 僕たちの洗車旅。 | 2.3万人 | 【徹底比較】鉄粉が1番落ちるのはどれ？鉄粉取りシャンプー5種をガチ比較してみた！ | 2026-02-28 | 53,291 | 2.32 | 40:20 | https://www.youtube.com/watch?v=ezx17fKVjK0 | https://i.ytimg.com/vi/ezx17fKVjK0/hqdefault.jpg |
| ワイズ社長のワイズチャンネル | 12.5万人 | 【わずか１ヶ月でわかった】中古のテスラは絶対に買うな!! | 2026-06-24 | 275,902 | 2.21 | 20:13 | https://www.youtube.com/watch?v=LdsGxxKeSHc | https://i.ytimg.com/vi/LdsGxxKeSHc/hqdefault.jpg |
| WAX-WASH | 16.0万人 | 【コーティングの失敗？】艶ゼロのアリアを徹底洗車で救う！ | 2025-10-19 | 351,017 | 2.19 | 25:23 | https://www.youtube.com/watch?v=d9HmpAxOxj0 | https://i.ytimg.com/vi/d9HmpAxOxj0/hqdefault.jpg |
| センスアールのRYUYA | 2.8万人 | 【徹底比較2026】最強の簡易コーティングはどれ？Amazon人気3種＋CCゴールドをプロが本気検証 | 2026-04-28 | 59,425 | 2.16 | 16:36 | https://www.youtube.com/watch?v=wfut8KiFaVI | https://i.ytimg.com/vi/wfut8KiFaVI/hqdefault.jpg |
| センスアールのRYUYA | 2.8万人 | 【徹底比較】最強の窓ガラス撥水はどれ？人気ガラスコーティング5種を洗車のプロが本気検証！ | 2026-05-15 | 59,091 | 2.15 | 15:21 | https://www.youtube.com/watch?v=WDEdnY3X3kI | https://i.ytimg.com/vi/WDEdnY3X3kI/hqdefault.jpg |
| ワイズ社長のワイズチャンネル | 12.5万人 | 【大炎上中】ニコニコレンタカーの件をレンタカー業もやってる車屋が説明します | 2026-03-19 | 263,251 | 2.11 | 19:55 | https://www.youtube.com/watch?v=8ZPWNGxAY-0 | https://i.ytimg.com/vi/8ZPWNGxAY-0/hqdefault.jpg |
| 僕たちの洗車旅。 | 2.3万人 | 【経年車の傷・水シミ・水垢・下地処理には】BASEのシン・説明書｜ながら洗車 | 2026-04-04 | 48,154 | 2.09 | 36:26 | https://www.youtube.com/watch?v=Kbep9yIY4gM | https://i.ytimg.com/vi/Kbep9yIY4gM/hqdefault.jpg |
| センスアールのRYUYA | 2.8万人 | 【爆風注意】最強の洗車ブロワーはこっちだ！！ | 2026-01-04 | 57,526 | 2.09 | 9:23 | https://www.youtube.com/watch?v=1p87W5zZIqk | https://i.ytimg.com/vi/1p87W5zZIqk/hqdefault.jpg |
| WAX-WASH | 16.0万人 | 業者の失敗で艶が無くなったデリカを洗車で救う！ | 2025-10-10 | 334,451 | 2.09 | 37:59 | https://www.youtube.com/watch?v=obaZiFmcqnY | https://i.ytimg.com/vi/obaZiFmcqnY/hqdefault.jpg |
| 僕たちの洗車旅。 | 2.3万人 | 【塗るだけで車が汚れない！】プラズマコーティングαのシン・説明書｜ながら洗車 | 2026-03-07 | 46,798 | 2.03 | 35:13 | https://www.youtube.com/watch?v=uRJyAk7JqkU | https://i.ytimg.com/vi/uRJyAk7JqkU/hqdefault.jpg |
| 僕たちの洗車旅。 | 2.3万人 | 【警告】買ってはいけない洗車グッズ14選！愛車が台無しに | 2026-07-17 | 46,431 | 2.02 | 24:06 | https://www.youtube.com/watch?v=hp9aqETzNDs | https://i.ytimg.com/vi/hp9aqETzNDs/hqdefault.jpg |
| 僕たちの洗車旅。 | 2.3万人 | 【ウロコ瞬殺＆超撥水！雨の日も200%視界良好】スプラッシュ＆ガラスポリッシュのシン・説明書｜ながら洗車 | 2026-03-28 | 46,071 | 2.00 | 34:58 | https://www.youtube.com/watch?v=OVF8cuZhNks | https://i.ytimg.com/vi/OVF8cuZhNks/hqdefault.jpg |
| ワイズ社長のワイズチャンネル | 12.5万人 | 【倒　産】売上103億円でも負債額３１億円、債権者246人、2026最大の車屋倒産額。予言的中しすぎて怖い | 2026-05-16 | 247,280 | 1.98 | 13:32 | https://www.youtube.com/watch?v=jriQd-QR2eQ | https://i.ytimg.com/vi/jriQd-QR2eQ/hqdefault.jpg |
| ピットワン | 25.7万人 | 【閲覧注意】半額以下で買ったRAV4が腐ってる？虫だらけの車の中が壮絶だった… | 2026-04-11 | 504,879 | 1.96 | 15:27 | https://www.youtube.com/watch?v=buHO3yWj6WA | https://i.ytimg.com/vi/buHO3yWj6WA/hqdefault.jpg |
| ワイズ社長のワイズチャンネル | 12.5万人 | 【全額返金対応】本当に多大なご迷惑をおかけしました。申し訳ございません。 | 2025-11-17 | 241,595 | 1.93 | 10:58 | https://www.youtube.com/watch?v=TSQyaMQjMTE | https://i.ytimg.com/vi/TSQyaMQjMTE/hqdefault.jpg |
| ワイズ社長のワイズチャンネル | 12.5万人 | 【資金難で倒産寸前】すぐに現金化してくれるお店に直談判に行ってきました！売却なるか？ | 2026-04-11 | 239,369 | 1.91 | 16:03 | https://www.youtube.com/watch?v=hGiLpmEhQOY | https://i.ytimg.com/vi/hGiLpmEhQOY/hqdefault.jpg |
| ワイズ社長のワイズチャンネル | 12.5万人 | 【今Dラーでもやらない事】アレやったら1000万円のランクル潰れました | 2026-06-18 | 238,964 | 1.91 | 11:17 | https://www.youtube.com/watch?v=xWLTQ4SwqSU | https://i.ytimg.com/vi/xWLTQ4SwqSU/hqdefault.jpg |
| ワイズ社長のワイズチャンネル | 12.5万人 | 大暴落中の40ヴェル事故した客から相談が来た | 2026-08-17 | 238,901 | 1.91 | 9:42 | https://www.youtube.com/watch?v=K_jDKYigKk4 | https://i.ytimg.com/vi/K_jDKYigKk4/hqdefault.jpg |
| ワイズ社長のワイズチャンネル | 12.5万人 | 【初めて語る】EV車絶対に買うな！！興味ないなら尚更見ろ！ | 2026-01-07 | 238,622 | 1.91 | 15:05 | https://www.youtube.com/watch?v=NRuzbwAzrJc | https://i.ytimg.com/vi/NRuzbwAzrJc/hqdefault.jpg |
| ワイズ社長のワイズチャンネル | 12.5万人 | 【即出し無理】新車ハイエースを１ヵ月で売却した、なんちゃって視聴者が頭が悪すぎて損してワロタ | 2026-04-24 | 234,154 | 1.87 | 10:49 | https://www.youtube.com/watch?v=IqJh8rzlqO4 | https://i.ytimg.com/vi/IqJh8rzlqO4/hqdefault.jpg |
| ワイズ社長のワイズチャンネル | 12.5万人 | 【緊急配信】２７０万円で買った車が、たった３カ月で３０万円でしか買い取れない程の車でした。高級輸入車の高額販売と適正価格 | 2025-10-21 | 230,612 | 1.84 | 10:14 | https://www.youtube.com/watch?v=vB-DnFPcvvI | https://i.ytimg.com/vi/vB-DnFPcvvI/hqdefault.jpg |
| チャンネル隊長 | 21.7万人 | 【神コスパ】ホームセンターDCMの2,980円ポリッシャーで車を磨いてみた結果 | 2026-07-19 | 400,059 | 1.84 | 9:19 | https://www.youtube.com/watch?v=T5AmDk0f150 | https://i.ytimg.com/vi/T5AmDk0f150/hqdefault.jpg |
| ピットワン | 25.7万人 | ヤフオクで買ったレクサスESから大事故の痕跡が出まくった… | 2026-06-19 | 456,749 | 1.78 | 20:52 | https://www.youtube.com/watch?v=2gIQJvMHS9o | https://i.ytimg.com/vi/2gIQJvMHS9o/hqdefault.jpg |
| ワイズ社長のワイズチャンネル | 12.5万人 | 思いもしなかった、詐欺に遭いました。 | 2026-02-22 | 219,140 | 1.75 | 8:28 | https://www.youtube.com/watch?v=ZCdCFWSRZFE | https://i.ytimg.com/vi/ZCdCFWSRZFE/hqdefault.jpg |
| WAX-WASH | 16.0万人 | 触ると異常…レクサスNXのザラつきの正体 | 2026-08-27 | 270,482 | 1.69 | 16:38 | https://www.youtube.com/watch?v=vWuVOU53XHo | https://i.ytimg.com/vi/vWuVOU53XHo/hqdefault.jpg |
| ワイズ社長のワイズチャンネル | 12.5万人 | また小田オートに呼ばれたので行ってみると、小田がタヒそうになってました。爆笑　幻のGT-Rプレミアムエディション Tスペック | 2026-02-19 | 209,525 | 1.68 | 15:08 | https://www.youtube.com/watch?v=bmquMAqDNy4 | https://i.ytimg.com/vi/bmquMAqDNy4/hqdefault.jpg |
| ワイズ社長のワイズチャンネル | 12.5万人 | 【赤字確定した】プラドが大暴落したので販売します。買取赤字王 | 2026-02-09 | 195,558 | 1.56 | 14:29 | https://www.youtube.com/watch?v=OaXMMgJRirc | https://i.ytimg.com/vi/OaXMMgJRirc/hqdefault.jpg |
| ワイズ社長のワイズチャンネル | 12.5万人 | AA3.5点が『どう見ても事故歴ありだ！』と言うてきた客と揉めてます | 2026-07-29 | 194,240 | 1.55 | 11:56 | https://www.youtube.com/watch?v=lcUWGyYjNvA | https://i.ytimg.com/vi/lcUWGyYjNvA/hqdefault.jpg |
| ワイズ社長のワイズチャンネル | 12.5万人 | オークション仕入れミス | 2025-10-11 | 190,175 | 1.52 | 8:26 | https://www.youtube.com/watch?v=4j7FnMm_hcA | https://i.ytimg.com/vi/4j7FnMm_hcA/hqdefault.jpg |
| WAX-WASH | 16.0万人 | 【永久保存版】汚れ9割落ちる！年末に買うべき洗車用品2選 | 2025-12-06 | 239,974 | 1.50 | 11:58 | https://www.youtube.com/watch?v=yiIGnF8fkDc | https://i.ytimg.com/vi/yiIGnF8fkDc/hqdefault.jpg |
| ワイズ社長のワイズチャンネル | 12.5万人 | 【AA出品車が事故】車屋が解説します。ベントレー大事故の真相は？ | 2026-03-25 | 186,159 | 1.49 | 13:22 | https://www.youtube.com/watch?v=2XL5j-3Yggg | https://i.ytimg.com/vi/2XL5j-3Yggg/hqdefault.jpg |
| ワイズ社長のワイズチャンネル | 12.5万人 | やっぱりEV車は無理！イキって買ったテスラを３ヶ月で降りて売却します　＃テスラを売却　＃やっぱりEV車無理か　＃EV車のバブル | 2026-08-29 | 184,249 | 1.47 | 13:34 | https://www.youtube.com/watch?v=OTSOCrNkUBo | https://i.ytimg.com/vi/OTSOCrNkUBo/hqdefault.jpg |
| ワイズ社長のワイズチャンネル | 12.5万人 | 新車納車直前にひょう害！ディーラーの見解は？ | 2026-07-31 | 182,382 | 1.46 | 14:07 | https://www.youtube.com/watch?v=2mNEZbfTMNk | https://i.ytimg.com/vi/2mNEZbfTMNk/hqdefault.jpg |
| ワイズ社長のワイズチャンネル | 12.5万人 | 日本一舐めた営業マンが来た！高額機材５２万8000円の車診断機（テスター）買った | 2025-10-16 | 179,519 | 1.44 | 22:44 | https://www.youtube.com/watch?v=JunVeVBu8DA | https://i.ytimg.com/vi/JunVeVBu8DA/hqdefault.jpg |
| ワイズ社長のワイズチャンネル | 12.5万人 | 【前代未聞】超極上車のはずが価値なし！ | 2025-12-13 | 178,032 | 1.42 | 14:38 | https://www.youtube.com/watch?v=SqIuKTv2ucI | https://i.ytimg.com/vi/SqIuKTv2ucI/hqdefault.jpg |
| ワイズ社長のワイズチャンネル | 12.5万人 | 秒で売れたランクル300の「ルーフレールが無いからキャンセル」と言われたので純正で取付ました。実は後付けできます | 2026-06-04 | 177,873 | 1.42 | 16:22 | https://www.youtube.com/watch?v=ZqRATXAQfVk | https://i.ytimg.com/vi/ZqRATXAQfVk/hqdefault.jpg |
| ピットワン | 25.7万人 | 半額で買った軽自動車の中身があまりにも危険な状態でした、、、 | 2026-02-20 | 364,954 | 1.42 | 16:52 | https://www.youtube.com/watch?v=NRi-NGWMz80 | https://i.ytimg.com/vi/NRi-NGWMz80/hqdefault.jpg |
| ワイズ社長のワイズチャンネル | 12.5万人 | 小田オートが大きなミスをしたので冷やかしに行きました | 2025-12-30 | 177,289 | 1.42 | 9:50 | https://www.youtube.com/watch?v=qifC0dNn-9E | https://i.ytimg.com/vi/qifC0dNn-9E/hqdefault.jpg |
| ワイズ社長のワイズチャンネル | 12.5万人 | 小田オートが資金難で土下座して泣きついてきました | 2026-02-18 | 173,946 | 1.39 | 18:20 | https://www.youtube.com/watch?v=Z0QAAfa0aXQ | https://i.ytimg.com/vi/Z0QAAfa0aXQ/hqdefault.jpg |
| ピットワン | 25.7万人 | 事故車でもないのにうるさ過ぎて乗れない!?トヨタシエンタの謎の音の正体とは？ | 2026-01-30 | 334,084 | 1.30 | 10:08 | https://www.youtube.com/watch?v=pWsBJpqkrX0 | https://i.ytimg.com/vi/pWsBJpqkrX0/hqdefault.jpg |
| ワイズ社長のワイズチャンネル | 12.5万人 | この車、リセール終わってます。。。新車440万円→○○万円 | 2026-05-18 | 161,729 | 1.29 | 8:56 | https://www.youtube.com/watch?v=YtHQegO5tOs | https://i.ytimg.com/vi/YtHQegO5tOs/hqdefault.jpg |
| ワイズ社長のワイズチャンネル | 12.5万人 | ２万円の車 | 2025-09-20 | 159,703 | 1.28 | 17:05 | https://www.youtube.com/watch?v=GLqCPFqrWnk | https://i.ytimg.com/vi/GLqCPFqrWnk/hqdefault.jpg |
| WAX-WASH | 16.0万人 | 洗車してるのに水垢が増える原因と正しい落とし方｜ランドクルーザー | 2026-03-14 | 203,156 | 1.27 | 30:04 | https://www.youtube.com/watch?v=2pcP02_iQGU | https://i.ytimg.com/vi/2pcP02_iQGU/hqdefault.jpg |
| ワイズ社長のワイズチャンネル | 12.5万人 | チャンネル登録者４万人の車屋がこんなことをしていましたので暴露します。許せますか？ | 2026-07-06 | 155,958 | 1.25 | 20:18 | https://www.youtube.com/watch?v=UZ3_nq_IAeE | https://i.ytimg.com/vi/UZ3_nq_IAeE/hqdefault.jpg |
| ワイズ社長のワイズチャンネル | 12.5万人 | ８万kmのCVTオイルがこんなにも汚いとは誰も思わなかった。トルコン太郎ではないATフルードオート交換機買ってみた。 | 2025-11-26 | 155,080 | 1.24 | 13:00 | https://www.youtube.com/watch?v=FUQBvTYWVAA | https://i.ytimg.com/vi/FUQBvTYWVAA/hqdefault.jpg |
| ワイズ社長のワイズチャンネル | 12.5万人 | 【カスタム総額４００万円】軽自動車１台分カスタムしてるエグい車買い取りました | 2026-06-06 | 154,458 | 1.24 | 15:30 | https://www.youtube.com/watch?v=8VLIrJPtxt8 | https://i.ytimg.com/vi/8VLIrJPtxt8/hqdefault.jpg |
| ピットワン | 25.7万人 | プロ直伝！見た事ない画期的なフィルムの貼り方を伝授 !? | 2026-08-21 | 317,182 | 1.23 | 19:08 | https://www.youtube.com/watch?v=9gFwpyLbpJY | https://i.ytimg.com/vi/9gFwpyLbpJY/hqdefault.jpg |
| ワイズ社長のワイズチャンネル | 12.5万人 | 買取後、重大な起因が見つかり事故歴あり認定、減額したので揉めてます | 2026-08-01 | 151,577 | 1.21 | 20:11 | https://www.youtube.com/watch?v=f2Po_VMN3q8 | https://i.ytimg.com/vi/f2Po_VMN3q8/hqdefault.jpg |
| ワイズ社長のワイズチャンネル | 12.5万人 | 【新たな急展開!!】車検にすんなり通ったキャンターの件で陸運局から謝罪電話がありました、さあミスったのはどちらの陸運局か？ | 2025-11-28 | 148,956 | 1.19 | 22:27 | https://www.youtube.com/watch?v=a8LuZMaZK7A | https://i.ytimg.com/vi/a8LuZMaZK7A/hqdefault.jpg |
| ワイズ社長のワイズチャンネル | 12.5万人 | 安っすいアルファード買ったけど実は最強かもな | 2026-08-04 | 145,276 | 1.16 | 13:20 | https://www.youtube.com/watch?v=nPPZfbLko-o | https://i.ytimg.com/vi/nPPZfbLko-o/hqdefault.jpg |
| WAX-WASH | 16.0万人 | 限界寸前のクラウンが洗車で奇跡の復活！！ | 2026-07-31 | 185,767 | 1.16 | 27:04 | https://www.youtube.com/watch?v=G_brZo2EyY0 | https://i.ytimg.com/vi/G_brZo2EyY0/hqdefault.jpg |
| WAX-WASH | 16.0万人 | 洗車だけで艶は戻る？5年目ノアの現実 | 2026-09-12 | 185,365 | 1.16 | 29:20 | https://www.youtube.com/watch?v=Vy1w76lZHU8 | https://i.ytimg.com/vi/Vy1w76lZHU8/hqdefault.jpg |
| ワイズ社長のワイズチャンネル | 12.5万人 | 今更クラウンを正直レビュー！いつかはクラウン世代がクラウンスポーツを乗ったらどう思うのか？ | 2026-09-19 | 144,525 | 1.16 | 17:26 | https://www.youtube.com/watch?v=kC1WBcIAgTA | https://i.ytimg.com/vi/kC1WBcIAgTA/hqdefault.jpg |
| ワイズ社長のワイズチャンネル | 12.5万人 | 【AA異常事態】実は今、オークションが異常事態！暴落もですがそれよりも凄いことに気づいた。戦争と物価高騰の裏でとんでもなくボロ儲けしてるところがありました。 | 2026-04-22 | 140,240 | 1.12 | 10:00 | https://www.youtube.com/watch?v=xckF92JaoPA | https://i.ytimg.com/vi/xckF92JaoPA/hqdefault.jpg |
| ピットワン | 25.7万人 | 事故を隠して中古車を売ってる？信じられない車業界の闇を見た、、、 | 2026-02-21 | 287,856 | 1.12 | 15:27 | https://www.youtube.com/watch?v=xAoyBSKDRcI | https://i.ytimg.com/vi/xAoyBSKDRcI/hqdefault.jpg |
| ワイズ社長のワイズチャンネル | 12.5万人 | 【極悪店】30プリウス前期を100万円以上で買わされて1カ月で廃車を余儀なくされた客 | 2025-10-14 | 139,121 | 1.11 | 14:53 | https://www.youtube.com/watch?v=A41Ftx6ZBKo | https://i.ytimg.com/vi/A41Ftx6ZBKo/hqdefault.jpg |
| ピットワン | 25.7万人 | 名車スカイライン復活の兆し！？超大手2社が手を組む奇跡の瞬間がこちら！！！ | 2025-10-04 | 284,843 | 1.11 | 17:26 | https://www.youtube.com/watch?v=SzS-oCeTs7k | https://i.ytimg.com/vi/SzS-oCeTs7k/hqdefault.jpg |
| ワイズ社長のワイズチャンネル | 12.5万人 | 【注意喚起】アホすぎてヤバい客 | 2026-04-25 | 136,694 | 1.09 | 10:24 | https://www.youtube.com/watch?v=eWSPkKxRTfQ | https://i.ytimg.com/vi/eWSPkKxRTfQ/hqdefault.jpg |
| WAX-WASH | 16.0万人 | 新車なのに…クラウンが水垢だらけになった理由　クラウンエステートcrownestate | 2025-11-30 | 174,433 | 1.09 | 22:36 | https://www.youtube.com/watch?v=y2u7tnr468c | https://i.ytimg.com/vi/y2u7tnr468c/hqdefault.jpg |
| ピットワン | 25.7万人 | 交通事故の恐ろしさを解明!?修理前の事故車がまさかの… | 2026-03-27 | 279,476 | 1.09 | 15:35 | https://www.youtube.com/watch?v=Kfs38sOo2g8 | https://i.ytimg.com/vi/Kfs38sOo2g8/hqdefault.jpg |
| ワイズ社長のワイズチャンネル | 12.5万人 | 新型エルグランド大暴落しました | 2026-08-08 | 131,367 | 1.05 | 12:27 | https://www.youtube.com/watch?v=fcO2GHHzlaI | https://i.ytimg.com/vi/fcO2GHHzlaI/hqdefault.jpg |
| ピットワン | 25.7万人 | 直しすぎた事故車!?説明のつかない傷があるCHRの謎に迫る… | 2026-06-06 | 269,381 | 1.05 | 23:19 | https://www.youtube.com/watch?v=Uz3PNp39_k8 | https://i.ytimg.com/vi/Uz3PNp39_k8/hqdefault.jpg |
| ワイズ社長のワイズチャンネル | 12.5万人 | 小田オートが緊急入院したので最後に一目会いに行きました | 2026-06-17 | 130,871 | 1.05 | 8:59 | https://www.youtube.com/watch?v=eQHeUhIV5fY | https://i.ytimg.com/vi/eQHeUhIV5fY/hqdefault.jpg |
| ワイズ社長のワイズチャンネル | 12.5万人 | ポルテ沼にハマった客が３台目の極上ポルテを買いました | 2026-09-01 | 130,238 | 1.04 | 10:03 | https://www.youtube.com/watch?v=IOXktfvwGWg | https://i.ytimg.com/vi/IOXktfvwGWg/hqdefault.jpg |
| ワイズ社長のワイズチャンネル | 12.5万人 | 新オーバートルク詐欺は実は友達でしたので聞いて激怒しました | 2026-06-19 | 127,256 | 1.02 | 10:03 | https://www.youtube.com/watch?v=X_oNi7yUv04 | https://i.ytimg.com/vi/X_oNi7yUv04/hqdefault.jpg |
| ワイズ社長のワイズチャンネル | 12.5万人 | 【注意喚起】買取詐欺にあって入金されていない方からの情報提供です。まだニュースになっていないので必ず見てください | 2025-10-31 | 126,997 | 1.02 | 9:36 | https://www.youtube.com/watch?v=ysXAXD17ONA | https://i.ytimg.com/vi/ysXAXD17ONA/hqdefault.jpg |

## ショート（基準以上・倍率降順・32本）

| チャンネル名 | 登録者数 | タイトル | 公開日 | 再生数 | 倍率 | 尺 | 動画URL | サムネイルURL |
|---|---|---|---|---|---|---|---|---|
| WAX-WASH | 16.0万人 | 洗車屋がやっている拭き上げの順番 | 2025-12-27 | 1,933,202 | 12.08 | — | https://www.youtube.com/watch?v=8crLJgzhdmY | https://i.ytimg.com/vi/8crLJgzhdmY/hqdefault.jpg |
| 僕たちの洗車旅。 | 2.3万人 | 細部洗浄、誰でも簡単にできる方法　#洗車 #洗車用品 #ながら洗車 #僕たちの洗車旅 #細部洗浄 #ブラシ | 2025-10-23 | 211,633 | 9.20 | — | https://www.youtube.com/watch?v=BA_bOJfyDek | https://i.ytimg.com/vi/BA_bOJfyDek/hqdefault.jpg |
| WAX-WASH | 16.0万人 | 安全な洗車の順番とは？ | 2025-11-10 | 1,410,289 | 8.81 | — | https://www.youtube.com/watch?v=YS2i4A-DPjM | https://i.ytimg.com/vi/YS2i4A-DPjM/hqdefault.jpg |
| WAX-WASH | 16.0万人 | 洗車用品「2つ」で車の汚れ９割落とせる。 | 2026-02-18 | 1,330,707 | 8.32 | — | https://www.youtube.com/watch?v=YjHQLyfGTLg | https://i.ytimg.com/vi/YjHQLyfGTLg/hqdefault.jpg |
| 僕たちの洗車旅。 | 2.3万人 | 塩カルを簡単に落とす方法 #洗車 #洗車用品 #ながら洗車 #塩カル #融雪剤 #冬の洗車 #サビ | 2025-11-28 | 186,222 | 8.10 | — | https://www.youtube.com/watch?v=cF_ZmI-Zt9w | https://i.ytimg.com/vi/cF_ZmI-Zt9w/hqdefault.jpg |
| WAX-WASH | 16.0万人 | キイロビンを使った安全な油膜の落とし方 | 2026-06-15 | 1,231,378 | 7.70 | — | https://www.youtube.com/watch?v=2djil5fL41k | https://i.ytimg.com/vi/2djil5fL41k/hqdefault.jpg |
| ピットワン | 25.7万人 | これは神ワザ？事故？GTR collision?#交通事故 #神ワザ#カスタム #gtr | 2025-11-22 | 1,789,993 | 6.96 | — | https://www.youtube.com/watch?v=ob8Ti_8_M_c | https://i.ytimg.com/vi/ob8Ti_8_M_c/hqdefault.jpg |
| WAX-WASH | 16.0万人 | 毎週洗車しているのに車がくすんでいる人の共通点とは？ | 2026-06-03 | 1,018,040 | 6.36 | — | https://www.youtube.com/watch?v=gTrhzaxGbx8 | https://i.ytimg.com/vi/gTrhzaxGbx8/hqdefault.jpg |
| 僕たちの洗車旅。 | 2.3万人 | グラスターゾルオートの本当の使い方 #洗車 #洗車用品 #グラスターゾルオート #艶出し #車 #車好き | 2025-11-07 | 143,501 | 6.24 | — | https://www.youtube.com/watch?v=hXICw95qUEo | https://i.ytimg.com/vi/hXICw95qUEo/hqdefault.jpg |
| 僕たちの洗車旅。 | 2.3万人 | 洗車タオルの洗い方！自宅で簡単に✨ #洗車 #洗車用品 #ながら洗車 #車 #車好き #マイクロファイバー #洗車クロス | 2025-12-09 | 112,916 | 4.91 | — | https://www.youtube.com/watch?v=FnSkA94vawo | https://i.ytimg.com/vi/FnSkA94vawo/hqdefault.jpg |
| 僕たちの洗車旅。 | 2.3万人 | このポイントで鉄粉除去がうまくいく！#洗車 #洗車用品 #ながら洗車 #鉄粉除去 #アイアンデリート | 2025-11-16 | 100,877 | 4.39 | — | https://www.youtube.com/watch?v=TeT9ojrLoZ0 | https://i.ytimg.com/vi/TeT9ojrLoZ0/hqdefault.jpg |
| 僕たちの洗車旅。 | 2.3万人 | ホイールの洗浄はこれでOK！面倒くさがりでも大丈夫！#洗車 #洗車用品 #ながら洗車 #ホイール #タイヤ #タイヤ洗浄 | 2025-12-08 | 94,769 | 4.12 | — | https://www.youtube.com/watch?v=CWxI7Kt4RJQ | https://i.ytimg.com/vi/CWxI7Kt4RJQ/hqdefault.jpg |
| 僕たちの洗車旅。 | 2.3万人 | ガラスコーティングした方がいい理由はこれ！#洗車 #洗車用品 #ながら洗車 #ガラスコーティング #diy | 2025-10-11 | 94,658 | 4.12 | — | https://www.youtube.com/watch?v=Qq0oxjN37OA | https://i.ytimg.com/vi/Qq0oxjN37OA/hqdefault.jpg |
| 僕たちの洗車旅。 | 2.3万人 | ガラコの性能を200%引き出す方法　#洗車 #洗車用品 #窓ガラス撥水 #ガラコ #graco #車好き #DIY | 2025-09-27 | 86,692 | 3.77 | — | https://www.youtube.com/watch?v=x3zH3faNNDg | https://i.ytimg.com/vi/x3zH3faNNDg/hqdefault.jpg |
| 僕たちの洗車旅。 | 2.3万人 | BASEでの失敗要因はこれでした…💦上手く施工するコツ‼️#洗車 #ながら洗車 #BASE #水シミ #小傷 #車 #車好き | 2026-04-17 | 78,645 | 3.42 | — | https://www.youtube.com/watch?v=O-Sb552-e7o | https://i.ytimg.com/vi/O-Sb552-e7o/hqdefault.jpg |
| WAX-WASH | 16.0万人 | 車の見た目を悪くする９割の原因はこれ。 | 2026-02-19 | 499,014 | 3.12 | — | https://www.youtube.com/watch?v=nf_lVPnUm3A | https://i.ytimg.com/vi/nf_lVPnUm3A/hqdefault.jpg |
| 僕たちの洗車旅。 | 2.3万人 | 車のステップの超簡単な洗い方！#洗車 #洗車用品 #ながら洗車 #車 #車好き #ステップ | 2025-10-10 | 71,723 | 3.12 | — | https://www.youtube.com/watch?v=BIObRph8em8 | https://i.ytimg.com/vi/BIObRph8em8/hqdefault.jpg |
| WAX-WASH | 16.0万人 | 紫外線で車が”くすむ”理由と対処方法 | 2026-02-12 | 446,445 | 2.79 | — | https://www.youtube.com/watch?v=_EJY2Oo09Ko | https://i.ytimg.com/vi/_EJY2Oo09Ko/hqdefault.jpg |
| WAX-WASH | 16.0万人 | 黒筋汚れを安全に落とす手順とは？ | 2026-07-04 | 445,137 | 2.78 | — | https://www.youtube.com/watch?v=GrNjyOPGZn0 | https://i.ytimg.com/vi/GrNjyOPGZn0/hqdefault.jpg |
| 僕たちの洗車旅。 | 2.3万人 | こんな組み合わせありなの⁉️BASE×〇〇で磨き傷ゼロへ #洗車 #ながら洗車 #base #車 #カーケア #車好き | 2026-04-24 | 62,917 | 2.74 | — | https://www.youtube.com/watch?v=2RkEa0bdq-M | https://i.ytimg.com/vi/2RkEa0bdq-M/hqdefault.jpg |
| 僕たちの洗車旅。 | 2.3万人 | 野外洗車での鉄粉除去のコツ！#洗車 #ながら洗車 #鉄粉除去 #車 #車好き | 2026-06-03 | 60,481 | 2.63 | — | https://www.youtube.com/watch?v=gxY6keM9wZE | https://i.ytimg.com/vi/gxY6keM9wZE/hqdefault.jpg |
| センスアールのRYUYA | 2.8万人 | 【プロ直伝】9割が知らないコメリ水垢剤「赤と青」の本当の使い分け！間違えると逆効果になりますショート2 | 2026-07-15 | 71,717 | 2.61 | — | https://www.youtube.com/watch?v=wC5d2-opptE | https://i.ytimg.com/vi/wC5d2-opptE/hqdefault.jpg |
| 僕たちの洗車旅。 | 2.3万人 | 【注意喚起】鉄粉除去パッドのよくある間違い #洗車 #洗車用品 #ながら洗車 #アイアンデリート #アイアンパッド #diy #鉄粉除去 #車 #車好き | 2025-12-04 | 58,299 | 2.53 | — | https://www.youtube.com/watch?v=E1zC0YXRuck | https://i.ytimg.com/vi/E1zC0YXRuck/hqdefault.jpg |
| 僕たちの洗車旅。 | 2.3万人 | 知らないと損！カーシャンプーの泡立ての極意　#洗車 #洗車用品 #ながら洗車 #カーシャンプー #シャンプー洗車 #車好き | 2025-10-03 | 54,166 | 2.36 | — | https://www.youtube.com/watch?v=QOT1K2bPvG4 | https://i.ytimg.com/vi/QOT1K2bPvG4/hqdefault.jpg |
| 僕たちの洗車旅。 | 2.3万人 | エンジンルームを超簡単に洗う方法　#洗車 #洗車用品 #DIY #ながら洗車 #エンジンルーム #コーティング #超簡単 | 2025-09-26 | 53,319 | 2.32 | — | https://www.youtube.com/watch?v=8rZeJyu-lC0 | https://i.ytimg.com/vi/8rZeJyu-lC0/hqdefault.jpg |
| センスアールのRYUYA | 2.8万人 | 【コメリ越え？】DCMがコスパ最強!!水アカクリーナー最強はどっち？洗車のプロがガチ比較 | 2026-09-06 | 61,622 | 2.24 | — | https://www.youtube.com/watch?v=AHEE43e_1o4 | https://i.ytimg.com/vi/AHEE43e_1o4/hqdefault.jpg |
| センスアールのRYUYA | 2.8万人 | 【本気検証】コメリ大人気傷埋め剤vs 自社新商品…キズが消えるのはどっち？ 切り抜き2 | 2026-08-11 | 58,821 | 2.14 | — | https://www.youtube.com/watch?v=J0PLSIrgh-o | https://i.ytimg.com/vi/J0PLSIrgh-o/hqdefault.jpg |
| WAX-WASH | 16.0万人 | 重ね塗りで車がくすむ理由 #car #detailing #carcare | 2025-12-18 | 310,667 | 1.94 | — | https://www.youtube.com/watch?v=UOCKtXabm8E | https://i.ytimg.com/vi/UOCKtXabm8E/hqdefault.jpg |
| ピットワン | 25.7万人 | GT-Rで事故!?#事故#交通事故 #skyline #diy #drift  #automobile #gtr #カスタム | 2026-01-02 | 482,323 | 1.88 | — | https://www.youtube.com/watch?v=FPbTsVw6D6A | https://i.ytimg.com/vi/FPbTsVw6D6A/hqdefault.jpg |
| WAX-WASH | 16.0万人 | コメリさんがとんでもない洗車スポンジ出してきた件 | 2026-06-03 | 294,954 | 1.84 | — | https://www.youtube.com/watch?v=ik81KePyPds | https://i.ytimg.com/vi/ik81KePyPds/hqdefault.jpg |
| WAX-WASH | 16.0万人 | 純水器の誤解。拭き上げ不要ではありません | 2026-03-08 | 218,019 | 1.36 | — | https://www.youtube.com/watch?v=vq2mRHsYqQE | https://i.ytimg.com/vi/vq2mRHsYqQE/hqdefault.jpg |
| ワイズ社長のワイズチャンネル | 12.5万人 | 緊急事態　車屋は絶対に見てくれ！ | 2026-05-11 | 144,249 | 1.15 | — | https://www.youtube.com/watch?v=9mKyzhktuOA | https://i.ytimg.com/vi/9mKyzhktuOA/hqdefault.jpg |

全件の生データ（基準未満含む 1186本）: competitors/raw.csv
