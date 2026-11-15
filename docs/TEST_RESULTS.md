# Deep Reef 1.0.10 — targeted verification

Fish bodies use 104 adaptive heading slots from 53 true upright mesh renders. Angular spacing improves from 5.625° to 1.40625° near head-on views and 0.703125° immediately around the forward/rear axis. Continuous silhouette widths and one body/tail/pectoral image per fish remain; no anatomy crossfades or runtime reflections are introduced.

Fish separation now predicts encounters using body/tail/fin envelopes, maximum pitch, actual species sizes and depth. Stable passing lanes and gradual braking avoid symmetric head-on traps. Safe spawning and continuous swept-cylinder guards prevent contact between physics samples. All poses are saved before stepping any fish, so collision tests and displayed interpolation share one time interval.

The existing 3D marine renders bend with a continuous, two-frequency current field. Thin immutable bands retain texture detail; branch/tentacle motion increases away from the pinned roots. Shared vertical boundaries remain within 0.0001px in host tests. Performance mode uses coarser bands. Occupancy reserves the entire tip excursion.

| Check | Result |
|---|---|
| Native/settings compiler | PASS, BrighterScript 0.73.8 |
| Package/artwork/tracking | PASS, 33 Python tests |
| Adaptive head-on angles | PASS, real mesh renders, bounds and continuous widths at every nonuniform boundary |
| Head-on raster comparison | PASS, peak frame changes 35–57% lower than the 64-angle subset, using single-pose draws in both cases |
| Fish spawning | PASS, 10 differently sized fish across four seeds, no overlapping envelopes |
| Fish traffic | PASS, head-on/depth/overtaking/crossing encounters; 360 ticks each, five displayed samples per tick, no contact or deadlock |
| Tunneling prevention | PASS, continuous swept collision detects passage through another body |
| Marine motion | PASS, roots fixed; maximum tested 60Hz displacement under 0.06px per frame |
| Native draw ordering | PASS, animated marine bands interleave with fish; one opaque body/tail/pectoral part each |
| Upright turning | PASS, full-circle pitched draws retain positive scales |
| Every-fish animation | PASS at Low/Medium/High with native shared-cursor semantics |
| Coral clearance | PASS, 60 targeted physics ticks with physical/interpolated footprints clear |
| Settings/waves/pacing | PASS, readable settings and Back/Done, synchronized waves and simulated frame pacing |
| Pan geometry | PASS, maximum centroid error 0.001959px in the tested segment |
| Browser inspection | PASS, lighting/play/pause/seek and all 48 runtime images, no page errors |
| Extended soaks | Not run; short validation requested |
| Actual Roku GPU/FPS | Not measured |

The refreshed navigation graph has 251 nodes and 544 bidirectional edges. Estimated active Sunset image textures occupy 66.19 MiB at the default density and 73.61 MiB at High. Marine bands share existing bitmaps and add no image textures. Add 8.44 MiB for the scene canvas and 15.82 MiB for FHD double buffers (6.25 MiB at HD), before driver/interpreter overhead. These are dimension-based estimates.

The tracked ZIP remains below 4,000,000 bytes. Exact package bytes and SHA-256 are in dist/build-report.json. Current evidence includes compiler, movement, fish-traffic, marine-motion, collision, settings, waves, render-depth, upright, turns, raster, pan and browser logs. Earlier extended-soak reports are historical.
