# Credits and licenses

## Deep Reef

Original BrightScript simulation, projection, renderer, native configuration interface, tests, build/deploy tools, offline mesh pipeline and documentation were created for this project. Original code is MIT licensed; see LICENSE. Original generated reef imagery and procedural effect artwork are dedicated under CC0; the legal text is in `assets/licenses/DEEP-REEF-ART-CC0.txt`. Third-party fish artwork retains its upstream MIT license.

The reef source and empty plate were generated specifically for Deep Reef through the session's available image-generation tool on 2026-11-13. No Roku Aquatic Life images, video or code were used. The exact prompts and processing provenance are retained in `assets/source/PROVENANCE.md`. Source images are included; rebuilding does not require the generator.

## Paul Robello — roku-fishtank

Source: https://github.com/paulrobello/roku-fishtank

Pinned revision: `8560cf0d3cfd22e267cf2d7ecdd1cfd80554914c`.

License: MIT, Copyright (c) 2026 Paul Robello. Retained at `assets/licenses/ROKU-FISHTANK-MIT.txt` and in the runtime package under `licenses/`.

Licensed reference portraits: ocellaris clownfish, yellow tang, royal gramma, emperor angelfish, Moorish idol and green chromis. Their upstream per-species provenance files are included under `assets/licenses/`. The upstream describes these as generated artwork; its reported generation process was not independently rerun. No independent scan/sculpt provenance is claimed. Deep Reef assembles these portraits into a six-species reference sheet, refines their appearance toward photographic fish using the session image tool, then normalizes the resulting cutouts and derives textured volume meshes and full-circle swimming atlases. The original reference sheet and final source pixels are included. The MIT attribution is retained for these derivatives. No SceneGraph aquarium runtime code from this repository is copied.

## Tim Saucer — Reef Glass

Source: https://github.com/timsaucer/reef_glass_roku_screensaver

Reviewed revision: `1ee1e5e88d7fbfced49ec4352385aff753bc4758`.

Code: Apache-2.0; art: CC0-1.0, according to its LICENSE, LICENSE-ART and CREDITS. Those notices are retained under `assets/licenses/`. The guarded memory-monitor initialization pattern in `source/main.brs` adapts its approach; the Apache license is also shipped inside the Roku ZIP. All other aquarium runtime code here is original.

Reef Glass's Git LFS artwork and models could not be retrieved through this environment's permitted endpoints. **None of its images or meshes are shipped.** Its source informed the practical choice of cached multi-view assets, native `roScreen` drawing and separate settings context. Its own device testing is not evidence for Deep Reef.

## AquariumTV — reviewed, not reused

https://github.com/khoople/aquariumtv was inspected for its SceneGraph architecture, sprite processing, animation and installation workflow. Its TERMS.txt grants personal viewing but explicitly withholds modification/redistribution rights. **No AquariumTV code or artwork is included.**

## Development dependencies

Python/Pillow, NumPy, SciPy, ModernGL/glcontext, libimagequant, Blender, BrighterScript and the `brs` interpreter are development tools installed separately under their own licenses. They are not bundled as dependencies in the Roku ZIP. The optional browser preview uses the browser's standard Canvas API with no CDN or external libraries.
