# Deep Reef 1.0.4 — verification results

Default scene: saturated Sunset, Slow camera, Medium fish density. The dapple layer is removed; rolling surface waves and moving sand caustics share one water-height cycle.

| Check | Result |
|---|---|
| Native source/settings compiler | PASS, BrighterScript 0.73.8 |
| Package, artwork and Git tracking | PASS, 24 Python tests |
| Production simulation/timing | PASS, 32 checks with Roku single-cursor semantics |
| Every fish advances | PASS, every body/fin phase advances at Low/Medium/High density |
| Full-fish coral avoidance | PASS, safe spawns, swept crossing, tail contact, and clear simulation/interpolated poses over 30 seconds with 18 fish |
| Settings | PASS, HD/FHD layout, labels/values, navigation, Back/Done and Restore Defaults |
| Display smoothness | PASS, intermediate-frame bubble/effect timing and clean recycle behavior |
| Wave synchronization | PASS, common 32-frame/eight-second phase and continuous loop |
| Presentation scheduling | PASS, 180 native-paced 60Hz and 120 capped 30Hz presents with simulated CPU/GPU work and blocking vsync; late-frame recovery |
| Browser preview | PASS, 601 production-world snapshots, 25 images, four lighting modes, play/pause/seek, no page errors |
| Real Roku performance | Not measured; no device configured |

The 60 fps path uses the double-buffered swap for pacing without an extra sleep. Performance uses 30 fps with a pre-swap wait. Auto locks to 30 fps after sustained output below 45 fps. These are implemented targets and host-checked scheduling rules, not measured device output.

Fish have 32 yaw views, eight tail bends and nine separate pectoral-fin strokes per yaw. Offline rasterization uses 4× supersampling. Avoidance pressure and turn-speed reductions ramp gradually. Bubbles/particles interpolate previous/current positions, while surface waves, coral and lighting use the continuous display clock.

`tools/waves.py` derives surface and sand animations from the same periodic height field. A floor mask keeps highlights on sand and the draw order keeps foreground fish above them. Static photo highlights are inpainted using neighboring sand and preserved grain. No dapple atlas, scene metadata or runtime draw remains; package tests check their absence.

Calculated texture storage: 50.8 MiB body atlases, 10.9 MiB fin atlases, 97.4 MiB active Sunset textures, approximately 113.3 MiB including FHD double buffers (104.5 MiB with HD buffers), before interpreter/driver overhead. These are dimension-based estimates. Fish use 128-color alpha-preserving palettes in lossless WebP containers; photographic backgrounds use WebP. No texture loading occurs in the frame loop.

The extended movement-code run covered 3,600 simulated seconds with six fish and 72 effect slots, with zero tank-boundary violations. Observed X: 106.47–1940.52, Z: 0.05487–0.96908. The final sand-mask revision is additionally covered by the separate current-source collision and package gates.

Current logs: `compiler-results.txt`, `package-results.txt`, `simulation-results.txt`, `movement-regression-results.txt`, `settings-results.txt`, `collision-results.txt`, `wave-smoothness-results.txt`, `soak-results.txt`, `browser-results.json`. Earlier Blender/surface/pectoral examples are historical offline fixtures.

Hardware checks still required: native image output, sustained FPS, graphics-memory usage, menu rendering and remote behavior, repeated activation and registry persistence. Desktop previews and interpreter timings do not establish Roku GPU behavior.

Tracked install ZIP: **3,948,464 bytes**. SHA-256: `ced4b73a57ea8d468607905b5bbacf10f4c8516d6f8934106829e26b7e541eee`.
