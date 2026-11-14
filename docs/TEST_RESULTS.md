# Deep Reef 1.0.7 — targeted verification

Upside-down turns are addressed by baking all 64 directions upright and using positive scales. Direction, tail and fin articulation blend continuously. The pan now presents an opaque overscan canvas at adjacent integer pixels with a fractional alpha weight, replacing the large-anchor scale adjustment. The reef is six sparse islands with three actual offline relief-mesh views each, stronger depth parallax, open channels and contact shadows.

| Check | Result |
|---|---|
| Native/settings compilation | PASS, BrighterScript 0.73.8 |
| Package, artwork and tracking | PASS, 29 Python tests |
| Every-fish regression | PASS, body/pectoral phases at all three densities with native shared-cursor semantics |
| Targeted coral collision | PASS, 60 physics ticks, 18 fish, full physical/interpolated footprints clear |
| Turn continuity | PASS, bounded speed/acceleration/jerk, cubic endpoint velocities and continuous view widths |
| Upright draw calls | PASS, full-circle pitched fish always use positive scales |
| Production pan calls | PASS, opaque base and adjacent offsets at HD/FHD |
| Pan geometry | PASS, maximum centroid error 0.001959px and 60Hz increment 0.027451px in tested segment |
| Render ordering | PASS, rear/middle/front fish interleave with six islands; interpolated body/fin views |
| Settings and wave timing | PASS, existing settings closure/labels and simulated 60/30Hz pacing |
| Browser preview | PASS, 26 images, lighting/play/pause/seek, no page errors |
| Extended simulations/soaks | Not run; user requested short validation |
| Actual Roku GPU/FPS | Not measured |

The body textures occupy approximately 61.84 MiB and fins 4.23 MiB decoded RGBA. Active Sunset textures total 93.87 MiB. The 2048×1080 opaque canvas adds 8.44 MiB; FHD double buffers bring the estimate to 118.13 MiB, HD to 109.34 MiB, before driver/interpreter overhead. These estimates are not measured device residency. Fin crop scaling and explicit fractional anchors preserve hinge placement while reducing their decoded storage by about 70%.

Per-destination BFS is replaced by an offline 296-node/668-edge next-hop graph. Waypoint visibility runs at 5Hz. Reused projection/probe/candidate/display objects and pre-bucketed effect depths reduce frame-loop allocations and repeated work. These changes target stalls but do not establish achieved Roku FPS.

The current preview is a short recording of production-world snapshots near the fastest camera phase. It uses the current sparse coral renders and upright/interpolated fish. Previous long-simulation/raster comparison logs are historical and were not rerun for this build.

ZIP: 3,570,635 bytes. SHA-256: `4f829b2afd2c22690f07563e6d7a4741293b101134238740789d770304e2c560`. The tracked installation ZIP matches the runtime source. Check on the user's Roku: upright turning, continuous pan, startup canvas allocation, sustained FPS/memory and normal settings/activation behavior.
