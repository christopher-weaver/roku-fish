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
- `assets/source/reef-midground-cutout.png`: generated RGBA isolation of the close reef, with clean coral tips and transparent water gaps. The exact source pixels are checked in.
- `reef-original.png` and `empty-original.png`: retained historical sources used by earlier releases.
- Six licensed/refined photographic fish portraits, plus source sheets. The Paul Robello MIT notices and provenance remain in `assets/licenses/` and CREDITS.
- `*-texture.png`, `*-pectoral.png` and NPZ volumes are derived from those portraits and rebuildable offline.

## Scene and waves

`art.py` invokes `scene.py` and `waves.py`. `scene.py` registers the transparent cutout over the original reference sand and separates eight mid-ground formations. Each cropped layer records its image origin, depth, half-thickness and parallax. A small overlapping seam margin prevents parallax gaps. Runtime alpha is quantized to 32 levels; WebP quality 72 stores the photographic color with lossless storage of that bounded alpha. Water plates use quality 74. No coral remains in the water/sand plate.

The same formation masks produce 8px occupancy grids. The generator checks a 3D lattice and its swept edges against all six species at maximum size and pitch throughout camera travel, retains the connected component and writes `navigation.json`. Runtime fish choose routes through this graph. Rebuild navigation whenever coral, projection, species size or collision margins change. A mask preview supports inspection.
Sand is not blurred, flattened or inpainted. `waves.py` preserves its original ridge/grain photo and generates a low-opacity, signed brightness overlay from the surface's shared eight-second periodic height field. A 256×24 light tile scales to the 2048×192 foreground band; this overlay contains no replacement sand texture. Thirty-two frames crossfade using the continuous display clock. The surface wave atlas remains separate, using the same phase.

## Fish

`fish_mesh.py` builds slim front/back textured volumes with a stitched rim and independently hinged pectoral fins. Body height remains reduced by 8%, with the existing thinner depth profiles. Source contrast and sharpness are improved. ModernGL renders each species at 33 unique half-circle yaw angles, mapped to 64 full-circle views by bilateral reflection and reversed tail bends, eight tail bends and nine independent fin strokes with depth testing and 4× supersampling.

The larger tang/angelfish/idol use 224×196 registration canvases; the other three use 208×182. Transparent margins are cropped, with anchors retained in `species.json`, and every packed image remains within 2048px. Display lengths increase by 60%. Raw atlas renders are cached in ignored `work/fish-raw/` to support palette tuning without losing the original rendered pixels.

`optimize.py` preserves alpha, uses 128-color body palettes and 96-color fin palettes without dithering. Fish are stored in lossless WebP containers. Wave sprites remain compact palette PNGs. `catalog.py` records dimensions and exact SHA-256 checksums. `build.py` checks every region and image and enforces the four-million-byte ZIP budget.

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
