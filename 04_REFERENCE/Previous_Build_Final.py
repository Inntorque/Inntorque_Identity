"""Compose the approved final identity from traceable, editable vector masters."""
from pathlib import Path
from html import escape
import json, math, shutil, subprocess, sys, xml.etree.ElementTree as ET
from svgpathtools import parse_path

BASE=Path(__file__).resolve().parent; OUT=BASE.parent; ROOT=OUT.parent
NAVY='#0E2D4D'; INK='#111416'; NS='{http://www.w3.org/2000/svg}'
NODE='/Users/patrickstar/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node'
RENDER=BASE/'render_svg.cjs'
def read(p):
    return [(n.get('id'),n.get('d')) for n in ET.parse(p).getroot().iter(NS+'path')]
def bounds(ps):
    bs=[parse_path(d).bbox() for _,d in ps]
    return min(b[0] for b in bs),min(b[2] for b in bs),max(b[1] for b in bs),max(b[3] for b in bs)
def dim(ps):
    a,b,c,d=bounds(ps);return c-a,d-b
def move(ps,x=0,y=0,s=1,normalize=True,prefix=''):
    bx,by,_,_=bounds(ps) if normalize else (0,0,0,0)
    return [(prefix+n,parse_path(d).translated(complex(-bx,-by)).scaled(s,origin=0).translated(complex(x,y)).d()) for n,d in ps]
def paths(ps):
    return ''.join(f'<path id="{escape(n,quote=True)}" d="{d}" fill="{NAVY}" fill-rule="evenodd"/>' for n,d in ps)
def svg(p,w,h,body,title):
    p.write_text(f'<svg xmlns="http://www.w3.org/2000/svg" width="{w:.9f}" height="{h:.9f}" viewBox="0 0 {w:.9f} {h:.9f}"><title>{escape(title)}</title>{body}</svg>',encoding='utf-8')
def render(src,dst,w):
    subprocess.run([NODE,str(RENDER),str(src),str(dst),str(int(w))],check=True,capture_output=True)

SY=read(OUT/'04_REFERENCE/MASTER2_Standard_Approved.svg')
MI=read(OUT/'04_REFERENCE/MASTER2_Micro_Approved.svg')
EN=read(BASE/'English_Reconstruction/InntQ_Wordmark.svg')
CN=move(read(OUT/'04_REFERENCE/YingTuo_Proposal02_Approved.svg'))
ew,eh=dim(EN); cw,ch=dim(CN)
# Preserve proposal 02's Chinese scale, baseline and separator spacing against the English cap height.
SEP=[('Separator / Bilingual',f'M{ew+38.5} 26.5h1v103h-1Z')]
BI=EN+SEP+move(CN,ew+76.75,22.5)
# Newly combined layout: symbol H192, English cap H130, true visible spacing44.
SY192=move(SY,s=192/dim(SY)[1]); sw=dim(SY192)[0]; tx=sw+44
def lockup(ps): return SY192+move(ps,tx,29,normalize=False)
LOGOEN=lockup(EN); LOGOBI=lockup(BI)
LOGOCN=SY192+move(CN,tx,(192-ch)/2)
# Equal-width stacked lockup: preserve all outlines with uniform scaling only.
stack_symbol_height=384
stack_line_gap=24
stack_chinese_scale=ew/cw
stack_block_height=eh+stack_line_gap+ch*stack_chinese_scale
stack_block_y=(stack_symbol_height-stack_block_height)/2
SY384=move(SY,s=stack_symbol_height/dim(SY)[1])
stackx=dim(SY384)[0]+48
stack_divider_height=1.0
stack_divider_y=stack_block_y+eh+(stack_line_gap-stack_divider_height)/2
STACK_DIVIDER=[('Divider / Horizontal',f'M{stackx} {stack_divider_y}h{ew}v{stack_divider_height}h{-ew}Z')]
STACK=SY384+move(EN,stackx,stack_block_y)+STACK_DIVIDER+move(CN,stackx,stack_block_y+eh+stack_line_gap,stack_chinese_scale)
ASSETS=[
 ('03_InntQ_Symbol',SY),('04_InntQ_English',EN),('05_InntQ_Chinese',CN),
 ('06_InntQ_Bilingual',BI),('07_InntQ_Logo_English',LOGOEN),
 ('08_InntQ_Logo_Bilingual',LOGOBI),('09_InntQ_Logo_Chinese',LOGOCN),
 ('14_InntQ_Symbol_Micro',MI),('17_InntQ_Logo_Stacked',STACK)]
manifest=[];library=[]
for i,(name,ps) in enumerate(ASSETS):
    w,h=dim(ps);s=1130/max(w,h); ww,hh=w*s,h*s
    if '--boards-only' not in sys.argv:
        p=OUT/'01_SVG'/f'{name}.svg'; svg(p,ww,hh,paths(move(ps,s=s)),name)
        shutil.copy2(p,OUT/'Attachments'/p.name)
        for factor in [1,2,4]:
            dest=OUT/'02_PNG'/f'{factor}x';dest.mkdir(exist_ok=True)
            render(p,dest/f'{name}.png',round(ww*factor))
        shutil.copy2(OUT/'02_PNG/4x'/f'{name}.png',OUT/'Attachments'/f'{name}.png')
    library.append(f'<g id="{name}">'+paths(move(ps,(i%4)*1280,(i//4)*1280,s,prefix=''))+'</g>')
    manifest.append({'name':name,'width':ww,'height':hh,'paths':len(ps),'source_bounds':bounds(ps),'scale':s,'color':NAVY})
svg(BASE/'InntQ_Component_Library.svg',4970,3690,''.join(library),'InntQ / Native component source')

texts={}
def text(name,value,x,y,size=22,weight=400,color=INK):
    texts[name]=value
    return f'<text id="{escape(name,quote=True)}" x="{x}" y="{y}" font-family="PingFang SC" font-size="{size}" font-weight="{weight}" fill="{color}">{escape(value)}</text>'
def display(ps,x,y,w,prefix): return paths(move(ps,x,y,w/dim(ps)[0],prefix=prefix))
def background():return '<rect id="Background / White" width="1600" height="1200" fill="#FFFFFF"/>'
concept_lines=[
 '两个互不接触的几何实体，通过中央留白形成动态关系，',
 '象征扭矩感知、反馈控制与具身智能。设计源于影拓的',
 '扭矩感知技术，也寓意品牌不断突破边界，开拓具身智能',
 '的未来。InntQ 与影拓以紧凑字形和统一蓝色延续工程气质。']
body=background()+text('Heading / Company','影拓 / InntQ',96,100,24,500)+text('Heading / Final','LOGO 最终整合方案',1250,100,22)
body+=display(LOGOBI,160,296,1280,'Primary / ')
body+='<path id="Rule / Content" d="M96 704H1504" stroke="#D9D9D9"/>'
body+=text('Label / Concept','设计理念',96,768,20,500,NAVY)
for i,v in enumerate(concept_lines):body+=text(f'Concept / Line {i+1:02d}',v,96,832+40*i,25)
body+=text('Label / English','英文字标',1112,768,20,500,NAVY)+display(EN,1112,816,392,'English / ')
body+=text('Label / Chinese','中文字标',1112,980,20,500,NAVY)+display(CN,1112,1010,200,'Chinese / ')
body+=text('Footer / Final','影拓 · 最终品牌标识方案',96,1144,18)
svg(BASE/'01_InntQ_Final_Proposal.svg',1600,1200,body,'InntQ / Final identity presentation')
render(BASE/'01_InntQ_Final_Proposal.svg',OUT/'Attachments/01_InntQ_Final_Proposal.png',3200)

body=background()+text('Variants / Heading','标识组合与扩展',96,100,28,500)+text('Variants / Tag','InntQ / 影拓',1325,100,22)
items=[('独立图案',SY),('中英文上下组合 · 等宽',STACK),('图案 + 英文',LOGOEN),('图案 + 中英文',LOGOBI),('图案 + 中文',LOGOCN),('中英文字标',BI)]
for i,(label,ps) in enumerate(items):
    x=96+(i%2)*760;y=224+(i//2)*286
    body+=text(f'Variants / Label {i+1:02d}',label,x,y,20,500,NAVY)
    w,h=dim(ps);sc=min(624/w,164/h)
    body+=paths(move(ps,x,y+44,sc,prefix=f'Variant {i+1:02d} / '))
body+=text('Variants / Footer','统一蓝色 #0E2D4D · InntQ / 影拓',96,1144,18)
svg(BASE/'15_InntQ_Lockup_Overview.svg',1600,1200,body,'InntQ / Lockup overview')
render(BASE/'15_InntQ_Lockup_Overview.svg',OUT/'Attachments/15_InntQ_Lockup_Overview.png',3200)

body=background()+text('Spec / Heading','颜色、安全区与最小尺寸',96,100,28,500)
body+=f'<rect id="Color / Blue" x="96" y="170" width="136" height="136" fill="{NAVY}"/>'
body+=text('Spec / Blue','Brand / Blue',264,207,24,500,NAVY)+text('Spec / Hex','#0E2D4D',264,250,26)
body+=text('Spec / Color rule','图案、英文字标、中文字标统一使用品牌蓝。',96,370,23)
body+=text('Spec / Clearspace label','安全区',96,454,20,500,NAVY)
# True bounds: symbol visible H192; X=48. Construction is outside logo assets.
bx,by=144,540; ww,hh=dim(LOGOEN)
body+=paths(move(LOGOEN,bx,by,prefix='Clear space / '))
body+=f'<rect id="Clear space / Boundary" x="96" y="492" width="{ww+96}" height="288" fill="none" stroke="#D9D9D9" stroke-dasharray="4 4"/>'
body+=text('Spec / Clearspace formula','Hs = 192 px    X = Hs / 4 = 48 px    最小留白 = 1X',96,834,22)
body+=text('Spec / Minimum label','实际尺寸验证',936,454,20,500,NAVY)
for i,h in enumerate([64,32,24,16]):
    x=936+i*144
    body+=paths(move(MI if h==16 else SY,x,524,h/dim(MI if h==16 else SY)[1],prefix=f'Minimum {h} / '))
    body+=text(f'Spec / Size {h}',f'{h} px',x,640,18)
body+=text('Spec / Minimum rule','完整组合：图案高度不小于 24 px。',936,714,22)
body+=text('Spec / Micro rule','16 px 使用独立图案 Micro 版本。',936,758,22)
body+=text('Spec / Stack rule','上下双语组合建议图案高度 ≥ 48 px。',936,806,22)
for h,y in [(64,880),(32,974),(24,1038)]:
    body+=paths(move(LOGOEN,936,y,h/192,prefix=f'Primary size {h} / '))
    body+=text(f'Spec / Primary {h}',f'Hs = {h} px',1256,y+24,18)
body+=text('Spec / Naming','品牌字标：InntQ / 影拓',96,956,24,500,NAVY)
body+=text('Spec / Fullname','公司名称：影拓 / Inntorque',96,1004,23)
body+=text('Spec / Footer','图案保持两个独立实体；几何与字形只允许等比缩放。',96,1144,18)
svg(BASE/'16_InntQ_Usage_Specification.svg',1600,1200,body,'InntQ / Usage specification')
render(BASE/'16_InntQ_Usage_Specification.svg',OUT/'Attachments/16_InntQ_Usage_Specification.png',3200)

(BASE/'Text_Content.json').write_text(json.dumps(texts,ensure_ascii=False,indent=2)+'\n')
(BASE/'asset_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
(OUT/'Attachments/02_InntQ_Design_Concept.txt').write_text('影拓 / InntQ — Logo 设计理念\n\n'+''.join(concept_lines)+'\n\n品牌字标：InntQ / 影拓\n公司名称：影拓 / Inntorque\n品牌蓝：#0E2D4D\n',encoding='utf-8-sig')
(BASE/'Brand.tokens.json').write_text(json.dumps({'Brand':{'Blue':{'$type':'color','$value':NAVY}}},indent=2)+'\n')
print(json.dumps({'assets':len(ASSETS),'navy':NAVY,'symbol_height':192,'wordmark_cap_height':130,'main_size':dim(LOGOBI)},indent=2))
