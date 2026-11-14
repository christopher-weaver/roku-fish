# Deep Reef 1.0.3 — verification results

Default scene: saturated pink/orange/red Sunset, Slow camera sweep, Medium fish density.

| Check | Result |
|---|---|
| Native source / settings compilation | PASS, BrighterScript 0.73.8, no diagnostics |
| Python package, asset and Git tracking tests | PASS, 22 tests |
| Production BrightScript behavior / timing tests | PASS, 32 checks with Roku single-cursor semantics |
| Population regression | Every body and pectoral phase advances for 30 frames at Low / Medium / High density |
| Coral regression | PASS, safe spawns, thin branches, swept depth crossings, tail-only contact and 30 simulated seconds of 18 fish with clear physics/interpolated footprints and no position jumps |
| Settings regression | PASS, HD/FHD layout scales; all labels/values populate; arrows edit; Back/Done request closure; key releases do not; Restore Defaults keeps the menu open; XML fonts/layer ordering verified |
| Frame pacing | PASS, 60Hz target switches to persistent 30Hz after sustained missed frames |
| Extended simulation | PASS, 3,600 simulated seconds, six fish, 72 effect slots, zero tank-boundary violations |
| Browser preview | PASS, no page errors; 601 snapshots at 10 Hz; all 18 body/fin animations advance; 33 preview textures load; four lighting modes and controls work |
| Sideload ZIP | PASS, tracked ordinary ZIP, root manifest, complete assets, valid atlas bounds, under 4,000,000 bytes; release guard confirms current source |
| Actual Roku device | Not tested in this environment |

ZIP: **3,964,119 bytes**.

SHA-256: `118a4651bf5067f0b18b5ca17738e9cfd15120d7da6faa8840c0ad0931c12f5b`.

All **39 images** validate. Each species has 24 yaw views, six body/tail poses and seven separately timed pectoral poses per yaw. A finer 320-column mesh and 3× supersampling improve silhouette quality. Existing slim body proportions, larger bubbles, surface ripples and four-minute camera sweep are retained.

Coral now has separate 8px occupancy maps for the two depth surfaces, filled small interior alpha holes, and animated soft-coral coverage at the correct plane. Collision checks sweep the projected full fish footprint, include pitch and camera travel, begin avoidance before contact and slide blocked movement along the reef. This is conservative 2.5D handling, not a full reef physics mesh.

Dappled warm sunlight uses twelve looping atlas frames in eight terrain-clipped patches, blending between frames over 24 seconds. Visual checks cover reef/sand lighting, alpha registration, compressed photo plates and fish edges. The browser uses production-world exports; its pixels do not establish Roku GPU output.

The settings scene scales its complete layout to HD/FHD design resolution, declares built-in system fonts in XML and draws its translucent highlight behind the rows. Back/Done set a close-request field, observed and polled by the main thread before explicitly saving and closing the screen. Host node adapters verify text and key behavior, not native SceneGraph rendering or real remote input.

Calculated active Sunset texture storage is approximately **70.2 MiB RGBA**, or **86.0 MiB** including FHD double buffers before interpreter/driver overhead. Only one reef color variant is loaded. These are estimates from image dimensions, not measured residency. Reef cutouts use WebP with lossless alpha; Roku supports WebP from OS 9.4, and this project targets modern OS 16 devices.

The one-hour host run observed X 98.02–1941.52 and Z 0.05143–0.96530. Populations remained bounded. This checks production simulation, not device frame rate or memory.

Retained current-build logs: `compiler-results.txt`, `package-results.txt`, `simulation-results.txt`, `movement-regression-results.txt`, `settings-results.txt`, `collision-results.txt`, `browser-results.json`, `soak-results.txt`. `blender-smoke-results.txt` describes the earlier optional exporter smoke test, not a new hardware result.

Remaining device checks: install/registration, native menu text/Back behavior, GPU output, sustained 60/30 FPS, memory trend, remote dismissal, repeated activation and power-cycle persistence. Saved preferences remain in place after updating.
