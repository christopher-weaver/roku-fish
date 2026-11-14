# Deep Reef 1.0.2 — verification results

Default scene: saturated pink/orange/red Sunset, Slow camera sweep, Medium fish density.

| Check | Result |
|---|---|
| Native source / settings compilation | PASS, BrighterScript 0.73.8, no diagnostics |
| Python package, asset and Git tracking tests | PASS, 19 tests |
| Production BrightScript behavior / timing tests | PASS, 32 checks with Roku single-cursor semantics |
| Reported one-fish bug | Reproduced before the fix: 1/18 fish updated. Fixed indexed loops: 18/18 update and animate |
| Population regression | Every body and pectoral phase advances for 30 frames at Low / Medium / High density |
| Extended simulation | PASS, 3,600 simulated seconds, 36,000 steps, six principal fish, 72 effect slots, zero boundary violations |
| Browser preview | PASS, no page errors; 601 snapshots at 10 Hz; all 18 body/fin animations advance; 32 preview textures load; four lighting modes and controls work |
| Offline Blender pipeline | PASS, one slim fish view with articulated fins and editable scene |
| Sideload ZIP | PASS, root manifest, valid entries, all assets and atlas bounds, under 4,000,000 bytes |
| Actual Roku device | Not tested in this environment |

ZIP: **3,779,298 bytes**.

SHA-256: `44f7782d1c98d37a16b176270611e8deea81455ee98083c1c5ec9905ff04f4ec`.

All **38 images** validate. Each species now uses 20 real yaw views, four body/tail poses and five separately timed pectoral poses per yaw. Cropped sprites carry anchors, and fin textures are tested to exclude the full body. Fish bodies are 8% shorter vertically and 20% thinner in depth than 1.0.1.

The new surface atlas loops without a seam, bubbles are approximately 13–28 logical pixels instead of 5–12, and the default camera goes left → right → left over 240 seconds with zero velocity at each reversal. Tests cover fixed-step accumulation with jittery render intervals, bounded catch-up and previous/current pose interpolation. Region filtering is smooth outside Performance mode.

The one-hour soak observed X 136.09–1885.79 and Z 0.05852–0.96111. Fish/effect populations remained bounded. This tests production simulation through a host compatibility adapter, not Roku GPU memory or frame rate. The earlier interpreter's independent JavaScript cursors missed the native enumeration bug; all current BrightScript checks explicitly emulate Roku's shared cursor.

Calculated active Sunset texture storage is approximately 51.4 MiB RGBA, or 67.2 MiB including FHD double buffers before interpreter/driver overhead. Cropping saves memory despite adding independent fins. These are estimates from image dimensions, not measured device memory.

Visual review includes the saturated default aquarium, front/behind coral masking, side/oblique body and fin strokes, surface comparisons and larger bubbles. The browser uses actual exported native-world snapshots at 10 Hz to avoid aliasing tail and fin rhythms. The pectoral GIF and deliberately placed close-up fixtures are inspection aids, not runtime video.

Retained logs: `compiler-results.txt`, `package-results.txt`, `simulation-results.txt`, `movement-regression-results.txt`, `soak-results.txt`, `browser-results.json`, `blender-smoke-results.txt`.

Remaining device checks: install/registration on the user's Roku, native GPU output, actual FPS, hardware memory trend, remote dismissal, repeated activation and power-cycle persistence. Saved preferences remain in place; choose Camera → Slow or Bubble density → Low/Medium if those settings were previously Off.
