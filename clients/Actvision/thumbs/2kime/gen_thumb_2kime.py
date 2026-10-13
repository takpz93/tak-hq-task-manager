import random
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops, ImageEnhance
W,H=1280,720
FONT="fonts/NotoSansJP-VF.ttf"  # Noto Sans JP 可変フォント（wght=900で使用）。同ディレクトリの fonts/ に置く
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

def text_layer(l1,l2):
    """透過PNGの文字レイヤー（文言差し替え用）"""
    t=Image.new("RGBA",(W,H),(0,0,0,0)); tw=TEXT_X1-TEXT_X0
    t.alpha_composite(stretched_text(l1,tw,L1_H,(255,255,255,255),(0,0,0,255),22),(TEXT_X0,L1_Y))
    t.alpha_composite(stretched_text(l2,tw,L2_H,(0,0,0,255),(0,0,0,255),34),(TEXT_X0,L2_Y))
    t.alpha_composite(stretched_text(l2,tw,L2_H,(255,230,0,255),(205,0,0,255),24),(TEXT_X0,L2_Y))
    ov=Image.new("RGBA",(W,H),(0,0,0,0)); ImageDraw.Draw(ov).rounded_rectangle(BADGE,radius=8,fill=(0,0,0,175)); t.alpha_composite(ov)
    d=ImageDraw.Draw(t); fb=font(32,800)
    d.text((BADGE[0]+18,BADGE[1]+8),"年間相談500件超",font=fb,fill=(255,255,255,255))
    d.text((BADGE[0]+18,BADGE[1]+50),"大阪の税理士",font=fb,fill=(255,255,255,255))
    return t

SPECS={"A":(scene_A,"創業融資は通った","2回目で落ちる"),"B":(scene_B,"返済の引落し2回","公庫は当分無理"),"C":(scene_C,"公庫は24ヶ月","次を貸さない")}
outs={}
for k,(sc,l1,l2) in SPECS.items():
    bg=desk_base().convert("RGBA"); sc(bg); bg=finish(bg); bg.convert("RGB").save(f"bg_2kime_{k}.png")
    tl=text_layer(l1,l2); tl.save(f"text_2kime_{k}.png")
    comp=bg.copy(); comp.alpha_composite(tl); comp=comp.convert("RGB"); comp.save(f"thumb_2kime_{k}.png"); outs[k]=comp
# layout guide（作業用）
g=outs["A"].copy().convert("RGBA"); ov=Image.new("RGBA",(W,H),(0,0,0,0)); dg=ImageDraw.Draw(ov)
dg.rectangle(PERF,fill=(0,255,120,40),outline=(0,255,120,255),width=4); dg.rectangle([1152,648,1279,719],fill=(255,80,80,70),outline=(255,80,80,255),width=3)
dg.text((870,30),"演者ゾーン（右1/3）",font=font(28,700),fill=(0,255,120,255)); dg.text((1000,612),"右下10%",font=font(22,700),fill=(255,120,120,255))
g.alpha_composite(ov); g.convert("RGB").save("thumb_2kime_layout_guide.png")
cs=Image.new("RGB",(3*640+4*30,480),(28,28,30)); dcs=ImageDraw.Draw(cs)
for i,k in enumerate("ABC"):
    x=30+i*670; cs.paste(outs[k].resize((640,360),Image.LANCZOS),(x,80)); dcs.text((x,24),f"{k}　{SPECS[k][1]}／{SPECS[k][2]}",font=font(28,700),fill=(240,240,240))
cs.save("thumb_2kime_contact.png"); print("done")
