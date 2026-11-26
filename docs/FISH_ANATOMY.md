# Fish anatomy and turning — 1.0.35

The copperband reference has a substantial frontal face/body rather than a paper edge. Its neutral rendered body width/height is now 40/131 (30.5%), versus 18/131 (13.7%). These measurements exclude the independently drawn pectoral fins. The other nine species also have fuller cross-sections. Source model X/Y vertices are unchanged, preserving the approved side silhouettes; Z extents and normals are updated, and the modeled eyeballs are refitted to the head.

These are visual modeling targets, not specimen measurements or a claim of exact biological proportions.

| Species | Previous body width/length | Fuller body width/length |
| --- | ---: | ---: |
| Ocellaris clownfish | 14.5% | 18% |
| Yellow tang | 8.5% | 12% |
| Royal gramma | 11.5% | 14.5% |
| Emperor angelfish | 10% | 14% |
| Moorish idol | 6.5% | 10% |
| Blue-green chromis | 11% | 14% |
| Regal blue tang | 9% | 12.5% |
| Copperband butterflyfish | 6% | 16% |
| Banggai cardinalfish | 9% | 12.5% |
| Mandarin dragonet | 15% | 18% |

S/inverse-S swimming remains a depth-axis mesh deformation. The C-turn coefficient is reduced from 6.5% to 4% of model span for a gentler bend. The turn bank now retains all 25 refined frontal samples; broadside slots share neutral projections, while visible curved poses are baked from the volume mesh. Actual signed C-crop edges drive the interpolation, instead of incorrectly stretching curved bodies using resting-body widths.

The outgoing textured outline can fade rather than staying opaque until a view changes. Small quarter-resolution material masks keep the shared interior opaque. These masks contain no skin texture; body, fin, eye and tail sprite resolution stays unchanged. Head counter-sway fades during deliberate steering, preserving a steady displayed turn rate. Both S and C tail roots follow the same projected deformation and envelope as the body.

[Full-turn comparison](previews/turn-comparison.gif) · [Copperband frontal comparison](previews/copperband-front.png). Previews replay native draw commands on the host.

## Morphology references

- [University of Michigan, Acanthuridae](https://animaldiversity.org/accounts/Acanthuridae/): deep, compressed tang/surgeonfish bodies.
- [University of Michigan, Chaetodontidae](https://animaldiversity.org/accounts/Chaetodontidae/): deep, laterally compressed butterflyfish bodies.
- [USGS, Moorish idol](https://nas.er.usgs.gov/queries/factsheet.aspx?SpeciesID=2303): strongly compressed body.
- [FAO, emperor angelfish](https://www.fao.org/4/y0770e/y0770e50.pdf): deep, laterally compressed oval body.
- [National Museum of Nature and Science, ocellaris clownfish](https://www.kahaku.go.jp/research/db/zoology/Fishes_of_Andaman_Sea/contents/pomacentridae/11.html): moderately deep, compressed body.
- [University of Michigan, Pomacentridae](https://animaldiversity.org/accounts/Pomacentridae/): oval, laterally compressed damselfish forms.
- [FishBase, Banggai cardinalfish](https://www.fishbase.org/summary/Pterapogon_kauderni.html): compressed cross-section.
- [Monaco Nature Encyclopedia, mandarinfish](https://www.monaconatureencyclopedia.com/synchiropus-splendidus/?lang=en): cylindrical body.
- [University of Hawaii, fish structure and swimming](https://manoa.hawaii.edu/exploringourfluidearth/biological/fish/structure-and-function-fish): lateral muscle contraction and caudal propulsion.

Rebuild artwork with `python tools/whole_swim.py`; it uses the approved source meshes/textures and `tools/lateral_swim.py`. This is offline work; the Roku renders prebuilt regions.
