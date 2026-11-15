# Deep Reef

**[Download the ready-to-install Roku ZIP](https://github.com/christopher-weaver/roku-fish/raw/refs/heads/main/dist/deep-reef-screensaver.zip)** · [Step-by-step installation](INSTALL.md)

A connected, reference-aligned coral aquarium with larger fish, a shared rock foundation and sharp sand ridges. This is a self-contained native Roku aquarium screensaver with a pink, orange and red **Sunset** default, ten marine species, autonomous three-dimensional movement and layered coral occlusion. It has no runtime network dependency, video playback, ordinary channel entry point, or Home-screen launch flow.

**Install:** upload `dist/deep-reef-screensaver.zip` to the Roku Developer Application Installer, then choose **Settings → Theme → Screensavers → Deep Reef → Set as screensaver**. Some firmware labels sideloaded screensavers **dev**. See [INSTALL.md](INSTALL.md).

![Default sunset aquarium](docs/previews/sunset.png)

The aquarium includes ocellaris clownfish, yellow tang, royal gramma, emperor angelfish, Moorish idol, blue-green chromis, regal blue tang, copperband butterflyfish, Banggai cardinalfish and mandarin dragonet. Medium now displays eight fish instead of eighteen. Each activation shuffles a unique-species roster. Higher-resolution fish canvases, denser meshes, rounded body contours, thin fin edges and normal-based shading improve the models. Fish body turns use 112 adaptive heading slots from 57 upright renders, with four to eight times finer spacing near head-on views. Tails and fins retain their independent 64-slot rigs; bilateral views share pixels without runtime reflection. The body mesh excludes the independently animated caudal tail, so only one tail is visible; pectoral fins also move independently. There are no anatomy crossfades.

Variable wave-shaped shadows sweep over the existing sand highlights. Their shape, width and strength change with the same cycle that drives the water surface. Coral masks keep these floor shadows off the reef, and the photographed sand ridges remain visible.

The reef follows the supplied reference: touching bases on a nearly common line, a green cup at the left, a white crown over the center-left cave, tall antlers to the right, and smaller corals/clams along the foundation. The sea fan and anemone use closed, photo-textured 3D volumes with 65 complete mesh-deformation poses each, following the fish volume/atlas approach. Only one rendered view appears at a time. Their source meshes and the original Blender geometry are included. Each marine object draws as one coherent image. Runtime strip warps and camera-view snapping are removed; no pose crossfades are used.

The water/sand backgrounds were recreated after fixing the reef layout, with matching lighting, grain and contact shadows. The fixed reef textures draw at native design resolution. Extra layer resampling, coral-view blending and fish-pose crossfades are removed. Panning retains one final neighboring-pixel interpolation; exact 1:1 draws use DrawObject. Auto/High target 60 fps with an Auto 30 fps fallback; Performance targets 720p/30 fps. Actual Roku output still requires device checking.

The settings menu uses readable system fonts, a translucent highlight behind the text, and explicit Back/Done closure. Settings persist in the Roku registry: lighting (Sunset, Daylight, Dusk, Moonlight, Automatic), 6/8/10-fish populations, camera Off/Subtle/Slow, bubbles, particles, movement, quality, clock, FPS, and Restore Defaults. Clock and FPS default off. Camera movement defaults to Slow, sweeping left to right and back over three minutes. Existing saved settings are retained; choose Camera movement → Slow to enable the widest sweep. Automatic uses the device's local time. All interaction belongs to the separate settings entry point.

## Build

The included runtime artwork is ready to use. Packaging requires **Python 3.10+ only**, with no image libraries or network access:

```sh
python tools/build.py
```

For a new release version:

```sh
python tools/build.py --increment
```

Optional deployment, after setting `ROKU_IP` and `ROKU_DEV_PASSWORD` in your shell:

```sh
python tools/deploy.py
```

The helper does not read `.env` automatically. `.env.example` documents the variable names; never commit actual credentials. Deployment replaces the device's single developer app. It was not attempted in this session because no Roku connection details were configured.

## Develop and verify

```sh
npm install
python -m pip install -r tools/requirements.txt
python tools/test.py --quick
```

`tools/test.py` compiles the native sources, runs package/asset checks, and executes production BrightScript simulation tests. The optional soak runs one simulated hour with six principal fish; it is a host test, not a Roku performance test. Device storage is represented by a small registry adapter in the host interpreter.

Regenerate the bundled artwork offline from checked-in sources:

```sh
python tools/generate_assets.py
python tools/build.py
```

Linux headless mesh rendering uses Mesa/EGL. See [ASSET_PIPELINE.md](ASSET_PIPELINE.md) for Windows/macOS alternatives and the optional Blender renderer.

For the interactive visual inspection recording:

```sh
python -m http.server 8000
```

Open `http://localhost:8000/docs/preview.html`. It displays snapshots exported from the real BrightScript brain, interpolated for inspection. The Roku ZIP contains no browser or server.

See [ARCHITECTURE.md](ARCHITECTURE.md), [PERFORMANCE.md](PERFORMANCE.md), [TESTING.md](TESTING.md) and [CREDITS.md](CREDITS.md).

**Validation boundary:** local compilation, direct simulation, asset checks, preview inspection and ZIP integrity are covered. Roku registration, actual GPU output, sustained 60/30 FPS, memory consumption, remote dismissal and reboot persistence require testing on a real device. The fish meshes are silhouette-derived textured volumes; a future artist can replace them with sculpted anatomical models using the supplied atlas interface. Camera travel deliberately uses 128 pixels of overscan instead of a stretched two-screen panorama.

## Keep the install ZIP on GitHub

`dist/deep-reef-screensaver.zip` is deliberately committed as a regular Git binary. It is available directly from this repository; it is not a Git LFS pointer or an expiring workflow artifact.

Whenever Roku sources or packaging change, rebuild and commit the release files with the source:

```sh
python tools/build.py
git add roku tools dist/deep-reef-screensaver.zip dist/build-report.json
python tools/check_release.py
git commit -m "Update aquarium and sideload package"
git push
```

For a new release version, use `python tools/build.py --increment` instead. The **Verify sideload ZIP** GitHub Actions workflow checks every push and pull request for a missing or stale package. `AGENTS.md` records the same requirement for future coding sessions.

## Version 1.0.2

Fixes the Roku shared-array iterator issue that advanced only the first fish. All 12/18/24 fish now update independently. Adds smoother swimming, moving pectoral fins, slimmer fish, larger bubbles, animated surface ripples, a wider slow camera sweep and more saturated reef colors. The host tests now emulate Roku’s single enumeration cursor so this device-specific regression cannot silently pass the JavaScript interpreter again.

## Version 1.0.3

Fixes invisible settings rows, fits the full menu on both 720p and 1080p screens, and repairs Back/Done exit handling. Prevents body, tail and fin clipping using fine per-layer coral masks, swept full-fish collision checks and early avoidance. Adds moving dappled sunlight on reef and sand, a 60 fps render target with stable automatic fallback, denser yaw/tail/fin poses, finer meshes and 3× supersampling. The tracked ZIP is rebuilt with every runtime change. Reef alpha plates use WebP with lossless alpha, supported since [Roku OS 9.4](https://developer.roku.com/dev/docs/media); this project targets modern Roku OS 16 devices.

## Version 1.0.4

Removes dappled reef lighting. A shared eight-second water-height cycle drives 32 rolling surface-wave frames and their moving sand caustics. Frozen caustic lines are softened out of the source sand photograph. Fish now have 32 yaw views, eight tail bends and nine pectoral-fin poses per yaw, rendered with 4× supersampling. Bubbles, surface waves, coral and light effects update on the interpolated display clock, and frame waiting occurs before the buffer swap. Avoidance and turn-speed changes ramp gradually. Native settings and full-fish coral collision handling are retained.

## Version 1.0.5

Keeps the existing pan rate and four-minute Slow cycle, but places scenery fractionally instead of rounding its travel to whole pixels. A startup pixel-readback check chooses a working floating-point drawing path and retains a safe fallback on unsupported hardware. The scene is rebuilt around the user's fuller, closer reef reference, with coral across the center and 60% larger fish. Higher-resolution fish textures retain 32 yaw views, eight tail bends and nine independent fin poses. Sand grain and defined ridges remain photographic; only a restrained light modulation changes with the waves. The rebuilt ZIP remains tracked and directly downloadable.


## Version 1.0.6

Replaces the two broad reef planes with eight independent mid-ground formations, a clean transparent reef source and clearance-validated routes through open water. Fish explore both sides of the reef rather than only repelling upward. Turning now uses 64 views with width-matched view blending, gentler angular acceleration and jerk, continuous display heading velocity, and GPU-probed fractional placement while pitched. Bilateral view reuse keeps decoded texture memory close to the previous release. The updated installation ZIP remains tracked on GitHub.

## Version 1.0.7

Fixes upside-down turns by replacing runtime reflections with 64 actual upright views. Body and pectoral poses now blend too. Replaces the large-anchor camera transform with adjacent-pixel blending of an opaque scene canvas, reduces frame-loop allocation/pathfinding work, and rebuilds the reef as six sparse islands with three rendered relief views each. The updated ZIP remains committed and directly downloadable.

## Version 1.0.8

Removes ghost-producing fish pose overlays and extra filtering. Rebuilds the reef as a touching, reference-aligned foundation rather than separate islands. Adds fish-style textured 3D fan/anemone volumes with seven sharp views each, and recreates the backgrounds around the fixed layout. The rebuilt ZIP remains tracked on GitHub.

## Version 1.0.9

Reduces density to 6/8/10 fish, adds four species (ten total), and shuffles a unique-species roster per activation. Improves fish volume contours, mesh density, render resolution and color detail, with a separate non-overlapping caudal-tail rig. Adds variable surface-wave shadows over the sand highlights. Loads only the species actually present. The refreshed installation ZIP remains tracked on GitHub.

## Version 1.0.10

Adds adaptive rendered body angles for smoother turns toward/away from the viewer: 1.40625° near head-on, and 0.703125° directly head-on, versus the previous 5.625°. Predictive, size-aware fish separation uses passing lanes, gradual braking, safe spawn placement and swept body/tail/fin envelopes that include pitch. Both marine objects now bend continuously with the display clock, with pinned roots and extra collision clearance for moving tips. The refreshed ZIP remains tracked on GitHub.

## Version 1.0.11

Refines fish turns to 112 heading slots and makes swimming predominantly lateral, with home-depth routes and side-facing hover poses. Replaces the seam-prone marine strip renderer with 65 complete, root-pinned 3D mesh poses per object. Adds a slightly goofy moray peeking from the real lower tunnel, with slow eased emergence, retreat and pauses. Speeds Slow panning from four minutes to three and adds a soft, animated cellular wave-net shadow over the entire scene. The updated ZIP remains tracked on GitHub.
