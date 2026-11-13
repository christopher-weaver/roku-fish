# Reproducible artwork pipeline

All required runtime art and every source image used by this build are included. Rebuilding requires no generation service, paid API, model weights, asset-store account or runtime network access.

```sh
python -m venv .venv
# Activate .venv using the normal command for your shell.
python -m pip install -r tools/requirements.txt
python tools/generate_assets.py
python tools/build.py
```

The primary headless renderer uses ModernGL/EGL with Mesa on Linux. `LIBGL_ALWAYS_SOFTWARE=1` is supported. EGL availability is an offline authoring requirement only. On Windows/macOS, use a supported EGL/OpenGL environment, run the pipeline in Linux, or edit/render the checked-in meshes in Blender using the optional exporter below. The finished Roku package needs none of these libraries.

## Inputs and provenance

- `assets/source/reef-original.png`: original generated reef photograph, created for this project with the available image-generation tool. Prompt and provenance are in `assets/source/PROVENANCE.md`.
- `empty-original.png`: matching empty aquarium plate retained for future layering edits. The final scene deliberately retains the full rear reef photograph for visual cohesion.
- Six photographic fish refinements derived from Paul Robello's MIT-licensed `roku-fishtank` portraits. `fish-studies.png` retains the original six-species reference sheet; `fish-photographic-sheet.png` retains the generated refinement. `tools/split_fish.py` reproduces the six cropped sources. Original notices, upstream provenance, the refinement prompt and revision are retained.
- `*-texture.png` and `*.npz`: normalized textures and generated 3D mesh arrays. NPZ contains vertices, UV coordinates and triangle faces.

The fish refinement uses the same licensed species profiles with more photographic textures and smaller eyes. The original generation service is not needed to reproduce the delivered images: the source pixels are checked in. Generating a new reef with the same prompt is not claimed to be byte-deterministic.

## Stages

`tools/art.py` resamples the reef to the registered 2048×1152 plate, applies the sunset color transform, extracts two alpha occlusion surfaces with hand-reviewed silhouette envelopes and water rejection, creates occupancy cells, and builds three scan-line-deformed soft-coral frames. It generates eight caustic tiles, ray/particle/bubble sprites and manifest art. It preserves matching source pixel coordinates so the layers align.

`tools/fish_mesh.py` normalizes each fish's alpha portrait, constructs front and back volume surfaces using a smoothed distance-field thickness and stitches the silhouette rim. Fins remain thinner than the body. UV coordinates project the detailed licensed portrait onto both flanks. The mesh rotates through **16 distinct full-circle yaw angles** and bends through **three swimming poses**. Every frame is rasterized in 3D with depth testing; no runtime image squash substitutes for turning. The resulting atlases are 1536×1008, with 192×168 registered cells. `species.json` records each frame's position, orientation and pose. A six-species orientation contact sheet is generated for review.

These are silhouette-derived volume models, with simpler head anatomy than a sculpted or scanned fish. This is a material fidelity compromise. The source models and pipeline are included so better anatomical meshes can replace them. The species interface and runtime need not change when atlases are replaced.

`tools/optimize.py` uses libimagequant for alpha-preserving, dithered palette PNGs and recompresses JPEG plates/splash art. `tools/catalog.py` records exact dimensions and SHA-256 checksums. `tools/build.py` rejects missing or modified catalog files, out-of-range atlas frames, oversized textures and ZIPs over the conservative four-million-byte package budget.

For a source change, rerun **generate_assets.py**, not optimize.py repeatedly over already quantized PNGs. Intermediate rendering and palette compression may vary slightly across graphics drivers or library versions; checksums describe the delivered bytes, not a cross-platform bit-exact rendering guarantee.

## Blender editing / rendering

With Blender available:

```sh
blender --background --python tools/blender_render.py -- --species yellow_tang --output work/blender
```

The script loads the same NPZ mesh and normalized photo texture, renders 48 transparent views, and saves an editable `.blend`. These optional Blender renders are inspection/replacement outputs; the default atlas build uses the ModernGL rasterizer. To replace a model, preserve the frame center and nominal length, render the same yaw/pose grid, pack it to the species atlas and update the frame metadata and asset catalog. Review the contact sheet before packaging.

## Preview exports

After installing Node development dependencies:

```sh
npx brs --root roku roku/source/math.brs roku/source/camera.brs roku/source/settings-model.brs roku/source/aquarium.brs roku/source/fish.brs roku/source/schooling.brs roku/source/effects.brs tests/export.brs > work/frames.log
python tools/preview.py
```

Create `work/` first if necessary. The exporter runs the actual production movement rules, emits a high-density fixture plus 61 deterministic timeline snapshots, and the Python utility composites those states with runtime assets. It writes Sunset/Daylight/Dusk/Moonlight, low/high density, front/behind occlusion and close three-quarter samples. The browser inspection recording uses the same exports. Screenshot fixtures explicitly marked occlusion/three-quarter place fish for inspection; the default sunset image uses an unmodified production snapshot.
