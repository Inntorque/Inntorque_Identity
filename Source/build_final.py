"""Build the approved InntQ. identity in navy and pure black.

The I, n, n and t outlines remain unchanged. The open-counter uppercase Q
is uniformly sized so its outer bowl matches n height and baseline; its tail
projects below. Primary symbol height is phi times n height. The approved
period retains its curve and baseline; main lockups align symbol and text bottoms.
In symbol-leading English compositions, the original symbol serves as I.
The literal I is removed; all remaining artwork keeps its prior physical scale.
"""
from pathlib import Path
from html import escape
import json
import math
import subprocess
import sys
import xml.etree.ElementTree as ET
from svgpathtools import Line, Path as SvgPath, parse_path

BASE = Path(__file__).resolve().parent
sys.dont_write_bytecode = True
sys.path.insert(0, str(BASE/'English_Reconstruction'))
from q_weight_correction import restore_q_weight
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

BASE_EN = read(OUT/'04_REFERENCE/InntQ_Base_Wordmark_Original.svg')
# Preserve the original x position and t-to-Q gap; open the counter inside the fixed smaller bounds.
base_q_name, base_q_data = BASE_EN[4]
base_q = parse_path(base_q_data)
qb = base_q.bbox()
n_bounds = parse_path(BASE_EN[1][1]).bbox()
q_scale = (n_bounds[3]-n_bounds[2])/(qb[3]-qb[2])
small_q = base_q.translated(-complex(qb[0], qb[2])).scaled(q_scale, origin=0).translated(complex(qb[0], n_bounds[2]))
open_q, open_q_note = restore_q_weight(small_q, q_scale)
x_height = n_bounds[3]-n_bounds[2]
q_bowl_scale = x_height/(2*open_q_note['outer_ellipse_radii'][1])
q_anchor = complex(open_q.bbox()[0], open_q_note['outer_ellipse_center'][1]-open_q_note['outer_ellipse_radii'][1])
q_target = complex(qb[0], n_bounds[2])
final_q = open_q.translated(-q_anchor).scaled(q_bowl_scale, origin=0).translated(q_target)
q_bowl_center = (complex(*open_q_note['outer_ellipse_center'])-q_anchor)*q_bowl_scale+q_target
q_bowl_rx, q_bowl_ry = [value*q_bowl_scale for value in open_q_note['outer_ellipse_radii']]
q_geometry_note = {
    'uniform_scale_from_open_counter': q_bowl_scale,
    'visible_bounds': [final_q.bbox()[0], final_q.bbox()[2], final_q.bbox()[1], final_q.bbox()[3]],
    'outer_bowl_bounds': [q_bowl_center.real-q_bowl_rx, q_bowl_center.imag-q_bowl_ry, q_bowl_center.real+q_bowl_rx, q_bowl_center.imag+q_bowl_ry],
    'bowl_height': 2*q_bowl_ry, 'baseline': n_bounds[3],
    'tail_below_baseline': final_q.bbox()[3]-n_bounds[3],
    'tail_nominal_width': open_q_note['tail_width']*q_bowl_scale,
    'bowl_weights': {name:value*q_bowl_scale for name,value in open_q_note['bowl_weights'].items()},
    'counter_dimensions': [2*value*q_bowl_scale for value in open_q_note['counter_ellipse_radii']],
    'method': 'Uniform scale of the accepted open-counter Q so its outer bowl equals n height; outer bowl bottom aligned to baseline and tail allowed below.'
}
ADJUSTED_BASE_EN = BASE_EN[:4] + [(base_q_name, final_q.d())]
REFERENCE_EN = read(OUT/'04_REFERENCE/English_Proposal02_Reference.svg')
period_name, period_data = next(p for p in REFERENCE_EN if p[0].endswith('-period'))
r_path = parse_path(next(d for n, d in REFERENCE_EN if n.endswith('-r')))
period_path = parse_path(period_data)
pb = period_path.bbox()
period_center_y = (pb[2]+pb[3])/2
intersections = r_path.intersect(SvgPath(Line(complex(-100, period_center_y), complex(1000, period_center_y))))
stem_right = max(r_path.point(hit[0][0]).real for hit in intersections)
period_gap = pb[0]-stem_right
period_translation = final_q.bbox()[1]+period_gap-pb[0]
EN = ADJUSTED_BASE_EN + [('Wordmark-InntQ-period', period_path.translated(period_translation).d())]
assert len(EN) == 6 and all(EN[i] == BASE_EN[i] for i in range(4))
svg(BASE/'English_Reconstruction/InntQ_Period_Wordmark.svg', *dim(EN), paths(EN, COLORS['Blue']), 'InntQ. / Approved period added to the preserved wordmark')

SY = read(OUT/'04_REFERENCE/MASTER2_Standard_Approved.svg')
MI = read(OUT/'04_REFERENCE/MASTER2_Micro_Approved.svg')
CN = move(read(OUT/'04_REFERENCE/YingTuo_Proposal02_Approved.svg'))
ew, eh = dim(EN)
cw, ch = dim(CN)
cap_height = dim([EN[0]])[1]
bilingual_chinese_scale = cap_height/ch
bilingual_gap = 32
bilingual_chinese_y = n_bounds[3]-ch*bilingual_chinese_scale
BI = EN + move(CN, ew+bilingual_gap, bilingual_chinese_y, bilingual_chinese_scale)
phi = (1+math.sqrt(5))/2
main_symbol_height = phi*x_height
clear_space = main_symbol_height/4
SY_MAIN = move(SY, scale=main_symbol_height/dim(SY)[1])
tx = dim(SY_MAIN)[0]+44
main_english_y = main_symbol_height-n_bounds[3]
# The first n moves to the former I position, preserving the symbol-to-letter gap.
first_n_min_x = bounds([EN[1]])[0]
LOGOEN = SY_MAIN + move(EN[1:], tx-first_n_min_x-26, main_english_y, normalize=False)
LOGOBI = SY_MAIN + move(BI[1:], tx-first_n_min_x-26, main_english_y, normalize=False)
chinese_logo_scale = bilingual_chinese_scale
chinese_logo_y = main_symbol_height-ch*chinese_logo_scale
LOGOCN = SY_MAIN + move(CN, tx, chinese_logo_y, chinese_logo_scale)

# Match Chinese to the visible I/t cap height without horizontal stretching.
stack_width = dim(BASE_EN)[0]
stack_english_scale = stack_width/ew
stack_chinese_scale = cap_height*stack_english_scale/ch
stack_english_height = eh*stack_english_scale
stack_chinese_height = ch*stack_chinese_scale
stack_line_gap = 16
stack_block_height = stack_english_height+stack_line_gap+stack_chinese_height
previous_stack_symbol_height = 384
previous_stack_block_height = 360.85390639102667
stack_symbol_to_block_ratio = previous_stack_symbol_height/previous_stack_block_height
stack_symbol_height = stack_block_height*stack_symbol_to_block_ratio
stack_symbol_gap = 16
stack_symbol_gap_ratio = stack_symbol_gap/stack_symbol_height
stack_block_y = (stack_symbol_height-stack_block_height)/2
SY_STACK = move(SY, scale=stack_symbol_height/dim(SY)[1])
stack_x = dim(SY_STACK)[0]+stack_symbol_gap
stack_english_optical_shift = 27.22709000224195
stack_chinese_indent = 16
stack_english_left = stack_x-stack_english_optical_shift
stack_chinese_left = stack_x+stack_chinese_indent
STACK = SY_STACK + move(EN[1:], stack_english_left-first_n_min_x*stack_english_scale, stack_block_y, stack_english_scale, normalize=False) + move(CN, stack_chinese_left, stack_block_y+stack_english_height+stack_line_gap, stack_chinese_scale)

# Frozen pre-replacement values keep export and board artwork sizes unchanged.
# Do not normalize the shorter compositions back to 1130 units wide.
PRESERVED_EXPORT_SCALES = {
    "07_InntQ_Logo_English": 1.7798014031469325,
    "08_InntQ_Logo_Bilingual": 1.1432416547228115,
    "17_InntQ_Logo_Stacked": 1.7192413596612215,
}
PRESERVED_DISPLAY_DIMENSIONS = {
    id(LOGOEN): (634.9022975271316, 172.8491297114022),
    id(LOGOBI): (988.4174490422831, 172.8491297114022),
    id(STACK): (657.2666447616568, 291.3574277610546),
}
def display_dimensions(items):
    return PRESERVED_DISPLAY_DIMENSIONS.get(id(items), dim(items))
ASSETS = [('03_InntQ_Symbol', SY), ('07_InntQ_Logo_English', LOGOEN), ('08_InntQ_Logo_Bilingual', LOGOBI), ('09_InntQ_Logo_Chinese', LOGOCN), ('14_InntQ_Symbol_Micro', MI), ('17_InntQ_Logo_Stacked', STACK)]

manifest = []
library = []
for color_index, (label, color) in enumerate(COLORS.items()):
    for i, (name, items) in enumerate(ASSETS):
        asset_name = name+'_'+label
        w, h = dim(items)
        scale = PRESERVED_EXPORT_SCALES.get(name, 1130/max(w, h))
        normalized = move(items, scale=scale)
        path = OUT/'01_SVG'/(asset_name+'.svg')
        svg(path, w*scale, h*scale, paths(normalized, color), asset_name+' / InntQ.')
        lx = color_index*2816+(i%2)*1280
        ly = (i//2)*1280
        library.append(f'<g id="{asset_name}">'+paths(move(items, lx, ly, scale), color)+'</g>')
        manifest.append({'name': asset_name, 'color_name': label, 'color': color, 'width': w*scale, 'height': h*scale, 'paths': len(items), 'source_bounds': list(bounds(items)), 'scale': scale, 'library_x': lx, 'library_y': ly, 'export_presets': ['SVG', 'PNG 1x', 'PNG 2x', 'PNG 4x']})
svg(BASE/'InntQ_Period_Black_Component_Library.svg', 5226, 3690, ''.join(library), 'InntQ. / 12 native component import groups')
(BASE/'asset_manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n')
(BASE/'Period_Geometry.json').write_text(json.dumps({'wordmark': 'InntQ.', 'character_count': 6, 'preserved_letter_paths': 4, 'Q_initial_outer_scale': q_scale, 'Q_bowl_alignment': q_geometry_note, 'Q_bounds': q_geometry_note['visible_bounds'], 'phi': phi, 'x_height': x_height, 'main_symbol_height': main_symbol_height, 'clear_space': clear_space, 'n_bounds': [n_bounds[0], n_bounds[2], n_bounds[1], n_bounds[3]], 'main_english_y': main_english_y, 'main_symbol_bottom': main_symbol_height, 'main_letter_baseline': main_english_y+n_bounds[3], 'bilingual_chinese_y': bilingual_chinese_y, 'bilingual_chinese_bottom': bilingual_chinese_y+ch*bilingual_chinese_scale, 'bilingual_chinese_height': ch*bilingual_chinese_scale, 'bilingual_chinese_scale': bilingual_chinese_scale, 'bilingual_english_chinese_gap': bilingual_gap, 'chinese_logo_scale': chinese_logo_scale, 'chinese_logo_y': chinese_logo_y, 'chinese_logo_visible_height': ch*chinese_logo_scale, 'chinese_logo_visible_bottom': chinese_logo_y+ch*chinese_logo_scale, 'original_period_bounds': [pb[0], pb[2], pb[1], pb[3]], 'original_lower_r_stem_right': stem_right, 'period_gap': period_gap, 'period_translation_x': period_translation, 'period_translation_y': 0, 'period_uniform_scale': 1, 'wordmark_bounds': list(bounds(EN)), 'stack_symbol_height': stack_symbol_height, 'stack_column_width': dim(EN[1:])[0]*stack_english_scale, 'stack_full_wordmark_reference_width': stack_width, 'stack_english_scale': stack_english_scale, 'stack_chinese_scale': stack_chinese_scale, 'stack_block_y': stack_block_y, 'stack_block_height': stack_block_height, 'stack_line_gap': stack_line_gap, 'logo_divider_count': 0, 'stack_I_t_cap_height': cap_height*stack_english_scale, 'stack_chinese_height': stack_chinese_height, 'stack_chinese_width': cw*stack_chinese_scale, 'stack_reference_symbol_gap': stack_symbol_gap, 'stack_upper_body_to_English_gap': 14, 'stack_symbol_to_Chinese_gap': 32, 'stack_symbol_to_textblock_ratio': stack_symbol_to_block_ratio, 'stack_symbol_gap_ratio': stack_symbol_gap_ratio}, indent=2)+'\n')
(BASE/'Q_Bowl_Aligned_Geometry.json').write_text(json.dumps(q_geometry_note, indent=2)+'\n')
(BASE/'Golden_Ratio_Geometry.json').write_text(json.dumps({'phi': phi, 'x_height': x_height, 'main_symbol_height': main_symbol_height, 'ratio': main_symbol_height/x_height, 'clear_space': clear_space, 'horizontal_gap': 18, 'Chinese_only_symbol_gap': 44, 'primary_baseline': main_symbol_height, 'primary_tail_bottom': main_english_y+final_q.bbox()[3], 'Chinese_logo_scale': chinese_logo_scale, 'Chinese_logo_height': ch*chinese_logo_scale, 'Chinese_logo_top': chinese_logo_y, 'Chinese_logo_bottom': main_symbol_height, 'Chinese_ratio_note': 'Uses the common primary symbol height; local symbol-to-Chinese height is not phi.', 'stack_note': 'Two-line English and Chinese share the t cap height. English sits closer to the upper symbol body; Chinese is indented right. Symbol and lettering sizes and all vertical positions are preserved.'}, indent=2)+'\n')
(BASE/'Unified_Height_Geometry.json').write_text(json.dumps({'English_cap_height': cap_height, 'horizontal_Chinese_height': ch*bilingual_chinese_scale, 'horizontal_Chinese_scale': bilingual_chinese_scale, 'horizontal_English_Chinese_gap': bilingual_gap, 'horizontal_Chinese_baseline': bilingual_chinese_y+ch*bilingual_chinese_scale, 'logo_divider_count': 0, 'Chinese_logo_height': ch*chinese_logo_scale, 'Chinese_logo_baseline': chinese_logo_y+ch*chinese_logo_scale, 'stack_English_width': dim(EN[1:])[0]*stack_english_scale, 'stack_full_wordmark_reference_width': stack_width, 'stack_I_t_cap_height': cap_height*stack_english_scale, 'stack_Chinese_height': stack_chinese_height, 'stack_Chinese_width': cw*stack_chinese_scale, 'stack_Chinese_scale': stack_chinese_scale, 'stack_vertical_gap_after_English_tail': stack_line_gap, 'stack_textblock_height': stack_block_height, 'stack_symbol_height': stack_symbol_height, 'stack_symbol_to_textblock_ratio': stack_symbol_to_block_ratio, 'previous_stack_symbol_height': previous_stack_symbol_height, 'previous_stack_textblock_height': previous_stack_block_height, 'stack_reference_symbol_gap': stack_symbol_gap, 'stack_upper_body_to_English_gap': 14, 'stack_symbol_to_Chinese_gap': 32, 'stack_gap_to_symbol_height_ratio': stack_symbol_gap_ratio, 'stack_reference_text_left': stack_x, 'stack_English_left': stack_english_left, 'stack_Chinese_left': stack_chinese_left, 'stack_block_top': stack_block_y}, indent=2)+'\n')
(BASE/'Symbol_I_Geometry.json').write_text(json.dumps({
    'scope': 'In symbol-leading compositions 07, 08 and 17, the two-body symbol serves as the initial I. Text-only artwork 04, 05 and 06 is removed from active delivery; full spelling remains in ordinary brand text and engineering references.',
    'first_n_original_min_x': first_n_min_x,
    'horizontal_text_translation_left': first_n_min_x+26,
    'stack_English_translation_left': first_n_min_x*stack_english_scale+20.41967847013185+stack_english_optical_shift,
    'stack_Chinese_translation': -20.41967847013185+stack_chinese_indent,
    'preserved_export_scales': PRESERVED_EXPORT_SCALES,
    'previous_display_dimensions': {'07_InntQ_Logo_English': list(display_dimensions(LOGOEN)), '08_InntQ_Logo_Bilingual': list(display_dimensions(LOGOBI)), '17_InntQ_Logo_Stacked': list(display_dimensions(STACK))},
    'new_canonical_dimensions': {'07_InntQ_Logo_English': list(dim(LOGOEN)), '08_InntQ_Logo_Bilingual': list(dim(LOGOBI)), '17_InntQ_Logo_Stacked': list(dim(STACK))},
    'new_stack_English_width': dim(EN[1:])[0]*stack_english_scale,
    'stack_Chinese_width': dim(CN)[0]*stack_chinese_scale,
    'horizontal_symbol_to_first_n_gap': 18, 'Chinese_only_symbol_gap': 44,
    'horizontal_English_Chinese_gap': bilingual_gap,
    'stack_full_symbol_bbox_to_first_n_gap': stack_symbol_gap-stack_english_optical_shift, 'stack_upper_body_to_first_n_gap': 14, 'stack_symbol_to_Chinese_gap': 32,
    'preserved_sizes': 'All symbol and remaining glyph dimensions are unchanged, including actual native/library export scale and each board occurrence scale. Only frame widths shrink.',
    'logo_divider_count': 0,
}, indent=2)+'\n')
(BASE/'Stacked_Optical_Geometry.json').write_text(json.dumps({
    'English_shift_left_from_compact': stack_english_optical_shift,
    'Chinese_shift_right_from_compact': stack_chinese_indent,
    'English_first_n_left': stack_english_left,
    'Chinese_left': stack_chinese_left,
    'upper_body_to_first_n_visible_gap': 14,
    'full_symbol_bbox_to_first_n_gap': stack_symbol_gap-stack_english_optical_shift,
    'full_symbol_bbox_to_Chinese_gap': stack_symbol_gap+stack_chinese_indent,
    'English_row_top': stack_block_y,
    'Chinese_row_top': stack_block_y+stack_english_height+stack_line_gap,
    'vertical_row_gap': stack_line_gap,
    'all_sizes_and_y_positions_preserved': True,
    'export_scale_preserved': PRESERVED_EXPORT_SCALES['17_InntQ_Logo_Stacked'],
    'display_dimensions_preserved': list(display_dimensions(STACK)),
    'alignment_rule': 'English is optically closer to the upper initiating body. Chinese is indented to the right; row left edges are intentionally different.',
}, indent=2)+'\n')
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
        self.body += paths(move(items, x, y, width/display_dimensions(items)[0], prefix=self.name+' / '+name+' / '), self.color)

    def fit(self, items, x, y, max_width, max_height, name):
        w, h = display_dimensions(items)
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
    b.text('Label / Structure', '图案作为首字母 I', 1112, 768, 20, 500, b.color)
    b.text('Structure / Brand', 'InntQ. / 影拓', 1112, 832, 25)
    b.text('Label / Fullname', '公司名称', 1112, 944, 20, 500, b.color)
    b.text('Structure / Fullname', '影拓 / Inntorque', 1112, 1008, 25)
    b.text('Footer / Final', '影拓 · 最终品牌标识方案 · '+color_cn+'版本', 96, 1144, 18)
    b.save()

def overview(name, label):
    b = Board(name, label)
    color_cn = '蓝色' if label == 'Blue' else '黑色'
    b.text('Variants / Heading', '标识组合与扩展 · '+color_cn, 96, 100, 28, 500)
    b.text('Variants / Tag', 'InntQ. / 影拓', 1296, 100, 22)
    items = [('独立图案 · Standard', SY), ('小尺寸图案 · Micro', MI), ('图案 + 英文', LOGOEN), ('图案 + 中英文', LOGOBI), ('图案 + 中文', LOGOCN), ('中英文上下组合 · 等高', STACK)]
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
    b.text('Spec / Clearspace label', '安全区 · Hs / x-height ≈ 1.618', 96, 454, 20, 500, b.color)
    b.native_size(LOGOEN, 96+clear_space, 492+clear_space, 1, 'Clear space')
    clear_w, clear_h = dim(LOGOEN)
    b.body += f'<rect id="{name} / Clear space / Boundary" x="96" y="492" width="{clear_w+2*clear_space}" height="{clear_h+2*clear_space}" fill="none" stroke="#D9D9D9" stroke-dasharray="4 4"/>'
    b.text('Spec / Clearspace formula', f'X = Hs / 4 ≈ {clear_space:.2f} px · 最小留白 = 1X', 96, 834, 22)
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
        b.native_size(LOGOEN, 936, y, height/main_symbol_height, f'Primary size {height}')
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
