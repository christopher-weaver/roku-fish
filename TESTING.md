# Verification

Run all local gates after building:

```sh
npm install
python -m pip install -r tools/requirements.txt
python tools/build.py
python tools/test.py
python tools/test.py --soak
```

`BSC_BIN` and `BRS_BIN` can point to existing tool binaries instead of a project-local npm installation.

## Automated coverage

- BrighterScript 0.73.8 parses and validates all runtime source and both SceneGraph component scripts. The release contains no `Main()` or `RunUserInterface()`.
- Twenty-six Python checks validate the manifest, actual ZIP root/integrity/budget, six species, 32-yaw × eight-pose body atlases and independent nine-pose fin atlases, asset dimensions/checksums, real alpha masks, offline runtime, shipped license notices, rejected malformed manifest and refusal to deploy without connection details.
- Thirty-two direct BrightScript checks execute the actual production functions for defaults, invalid settings, registry serialization roundtrip, populations, seeded initialization and full-simulation determinism, speed/acceleration/turn limits, tank boundaries, timestep cap, perspective, reef occupancy, camera bounds, smooth local-time lighting, adaptive quality, fixed pools, boids cohesion/alignment/separation, blocked rock-plane crossing daily timer rollover, smooth camera reversal, surface-loop continuity, larger bubbles, fixed-step frame jitter, display interpolation and independent fin phase.
- The off-device `brs` interpreter does not implement the real device registry. `tests/registry-stub.brs` supplies the platform Read/Write/Exists/Flush interface. The production serialization, validation and persistence call sequence are retained. This does **not** verify storage survival across Roku restarts.
- `tests/soak.brs` advances **one simulated hour**, 36,000 capped 100 ms steps, with six principal fish using unchanged production movement functions and 72 effect slots. It checks every fish against tank boundaries at every step and verifies bounded final populations. This does **not** measure device FPS or resident memory.

Delivered logs: `docs/compiler-results.txt`, `docs/package-results.txt`, `docs/simulation-results.txt`, `docs/soak-results.txt`, `docs/browser-results.json`, `docs/blender-smoke-results.txt`. The final consolidated results are in `docs/TEST_RESULTS.md`.

## Visual workflow

`tests/export.brs` exports world state from the native brain, including a High-density fixture and 601 snapshots at 10 Hz. `tools/preview.py` composites real runtime images and atlas cells using that state. A separate movement implementation is not used. The browser preview interpolates the exported recording for smooth inspection; the actual Roku runs indefinitely with autonomous state.

Delivered examples under `docs/previews/`:

- `sunset.png`: default pink/orange/red aquarium from an unmodified 20-second native simulation snapshot.
- `daylight.png`, `dusk.png`, `moonlight.png`.
- `low-density.png`, `high-density.png` (the latter from a real 24-fish initialization).
- `occlusion-behind.png`, `occlusion-front.png`: deliberately placed same-species depth fixtures.
- `three-quarter.png`: a deliberately placed close fish using a real mesh-rendered oblique frame.
- `fish-orientations.jpg`: six species, side, oblique, head-on and rear views.
- `time-00.jpg`, `time-12.jpg`, `time-40.jpg`, `time-60.jpg`: independent movement and chromis grouping.

Review criteria include layer registration, texture quality after compression, continuous camera coverage, front/behind masking, fish volume, edge transparency, moderate bubbles, subtle coral motion and the requested sunset palette. `pectoral-motion.gif` shows an enlarged fin stroke; `surface-0.png` and `surface-3.png` inspect wavelet changes. The browser gate checks actual loading, lighting selection, seeking, pause/resume and page errors in Chromium and captures the canvas. Python/PIL preview pixels and Roku GPU pixels are not assumed to be identical.

The optional Blender pipeline is exercised with one rendered view using `--limit 1`; it is not a performance claim for the default ModernGL asset generator.

## Hardware still required

No Roku IP or development password was supplied/configured, so no deployment was attempted. Screensaver registration, idle activation, system dismissal, native GPU draw output, sustained 60/30 FPS, memory trend, settings survival across power cycles and repeated activations remain unverified. Follow INSTALL and PERFORMANCE for the TV test procedure; do not treat the local logs or source-project device claims as results for this build.

## GitHub package tracking

Four additional host tests exercise the release guard against a temporary Git repository: a fresh tracked ZIP passes, stale bytes fail and are rebuilt, an untracked ZIP fails, and a Git LFS pointer fails. The current suite has 26 Python tests, including these four release guards and the new fin, slim-body and surface/bubble checks. The GitHub workflow runs the release guard and these four tracking tests on pushes and pull requests.

## Roku enumeration regression

The original host interpreter used independent JavaScript iterators and missed the hardware bug: `ReefStep` enumerated the fish array while its neighbor scan enumerated the same array. Native Roku stores one `ifEnum` cursor per object, so the inner scan exhausted the outer loop after fish zero. `tests/roku_runner.cjs` now adapts the host FOR EACH implementation to that documented single-cursor behavior without replacing the fish logic. The before-fix fixture advanced 1/18 fish; the fixed indexed loops advance 18/18. The regression also checks every body and pectoral phase for 30 frames at Low, Medium and High densities. All production BrightScript checks and the one-hour soak now run through this adapter. It emulates the relevant enumeration rule, not the entire Roku OS or GPU.

## Coral, settings and pacing regressions

`tests/reef_collision.brs` checks safe full-body spawns, thin partial cells, swept depth tunneling, tail contact with a clear center, and 30 simulated seconds of 18 fish at 30Hz. Both physics and interpolated display poses must stay clear of coral without position jumps. It also exercises the 60Hz target and persistent 30Hz fallback.

`tests/settings_ui.brs` runs the production settings initialization and key handler with node/registry adapters: HD/FHD layouts scale correctly; all 11 labels and 9 values populate; arrows edit settings; Done and Back request closure; key releases do not; Restore Defaults keeps the menu open. XML checks require system fonts on every row and the highlight before the row group. These host checks do not render Roku SceneGraph or establish real remote/device behavior. See `docs/settings-results.txt` and `docs/collision-results.txt`.

## Synchronized waves and smooth presentation

`tests/waves_smoothness.brs` verifies intermediate-frame bubble/display-clock movement, bubble interpolation and recycle handling, a continuous shared surface/sand phase, 180 evenly spaced 60Hz presents and 120 capped 30Hz presents with simulated CPU/GPU work and blocking vsync, stall recovery, and denser animation data for every species. Python checks verify removal of dapple assets, temporal variation in both wave atlases, confinement of floor highlights, and the wait-before-swap order. This verifies scheduling logic, not actual Roku GPU timing. See `docs/wave-smoothness-results.txt`.

The current 1.0.4 results are in `docs/TEST_RESULTS.md`. Earlier standalone surface/pectoral GIF fixtures remain historical examples; the current preview and orientation sheet use the new assets.

## Close reef / fractional pan release

The current scene uses the reference-inspired full-width coral, 60% larger fish and higher-resolution portraits. Python checks validate central reef coverage, cropped layer registration, increased fish detail, preserved sand-grain energy and a restrained floor-light alpha. The GPU probe's pixel classifier is tested with normal and flipped/channel-varied readback and must reject integer-only placement. The float32 placement gate runs at HD and FHD, including the existing camera's fastest part.

Run `python tools/test.py --scene-soak` for a ten-minute, six-principal-fish check with the shipped close-reef masks; both tank-boundary violations and coral intersections must remain zero. The one-hour `--soak` option is still available. Current results and hardware limits are in `docs/TEST_RESULTS.md`. Actual pan smoothness/FPS on the user's Roku remains a hardware check.
