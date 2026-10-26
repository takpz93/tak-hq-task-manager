import random
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops, ImageEnhance
W,H=1280,720
FONT="fonts/NotoSansJP-VF.ttf"  # Noto Sans JP 可変フォント（wght=900）
def font(size,wght=900):
    f=ImageFont.truetype(FONT,size); f.set_variation_by_axes([wght]); return f
random.seed(7)
# 右1/3（x>=853）は演者用に空ける。右下10%（x>=1152,y>=648）には文字を置かない
TEXT_X0,TEXT_X1=28,836
L1_Y,L1_H=36,140
L2_Y,L2_H=196,224
BADGE=(28,560,318,652)
PERF=(853,0,1280,720)

def desk_base():
    img=Image.new("RGB",(W,H)); px=img.load()
    for y in range(H):
        t=y/H; c=(int(58-18*t),int(50-16*t),int(44-14*t))
        for x in range(W): px[x,y]=c
    noise=Image.effect_noise((W,H),28).convert("L").filter(ImageFilter.GaussianBlur(1.2))
    grain=Image.merge("RGB",(noise,noise,noise)).point(lambda v:int(v*0.25))
    return ImageChops.add(img,grain,scale=1.0,offset=-20)
def paper(w,h,fill=(242,238,226,255)):
    p=Image.new("RGBA",(w,h),(0,0,0,0)); d=ImageDraw.Draw(p)
    d.rectangle([0,0,w-1,h-1],fill=fill,outline=(200,195,180,255),width=2); return p
def paste_rot(bg,layer,pos,angle):
    rot=layer.rotate(angle,expand=True,resample=Image.BICUBIC)
    sh=Image.new("RGBA",rot.size,(0,0,0,0)); sh.paste((0,0,0,140),(0,0),rot.split()[3])
    bg.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10)),(pos[0]+14,pos[1]+18)); bg.alpha_composite(rot,pos)
def doc_lines(d,x,y,w,n,gap=22,col=(120,115,105,255)):
    for i in range(n): d.line([(x,y+i*gap),(x+int(w*random.uniform(0.55,1.0)),y+i*gap)],fill=col,width=3)
def stamp(d,cx,cy,r,text,f):
    d.ellipse([cx-r,cy-r,cx+r,cy+r],outline=(200,30,30,230),width=6)
    d.ellipse([cx-r+10,cy-r+10,cx+r-10,cy+r-10],outline=(200,30,30,200),width=2)
    bb=d.textbbox((0,0),text,font=f); d.text((cx-(bb[2]-bb[0])/2-bb[0],cy-(bb[3]-bb[1])/2-bb[1]),text,font=f,fill=(200,30,30,230))

def scene_A(bg):
    f_t=font(30,700); f_s=font(20,400)
    p=paper(520,640); d=ImageDraw.Draw(p)
    d.text((40,40),"融資承認のお知らせ",font=f_t,fill=(40,40,40,255)); d.line([(40,90),(480,90)],fill=(60,60,60,255),width=3)
    d.text((40,110),"ご申込みの創業資金について、下記のとおり",font=f_s,fill=(70,70,70,255))
    d.text((40,140),"融資を承認いたしましたのでお知らせします。",font=f_s,fill=(70,70,70,255))
    doc_lines(d,40,200,440,9,30); stamp(d,300,236,56,"承認",font(36,900))
    paste_rot(bg,p,(30,400),6)
    p2=paper(470,600); d=ImageDraw.Draw(p2)
    d.text((36,36),"借入申込書（2回目）",font=f_t,fill=(40,40,40,255)); d.line([(36,86),(434,86)],fill=(60,60,60,255),width=3)
    for i,lab in enumerate(["申込金額","資金使途","直近決算","返済状況","自己資金"]):
        y=120+i*70; d.rectangle([36,y,434,y+46],outline=(140,135,125,255),width=2)
        d.text((48,y+10),lab,font=f_s,fill=(80,80,80,255)); d.line([(190,y+32),(414,y+32)],fill=(150,145,135,255),width=2)
    d.text((36,490),"審査結果",font=f_t,fill=(40,40,40,255)); d.rectangle([36,535,434,585],outline=(140,135,125,255),width=2)
    paste_rot(bg,p2,(400,120),-5)
    x=Image.new("RGBA",(W,H),(0,0,0,0)); dx=ImageDraw.Draw(x); cx,cy=640,430
    for a,b in [((cx-200,cy-250),(cx+200,cy+250)),((cx+200,cy-250),(cx-200,cy+250))]: dx.line([a,b],fill=(215,25,25,235),width=32)
    bg.alpha_composite(x.filter(ImageFilter.GaussianBlur(0.8)))

def scene_B(bg):
    f_h=font(26,700); f_r=font(30,500); f_red=font(30,900)
    p=paper(900,780,(238,240,236,255)); d=ImageDraw.Draw(p)
    d.text((40,24),"普通預金　ご利用明細",font=f_h,fill=(60,60,60,255))
    for lab,x in [("年月日",40),("お取引内容",220),("お支払金額",520),("差引残高",720)]: d.text((x,80),lab,font=f_h,fill=(80,80,80,255))
    d.line([(30,120),(870,120)],fill=(90,90,90,255),width=3)
    rows=[("8-27","振込　ウリアゲ","","1,604,320",False),("9-05","振替　シイレ","342,000","1,262,320",False),
          ("9-10","振込　ヤチン","298,000","964,320",False),("9-20","カード","450,000","114,320",False),
          ("9-25","融資返済　引落不能","","114,320",True),("9-26","残高不足","","114,320",True),
          ("10-25","融資返済　引落不能","","96,800",True),("10-26","残高不足","","96,800",True)]
    y=140
    for dt,desc,pay,bal,red in rows:
        col=(205,20,20,255) if red else (50,50,50,255); f=f_red if red else f_r
        for txt,x in [(dt,40),(desc,220),(pay,520),(bal,720)]: d.text((x,y),txt,font=f,fill=col)
        d.line([(30,y+54),(870,y+54)],fill=(190,190,185,255),width=2); y+=68
    paste_rot(bg,p,(-20,-20),-2)

def scene_C(bg):
    f_h=font(34,700); f_d=font(26,500)
    p=paper(780,640,(246,244,238,255)); d=ImageDraw.Draw(p)
    d.rectangle([0,0,779,80],fill=(60,60,70,255)); d.text((30,20),"10",font=font(40,900),fill=(255,255,255,255)); d.text((100,30),"October",font=f_h,fill=(220,220,220,255))
    cw=780//7
    for i,dn in enumerate("日月火水木金土"): d.text((i*cw+40,95),dn,font=f_d,fill=(200,40,40,255) if i in (0,6) else (70,70,70,255))
    d.line([(0,135),(779,135)],fill=(120,120,120,255),width=2)
    day=1
    for r in range(5):
        for c in range(7):
            x0,y0=c*cw,140+r*100; d.rectangle([x0,y0,x0+cw,y0+100],outline=(190,190,185,255),width=1)
            if r*7+c>=3 and day<=31: d.text((x0+10,y0+8),str(day),font=f_d,fill=(200,40,40,255) if c in (0,6) else (60,60,60,255)); day+=1
    cx,cy=cw*3,140+3*100+40
    for k in range(3): d.ellipse([cx-150-k,cy-62-k,cx+150+k,cy+62+k],outline=(215,25,25,240),width=6)
    fm=font(64,900); bb=d.textbbox((0,0),"24ヶ月",font=fm); d.text((cx-(bb[2]-bb[0])//2-bb[0],cy-(bb[3]-bb[1])//2-bb[1]),"24ヶ月",font=fm,fill=(215,25,25,250))
    paste_rot(bg,p,(30,40),-4)
    p2=paper(420,280); d2=ImageDraw.Draw(p2)
    d2.text((30,24),"借入申込書",font=f_h,fill=(40,40,40,255)); d2.line([(30,70),(390,70)],fill=(60,60,60,255),width=3); doc_lines(d2,30,100,360,6,28)
    paste_rot(bg,p2,(560,480),7)

def finish(bg):
    img=bg.convert("RGB").filter(ImageFilter.GaussianBlur(0.6))
    img=ImageEnhance.Brightness(img).enhance(0.40); img=ImageEnhance.Color(img).enhance(0.75)
    v=Image.new("L",(W,H),0); ImageDraw.Draw(v).ellipse([-200,-180,W+200,H+180],fill=255); v=v.filter(ImageFilter.GaussianBlur(160))
    return Image.composite(img,Image.new("RGB",(W,H),(0,0,0)),v.point(lambda p:int(60+p*0.75))).convert("RGBA")

def stretched_text(text,tw,th,fill,stroke,sw,base=260):
    f=font(base,900); d=ImageDraw.Draw(Image.new("RGBA",(10,10)))
    bb=d.textbbox((0,0),text,font=f,stroke_width=sw); w,h=bb[2]-bb[0],bb[3]-bb[1]
    layer=Image.new("RGBA",(w+40,h+40),(0,0,0,0)); ImageDraw.Draw(layer).text((20-bb[0],20-bb[1]),text,font=f,fill=fill,stroke_width=sw,stroke_fill=stroke)
    return layer.resize((tw,th),Image.LANCZOS)


def stretched_segments(segs,tw,th,sw_outer=34,sw_inner=24,base=260):
    f=font(base,900); d=ImageDraw.Draw(Image.new("RGBA",(10,10)))
    boxes=[d.textbbox((0,0),t,font=f,stroke_width=sw_outer) for t,_,_ in segs]
    adv=[d.textlength(t,font=f) for t,_,_ in segs]
    w=int(sum(adv))+sw_outer*2+40; h=max(b[3]-b[1] for b in boxes)+40; top=min(b[1] for b in boxes)
    layer=Image.new("RGBA",(w,h),(0,0,0,0)); dl=ImageDraw.Draw(layer)
    for pas in ("outer","inner"):
        x=20+sw_outer
        for (t,fill,stroke),a in zip(segs,adv):
            if pas=="outer": dl.text((x,20-top),t,font=f,fill=(0,0,0,255),stroke_width=sw_outer,stroke_fill=(0,0,0,255))
            else: dl.text((x,20-top),t,font=f,fill=fill,stroke_width=sw_inner,stroke_fill=stroke)
            x+=a
    return layer.resize((tw,th),Image.LANCZOS)

YEL=(255,230,0,255); RED_S=(205,0,0,255); EMP=(240,40,40,255); BLK=(0,0,0,255)
def text_layer(l1,l2segs):
    t=Image.new("RGBA",(W,H),(0,0,0,0)); tw=TEXT_X1-TEXT_X0
    t.alpha_composite(stretched_text(l1,tw,L1_H,(255,255,255,255),(0,0,0,255),22),(TEXT_X0,L1_Y))
    t.alpha_composite(stretched_segments(l2segs,tw,L2_H),(TEXT_X0,L2_Y))
    ov=Image.new("RGBA",(W,H),(0,0,0,0)); ImageDraw.Draw(ov).rounded_rectangle(BADGE,radius=8,fill=(0,0,0,175)); t.alpha_composite(ov)
    d=ImageDraw.Draw(t); fb=font(32,800)
    d.text((BADGE[0]+18,BADGE[1]+8),"年間相談500件超",font=fb,fill=(255,255,255,255))
    d.text((BADGE[0]+18,BADGE[1]+50),"大阪の税理士",font=fb,fill=(255,255,255,255))
    return t

def sheet_doc(title,rows,w=520,h=560,fill=(242,238,226,255)):
    p=paper(w,h,fill); d=ImageDraw.Draw(p); f_t=font(30,700); f_s=font(24,500)
    d.text((36,30),title,font=f_t,fill=(40,40,40,255)); d.line([(36,78),(w-36,78)],fill=(60,60,60,255),width=3)
    for i,(lab,val,red) in enumerate(rows):
        yy=100+i*58; d.text((36,yy),lab,font=f_s,fill=(70,70,70,255)); fv=font(30,900) if red else f_s
        d.text((w-36-d.textlength(val,font=fv),yy),val,font=fv,fill=(205,20,20,255) if red else (50,50,50,255))
        d.line([(36,yy+48),(w-36,yy+48)],fill=(200,195,185,255),width=1)
    return p

def scene_A(bg):
    p=sheet_doc("領収書",[("備品・ソフト購入","1,000,000",False),("支払方法","現金",False),("目的","決算前の節税",False)],w=460,h=330)
    ImageDraw.Draw(p).text((36,270),"¥1,000,000",font=font(40,900),fill=(40,40,40,255)); paste_rot(bg,p,(40,110),-6)
    p2=sheet_doc("節税の効果",[("使ったお金","1,000,000",False),("減った税金（税率30%）","▲300,000",True),("手元から出た現金","700,000",True),("残った現金","▲700,000",True)],w=520,h=400,fill=(246,244,238,255))
    paste_rot(bg,p2,(380,330),4)
def scene_B(bg):
    p=sheet_doc("販売費及び一般管理費",[("役員報酬","12,000,000",False),("交際費","20,000,000",True),("車両費","4,800,000",False),("広告宣伝費","1,200,000",False),("支払利息","900,000",False)],w=560,h=440)
    paste_rot(bg,p,(40,120),-4)
    p2=sheet_doc("融資審査メモ",[("交際費／売上","異常値",True),("経費の使い方","放漫",True),("総合評価","要注意先",True)],w=440,h=380,fill=(246,244,238,255))
    stamp(ImageDraw.Draw(p2),350,318,52,"要注意",font(24,900)); paste_rot(bg,p2,(420,330),5)
def scene_C(bg):
    p=sheet_doc("請求書",[("機械設備　一式","8,500,000",False),("支払条件","現金一括",True),("支払期日","納品時",False)],w=480,h=330)
    ImageDraw.Draw(p).text((36,270),"¥8,500,000",font=font(40,900),fill=(40,40,40,255)); paste_rot(bg,p,(40,110),-6)
    f_h=font(24,700); f_r=font(28,500); f_red=font(28,900)
    p2=paper(620,420,(238,240,236,255)); d=ImageDraw.Draw(p2)
    d.text((30,20),"普通預金　ご利用明細",font=f_h,fill=(60,60,60,255))
    for lab,x in [("年月日",30),("お取引内容",180),("差引残高",420)]: d.text((x,64),lab,font=f_h,fill=(80,80,80,255))
    d.line([(20,100),(600,100)],fill=(90,90,90,255),width=3); y=112
    for dt,desc,bal,red in [("9-25","振込　ウリアゲ","9,120,000",False),("9-30","設備代金　一括","620,000",True),("10-25","融資返済","430,000",True),("10-31","給与振込","▲ 不足",True)]:
        col=(205,20,20,255) if red else (50,50,50,255); f=f_red if red else f_r
        d.text((30,y),dt,font=f,fill=col); d.text((180,y),desc,font=f,fill=col); d.text((420,y),bal,font=f,fill=col)
        d.line([(20,y+50),(600,y+50)],fill=(190,190,185,255),width=2); y+=62
    paste_rot(bg,p2,(330,340),4)


WHT=(255,255,255,255)
def text_layer2(l1segs,l2segs,l1h=L1_H,l2h=L2_H,gap=16):
    """上段・下段とも区切りごとに色指定。行の高さを案ごとに変えられる"""
    t=Image.new("RGBA",(W,H),(0,0,0,0)); tw=TEXT_X1-TEXT_X0
    t.alpha_composite(stretched_segments(l1segs,tw,l1h,sw_outer=30,sw_inner=18),(TEXT_X0,L1_Y))
    t.alpha_composite(stretched_segments(l2segs,tw,l2h),(TEXT_X0,L1_Y+l1h+gap))
    ov=Image.new("RGBA",(W,H),(0,0,0,0)); ImageDraw.Draw(ov).rounded_rectangle(BADGE,radius=8,fill=(0,0,0,175)); t.alpha_composite(ov)
    d=ImageDraw.Draw(t); fb=font(32,800)
    d.text((BADGE[0]+18,BADGE[1]+8),"年間相談500件超",font=fb,fill=WHT)
    d.text((BADGE[0]+18,BADGE[1]+50),"大阪の税理士",font=fb,fill=WHT)
    return t


def phone(w=300,h=520):
    p=Image.new("RGBA",(w,h),(0,0,0,0)); d=ImageDraw.Draw(p)
    d.rounded_rectangle([0,0,w-1,h-1],radius=40,fill=(30,30,34,255),outline=(90,90,95,255),width=4)
    d.rounded_rectangle([14,14,w-15,h-15],radius=30,fill=(245,247,250,255))
    d.rounded_rectangle([w//2-50,22,w//2+50,34],radius=6,fill=(30,30,34,255))
    return p

def scene_A(bg):
    """メインバンク選定シート（3択）と通帳3冊。答えは出さず「1択」のスタンプだけ"""
    f_t=font(30,700); f_s=font(24,500)
    p=paper(560,420,(246,244,238,255)); d=ImageDraw.Draw(p)
    d.text((36,30),"創業時のメインバンク",font=f_t,fill=(40,40,40,255)); d.line([(36,78),(524,78)],fill=(60,60,60,255),width=3)
    for i,lab in enumerate(["ネット銀行","メガバンク","地方銀行","信用金庫"]):
        yy=100+i*68; d.rectangle([40,yy+6,72,yy+38],outline=(90,90,90,255),width=3); d.text((90,yy),lab,font=font(28,600),fill=(60,60,60,255))
        d.text((360,yy),"融資　　　口座",font=f_s,fill=(120,120,120,255))
    paste_rot(bg,p,(30,330),-4)
    for i,(lab,col,pos,ang) in enumerate([("総合口座",(70,110,160,255),(600,430),8),("普通預金",(120,70,70,255),(690,480),3),("通帳",(60,100,80,255),(780,450),-6)]):
        b=Image.new("RGBA",(200,320),(0,0,0,0)); db=ImageDraw.Draw(b)
        db.rounded_rectangle([0,0,199,319],radius=10,fill=col,outline=(230,230,230,120),width=2)
        db.rounded_rectangle([30,60,170,110],radius=6,fill=(240,236,225,255)); db.text((44,72),lab,font=font(22,700),fill=(60,60,60,255))
        paste_rot(bg,b,pos,ang)

def scene_B(bg):
    """スマホのネット銀行画面と、融資申込書の対象外スタンプ"""
    ph=phone(); d=ImageDraw.Draw(ph)
    d.text((40,70),"ネット銀行",font=font(26,700),fill=(60,60,70,255)); d.line([(30,110),(270,110)],fill=(200,200,205,255),width=2)
    d.text((40,130),"普通預金",font=font(20,500),fill=(110,110,120,255)); d.text((40,160),"¥ 1,842,300",font=font(34,900),fill=(40,40,50,255))
    for i,(lab,v) in enumerate([("振込","0円"),("ATM","無料"),("融資","—")]):
        yy=230+i*70; d.rounded_rectangle([30,yy,270,yy+54],radius=10,fill=(235,238,243,255))
        d.text((44,yy+14),lab,font=font(22,600),fill=(70,70,80,255)); d.text((200,yy+14),v,font=font(22,700),fill=(205,20,20,255) if v=="—" else (70,70,80,255))
    d.text((40,450),"窓口・担当者：なし",font=font(20,600),fill=(205,20,20,255))
    paste_rot(bg,ph,(70,150),-6)
    f_t=font(30,700); f_s=font(22,500)
    p=paper(480,460); d=ImageDraw.Draw(p)
    d.text((36,30),"融資申込書",font=f_t,fill=(40,40,40,255)); d.line([(36,78),(444,78)],fill=(60,60,60,255),width=3)
    for i,(lab,val,red) in enumerate([("メインバンク","ネット銀行",False),("取引担当者","なし",True),("入出金の履歴","確認できず",True),("審査","保留",True)]):
        yy=100+i*64; d.text((36,yy),lab,font=f_s,fill=(70,70,70,255)); fv=font(28,900) if red else f_s
        d.text((444-d.textlength(val,font=fv),yy),val,font=fv,fill=(205,20,20,255) if red else (50,50,50,255))
        d.line([(36,yy+52),(444,yy+52)],fill=(200,195,185,255),width=1)
    paste_rot(bg,p,(400,250),5)

def scene_C(bg):
    """大手銀行の総合口座通帳と、創業期の審査メモ"""
    b=Image.new("RGBA",(360,560),(0,0,0,0)); db=ImageDraw.Draw(b)
    db.rounded_rectangle([0,0,359,559],radius=12,fill=(40,60,110,255),outline=(230,230,230,120),width=2)
    db.rounded_rectangle([50,90,310,160],radius=6,fill=(240,236,225,255)); db.text((70,108),"総合口座通帳",font=font(28,700),fill=(60,60,60,255))
    db.text((70,200),"メガバンク",font=font(26,600),fill=(220,225,235,255)); db.text((70,240),"法人口座",font=font(22,500),fill=(190,195,210,255))
    db.line([(50,480),(310,480)],fill=(200,205,220,160),width=2)
    paste_rot(bg,b,(60,130),-6)
    f_t=font(30,700); f_s=font(22,500)
    p=paper(500,440,(246,244,238,255)); d=ImageDraw.Draw(p)
    d.text((36,30),"融資審査メモ（創業期）",font=f_t,fill=(40,40,40,255)); d.line([(36,78),(464,78)],fill=(60,60,60,255),width=3)
    for i,(lab,val,red) in enumerate([("年商","2,400万",False),("希望額","500万",False),("取引規模","小口",True),("担当者の訪問","なし",True),("判定","",True)]):
        yy=100+i*58; d.text((36,yy),lab,font=f_s,fill=(70,70,70,255)); fv=font(28,900) if red else f_s
        d.text((464-d.textlength(val,font=fv),yy),val,font=fv,fill=(205,20,20,255) if red else (50,50,50,255))
        d.line([(36,yy+48),(464,yy+48)],fill=(200,195,185,255),width=1)
    paste_rot(bg,p,(400,260),5)


def fit_segments(segs,tw,maxh,min_aspect,sw_outer,sw_inner,base=260):
    """縦横比を保って幅 tw に収める。min_aspect まで横に詰めてよい（例 0.85＝最大15%圧縮）。高さは maxh を上限"""
    f=font(base,900); d=ImageDraw.Draw(Image.new("RGBA",(10,10)))
    adv=sum(d.textlength(t,font=f) for t,_,_ in segs)+sw_outer*2+40
    bb=d.textbbox((0,0),"".join(t for t,_,_ in segs),font=f,stroke_width=sw_outer); nh=bb[3]-bb[1]+40
    h=int(min(maxh, tw/(adv/nh)/min_aspect))
    return stretched_segments(segs,tw,h,sw_outer=sw_outer,sw_inner=sw_inner,base=base),h

def text_layer3(l1segs,l2segs,gap=16):
    t=Image.new("RGBA",(W,H),(0,0,0,0)); tw=TEXT_X1-TEXT_X0
    a,h1=fit_segments(l1segs,tw,L1_H,0.85,30,18); t.alpha_composite(a,(TEXT_X0,L1_Y))
    b,h2=fit_segments(l2segs,tw,L2_H,0.62,34,24); t.alpha_composite(b,(TEXT_X0,L1_Y+h1+gap))
    ov=Image.new("RGBA",(W,H),(0,0,0,0)); ImageDraw.Draw(ov).rounded_rectangle(BADGE,radius=8,fill=(0,0,0,175)); t.alpha_composite(ov)
    d=ImageDraw.Draw(t); fb=font(32,800)
    d.text((BADGE[0]+18,BADGE[1]+8),"年間相談500件超",font=fb,fill=WHT)
    d.text((BADGE[0]+18,BADGE[1]+50),"大阪の税理士",font=fb,fill=WHT)
    return t,h1,h2

FINAL={
 "A":dict(scene=scene_A,l1=[("その銀行だから",WHT,BLK)],l2=[("融資が下りない",YEL,RED_S)]),
 "B":dict(scene=scene_B,l1=[("ネット銀行がメイン？",WHT,BLK)],l2=[("税理士の答えは？",YEL,RED_S)]),
 "C":dict(scene=scene_C,l1=[("創業時、避けたい",WHT,BLK)],l2=[("あの〇〇銀行",YEL,RED_S)]),
}
outs={}
for k,sp in FINAL.items():
    bg=desk_base().convert("RGBA"); sp["scene"](bg); bg=finish(bg); bg.convert("RGB").save(f"bg_ginko5_{k}.png")
    tl,h1,h2=text_layer3(sp["l1"],sp["l2"]); tl.save(f"text_ginko5_{k}.png"); print(k,"line heights",h1,h2)
    comp=bg.copy(); comp.alpha_composite(tl); comp=comp.convert("RGB"); comp.save(f"thumb_ginko5_{k}.png"); outs[k]=comp
cs=Image.new("RGB",(3*640+4*30,480),(28,28,30)); dcs=ImageDraw.Draw(cs)
for i,k in enumerate(FINAL):
    x=30+i*670; cs.paste(outs[k].resize((640,360),Image.LANCZOS),(x,80))
    t1="".join(t for t,_,_ in FINAL[k]["l1"]); t2="".join(t for t,_,_ in FINAL[k]["l2"])
    dcs.text((x,24),f"{k}　{t1}／{t2}",font=font(28,700),fill=(240,240,240))
cs.save("contact_sheet_ginko5.png"); print("done")
