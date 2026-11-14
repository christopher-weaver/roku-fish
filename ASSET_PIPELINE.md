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
- `assets/source/reef-midground-cutout.png`: historical generated RGBA isolation retained from version 1.0.6. The exact source pixels are checked in.
- `reef-original.png` and `empty-original.png`: retained historical sources used by earlier releases.
- Six licensed/refined photographic fish portraits, plus source sheets. The Paul Robello MIT notices and provenance remain in `assets/licenses/` and CREDITS.
- `*-texture.png`, `*-pectoral.png` and NPZ volumes are derived from those portraits and rebuildable offline.

## Scene, coral renders and waves

`coral-islands-sheet.png` is a generated 3×2 RGBA collection derived from the established reef reference. `coral_render.py` separates its six objects and builds a 129×129 textured relief mesh for each, using alpha distance and fine luminance relief. ModernGL renders -5°, 0° and +5° views with surface-normal lighting and 2× supersampling. The 3-view 1344×448 WebP atlases have bounded alpha and recorded silhouettes. These source-derived volumes preserve photographic detail; they are not anatomical coral scans.

`scene.py` places the six islands at separate depths with open sand/water channels. It records display bounds, view dimensions and parallax in tank.json, reserves the union of rendered silhouettes in occupancy.json, and builds a connected graph plus its precomputed next-hop table. Contact shadows and a hazy, finely textured far floor ground the islands. The original defined foreground sand photo remains, with the same restrained wave-linked lighting. `waves.py` retains the shared eight-second surface/sand phase and 32 frames. No dapple asset is used.

## Fish

`fish_mesh.py` renders all 64 directions directly with positive upright geometry, four body bends and five independently hinged fin poses. There is no runtime mirror/negative-scale dependency. Direction, tail and fin states blend at display time rather than snapping. Body canvases retain 224×196 or 208×182 registration and 4× supersampling. Fin crops are stored at half resolution with explicit 2× display scale and fractional anchors; body detail is unchanged in resolution.

`optimize.py` uses 88-color large-fish body palettes, 80-color small-fish palettes and 64-color fin palettes without dithering, stored in lossless WebP containers. The coral atlases use quality 69; water plates quality 74. `catalog.py` records image dimensions/checksums and `build.py` checks texture/frame bounds and the four-million-byte ZIP budget. Raw fish atlases remain cached under ignored work/fish-raw. Regenerate from source pixels instead of repeatedly quantizing delivered output.

## Preview and editing

```sh
node tests/roku_runner.cjs --root roku roku/source/math.brs roku/source/camera.brs roku/source/settings-model.brs roku/source/aquarium.brs roku/source/fish.brs roku/source/schooling.brs roku/source/effects.brs tests/export_preview.brs > work/frames.log
python tools/preview.py
python -m http.server 8000
```

Create `work/` first. The export records the production brain, not a separate fish simulator. The preview reads current layer and wave metadata, so cropped registration matches the native renderer. Open `http://localhost:8000/docs/preview.html` for lighting/seek/play inspection. It does not establish Roku GPU output.

Optional Blender editing:

```sh
blender --background --python tools/blender_render.py -- --species yellow_tang --output work/blender
```

The exporter reads the same NPZ rig and photo textures, supports fin poses 0–8, and saves an editable blend. These remain inspection/replacement renders; the production atlas build uses ModernGL. The meshes are silhouette-derived textured volumes rather than anatomical scans.
