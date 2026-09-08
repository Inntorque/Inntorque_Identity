"""Build the approved InntQ. identity in navy and pure black.

The previous five letter outlines remain unchanged. The approved proposal 02
period is translated horizontally without changing its baseline or curvature.
"""
from pathlib import Path
from html import escape
import json
import subprocess
import sys
import xml.etree.ElementTree as ET
from svgpathtools import Line, Path as SvgPath, parse_path

BASE = Path(__file__).resolve().parent
OUT = BASE.parent
NS = '{http://www.w3.org/2000/svg}'
COLORS = {'Blue': '#0E2D4D', 'Black': '#000000'}
INK = '#111416'
NODE = '/Users/patrickstar/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node'
ET.register_namespace('', NS[1:-1])

def read(path):
    return [(n.get('id'), n.get('d')) for n in ET.parse(path).getroot().iter(NS+'path')]

def bounds(items):
    boxes = [parse_path(d).bbox() for _, d in items]
    return min(b[0] for b in boxes), min(b[2] for b in boxes), max(b[1] for b in boxes), max(b[3] for b in boxes)

def dim(items):
    x0, y0, x1, y1 = bounds(items)
    return x1-x0, y1-y0

def move(items, x=0, y=0, scale=1, normalize=True, prefix=''):
    bx, by, _, _ = bounds(items) if normalize else (0, 0, 0, 0)
    return [(prefix+n, parse_path(d).translated(-complex(bx, by)).scaled(scale, origin=0).translated(complex(x, y)).d()) for n, d in items]

def paths(items, color):
    return ''.join(f'<path id="{escape(n, quote=True)}" d="{d}" fill="{color}" fill-rule="evenodd"/>' for n, d in items)

def svg(path, width, height, body, title):
    root = ET.fromstring(f'<svg xmlns="{NS[1:-1]}" width="{width:.9f}" height="{height:.9f}" viewBox="0 0 {width:.9f} {height:.9f}"><title>{escape(title)}</title>{body}</svg>')
    ET.indent(root, space='  ')
    path.write_text(ET.tostring(root, encoding='unicode')+'\n', encoding='utf-8')

def render(source, target, width):
    subprocess.run([NODE, str(BASE/'render_svg.cjs'), str(source), str(target), str(width)], check=True, capture_output=True)

BASE_EN = read(BASE/'English_Reconstruction/InntQ_Base_Wordmark.svg')
REFERENCE_EN = read(OUT/'04_REFERENCE/English_Proposal02_Reference.svg')
period_name, period_data = next(p for p in REFERENCE_EN if p[0].endswith('-period'))
r_path = parse_path(next(d for n, d in REFERENCE_EN if n.endswith('-r')))
period_path = parse_path(period_data)
pb = period_path.bbox()
period_center_y = (pb[2]+pb[3])/2
intersections = r_path.intersect(SvgPath(Line(complex(-100, period_center_y), complex(1000, period_center_y))))
stem_right = max(r_path.point(hit[0][0]).real for hit in intersections)
period_gap = pb[0]-stem_right
period_translation = bounds(BASE_EN)[2]+period_gap-pb[0]
EN = BASE_EN + [('Wordmark-InntQ-period', period_path.translated(period_translation).d())]
assert len(EN) == 6 and all(EN[i] == BASE_EN[i] for i in range(5))
svg(BASE/'English_Reconstruction/InntQ_Period_Wordmark.svg', *dim(EN), paths(EN, COLORS['Blue']), 'InntQ. / Approved period added to the preserved wordmark')

SY = read(OUT/'04_REFERENCE/MASTER2_Standard_Approved.svg')
MI = read(OUT/'04_REFERENCE/MASTER2_Micro_Approved.svg')
CN = move(read(OUT/'04_REFERENCE/YingTuo_Proposal02_Approved.svg'))
ew, eh = dim(EN)
cw, ch = dim(CN)
SEP = [('Divider / Vertical', f'M{ew+38.5} 26.5h1v103h-1Z')]
BI = EN + SEP + move(CN, ew+76.75, 22.5)
SY192 = move(SY, scale=192/dim(SY)[1])
tx = dim(SY192)[0]+44
LOGOEN = SY192 + move(EN, tx, 29, normalize=False)
LOGOBI = SY192 + move(BI, tx, 29, normalize=False)
LOGOCN = SY192 + move(CN, tx, (192-ch)/2)

# Keep the prior stacked symbol and text-column width unchanged.
stack_symbol_height = 384
stack_width = dim(BASE_EN)[0]
stack_english_scale = stack_width/ew
stack_chinese_scale = stack_width/cw
stack_english_height = eh*stack_english_scale
stack_chinese_height = ch*stack_chinese_scale
stack_line_gap = 24
stack_block_height = stack_english_height+stack_line_gap+stack_chinese_height
stack_block_y = (stack_symbol_height-stack_block_height)/2
SY384 = move(SY, scale=stack_symbol_height/dim(SY)[1])
stack_x = dim(SY384)[0]+48
stack_divider_height = 1.0
stack_divider_y = stack_block_y+stack_english_height+(stack_line_gap-stack_divider_height)/2
STACK_DIVIDER = [('Divider / Horizontal', f'M{stack_x} {stack_divider_y}h{stack_width}v{stack_divider_height}h{-stack_width}Z')]
STACK = SY384 + move(EN, stack_x, stack_block_y, stack_english_scale) + STACK_DIVIDER + move(CN, stack_x, stack_block_y+stack_english_height+stack_line_gap, stack_chinese_scale)
ASSETS = [('03_InntQ_Symbol', SY), ('04_InntQ_English', EN), ('05_InntQ_Chinese', CN), ('06_InntQ_Bilingual', BI), ('07_InntQ_Logo_English', LOGOEN), ('08_InntQ_Logo_Bilingual', LOGOBI), ('09_InntQ_Logo_Chinese', LOGOCN), ('14_InntQ_Symbol_Micro', MI), ('17_InntQ_Logo_Stacked', STACK)]

manifest = []
library = []
for color_index, (label, color) in enumerate(COLORS.items()):
    for i, (name, items) in enumerate(ASSETS):
        asset_name = name+'_'+label
        w, h = dim(items)
        scale = 1130/max(w, h)
        normalized = move(items, scale=scale)
        path = OUT/'01_SVG'/(asset_name+'.svg')
        svg(path, w*scale, h*scale, paths(normalized, color), asset_name+' / InntQ.')
        lx = color_index*4096+(i%3)*1280
        ly = (i//3)*1280
        library.append(f'<g id="{asset_name}">'+paths(move(items, lx, ly, scale), color)+'</g>')
        manifest.append({'name': asset_name, 'color_name': label, 'color': color, 'width': w*scale, 'height': h*scale, 'paths': len(items), 'source_bounds': list(bounds(items)), 'scale': scale, 'library_x': lx, 'library_y': ly, 'export_presets': ['SVG', 'PNG 1x', 'PNG 2x', 'PNG 4x']})
svg(BASE/'InntQ_Period_Black_Component_Library.svg', 7786, 3690, ''.join(library), 'InntQ. / 18 native component import groups')
(BASE/'asset_manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n')
(BASE/'Period_Geometry.json').write_text(json.dumps({'wordmark': 'InntQ.', 'character_count': 6, 'preserved_letter_paths': 5, 'original_period_bounds': [pb[0], pb[2], pb[1], pb[3]], 'original_lower_r_stem_right': stem_right, 'period_gap': period_gap, 'period_translation_x': period_translation, 'period_translation_y': 0, 'period_uniform_scale': 1, 'wordmark_bounds': list(bounds(EN)), 'stack_symbol_height': stack_symbol_height, 'stack_column_width': stack_width, 'stack_english_scale': stack_english_scale, 'stack_chinese_scale': stack_chinese_scale, 'stack_block_y': stack_block_y, 'stack_block_height': stack_block_height, 'stack_line_gap': stack_line_gap, 'stack_divider_height': stack_divider_height}, indent=2)+'\n')
(BASE/'Brand.tokens.json').write_text(json.dumps({'Brand': {label: {'$type': 'color', '$value': color} for label, color in COLORS.items()}}, indent=2)+'\n')
if '--assets-only' in sys.argv:
    print(json.dumps({'asset_count': len(manifest), 'library': str(BASE/'InntQ_Period_Black_Component_Library.svg'), 'wordmark_bounds': bounds(EN)}, indent=2))
    raise SystemExit(0)

TEXT_CONTENT = {}
BOARD_MANIFEST = []
CONCEPT_LINES = [
    '两个互不接触的几何实体，通过中央留白形成动态关系，',
    '象征扭矩感知、反馈控制与具身智能。设计源于影拓的',
    '扭矩感知技术，也寓意品牌不断突破边界，开拓具身智能',
    '的未来。InntQ. 与影拓延续紧凑字形与克制的工程气质。',
]

class Board:
    def __init__(self, name, color_label):
        self.name = name
        self.color_label = color_label
        self.color = COLORS[color_label]
        self.body = '<rect id="'+name+' / Background / White" width="1600" height="1200" fill="#FFFFFF"/>'
        self.text_count = 0

    def text(self, name, value, x, y, size=22, weight=400, color=INK):
        field = self.name+' / '+name
        TEXT_CONTENT[field] = value
        self.body += f'<text id="{escape(field, quote=True)}" x="{x}" y="{y}" font-family="PingFang SC" font-size="{size}" font-weight="{weight}" fill="{color}">{escape(value)}</text>'
        self.text_count += 1

    def display(self, items, x, y, width, name):
        self.body += paths(move(items, x, y, width/dim(items)[0], prefix=self.name+' / '+name+' / '), self.color)

    def fit(self, items, x, y, max_width, max_height, name):
        w, h = dim(items)
        self.body += paths(move(items, x, y, min(max_width/w, max_height/h), prefix=self.name+' / '+name+' / '), self.color)

    def native_size(self, items, x, y, scale, name):
        self.body += paths(move(items, x, y, scale, prefix=self.name+' / '+name+' / '), self.color)

    def save(self):
        path = BASE/(self.name+'.svg')
        svg(path, 1600, 1200, self.body, self.name+' / InntQ.')
        preview = OUT/'QA/Previews'/(self.name+'.png')
        render(path, preview, 3200)
        BOARD_MANIFEST.append({'name': self.name, 'source_svg': str(path), 'preview_png': str(preview), 'width': 1600, 'height': 1200, 'color_name': self.color_label, 'color': self.color, 'text_nodes': self.text_count, 'native_png_export_scale': 2})

def proposal(name, label):
    b = Board(name, label)
    color_cn = '蓝色' if label == 'Blue' else '黑色'
    b.text('Heading / Company', '影拓 / InntQ.', 96, 100, 24, 500)
    b.text('Heading / Final', 'LOGO 最终方案 · '+color_cn, 1208, 100, 22)
    b.display(LOGOBI, 160, 296, 1280, 'Primary')
    b.body += f'<path id="{name} / Rule / Content" d="M96 704H1504" stroke="#D9D9D9"/>'
    b.text('Label / Concept', '设计理念', 96, 768, 20, 500, b.color)
    for i, value in enumerate(CONCEPT_LINES):
        b.text(f'Concept / Line {i+1:02d}', value, 96, 832+40*i, 25)
    b.text('Label / English', '英文字标', 1112, 768, 20, 500, b.color)
    b.display(EN, 1112, 816, 392, 'English')
    b.text('Label / Chinese', '中文字标', 1112, 980, 20, 500, b.color)
    b.display(CN, 1112, 1010, 200, 'Chinese')
    b.text('Footer / Final', '影拓 · 最终品牌标识方案 · '+color_cn+'版本', 96, 1144, 18)
    b.save()

def overview(name, label):
    b = Board(name, label)
    color_cn = '蓝色' if label == 'Blue' else '黑色'
    b.text('Variants / Heading', '标识组合与扩展 · '+color_cn, 96, 100, 28, 500)
    b.text('Variants / Tag', 'InntQ. / 影拓', 1296, 100, 22)
    items = [('独立图案', SY), ('中英文上下组合 · 等宽', STACK), ('图案 + 英文', LOGOEN), ('图案 + 中英文', LOGOBI), ('图案 + 中文', LOGOCN), ('中英文字标', BI)]
    for i, (title, items) in enumerate(items):
        x = 96+(i%2)*760
        y = 224+(i//2)*286
        b.text(f'Variants / Label {i+1:02d}', title, x, y, 20, 500, b.color)
        b.fit(items, x, y+44, 624, 164, f'Variant {i+1:02d}')
    b.text('Variants / Footer', color_cn+'版本 '+b.color+' · InntQ. / 影拓', 96, 1144, 18)
    b.save()

def specification(name, label):
    b = Board(name, label)
    b.text('Spec / Heading', '颜色、安全区与最小尺寸', 96, 100, 28, 500)
    for color_label, color, x in [('Blue', COLORS['Blue'], 96), ('Black', COLORS['Black'], 608)]:
        b.body += f'<rect id="{name} / Color / {color_label}" x="{x}" y="170" width="136" height="136" fill="{color}"/>'
        b.text('Spec / '+color_label, 'Brand / '+color_label, x+168, 207, 24, 500, color)
        b.text('Spec / '+color_label+' Hex', color, x+168, 250, 26)
    b.text('Spec / Color rule', '可使用品牌蓝或纯黑；同一组合中的图案与字标保持同色。', 96, 370, 23)
    b.text('Spec / Clearspace label', '安全区', 96, 454, 20, 500, b.color)
    b.native_size(LOGOEN, 144, 540, 1, 'Clear space')
    clear_w, clear_h = dim(LOGOEN)
    b.body += f'<rect id="{name} / Clear space / Boundary" x="96" y="492" width="{clear_w+96}" height="288" fill="none" stroke="#D9D9D9" stroke-dasharray="4 4"/>'
    b.text('Spec / Clearspace formula', 'Hs = 192 px    X = Hs / 4 = 48 px    最小留白 = 1X', 96, 834, 22)
    b.text('Spec / Minimum label', '实际尺寸验证', 936, 454, 20, 500, b.color)
    for i, height in enumerate([64, 32, 24, 16]):
        x = 936+i*144
        items = MI if height == 16 else SY
        b.native_size(items, x, 524, height/dim(items)[1], f'Minimum {height}')
        b.text(f'Spec / Size {height}', f'{height} px', x, 640, 18)
    b.text('Spec / Minimum rule', '完整组合：图案高度不小于 24 px。', 936, 714, 22)
    b.text('Spec / Micro rule', '16 px 使用独立图案 Micro 版本。', 936, 758, 22)
    b.text('Spec / Stack rule', '上下双语组合建议图案高度 ≥ 48 px。', 936, 806, 22)
    for height, y in [(64, 880), (32, 974), (24, 1038)]:
        b.native_size(LOGOEN, 936, y, height/192, f'Primary size {height}')
        b.text(f'Spec / Primary {height}', f'Hs = {height} px', 1256, y+24, 18)
    b.text('Spec / Naming', '品牌字标：InntQ. / 影拓', 96, 956, 24, 500, b.color)
    b.text('Spec / Fullname', '公司名称：影拓 / Inntorque', 96, 1004, 23)
    b.text('Spec / Footer', '图案保持两个独立实体；几何与字形只允许等比缩放。', 96, 1144, 18)
    b.save()

for label, names in [
    ('Blue', ['01_Blue_Proposal', '02_Blue_Overview', '03_Blue_Specification']),
    ('Black', ['04_Black_Proposal', '05_Black_Overview', '06_Black_Specification']),
]:
    proposal(names[0], label)
    overview(names[1], label)
    specification(names[2], label)
(BASE/'Text_Content.json').write_text(json.dumps(TEXT_CONTENT, ensure_ascii=False, indent=2)+'\n')
(BASE/'board_manifest.json').write_text(json.dumps(BOARD_MANIFEST, ensure_ascii=False, indent=2)+'\n')
(OUT/'Attachments/Design_Concept.txt').write_text('影拓 / InntQ. — Logo 设计理念\n\n'+''.join(CONCEPT_LINES)+'\n\n品牌字标：InntQ. / 影拓\n公司名称：影拓 / Inntorque\n品牌蓝：#0E2D4D\n纯黑版本：#000000\n', encoding='utf-8-sig')
print(json.dumps({'assets': len(manifest), 'boards': len(BOARD_MANIFEST), 'wordmark': 'InntQ.', 'colors': COLORS}, indent=2))
