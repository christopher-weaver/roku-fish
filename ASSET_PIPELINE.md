# Offline artwork pipeline

All runtime artwork and source pixels are included. No generation service, model weights, paid API, download or runtime server is required to rebuild.

```sh
python -m venv .venv
python -m pip install -r tools/requirements.txt
python tools/generate_assets.py
python tools/build.py
```

Activate the venv using the normal command for your shell. The headless mesh renderer uses ModernGL/EGL with Mesa on Linux; `LIBGL_ALWAYS_SOFTWARE=1` is supported. Windows/macOS can use a suitable EGL environment or Linux, and the optional Blender exporter remains available.

## Active inputs

- `assets/source/reef-close-reference.png`: active 1672×941 generated close reef, based on the user-supplied composition reference. It preserves the requested sunset palette, full-width coral and defined sand ridges. Provenance and prompt notes are in `assets/source/PROVENANCE.md`.
- `reef-original.png` and `empty-original.png`: retained historical sources used by earlier releases.
- Six licensed/refined photographic fish portraits, plus source sheets. The Paul Robello MIT notices and provenance remain in `assets/licenses/` and CREDITS.
- `*-texture.png`, `*-pectoral.png` and NPZ volumes are derived from those portraits and rebuildable offline.

## Scene and waves

`art.py` supplies manifest artwork and invokes `scene.py` and `waves.py`. `scene.py` resamples the active plate, builds gradient-guided reef masks from reviewed silhouette seeds, splits mid/front occlusion and records cropped image registration in `tank.json`. It builds conservative per-plane occupancy and the masked white coral crown. The crown is stored once and moved slightly at runtime, instead of storing three nearly identical copies.

The rear plate keeps the photographed sky and sand while replacing hidden coral with ambient water. Mid/front layers share one warm photographic source; lighting modes use different water/tints. Reef textures use WebP quality 74, water plates quality 74, and the crown quality 76. Alpha remains lossless. A small mask preview is generated for review.

Sand is not blurred, flattened or inpainted. `waves.py` preserves its original ridge/grain photo and generates a low-opacity, signed brightness overlay from the surface's shared eight-second periodic height field. A 256×24 light tile scales to the 2048×192 foreground band; this overlay contains no replacement sand texture. Thirty-two frames crossfade using the continuous display clock. The surface wave atlas remains separate, using the same phase.

## Fish

`fish_mesh.py` builds slim front/back textured volumes with a stitched rim and independently hinged pectoral fins. Body height remains reduced by 8%, with the existing thinner depth profiles. Source contrast and sharpness are improved. ModernGL renders each species at 32 full-circle yaw angles, eight tail bends and nine independent fin strokes with depth testing and 4× supersampling.

The larger tang/angelfish/idol use 224×196 registration canvases; the other three use 208×182. Transparent margins are cropped, with anchors retained in `species.json`, and every packed image remains within 2048px. Display lengths increase by 60%. Raw atlas renders are cached in ignored `work/fish-raw/` to support palette tuning without losing the original rendered pixels.

`optimize.py` preserves alpha, uses 144-color body palettes for the larger species and 128 for the smaller ones, and 96-color fin palettes without dithering. Fish are stored in lossless WebP containers. Wave sprites remain compact palette PNGs. `catalog.py` records dimensions and exact SHA-256 checksums. `build.py` checks every region and image and enforces the four-million-byte ZIP budget.

Always regenerate from original source pixels after changing the artwork; do not repeatedly quantize already palettized output. Rendering and quantization can vary slightly between graphics drivers/library versions; catalog hashes describe the delivered bytes rather than a cross-platform bit-exact guarantee.

## Preview and editing

```sh
node tests/roku_runner.cjs --root roku roku/source/math.brs roku/source/camera.brs roku/source/settings-model.brs roku/source/aquarium.brs roku/source/fish.brs roku/source/schooling.brs roku/source/effects.brs tests/export.brs > work/frames.log
python tools/preview.py
python -m http.server 8000
```

Create `work/` first. The export records the production brain, not a separate fish simulator. The preview reads current layer and wave metadata, so cropped registration matches the native renderer. Open `http://localhost:8000/docs/preview.html` for lighting/seek/play inspection. It does not establish Roku GPU output.

Optional Blender editing:

```sh
blender --background --python tools/blender_render.py -- --species yellow_tang --output work/blender
```

The exporter reads the same NPZ rig and photo textures, supports fin poses 0–8, and saves an editable blend. These remain inspection/replacement renders; the production atlas build uses ModernGL. The meshes are silhouette-derived textured volumes rather than anatomical scans.
