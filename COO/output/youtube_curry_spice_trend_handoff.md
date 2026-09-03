# YouTube横断「伸びた動画」収集レポート（カレー／スパイス／血糖値・腸活）引き継ぎ版
生成日: 2026-09-03　データ源: YouTube InnerTube（search/next）。フル版: COO/output/youtube_curry_spice_trend.md, .csv, .json（ブランチ claude/youtube-curry-spice-collection-5zgeo3）

## 抽出条件
- 検索KW 13語（カレー軸: カレー 健康／カレー 血糖値／スパイスカレー 健康／カレー粉／カレールー 比較／インドカレー 健康、スパイス軸: ターメリック 効果／クミン 効果／スパイス 効果 健康／スパイス 腸内環境、血糖値・腸活軸: 血糖値 上げない 食べ方／白米 血糖値 対策／腸活 レシピ）× 5パターン（1年以内×関連順・再生順・新着順、期間なし×関連順・再生順）＋続きページ。参考枠用に英語4語（turmeric benefits / curry health benefits / spices gut health / blood sugar rice）
- 公開1年以内が主枠。1年以内の該当が5本未満のKWは1〜2年前まで補完
- 180秒以下は除外。倍率 = 再生数 ÷ 登録者数。基準: 10万人以上≧1倍／1万〜10万人≧2倍／1万人未満≧3倍
- 追加の前提: 再生数1,000回未満は除外。タイトルにトピック語（カレー／スパイス／粉／食材／血糖値／腸活／米 等）を含まないものは別掲。登録者非公開は判定不可で別掲
- 言語判定: 英語UIで取得した原題に仮名が残れば日本語。海外動画は原題で表示
- 型判定: タイトル・CH名のキーワードで「専門家の解説型」「レシピ・料理型」に二分（レシピ／作り方／常備菜／混ぜるだけ／料理名のみ／料理系CH→料理型、医師／栄養士／解説／研究／効果／血糖値／クリニック系CH→解説型）
## 収集サマリー
| 項目 | 件数 |
|---|---|
| 検索でヒットしたユニーク動画 | 1308 |
| 事前フィルタ通過（尺・期間・再生数） | 621 |
| 詳細取得後に条件内 | 557 |
| 倍率基準クリア（全言語） | 158 |
| **主枠（日本語・1年以内）** | **65** |
| 主枠補完（日本語・1〜2年） | 6 |
| 参考枠（英語・中国語圏・その他言語） | 44 |
| トピック語なし（別掲・参考） | 24 |
| 登録者数非公開で判定不可 | 3 |

### キーワード別 主枠ヒット数
| 軸 | キーワード | 1年以内 | 補完(1〜2年) |
|---|---|---|---|
| カレー軸 | カレー 健康 | 1 | 1 |
| カレー軸 | カレー 血糖値 | 4 | 1 |
| カレー軸 | スパイスカレー 健康 | 2 | 1 |
| カレー軸 | カレー粉 | 4 | 0 |
| カレー軸 | カレールー 比較 | 3 | 2 |
| カレー軸 | インドカレー 健康 | 0 | 0 |
| スパイス軸 | ターメリック 効果 | 5 | - |
| スパイス軸 | クミン 効果 | 4 | 1 |
| スパイス軸 | スパイス 効果 健康 | 11 | - |
| スパイス軸 | スパイス 腸内環境 | 6 | - |
| 血糖値・腸活軸 | 血糖値 上げない 食べ方 | 21 | - |
| 血糖値・腸活軸 | 白米 血糖値 対策 | 6 | - |
| 血糖値・腸活軸 | 腸活 レシピ | 14 | - |

## 主枠：日本語チャンネル・1年以内（65本、倍率順）
| 倍率 | タイトル | URL | CH名 | 登録者 | 再生数 | 公開日 | 尺 | 型 | ヒットKW |
|---|---|---|---|---|---|---|---|---|---|
| 86.7x | 【腸活最強】漬けるだけで痩せ常備菜！きのこ４種のポン酢漬けがご飯にもパスタにも万能すぎる | https://www.youtube.com/watch?v=rfXUvxTSkzY | 頑張らないひとりごはん | 5,060 | 438,844 | 2026-04-25 | 5:41 | レシピ | 腸活 レシピ |
| 69.8x | 【9割が知らない健康雑学】朝にシナモンをとる人　ほぼ全員⚫︎⚫︎になります！聞き流し雑学 | https://www.youtube.com/watch?v=QifO7VujUEU | 今よりちょっと健康雑学 | 5,700 | 397,635 | 2026-02-17 | 4:33 | 専門家 | クミン 効果 / スパイス 効果 健康 |
| 60.1x | 【あなたは知ってる？】ブルーベリーの68倍！老化遅い人が密かに摂る“最強の粉”5選 | https://www.youtube.com/watch?v=kNvDnGZQxbY | 老化知らず研究所 | 2,940 | 176,832 | 2026-02-26 | 10:55 | 専門家 | クミン 効果 |
| 53.3x | 【保存版】実は納豆に混ぜるだけで「腐った便」が全部出て、血糖値が驚くほど改善します【知って得する健康雑学】【便秘/腸内環境/腸活/糖尿病】【聞き流し】 | https://www.youtube.com/watch?v=_ADGGa3imSg | 【知って得する】健康雑学 | 2.9万 | 1,540,148 | 2026-02-21 | 16:49 | 専門家 | 腸活 レシピ |
| 45.8x | 「緑茶の20倍の老化防止効果！」研究データも証明する『70代からでも脳と筋肉が覚醒する神食材ベスト7（スーパーで買える）※脳筋覚醒【食で長生き】 | https://www.youtube.com/watch?v=dIL1zRxK46c | 老後の健康案内所 | 2,050 | 93,990 | 2026-08-19 | 26:59 | 専門家 | スパイス 効果 健康 |
| 34.4x | 【東京 五反田】1日で200杯のカレーが消える！中毒者が続出で行列が絶えないこだわりカレー屋の仕込みに密着！ | https://www.youtube.com/watch?v=arqWdexcFik | フーズラボ | 1,590 | 54,768 | 2026-08-26 | 21:01 | レシピ | カレー粉 |
| 32.5x | 【医学解説】「緑茶の200倍の抗酸化力!? 中高年を若返らせる神食材と本当の若返り戦略」 | https://www.youtube.com/watch?v=x9xVI5ugLBQ | ペンタのおとな健康大学 [中高年の悩み解決] | 1.6万 | 536,717 | 2026-03-02 | 8:15 | 専門家 | クミン 効果 / スパイス 効果 健康 |
| 21.0x | 【血糖値200→98】 コーヒーと●●の組み合わせが糖尿病にすごい効果！血糖値・HbA1cを劇的に下げる最強の食べ物TOP5と危険な飲み方!（糖尿病・高齢者） | https://www.youtube.com/watch?v=v3NIs8SVHCM | 予防先生・YouTube体質改善クリニック | 3.5万 | 733,820 | 2026-04-18 | 25:14 | 専門家 | 血糖値 上げない 食べ方 |
| 18.1x | 【衝撃】1万歩ウォーキングよりコレ1本でHbA1c・血糖値は下がる!?【糖尿病専門クリニック現役医師】 | https://www.youtube.com/watch?v=ZBEJhHU6oKg | 糖尿病の専門家 | 21.8万 | 3,941,856 | 2025-09-13 | 25:27 | 専門家 | 血糖値 上げない 食べ方 |
| 17.4x | 【9割が知らない】実は納豆に混ぜるだけ!?「腐った便」が消えて血糖値が劇的に改善します!【血糖値改善/腸内環境/糖尿病予防/デトックス/便秘解消】 | https://www.youtube.com/watch?v=JoIcTWJ7UQY | ズバッと知りたい雑学 | 1.5万 | 253,848 | 2026-02-01 | 10:59 | 専門家 | 血糖値 上げない 食べ方 |
| 15.8x | 【知らないと損】毎朝食べるだけ！血糖値とHbA1cをグングン下げる食材TOP5！超意外な糖尿病を予防する最強の朝食とは？｜空腹腹時血糖対策｜体脂肪 | https://www.youtube.com/watch?v=aFd12CNtj78 | 予防先生・YouTube体質改善クリニック | 3.5万 | 554,350 | 2026-03-28 | 23:00 | 専門家 | 血糖値 上げない 食べ方 |
| 15.7x | 炒めないのに甘い！ノンオイル無水カレー｜SB赤缶で作るヘルシー＆簡単スパイスカレー | https://www.youtube.com/watch?v=KOCWhYzoJBs | さこゆうのスパイスキッチン | 1,620 | 25,369 | 2025-10-22 | 5:50 | レシピ | スパイスカレー 健康 |
| 14.9x | 【脂肪肝を改善して瘦せる】脂肪肝を改善して驚異的に痩せる裏技TOP５（脂肪肝 脂質異常症 血圧 血糖値） | https://www.youtube.com/watch?v=A1ZYg_TXY24 | 人生最後のダイエットチャンネル | 9.0万 | 1,337,810 | 2025-10-09 | 17:08 | 専門家 | 白米 血糖値 対策 |
| 12.2x | 【さつまいもでコレ絶対やって！】切って焼くだけ揚げずに簡単な腸活おさつポテト！さくさくやみつき食感でサツマイモ大量消費 | https://www.youtube.com/watch?v=q0V2YkabCfw | リツの健康飯 | 11.0万 | 1,339,901 | 2025-10-25 | 4:08 | レシピ | 腸活 レシピ |
| 10.5x | 【必見】糖尿病リスクを爆上げする危険な食べ物5選〜薬に頼らず血糖値を下げる最強の習慣〜 | https://www.youtube.com/watch?v=MzuB4eYE_Vg | 理学療法士監修　一生役立つカラダの教科書 | 560 | 5,855 | 2025-12-21 | 18:05 | 専門家 | 白米 血糖値 対策 |
| 9.5x | 【空腹時血糖値180→98】ヨーグルト+⚪︎⚪︎⚪︎⚪︎⚪︎⚪︎が糖尿病をよくする理由【糖尿病専門クリニック現役医師】 | https://www.youtube.com/watch?v=8VD8jwklTmA | 糖尿病の専門家 | 21.8万 | 2,067,833 | 2025-09-06 | 19:29 | 専門家 | 血糖値 上げない 食べ方 |
| 9.4x | 【知らないと損】シナモンは「この食べ方」で効果10倍！血糖値・血管・腸を守る最強の組み合わせ3選 ｜ 生活の知恵 | https://www.youtube.com/watch?v=_d9JMKzj6Mo | 野菜と健康の知恵 | 1,670 | 15,733 | 2026-08-02 | 30:24 | 専門家 | スパイス 腸内環境 |
| 9.4x | 【朝1個食べるだけ】寝起きにコレを食べたらスルスル体重・体脂肪・血糖値が落ちました【糖尿病専門クリニック現役医師】 | https://www.youtube.com/watch?v=0MeYZ3q4n5o | 糖尿病の専門家 | 21.8万 | 2,042,658 | 2026-01-10 | 15:50 | 専門家 | 白米 血糖値 対策 / 血糖値 上げない 食べ方 |
| 9.1x | ブルーベリーを続けても無駄？白髪と視力が変わった最強の粉3選｜数値で判明した若返りの正体【60歳からの健康習慣】 | https://www.youtube.com/watch?v=YDmKwOWQxIQ | 健康寿命を伸ばす ご長寿チャンネル | 3,620 | 32,891 | 2026-03-02 | 19:43 | 専門家 | スパイス 効果 健康 |
| 8.9x | 「買わなきゃ損」腸活を極めたプロのおすすめ無印良品食品6選が美味しすぎた | https://www.youtube.com/watch?v=4Zsk228DWM4 | 【下川先生】の菌ケア大学 | 6.8万 | 608,437 | 2025-11-01 | 13:16 | 専門家 | スパイス 腸内環境 / 腸活 レシピ |
| 6.8x | 【50代以降】ブルーベリー毎日食べたら大変なことになりました【糖尿病専門クリニック現役医師】 | https://www.youtube.com/watch?v=yw6risIbKh4 | 糖尿病の専門家 | 21.8万 | 1,474,236 | 2025-10-04 | 19:22 | 専門家 | 血糖値 上げない 食べ方 |
| 6.5x | 【保存版】ブルーベリーは古い？40代から白髪と視力が劇的に若返る「3つの最強パウダー」とは【誰かに話したくなる健康雑学】 | https://www.youtube.com/watch?v=aE14gR07Rbs | そろそろ気になる雑学【健康雑学】 | 4.9万 | 317,215 | 2026-02-10 | 10:22 | 専門家 | スパイス 効果 健康 |
| 5.9x | 【血糖値の新常識】糖質を恐れなくていい！血糖値を安定させる3つの要因と耐糖能を高める食事法を解説 | https://www.youtube.com/watch?v=AqBaJi01AkU | れんのYouTube栄養大学 | 1.8万 | 105,999 | 2026-05-20 | 35:42 | 専門家 | 白米 血糖値 対策 / 血糖値 上げない 食べ方 |
| 5.8x | 【若返り】ブルーベリーの48倍白髪と視力が劇的に若返る！40歳以降の老化が止まる最強パウダー3選!【老化防止・視力回復・認知機能・頭皮改善】 | https://www.youtube.com/watch?v=ngmyTELKg-o | ひろよ・美齢活の専門家 | 9,300 | 54,287 | 2026-04-11 | 15:06 | 専門家 | スパイス 腸内環境 |
| 5.8x | 【衝撃】きな粉の◯◯の組み合わせが若返りにすごい効果！白髪が減り、血管・歯茎も若返る本当の使い方!【アンチエイジング】 | https://www.youtube.com/watch?v=PCAxTmHE7-U | ありんこ先生・美活の専門家 | 5.7万 | 332,298 | 2026-05-30 | 26:26 | 専門家 | ターメリック 効果 |
| 5.5x | 【血糖値・HbA1cが下がる!?】現役医師推薦の食べた方がいいフルーツTOP5【糖尿病専門クリニック内科医】 | https://www.youtube.com/watch?v=3Ev0AWSK7kE | 糖尿病の専門家 | 21.8万 | 1,206,762 | 2025-09-20 | 18:45 | 専門家 | 血糖値 上げない 食べ方 |
| 5.3x | コーヒーにこの粉を加えるだけで驚くべき効果が！40歳の頃のように歩ける！足腰が劇的に若返る飲み方【食で長生き】 | https://www.youtube.com/watch?v=2WYo3YydRqo | 食で長生き【60歳からの正しい食生活】 | 5.4万 | 284,582 | 2026-01-22 | 22:34 | 専門家 | ターメリック 効果 |
| 5.1x | 「毎日食べてます」腸活を極めたプロが厳選した1日のフル食を大公開！ | https://www.youtube.com/watch?v=fpAnuNrRW6E | 【下川先生】の菌ケア大学 | 6.8万 | 350,009 | 2025-10-21 | 16:26 | 専門家 | 腸活 レシピ |
| 4.8x | 【医師が驚愕】「毎日たった2粒で体が若返る!?知らないと損するクローブの真実」 | https://www.youtube.com/watch?v=d8vPEYssX7k | ペンタのおとな健康大学 [中高年の悩み解決] | 1.6万 | 78,424 | 2026-04-07 | 8:15 | 専門家 | スパイス 効果 健康 |
| 4.7x | シニア世代の方へ：ターメリックと一緒に食べてはいけない3つの食品とは？｜健康寿命 | https://www.youtube.com/watch?v=4Lc4-8e7syE | 老後のやすらぎ | 943 | 4,403 | 2025-10-16 | 19:11 | 専門家 | ターメリック 効果 |
| 4.4x | 52歳・68kg→58kgに変わったKさんの秘密→ヨーグルトに「小さじ1杯」足すだけ。痩せホルモンが2倍になる黄金レシピTOP5【スーパー食材のみ】 | https://www.youtube.com/watch?v=QPofD-xkdHI | たくみ先生 ｜ 40代からの食べやせ教室 | 19.2万 | 848,692 | 2026-03-09 | 20:13 | 専門家 | クミン 効果 / 腸活 レシピ |
| 3.8x | 驚愕！たった2粒のクローブで7日後に体が別人に！？高齢者必見！ | https://www.youtube.com/watch?v=Ff54KBHXb60 | シニアの知恵袋 | 1.9万 | 72,232 | 2025-09-12 | 28:44 | 専門家 | スパイス 効果 健康 / ターメリック 効果 |
| 3.7x | 手軽なスパイスの驚くべき健康効果 | https://www.youtube.com/watch?v=YZLNmlJhL_E | 平岳大のハリウッド・ノート | 1.6万 | 58,467 | 2026-08-14 | 13:52 | 専門家 | スパイス 効果 健康 |
| 3.5x | みんな大好き⁉カレーライスで血糖測定検証をしてみました😊 | https://www.youtube.com/watch?v=YfZf1E53v4s | 糖尿どんぶりかあさん | 291 | 1,031 | 2026-04-27 | 7:52 | レシピ | カレー 血糖値 |
| 3.5x | 【腸活ダイエット】食物繊維たっぷり！簡単５分でデトックスえのきわかめ | https://www.youtube.com/watch?v=tKCBooTbZWQ | 調理師ゆめ子のこだわりレシピ | 13.0万 | 453,612 | 2025-10-19 | 3:41 | レシピ | 腸活 レシピ |
| 3.4x | 【知らなきゃ損】睡眠改善して血糖値・HbA1c・体重が下がる!?夜にヨーグルトを食べるとこうなります【糖尿病専門クリニック現役医師】 | https://www.youtube.com/watch?v=gWcpsGrltNo | 糖尿病の専門家 | 21.8万 | 751,287 | 2026-07-18 | 17:01 | 専門家 | 血糖値 上げない 食べ方 |
| 3.4x | 【正直うまい】すき家のチキンカレーって実際どう？食べてみた結果… | https://www.youtube.com/watch?v=hjQVccC7ZeA | ながちゃんグルメ | 716 | 2,415 | 2026-04-04 | 6:24 | レシピ | カレールー 比較 |
| 3.2x | 玄米 vs 押し麦 vs もち麦。結局、血糖値に一番良いのはどれ？【リブレ検証】 | https://www.youtube.com/watch?v=f3iMWyQhMtI | 糖尿病おじさんの食卓 | 6,550 | 21,117 | 2025-10-08 | 15:39 | レシピ | 白米 血糖値 対策 |
| 3.2x | 【それ丁寧な暮らし?】血糖値・HbA1cを爆上げします！【糖尿病専門クリニック現役医師】 | https://www.youtube.com/watch?v=nHMuut_1Ons | 糖尿病の専門家 | 21.8万 | 695,637 | 2025-10-25 | 22:32 | 専門家 | カレー 健康 / カレー 血糖値 / 白米 血糖値 対策 / 血糖値 上げない 食べ方 |
| 3.2x | 朝コーヒーに混ぜるだけ！血糖値やHbA1cがどんどん下がるだけでなく、内臓脂肪減少にも効果テキメンな最強の食べ物５選【糖尿病・肥満予防】 | https://www.youtube.com/watch?v=VeSLpSKmHLs | 管理栄養士が教える健康的な習慣チャンネル | 7.8万 | 247,851 | 2026-01-14 | 21:57 | 専門家 | カレー 血糖値 / 血糖値 上げない 食べ方 |
| 2.7x | 【レビュー】激辛レトルトカレー8品を食べ比べ！辛すぎて食べれない！？【ずんだもん解説】 | https://www.youtube.com/watch?v=cqcUQw_sawo | かけそば【ずんだもん-食の情報】 | 8.8万 | 239,769 | 2026-04-20 | 32:36 | 専門家 | カレールー 比較 |
| 2.6x | 【レンチン3分】腸活力9倍！砂糖・小麦不使用、切って混ぜるだけのさつまいもりんご蒸しパン | https://www.youtube.com/watch?v=n852YSudHmc | 糖質オフ専門・いずみの太らない食生活 | 32.2万 | 849,507 | 2025-10-08 | 13:29 | レシピ | 腸活 レシピ |
| 2.6x | 【HbA1c爆上げ↑↑】糖尿病不可避！血糖値を底上げしてしまう最悪の朝食【糖尿病専門クリニック現役医師】 | https://www.youtube.com/watch?v=4FkmCs4iVgM | 糖尿病の専門家 | 21.8万 | 565,168 | 2025-10-18 | 17:01 | 専門家 | 血糖値 上げない 食べ方 |
| 2.6x | 美容院は教えない。トマトジュースに「これ」混ぜるだけで効果が10倍に。白髪と薄毛が99％黒髪に生まれ変わる最強の飲み方。（腸活・血圧改善にも効果大） | https://www.youtube.com/watch?v=MEqQovombDg | プロの裏技TV | 2.9万 | 75,891 | 2025-09-28 | 20:03 | レシピ | ターメリック 効果 |
| 2.6x | 【なぜ？体重/HbA1cがストンと落ちる】ダイエット・血糖コントロールにいい食品/食べ物【糖尿病専門クリニック現役医師】 | https://www.youtube.com/watch?v=QN6uD6f4ijE | 糖尿病の専門家 | 21.8万 | 556,802 | 2025-11-08 | 16:57 | 専門家 | 血糖値 上げない 食べ方 |
| 2.5x | 老後健康：60代から脳と筋肉が目覚める 最強スパイス＆食材7選｜医師が警告 | https://www.youtube.com/watch?v=wTUS46iPQEc | 老後健康 | 2.7万 | 67,347 | 2026-02-07 | 27:43 | 専門家 | スパイス 効果 健康 / スパイスカレー 健康 |
| 2.5x | 冷え・老化防止に最強な有名スーパーのシナモン。買っていいのはどっち？60代からの正しい選び方と許容量はどれくらい？【食で長生き】 | https://www.youtube.com/watch?v=8R-0mmsxuPM | 食で長生き【60歳からの正しい食生活】 | 5.4万 | 133,597 | 2026-03-20 | 18:52 | 専門家 | スパイス 効果 健康 |
| 2.5x | 【衝撃】「発酵食品＝腸活」は時代遅れ！？全日本人がやるべき『本当の腸活』を医師が解説：七合診療所 所長 本間 真二郎 | https://www.youtube.com/watch?v=chkEywJIfko | ヘルスアカデミー公式YTチャンネル | 29.4万 | 724,461 | 2025-09-16 | 14:18 | 専門家 | スパイス 効果 健康 / スパイス 腸内環境 / 腸活 レシピ |
| 2.4x | 【バターチキンカレー】このレシピ知ったら市販品に戻れなくなります | https://www.youtube.com/watch?v=KUbxAewqNk8 | ドラゴンキッチン | 10.0万 | 240,922 | 2026-01-17 | 5:37 | レシピ | カレー粉 |
| 2.4x | 【レビュー】激安レトルトカレーを食べ比べ！半分以上マズい！？【ずんだもん解説】 | https://www.youtube.com/watch?v=FF1xccHfW78 | かけそば【ずんだもん-食の情報】 | 8.8万 | 210,690 | 2025-12-08 | 28:42 | 専門家 | カレールー 比較 |
| 2.1x | 【糖尿病】ベジファーストはもう古い！？食べる順番を変えるだけで血糖値が劇的に下がる「新常識」を専門医が解説 | https://www.youtube.com/watch?v=oh3lDzbq88k | 糖尿病専門医　よしの内科クリニック | 4.1万 | 87,562 | 2026-02-14 | 15:12 | 専門家 | 血糖値 上げない 食べ方 |
| 2.1x | 【食べたら糖尿病まっしぐら】血糖値・HbA1cが悪化する食べ物【現役糖尿病内科医】 | https://www.youtube.com/watch?v=KKheuI-eaRY | 血糖おじさんのセルフ治療 | 46.8万 | 986,248 | 2025-10-11 | 10:27 | 専門家 | カレー 血糖値 / 血糖値 上げない 食べ方 |
| 2.0x | 【ピーマンでコレ絶対やって！】簡単5分腸活にも良い！作り置き大量消費レシピ | https://www.youtube.com/watch?v=rFWexxKiuWw | リツの健康飯 | 11.0万 | 219,910 | 2025-09-28 | 3:45 | レシピ | 腸活 レシピ |
| 2.0x | 【痩せるコンビニおやつ!?】私が-20kgのダイエットした体重をキープするために食べている罪悪感ゼロの太らないお菓子10選【糖尿病専門クリニック現役医師】 | https://www.youtube.com/watch?v=3cN809Xdpg0 | 糖尿病の専門家 | 21.8万 | 427,788 | 2026-01-03 | 13:00 | 専門家 | 血糖値 上げない 食べ方 |
| 1.9x | 【インナーケア】おすすめ食材からサプリまで✨皮膚の変態が続けてきた"美肌のための食事"を大公開👀これだけは摂って！【大野真理子】 | https://www.youtube.com/watch?v=ERWPlBWpqc8 | 【美容家 ｜ 皮膚の変態】大野真理子のご一緒よろしいですか | 15.3万 | 294,609 | 2025-11-15 | 14:09 | 専門家 | スパイス 腸内環境 |
| 1.6x | にんじんクリームチキンカレー | https://www.youtube.com/watch?v=LM26WCFV7Nc | 長谷川あかり | 26.5万 | 416,248 | 2026-07-23 | 20:06 | レシピ | カレー粉 |
| 1.5x | 【腸内環境改善】痩せたければこのSラインのものを摂ってください【糖尿病専門クリニック現役医師】 | https://www.youtube.com/watch?v=b5PqchU6K0A | 糖尿病の専門家 | 21.8万 | 320,372 | 2026-07-04 | 18:15 | 専門家 | 腸活 レシピ |
| 1.5x | 【9割が知らない】血糖値を爆上げてしまう本当の原因【糖尿病専門クリニック現役医師】 | https://www.youtube.com/watch?v=LaKlCPjTKpo | 糖尿病の専門家 | 21.8万 | 318,125 | 2026-01-24 | 16:02 | 専門家 | 血糖値 上げない 食べ方 |
| 1.3x | 【材料3つ】混ぜるだけの最強腸活。内臓脂肪減少・高血圧・生活習慣病・コレステロールにも◎腸活効果をさらに高める乳酸菌アレンジメニューもご紹介します。 | https://www.youtube.com/watch?v=-mePkrlebL8 | 糖質オフ専門・いずみの太らない食生活 | 32.2万 | 432,152 | 2026-03-06 | 13:03 | 専門家 | 腸活 レシピ |
| 1.3x | 【身近なのに】食べた方が血糖値・HbA1cにいいおやつ・お菓子【糖尿病専門クリニック現役医師】 | https://www.youtube.com/watch?v=ma3pgfjLyxY | 糖尿病の専門家 | 21.8万 | 280,329 | 2025-09-27 | 16:39 | 専門家 | 血糖値 上げない 食べ方 |
| 1.3x | 薬味たっぷり出汁カレー | https://www.youtube.com/watch?v=TugIH6TeKKI | 長谷川あかり | 26.5万 | 339,115 | 2026-04-23 | 23:05 | レシピ | カレー粉 |
| 1.2x | 【2000人が便秘薬卒業】3日で宿便3kgドバドバ出す！最強の腸内洗浄食材TOP5 | https://www.youtube.com/watch?v=7xdqK3ejl3c | たくみ先生 ｜ 40代からの食べやせ教室 | 19.2万 | 231,431 | 2026-02-15 | 16:06 | 専門家 | スパイス 腸内環境 / 腸活 レシピ |
| 1.2x | 【切って混ぜるだけ】野菜を食べる万能常備菜。内臓脂肪減少・腸活・高血圧・生活習慣病・コレステロールにも◎ | https://www.youtube.com/watch?v=Ip45UzCHeJE | 糖質オフ専門・いずみの太らない食生活 | 32.2万 | 382,004 | 2026-08-20 | 9:40 | レシピ | 腸活 レシピ |
| 1.1x | 【食後に簡単】血糖値を下げる運動🍚立ったままできる全身トレーニング﻿ #459 | https://www.youtube.com/watch?v=faMgtWUAgsg | カーディオ ワークアウト / Cardio Workout | 22.3万 | 246,201 | 2026-04-29 | 7:22 | 専門家 | 血糖値 上げない 食べ方 |
| 1.1x | 甘いおやつを食べながらHbA1cが下がった人はコレを食べてました【現役糖尿病内科医】 | https://www.youtube.com/watch?v=tojToiG17BY | 血糖おじさんのセルフ治療 | 46.8万 | 503,842 | 2025-09-06 | 13:32 | 専門家 | 血糖値 上げない 食べ方 |

## 主枠補完：日本語・1〜2年（6本）
| 倍率 | タイトル | URL | CH名 | 登録者 | 再生数 | 公開日 | 尺 | 型 | ヒットKW |
|---|---|---|---|---|---|---|---|---|---|
| 25.2x | 血糖値スパイクで爆睡が止まらないと悩むスバルに、ガチの医療従事者や糖尿病ニキから警告をもらい衝撃の事実に気付くホワるとスバ友ｗ雑談面白まとめ【大空スバル/ホロライブ/切り抜き】 | https://www.youtube.com/watch?v=tpjMsYiVtJA | ほろおん!【ホロライブ観測所】 | 2.4万 | 615,103 | 2024-11-29 | 10:24 | 専門家 | カレー 血糖値 |
| 21.4x | カレーのルー、ランキング | https://www.youtube.com/watch?v=8dVyVgMley8 | いらすとニュースチャンネル | 174 | 3,732 | 2025-07-05 | 3:18 | 専門家 | カレールー 比較 |
| 20.7x | 【腎臓病保存期の方向け】栄養士が教える！カリウム・塩分控えめでも美味しいカレーライスレシピ｜× 管理栄養士ファンデリー　#料理　#腎臓病  | https://www.youtube.com/watch?v=9k5budgRz60 | 透析病院ドットコム | 1.6万 | 335,745 | 2025-05-30 | 5:25 | 専門家 | カレー 健康 |
| 9.7x | 基本のスパイスカレーの作り方【初級編】【永久保存版】 | https://www.youtube.com/watch?v=dVw-xjhEj5c | YUKI / Spice Life | 1,780 | 17,321 | 2024-10-01 | 25:06 | レシピ | スパイスカレー 健康 |
| 9.5x | 老化した細胞を若返らせる!? 日々の疲れを癒す魔法のスパイス10選を大公開！【最新研究】 | https://www.youtube.com/watch?v=BmmbQZ_c8F8 | なんでも健康雑学【手軽に勉強】 | 592 | 5,651 | 2024-10-23 | 11:49 | 専門家 | クミン 効果 / スパイス 効果 健康 |
| 1.0x | 【王道レトルトカレー食べ比べ】新ルール！パッケージ見ないで試食したら波乱！ | https://www.youtube.com/watch?v=B8TDiAokb3E | さまぁ〜ずチャンネル | 110.0万 | 1,122,495 | 2025-05-30 | 27:24 | レシピ | カレールー 比較 |

## 参考枠：英語・中国語圏・その他言語（44本、倍率順）
| 倍率 | タイトル | URL | CH名 | 登録者 | 再生数 | 公開日 | 尺 | 型 | ヒットKW | 言語 |
|---|---|---|---|---|---|---|---|---|---|---|
| 179.0x | Eat Curry Leaves for 14 Days – See What Happens to Your Body! | https://www.youtube.com/watch?v=B5sW3OhAsug | Dr. Jiya Health Guide | 86 | 15,398 | 2026-07-16 | 5:30 | 専門家 | curry health benefits | 英 |
| 84.9x | How To Eat RICE Without Spiking Blood Sugar (The Cooling Hack) | https://www.youtube.com/watch?v=_AF-9HAxuXA | DIABETES Made Simple | 85 | 7,220 | 2025-11-12 | 8:22 | 専門家 | blood sugar rice | 英 |
| 51.6x | Add THIS to Turmeric to Kill Inflammation FAST (NOT Black Pepper)｜ Boost Turmeric Power ｜Dr. Mandell | https://www.youtube.com/watch?v=gy3zUn9VaO0 | Health DR ALISHA | 1,440 | 74,270 | 2025-12-15 | 20:32 | 専門家 | turmeric benefits | 英 |
| 48.7x | The Best Rice For Diabetes! How to Eat Rice to Lower Blood Sugar | https://www.youtube.com/watch?v=rEG8YstHZlA | Coach Sophie Hung | 566 | 27,580 | 2025-09-17 | 7:18 | 専門家 | blood sugar rice | 英 |
| 31.8x | This 1 Spice DESTROYS Bad Gut Bacteria & REPLACES Probiotics | https://www.youtube.com/watch?v=RhAMw4IN8wM | Health Pulse | 482 | 15,305 | 2026-07-05 | 23:41 | 専門家 | spices gut health | 英 |
| 19.9x | Eat Bread, Rice, Potatoes WITHOUT Blood Sugar Spikes | https://www.youtube.com/watch?v=EIb-xmln6jY | Dr. Kenji Sato | 2.5万 | 494,965 | 2026-05-09 | 20:57 | 専門家 | blood sugar rice | 英 |
| 18.5x | I Tested 13 Indian Rices… One Crashed My Glucose. Two Did Nothing. | https://www.youtube.com/watch?v=BxoXmNdlhoQ | Sweetreactions | 6.6万 | 1,211,812 | 2025-08-05 | 17:48 | 専門家 | blood sugar rice | 英 |
| 16.9x | Add THIS To Turmeric To Kill Inflammation (Not Black Pepper) ｜ Boost Turmeric Power ｜｜ Dr. Mandell | https://www.youtube.com/watch?v=G1RuY-AZcIw | Science of Healing | 2,600 | 43,840 | 2025-11-27 | 20:36 | 専門家 | turmeric benefits | 英 |
| 13.2x | “Erase Dark Spots Naturally ✨ ｜ DIY Turmeric, Honey &t Lemon Face Mask for Glowing Skin” | https://www.youtube.com/watch?v=aF8zD_4i12U | Princesshaircare | 2,040 | 26,957 | 2025-09-27 | 8:45 | 専門家 | ターメリック 効果 | 英 |
| 12.4x | EAT Bread, Potatoes, Rice (Carbs) WITHOUT blood sugar spikes! | https://www.youtube.com/watch?v=BxEUCTlXS9Q | Dr. Dazer (Adaeze Ozoh, MD) | 20.7万 | 2,564,265 | 2024-12-04 | 19:10 | 専門家 | blood sugar rice | 英 |
| 9.0x | Never Eat Turmeric With These 3 Foods – It Can Cause Serious Health Problems | https://www.youtube.com/watch?v=jGTwIvHNx3o | ELDER'S INSIGHT | 9.8万 | 886,463 | 2025-03-31 | 23:43 | 専門家 | ターメリック 効果 | 英 |
| 8.8x | കറിവേപ്പിലയുടെ അത്ഭുത ഗുണങ്ങൾ ｜ Curry Leaves Health Benefits in Malayalam | https://www.youtube.com/watch?v=D0DoPyoCAOQ | Moments by sakee | 5,120 | 45,194 | 2026-08-27 | 132:20 | 専門家 | curry health benefits | 英 |
| 8.1x | Just Turmeric Powder! Anthurium Grows Healthy and Blooms All Year | https://www.youtube.com/watch?v=Xz6bJTX13OM | Plant Care Garden | 9,480 | 76,595 | 2026-07-16 | 13:30 | 専門家 | ターメリック 効果 | 英 |
| 7.9x | How to CONSUME TURMERIC DAILY FOR MAXIMUM BENEFITS | https://www.youtube.com/watch?v=LCKhUv-9VR8 | SCImplify, PhD | 35.8万 | 2,844,074 | 2024-09-24 | 5:30 | 専門家 | turmeric benefits / ターメリック 効果 | 英 |
| 7.8x | How to Reduce INFLAMMATION Naturally! ｜ Gut Health ｜ Maharishi Ayurveda | https://www.youtube.com/watch?v=YBKcnNf3L2k | Maharishi Ayurveda | 9.9万 | 771,056 | 2025-09-29 | 9:32 | 専門家 | spices gut health | 英 |
| 7.6x | Eggs and Jackfruit: Are these the Best Diabetic-Friendly Foods? Dr Anoop Misra | https://www.youtube.com/watch?v=pWOQC7rW77M | Health Wealth | 13.8万 | 1,043,539 | 2026-06-13 | 77:36 | 専門家 | blood sugar rice | 英 |
| 6.7x | Benefits Of Turmeric For Liver Health - HIDDEN SUPERFOOD! | https://www.youtube.com/watch?v=w40mDldBu94 | Dr. Chen | 320 | 2,146 | 2026-03-22 | 4:02 | 専門家 | turmeric benefits | 英 |
| 5.4x | සුද්දො කහ වලට වහ වැටිලද? ｜ The Hidden Power of Turmeric (Curcumin) ｜ Sam's Talk | https://www.youtube.com/watch?v=xqEKN19ZX-c | Sam's Talk | 4.5万 | 241,033 | 2025-10-04 | 15:30 | 専門家 | turmeric benefits | 英 |
| 4.8x | [Gas Human] Making authentic curry with my junior, UTA-kun | https://www.youtube.com/watch?v=aVd-7PL4t2s | 冨永愛 / Ai Tominaga | 5.2万 | 251,729 | 2026-08-31 | 22:54 | 専門家 | カレー粉 | 英 |
| 4.5x | 5-Minute Lentil Bread for Lowering Blood Sugar 🩸 | https://www.youtube.com/watch?v=ds3vuIxWIik |  Kochen  Familie  Cool  | 97.1万 | 4,408,626 | 2025-10-07 | 14:51 | 専門家 | blood sugar rice | 英 |
| 4.2x | Forget probiotics — This 1 spice flushes bad gut bacteria in 24 hours | https://www.youtube.com/watch?v=H6IjUuALAU8 | Healthy Aging | 4.9万 | 207,845 | 2026-04-01 | 18:09 | 専門家 | spices gut health | 英 |
| 4.2x | EAT Bread, Rice (Carbs), Potatoes WITHOUT Blood Sugar Spikes! | https://www.youtube.com/watch?v=wPA2Q7lr8sU | Senior Health Blog | 14.1万 | 597,690 | 2025-11-11 | 28:25 | 専門家 | blood sugar rice | 英 |
| 4.1x | Gas, Bloating, and Rumbling? This Spice Saves Your Gut | https://www.youtube.com/watch?v=xNbpPSVpvmw | Ирина Шиманская l Школа нутрициологии Holistica | 23.2万 | 945,121 | 2026-05-10 | 6:57 | 専門家 | spices gut health | 英 |
| 3.8x | Take HONEY with TURMERIC After 50 this what happen After Just 1 Week! | https://www.youtube.com/watch?v=wgxSjs8lilQ | One Small Jar | 25.7万 | 970,862 | 2024-09-20 | 17:43 | 専門家 | turmeric benefits | 英 |
| 3.8x | TURMERIC: Mga BENEPISYO at Epekto sa Kalusugan | https://www.youtube.com/watch?v=5jvy_9OXrtw | MedikoPh | 15.6万 | 585,029 | 2025-12-10 | 15:10 | 専門家 | turmeric benefits | 英 |
| 3.6x | 4 Spices that Prevent & Kill Cancer (Start NOW!) | https://www.youtube.com/watch?v=g40_qAvjoFo | Dr. Amy - Cancer Researcher & Cancer Survivor | 27.8万 | 1,005,192 | 2026-01-21 | 11:49 | 専門家 | turmeric benefits | 英 |
| 3.6x | Eat Bread, Rice, Potatoes WITHOUT Blood Sugar Spikes | https://www.youtube.com/watch?v=Ed2kky2yClA | Leonid Kim MD | 88.1万 | 3,143,271 | 2025-10-27 | 9:12 | 専門家 | blood sugar rice | 英 |
| 3.3x | The Best Rice For Diabetes! I Finally Found It! | https://www.youtube.com/watch?v=FcrAweFVE-I | Type One Talks | 43.1万 | 1,410,094 | 2025-02-01 | 15:34 | 専門家 | blood sugar rice | 英 |
| 3.2x | How Much Does Eating Rice Raise Blood Sugar in Diabetes? ｜ You'll Be Shocked by the Truth | https://www.youtube.com/watch?v=A3h0NGjooMA | AyurLife

 | 9,220 | 29,224 | 2026-06-16 | 11:36 | 専門家 | blood sugar rice | 英 |
| 3.1x | Moringa vs Turmeric: Best Superfood for Immunity, Energy & Anti-Inflammation | https://www.youtube.com/watch?v=tQhyokuDpcw | Health Daily Guide | 469 | 1,459 | 2025-09-24 | 20:50 | 専門家 | turmeric benefits | 英 |
| 2.5x | Never Eat Turmeric With These 3 Foods - Deadly Food Combos with Turmeric | https://www.youtube.com/watch?v=htCyDqqIqUE | Health Guide | 19.0万 | 467,902 | 2025-04-01 | 24:01 | 専門家 | ターメリック 効果 | 英 |
| 2.4x | What's the difference between cheap and expensive curry roux? A taste test revealed some surprisi... | https://www.youtube.com/watch?v=kos1kb0Oaeo | 生活知恵袋 | 1.1万 | 27,448 | 2026-05-08 | 5:48 | 専門家 | カレールー 比較 | 英 |
| 2.4x | GAS, BLOATING, RUMBLING? This spice saves your gut | https://www.youtube.com/watch?v=UZkLN4XILC8 | Доктор Булат Ибрагимов | 6.6万 | 159,134 | 2026-05-26 | 44:37 | 専門家 | spices gut health | 英 |
| 2.4x | Stop Taking Fibre: This 1 Spice Flushes Bad Gut Bacteria Instantly ｜ Dr Sebi | https://www.youtube.com/watch?v=qBAEZfqMUpI | HealthQuest | 20.3万 | 482,514 | 2026-03-27 | 16:21 | 専門家 | spices gut health | 英 |
| 2.4x | Curry Leaves: The Superfood Your Body Needs! ｜ Good Health Assamese | https://www.youtube.com/watch?v=hh9PkbtbUmU | GOOD HEALTH - ASSAMESE HEALTH VIDEOS | 1.2万 | 28,633 | 2026-07-20 | 8:51 | 専門家 | curry health benefits | 英 |
| 2.3x |  ਇਸ ਤਰੀਕੇ ਨਾਲ ਖਾਓ ਹਲਦੀ – ਫਾਇਦੇ 2000% ਵਧਣਗੇ ｜ Turmeric Benefits ਸਿਕ੍ਰੇਟਸ ｜｜ Healthy Duniya Punjabi | https://www.youtube.com/watch?v=DGpwKTUaPCg | Healthy Duniya Punjabi | 3.0万 | 67,543 | 2025-09-02 | 21:50 | 専門家 | turmeric benefits | 英 |
| 2.2x | 3 Pagkain na 'Di Dapat Isinasabay sa Turmeric at 3 na Dapat Isabay   Alamin Bakit! | https://www.youtube.com/watch?v=VABMOO8DVwE | Gintong Sustansya 🌿🍂 | 4.8万 | 105,958 | 2025-09-14 | 17:42 | 専門家 | turmeric benefits | 英 |
| 2.1x | Medicube Turmeric – Should You Buy or Bye? | https://www.youtube.com/watch?v=SBBmMuGZ89g | BME Kween | 1.4万 | 29,401 | 2025-12-07 | 14:28 | 専門家 | ターメリック 効果 | 英 |
| 2.0x | 🌿 सकाळी उपाशीपोटी हळदीचे पाणी प्यायल्यास काय होते? ११ जबरदस्त फायदे!｜Turmeric Water Benefits #health | https://www.youtube.com/watch?v=X16FfEUmEds | Priyanka's Kitchen Tips | 16.5万 | 324,830 | 2026-09-02 | 13:06 | 専門家 | turmeric benefits | 他 |
| 1.7x | 3 Simple After‑Meal Habits to Control Blood Sugar Spikes (Doctor’s Guide) | https://www.youtube.com/watch?v=ZTv-hZlhnqo | Dr Sumit Kapadia Vascular Surgeon | 39.4万 | 650,507 | 2025-12-13 | 8:27 | 専門家 | blood sugar rice | 英 |
| 1.4x | My ultimate anti-inflammatory bone broth for gut health and immunity | https://www.youtube.com/watch?v=4iswJTdV-oo | The Doctor's Kitchen | 76.2万 | 1,091,636 | 2025-11-02 | 8:59 | 専門家 | spices gut health | 英 |
| 1.2x | சுகர் நோயாளிகள் பயமில்லாமல் சோறு சாப்பிட 8 டிப்ஸ்! Diabetes tips in Tamil | https://www.youtube.com/watch?v=ITvpLJV6xMY | Sri Parvathi Diabetic Hospital | 33.4万 | 403,351 | 2026-06-27 | 9:26 | 専門家 | blood sugar rice | 他 |
| 1.2x | 6 Best Foods to Reverse Diabetes & Lower Blood Sugar ｜ Fit Tuber Hindi | https://www.youtube.com/watch?v=s3YzO0xO-mo | Fit Tuber Hindi | 470.0万 | 5,596,707 | 2025-03-28 | 17:19 | 専門家 | blood sugar rice | 英 |
| 1.1x | 5 Easy Rice Hacks For Diabetics To Lower Blood Sugar Instantly ｜ Doctor Explains | https://www.youtube.com/watch?v=Au0vG3qw4tU | Dr Rohini Patil | 26.3万 | 290,663 | 2025-10-17 | 11:01 | 専門家 | blood sugar rice | 英 |

## 別掲：倍率基準クリアだがタイトルにトピック語なし（24本、参考）
| 倍率 | タイトル | URL | CH名 | 登録者 | 再生数 | 公開日 | 尺 | 型 | ヒットKW | 言語 |
|---|---|---|---|---|---|---|---|---|---|---|
| 172.8x | 【９割知らない健康雑学】毎日ゆで卵を食べる人、ほぼ全員●●になります〈睡眠の質/ダイエット/生活習慣病〉 | https://www.youtube.com/watch?v=mpkEKq2hI9g | 3分で知っトク健康雑学 | 4,690 | 810,247 | 2025-12-01 | 3:44 | 専門家 | クミン 効果 | 日 |
| 63.6x | 【雑学】実は植物を育てるのが好きな人は… | https://www.youtube.com/watch?v=edvhC31Mwvs | 雑学宅急便。 | 5,950 | 378,502 | 2025-09-11 | 3:55 | 専門家 | クミン 効果 | 日 |
| 21.6x | Add This to Coffee Every Morning After 60: 24% More Mitochondria in 8 Weeks (Peer-Reviewed) | https://www.youtube.com/watch?v=V2_-Oj4vH5M | Vitality Protocol | 7,550 | 163,014 | 2026-04-05 | 12:13 | 専門家 | turmeric benefits | 英 |
| 20.2x | The SHOCKING Benefits of Adding THIS Powder to Your Coffee ｜ Senior Health | https://www.youtube.com/watch?v=y3WeAZqKojg | Senior Vital Health  | 10.4万 | 2,097,435 | 2025-10-03 | 18:19 | 専門家 | turmeric benefits | 英 |
| 18.1x | 【小松菜でコレ絶対やって！】簡単5分一度食べたらやめられない小松菜の簡単作り置きレシピ | https://www.youtube.com/watch?v=bPdbcDO_biU | リツの健康飯 | 11.0万 | 1,992,962 | 2025-10-06 | 4:32 | レシピ | 腸活 レシピ | 日 |
| 18.1x | 毎朝これを食べて——体力と活力を取り戻す | https://www.youtube.com/watch?v=8GaPRcX-pTY | 人生60+ | 5,810 | 104,904 | 2026-05-06 | 27:31 | 専門家 | ターメリック 効果 | 日 |
| 17.0x | 【40代50代】“科学的に”証明された飲めば飲むほど若返る飲み物５選‼️シミ・顔のたるみ・ほうれい線を解消！【アンチエイジング】 | https://www.youtube.com/watch?v=PjdPor_hqhc | ありんこ先生・美活の専門家 | 5.7万 | 969,758 | 2025-03-21 | 20:23 | 専門家 | ターメリック 効果 | 日 |
| 16.1x | 【超簡単】朝一杯コレ飲むだけでシミ・しわ・たるみが解消されていきます【若返り/老化/アンチエイジング/朝習慣/モーニングルーティン】 | https://www.youtube.com/watch?v=IIUf_WV7-Bo | Dr.スズキの若返り革命ch | 7.8万 | 1,260,350 | 2025-06-14 | 27:23 | 専門家 | ターメリック 効果 | 日 |
| 14.3x | ノーベル賞薬イベルメクチン、ガンにどこまで効くのか？ 医師が作用を解説〜古田一徳・ふるたクリニック | https://www.youtube.com/watch?v=teUNf9z2Xhk | ふるたクリニック 百合ヶ丘 ドクターふるた YouTube講座 | 2.3万 | 325,442 | 2025-11-28 | 8:44 | 専門家 | クミン 効果 | 日 |
| 10.2x | ゆで卵を食べる人は10年後の脳が違う！？40代からの物忘れと白髪を防ぐ最強習慣【誰かに話したくなる健康と人の役立つ雑学】 | https://www.youtube.com/watch?v=W2lDkocAjsM | ウマい健康雑学 | 1.4万 | 146,985 | 2026-02-28 | 10:03 | 専門家 | カレー 健康 | 日 |
| 9.1x | 【すぐに実践できる雑学】朝に紅茶を飲む人ほぼ全員⚫︎⚫︎になります！ | https://www.youtube.com/watch?v=oAWfRO6KgXI | 今よりちょっと健康雑学 | 5,700 | 51,886 | 2026-01-08 | 3:18 | 専門家 | スパイス 効果 健康 | 日 |
| 3.8x | 【脂質1/8】低カロリーなのに濃厚で美味しい！たっぷりつけても罪悪感なし。牛乳と少しのバターを混ぜて12倍に増やす方法　脂質制限・ダイエット・節約にも!! 四毒抜きレシピではありません。 | https://www.youtube.com/watch?v=eTJAc5Cbdoo | HIRO Cooking 簡単美味しいこだわりレシピ | 10.8万 | 411,374 | 2025-11-29 | 8:03 | レシピ | カレールー 比較 | 日 |
| 3.6x | 【きのこ 大葉 漬け】きのこは全部コレにして！体調がすこぶる良くなる きのこの大葉漬け 栄養が13倍になる！ きのこの保存方法も紹介 無限きのこ 作り置き 大量消費 | https://www.youtube.com/watch?v=P1HCRyZyPyc | プラントベースゴハン | 29.8万 | 1,077,023 | 2025-09-05 | 12:28 | レシピ | 腸活 レシピ | 日 |
| 3.6x | 【脂肪肝を改善して瘦せる】3ヵ月で-8kg痩せるために最初にやった内臓脂肪を減らす食べ物8選【50代ダイエット】 | https://www.youtube.com/watch?v=Ki7J3qoUVCg | 家トレダイエット-のりfitness | 22.6万 | 814,076 | 2026-02-13 | 24:29 | 専門家 | 腸活 レシピ | 日 |
| 3.2x | Top 3 Exercises To Lower Blood Pressure Naturally | https://www.youtube.com/watch?v=XF2KX_xy_2g | Dr. Mitch Rice | 23.1万 | 732,060 | 2025-10-25 | 9:09 | 専門家 | blood sugar rice | 英 |
| 3.0x | 【爆発的大ヒット】噂以上に最高だった…！自動調理ポットがラクで美味し過ぎる12選！/recolte/スープメーカー/自動調理/レコルト | https://www.youtube.com/watch?v=UNMBp5WA0cs | 大人の暮らしStyle  | 22.5万 | 683,743 | 2025-12-10 | 20:00 | レシピ | カレールー 比較 | 日 |
| 2.2x | Eat Sweet Potato but NEVER Make These 5 Deadly Mistakes ｜ Boost Your Health with These Pairings! | https://www.youtube.com/watch?v=AH327PjH4wI | Dr Rohini Patil | 26.3万 | 580,875 | 2025-10-25 | 6:59 | 専門家 | curry health benefits | 英 |
| 2.1x | 「誰もが驚く衛生状態」弱い者は生き残れない、インドの衛生 | https://www.youtube.com/watch?v=D2zvsfpYxbg | 僕らの知らない物語 | 35.0万 | 730,438 | 2025-09-21 | 10:33 | 専門家 | インドカレー 健康 | 日 |
| 1.8x | トップバリュで一番ヤバい商品って結局どれなの？ | https://www.youtube.com/watch?v=ZCwSxiwxptc | 青海【おうみ】 | 31.6万 | 582,719 | 2025-09-26 | 11:44 | 専門家 | カレールー 比較 | 日 |
| 1.5x | 【必見】薬局ですぐ買える！がん抑制効果が期待できる“超苦い薬”とは（漢方薬・正露丸・メトホルミン・健康・がん予防・ナグモクリニック・予防医療） | https://www.youtube.com/watch?v=nYHFLa3X_KA | 【南雲吉則】Dr.ナグモの命の食事 | 18.9万 | 286,415 | 2026-05-13 | 18:20 | 専門家 | スパイス 効果 健康 | 日 |
| 1.4x | Doctor Explains How to Flush Sugar Out Your Body Overnight | https://www.youtube.com/watch?v=YRefJlnKkww | Dr. Mitch Rice | 23.1万 | 333,441 | 2026-08-03 | 8:57 | 専門家 | blood sugar rice | 英 |
| 1.4x | 【業務スーパー】ヘビーユーザー達が大絶賛した激ウマ商品１０品【徹底調査】 | https://www.youtube.com/watch?v=IvUojacnZa0 | バーキン君 | 81.9万 | 1,134,665 | 2026-05-30 | 32:22 | 専門家 | カレールー 比較 | 日 |
| 1.4x | 【サプリ級】一生歩ける体を作る！混ぜるだけで栄養が爆上がりする最強の副菜 | https://www.youtube.com/watch?v=7fgKmrNfeCU | 元気ママキッチン | 51.7万 | 704,454 | 2026-04-17 | 10:37 | レシピ | 腸活 レシピ | 日 |
| 1.3x | The one-pan protein dinner I make every week (healthy and anti-inflammatory) | https://www.youtube.com/watch?v=aXrfzqjv1E0 | The Doctor's Kitchen | 76.2万 | 1,011,287 | 2025-10-05 | 9:07 | 専門家 | curry health benefits | 英 |

## 追加集計：タイトル頻出ワード（主枠 全71本、出現本数）
- 名詞: 血糖値(20)、最強(14)、HbA1c(9)、腸活(9)、効果(8)、食材(6)、カレー(6)、劇的(6)、糖尿病(6)、ブルーベリー(5)、改善(5)、食べ物(5)、白髪(5)、本当(4)、簡単(4)、血圧(4)、レシピ(4)、シナモン(3)、老化(3)、若返り(3)、組み合わせ(3)、コーヒー(3)、コレ(3)、血糖(3)、爆上(3)、ヨーグルト(3)、体重(3)、視力(3)、食品(3)、毎日(3)
- 数字表現: TOP5(6)、3つ(4)、9割(3)、5選(3)、3選(3)、1日(2)、10倍(2)、40歳(2)、2粒(2)、5分(2)、60代(2)、10選(2)、4種(1)、68倍(1)、20倍(1)、70代(1)、ベスト7(1)、200杯(1)、200倍(1)、200→98(1)
- 【】内: 糖尿病専門クリニック現役医師(12)、食で長生き(3)、衝撃(3)、保存版(2)、9割が知らない(2)、知らないと損(2)、レビュー(2)、ずんだもん解説(2)、現役糖尿病内科医(2)、腸活最強(1)、9割が知らない健康雑学(1)、あなたは知ってる?(1)、知って得する健康雑学(1)、便秘/腸内環境/腸活/糖尿病(1)、聞き流し(1)、東京 五反田(1)、医学解説(1)、血糖値200→98(1)、血糖値改善/腸内環境/糖尿病予防/デトックス/便秘解消(1)、脂肪肝を改善して瘦せる(1)

## 追加集計：型別
| 型 | 本数 | 合計再生数 | 倍率中央値 | 倍率平均 |
|---|---|---|---|---|
| 専門家の解説型 | 54 | 28,809,518 | 5.3x | 11.0x |
| レシピ・料理型 | 17 | 6,000,470 | 3.2x | 11.0x |

### 専門家の解説型（54本）
- 名詞: 血糖値(19)、最強(13)、HbA1c(9)、効果(7)、食材(6)、劇的(6)、糖尿病(6)、ブルーベリー(5)、食べ物(5)、改善(4)、本当(4)、白髪(4)、腸活(4)、シナモン(3)、老化(3)
- 数字表現: TOP5(6)、3つ(4)、9割(3)、5選(3)、3選(3)、40歳(2)、2粒(2)、60代(2)、10選(2)、68倍(1)
- 【】内: 糖尿病専門クリニック現役医師(12)、食で長生き(3)、衝撃(3)、保存版(2)、9割が知らない(2)、知らないと損(2)、レビュー(2)、ずんだもん解説(2)、現役糖尿病内科医(2)、9割が知らない健康雑学(1)

### レシピ・料理型（17本）
- 名詞: 腸活(5)、カレー(4)、簡単(4)、常備菜(2)、万能(2)、スパイスカレー(2)、大量(2)、消費(2)、チキンカレー(2)、血圧(2)、レシピ(2)、きのこ(1)、パスタ(1)、ご飯(1)、ポン酢(1)
- 数字表現: 5分(2)、4種(1)、1日(1)、200杯(1)、9倍(1)、3分(1)、99%(1)、10倍(1)
- 【】内: 腸活最強(1)、東京 五反田(1)、さつまいもでコレ絶対やって!(1)、腸活ダイエット(1)、正直うまい(1)、リブレ検証(1)、レンチン3分(1)、バターチキンカレー(1)、ピーマンでコレ絶対やって!(1)、切って混ぜるだけ(1)

## 倍率上位30本 サムネ（ファイル名 → URL）
保存先 COO/output/thumbs_curry/。この環境からは画像ホスト(i.ytimg.com)が遮断され未保存。同フォルダの download_thumbs.sh を手元で実行すると保存される。

- 86.7_頑張らないひとりごはん_rfXUvxTSkzY.jpg → https://i.ytimg.com/vi/rfXUvxTSkzY/maxresdefault.jpg
- 69.8_今よりちょっと健康雑学_QifO7VujUEU.jpg → https://i.ytimg.com/vi/QifO7VujUEU/maxresdefault.jpg
- 60.1_老化知らず研究所_kNvDnGZQxbY.jpg → https://i.ytimg.com/vi/kNvDnGZQxbY/maxresdefault.jpg
- 53.3_【知って得する】健康雑学__ADGGa3imSg.jpg → https://i.ytimg.com/vi/_ADGGa3imSg/maxresdefault.jpg
- 45.8_老後の健康案内所_dIL1zRxK46c.jpg → https://i.ytimg.com/vi/dIL1zRxK46c/maxresdefault.jpg
- 34.4_フーズラボ_arqWdexcFik.jpg → https://i.ytimg.com/vi/arqWdexcFik/maxresdefault.jpg
- 32.5_ペンタのおとな健康大学_[中高年の悩み解決]_x9xVI5ugLBQ.jpg → https://i.ytimg.com/vi/x9xVI5ugLBQ/maxresdefault.jpg
- 21.0_予防先生・YouTube体質改善クリニック_v3NIs8SVHCM.jpg → https://i.ytimg.com/vi/v3NIs8SVHCM/maxresdefault.jpg
- 18.1_糖尿病の専門家_ZBEJhHU6oKg.jpg → https://i.ytimg.com/vi/ZBEJhHU6oKg/maxresdefault.jpg
- 17.4_ズバッと知りたい雑学_JoIcTWJ7UQY.jpg → https://i.ytimg.com/vi/JoIcTWJ7UQY/maxresdefault.jpg
- 15.8_予防先生・YouTube体質改善クリニック_aFd12CNtj78.jpg → https://i.ytimg.com/vi/aFd12CNtj78/maxresdefault.jpg
- 15.7_さこゆうのスパイスキッチン_KOCWhYzoJBs.jpg → https://i.ytimg.com/vi/KOCWhYzoJBs/maxresdefault.jpg
- 14.9_人生最後のダイエットチャンネル_A1ZYg_TXY24.jpg → https://i.ytimg.com/vi/A1ZYg_TXY24/maxresdefault.jpg
- 12.2_リツの健康飯_q0V2YkabCfw.jpg → https://i.ytimg.com/vi/q0V2YkabCfw/maxresdefault.jpg
- 10.5_理学療法士監修_一生役立つカラダの教科書_MzuB4eYE_Vg.jpg → https://i.ytimg.com/vi/MzuB4eYE_Vg/maxresdefault.jpg
- 9.5_糖尿病の専門家_8VD8jwklTmA.jpg → https://i.ytimg.com/vi/8VD8jwklTmA/maxresdefault.jpg
- 9.4_野菜と健康の知恵__d9JMKzj6Mo.jpg → https://i.ytimg.com/vi/_d9JMKzj6Mo/maxresdefault.jpg
- 9.4_糖尿病の専門家_0MeYZ3q4n5o.jpg → https://i.ytimg.com/vi/0MeYZ3q4n5o/maxresdefault.jpg
- 9.1_健康寿命を伸ばす_ご長寿チャンネル_YDmKwOWQxIQ.jpg → https://i.ytimg.com/vi/YDmKwOWQxIQ/maxresdefault.jpg
- 8.9_【下川先生】の菌ケア大学_4Zsk228DWM4.jpg → https://i.ytimg.com/vi/4Zsk228DWM4/maxresdefault.jpg
- 6.8_糖尿病の専門家_yw6risIbKh4.jpg → https://i.ytimg.com/vi/yw6risIbKh4/maxresdefault.jpg
- 6.5_そろそろ気になる雑学【健康雑学】_aE14gR07Rbs.jpg → https://i.ytimg.com/vi/aE14gR07Rbs/maxresdefault.jpg
- 5.9_れんのYouTube栄養大学_AqBaJi01AkU.jpg → https://i.ytimg.com/vi/AqBaJi01AkU/maxresdefault.jpg
- 5.8_ひろよ・美齢活の専門家_ngmyTELKg-o.jpg → https://i.ytimg.com/vi/ngmyTELKg-o/maxresdefault.jpg
- 5.8_ありんこ先生・美活の専門家_PCAxTmHE7-U.jpg → https://i.ytimg.com/vi/PCAxTmHE7-U/maxresdefault.jpg
- 5.5_糖尿病の専門家_3Ev0AWSK7kE.jpg → https://i.ytimg.com/vi/3Ev0AWSK7kE/maxresdefault.jpg
- 5.3_食で長生き【60歳からの正しい食生活】_2WYo3YydRqo.jpg → https://i.ytimg.com/vi/2WYo3YydRqo/maxresdefault.jpg
- 5.1_【下川先生】の菌ケア大学_fpAnuNrRW6E.jpg → https://i.ytimg.com/vi/fpAnuNrRW6E/maxresdefault.jpg
- 4.8_ペンタのおとな健康大学_[中高年の悩み解決]_d8vPEYssX7k.jpg → https://i.ytimg.com/vi/d8vPEYssX7k/maxresdefault.jpg
- 4.7_老後のやすらぎ_4Lc4-8e7syE.jpg → https://i.ytimg.com/vi/4Lc4-8e7syE/maxresdefault.jpg

## 別掲：登録者数非公開（判定不可）
- The Poo Doctor: This Cheap Spice Fixes A Damaged Gut! | The Diary Of A CEO、Dr. Will Bulsiewicz, The Gut Health MD | 3,219,155回 | 2026-01-01 | https://www.youtube.com/watch?v=5Tr7AhkOEj4
- They're Lying About 'Healthy' Foods & Sugar! Shocking New Research That's Harming You | The Diary Of A CEO、Glucose Revolution | 1,148,126回 | 2026-02-26 | https://www.youtube.com/watch?v=Xm_PHZXGe-w
- Delikado! Huwag Ihalo sa Turmeric ang 3 Pagkaing Ito - Alamin ang Dahilan! | Gintong Kalusugan🌾、Gintong Gabay | 305,258回 | 2025-09-12 | https://www.youtube.com/watch?v=yv89Zr6Xnc8
