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

- `assets/source/reef-connected-reference.png`: active connected RGBA reef; `background-matched-sunset.png` is its newly matched environment.
- `assets/source/marine-renders/`: Blender sources, finished textures, closed-volume NPZ meshes and seven-view metadata.
- `assets/source/reef-close-reference.png`: historical 1672×941 reference-inspired close reef. It preserves the requested sunset palette, full-width coral and defined sand ridges. Provenance and prompt notes are in `assets/source/PROVENANCE.md`.
- `assets/source/reef-midground-cutout.png`: historical generated RGBA isolation retained from version 1.0.6. The exact source pixels are checked in.
- `reef-original.png` and `empty-original.png`: retained historical sources used by earlier releases.
- Six licensed/refined photographic fish portraits and four new generated portraits, plus source sheets. The Paul Robello MIT notices and provenance remain in `assets/licenses/` and CREDITS.
- `*-texture.png`, `*-pectoral.png` and NPZ volumes are derived from those portraits and rebuildable offline.

## Connected reef and matched environment

`reef-connected-reference.png` is a generated RGBA reef based on the user's updated composition reference. `connected_scene.py` registers it to a common foundation and creates complementary mid-ground/foreground masks. These are native-resolution crops, not enlarged 448px island images. Coral color uses WebP quality 88 with preserved alpha. The guide used to recreate the environment is retained as reef-layout-guide-geometry.png.

`background-matched-sunset.png` was generated after fixing object positions, retaining matching water/sand perspective, lighting and contact darkening while removing the reef. Sunset and cooler Daylight runtime plates derive from these pixels. `waves.py` uses the new sand texture and excludes coral footprints from the animated floor-light mask.

## Fish-style 3D marine objects

`render_marine.py`, run with Blender, produces actual curved sea-fan and tentacle geometry and transparent Cycles renders. The original .blend/.png files are retained under marine-renders. An image-tool finishing pass adds natural anatomy and surface detail; its original sheet and extracted RGBA objects are included.

`marine_views.py` turns the finished textures into closed front/back volumes with stitched edges, fan curvature and anemone thickness, following the fish's textured-volume approach. It exports NPZ geometry and seven sharp, depth-tested camera angles from -8 to +8 degrees. Hidden fan pixels behind the fixed reef are cropped before packing. A 128-color, lossless WebP container compacts the view atlas without spatial blur. Metadata records frames, columns, origins, root height and mesh sizes. The runtime chooses one view, never a view crossfade.

`art.py` invokes the connected scene and waves; `generate_assets.py` rebuilds runtime art from checked-in source pixels and meshes without a generation service. To recreate the initial procedural Blender models separately, run `blender --background --python tools/render_marine.py`; the finished material sheet remains a fixed art input.

## Fish

`fish_mesh.py` fills 64 heading slots from 33 upright bilateral views with positive scales. The reverse half reuses matching body/fin views and reverses caudal-bend phase; it never reflects a runtime sprite. Each direction has one body image, four independently bent caudal-tail poses and five hinged pectoral-fin poses. Body and tail face sets partition the complete mesh without duplicating any tail geometry. Tail and pectoral passes are depth-tested against the body. Rounded anatomical cross-sections, thin peripheral fins and vertex-normal lighting replace the older uniformly inflated relief. Source grids are 384 samples wide, canvases are 240×210 or 224×196, and renders use 4× supersampling. Fin crops remain half resolution with explicit 2× scale and fractional anchors. Only species actually present are loaded on Roku.

`extract_additional_fish.py` extracts the four new portraits from the fixed source sheet; it does not require a generation service. `optimize.py` quantizes fresh raw atlases without dithering into lossless WebP. Body palettes use 144 colors, tails 112, fins 80. Coral and backgrounds are unchanged from 1.0.8. `waves.py` adds a 32-frame dark shadow atlas using the same periodic field as the surface and sand light; the photographic highlights and grain remain beneath it. `catalog.py` records dimensions/checksums and `build.py` checks all three fish-part atlases and the four-million-byte ZIP budget. Raw atlases are cached under ignored work/fish-raw; never repeatedly quantize delivered images.

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
