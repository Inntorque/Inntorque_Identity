# InntQ. / 影拓 — Brand Identity

The final identity combines the approved Master2 symbol with the second proposal's lettering style. The English brand wordmark is exactly **InntQ.**: five letters followed by the original proposal's outlined period. Ordinary brand text and engineering reference outlines retain this spelling. In symbol-leading English lockups, the existing two-body symbol serves as the initial I, followed by the outlined nntQ. lettering; the duplicate literal I is removed.

## Blue and black editions

Both editions contain the same six outlined assets: Standard symbol, Micro symbol, symbol plus English, symbol plus Chinese, horizontal bilingual lockup, and stacked bilingual lockup. Standalone English, Chinese and bilingual wordmark artwork is excluded from delivery and presentation boards.

- Brand/Blue: **#0E2D4D**
- Brand/Black: **#000000**
- The two symbol bodies always share the same color.
- Logo lockups contain no vertical or horizontal separators. Presentation layout rules and measurement borders are separate from the artwork.
- Chinese characters match the visible height of the English I and t through uniform scaling. Horizontal bilingual lettering shares a baseline and a 32-unit gap after the period.
- The stacked arrangement places English above Chinese with matching cap height. English sits closer to the upper symbol body; Chinese is indented to the right. Its rows have a 16-unit visible gap after the English tail.
- The original symbol and all remaining glyphs keep their previous actual sizes in native components, exports and presentation boards. Shorter lockups have narrower frames; they are not enlarged to fill their former width.
- The complete English outline remains an engineering reference. The I, n, n and t source outlines are preserved. The uppercase Q retains the accepted open-counter shape and is uniformly sized so its outer bowl matches the n height and baseline. Its tail extends below that baseline. The period retains its outline and vertical position, with the approved gap after Q.
- Main horizontal English and Chinese logo lockups align the letter baseline with the bottom of the symbol. In English lockups, the Q tail and the original period extend slightly below that baseline.
- The symbol plus Chinese lockup uses the same 130-unit Chinese height as the horizontal bilingual lettering, with its bottom aligned to the symbol. Standalone Chinese outlines and proportions are unchanged.
- No descriptor is added to the Chinese brand.

The primary English and horizontal bilingual lockups use the golden ratio between symbol height and the lowercase n height: **Hs = φ × x-height**, where φ = 1.61803398875. At the canonical n/Q bowl height of 101.6 units, Hs = 164.392253257 units. This reduces the symbol projection above the lettering while keeping the common bottom alignment and an 18-unit gap from the symbol to the first n.

The Chinese-only logo uses the common primary symbol height with 130-unit Chinese lettering and its unchanged 44-unit horizontal gap; its local symbol-to-Chinese ratio is not φ. In the stacked lockup, the English I/t and Chinese characters are both 124.837230 units high. The remaining nntQ. lettering is 457.603479 units wide; Chinese is naturally 308.746624 units wide. The English row has a 14-unit visible gap from the upper initiating body, measured across the first n. Chinese is indented to the right, with a 32-unit gap from the full symbol boundary. The row left edges are intentionally different. The symbol remains 291.357428 units high, and all glyph sizes and vertical positions remain unchanged. All scaling is uniform.

Minimum clear space is **X = Hs / 4 = 41.098063314 units** in the canonical primary construction. The measurement includes the Q tail in the logo boundary, so the full X margin surrounds all visible artwork.

## Deliverables

- 01_SVG: 12 outlined native Figma SVG exports, six per color.
- 02_PNG: 36 transparent native Figma PNG exports at 1x, 2x and 4x.
- 03_PDF: six-page native Figma PDF, ordered Blue proposal, overview, specification, then the matching Black pages.
- 05_FIGMA_EXPORT: genuine editable Figma local master and the color token definitions.
- Attachments: 12 SVG files, 12 transparent 4x PNG files, six 3200 x 2400 presentation PNG files, design concept text, and the six-page PDF.
- Source: clean reconstruction sources and original native exports.
- 04_REFERENCE: historical approved reconstruction references. Historical spellings are retained only as provenance.
- QA: geometry, color, typography, export, PDF and true-size checks.
- SHA256SUMS.txt: checksums for the complete package.

## Figma

File: **InntQ. Brand Identity — Final**

https://www.figma.com/design/e8TvGpVHBtyVIifltZrJbH/InntQ.-Brand-Identity-Final

The desktop file contains two pages: 00 — FINAL PRESENTATION (six independent boards) and 01 — COMPONENTS & EXPORTS (12 native components). Blue and black artwork is bound to Brand/Blue and Brand/Black in the InntQ Brand variable collection. Board text remains editable. Native component export presets are SVG plus PNG 1x, 2x and 4x; board PNG presets are 2x. The current local .fig archive passed ZIP CRC and native fig-kiwi format validation. Figma desktop checks confirmed 12 native components, both color variables, SVG and PNG 1x/2x/4x presets, and six current presentation boards with temporary groups removed.

## QA and minimum sizes

Current source geometry passes fixed-size, translation-only, color, baseline and spacing checks for all 12 retained assets. Horizontal symbol-to-English spacing is 18 units; the stacked first n has a 14-unit real gap from the upper symbol body, and Chinese has a 32-unit gap from the full symbol boundary. The Chinese-only logo retains its 44-unit gap. The six presentation boards contain 86 editable text items and no standalone wordmark artwork panels. All 12 current native SVGs and 36 transparent PNGs pass geometry, color, scale and crop checks. All six 3200 x 2400 native presentation PNGs pass source-artwork comparison and visual review, including all 86 text items. All six native PDF pages pass visual and text-object checks in the correct blue-then-black order, with 86 matching text objects and zero embedded raster images. The current symbol-as-I artwork and optical stacked placement are complete and uncropped.

Current native minimum-size checks pass at primary symbol height 24 px and stacked symbol height 48 px. The symbol represents I and the remaining nntQ. lettering stays legible, with an open Q counter and distinct period. At stacked Hs48, the upper symbol-to-n gap is approximately 2.31 px, and Chinese is indented approximately 7.12 px to the right of the English row. The lower body and first n also remain separate. No divider is present.

**NEEDS HUMAN REVIEW — final 16 px deployment:** integer-aligned Standard and Micro symbol previews retain two bodies, but fractional pixel placement can visually join antialiased edges. Micro was more robust in the tested quarter-pixel alignments. Use Micro at 16 px and review the final rendered placement; this is a small-raster placement limitation, not contact in the vector geometry.

Physical manufacturing proofs are outside this digital QA. No Illustrator file has been fabricated. No email was sent as part of this revision.
