# Deep Reef 1.0.6 — verification results

Fish turning uses 64 views, width-matched view blending, bounded angular acceleration/jerk and cubic heading interpolation. A startup GPU readback probe selects fractional placement for pitched fish. Eight separate mid-ground reef formations use registered collision volumes, individual parallax and a connected 185-node/400-edge navigation graph. The background contains water and photographic sand.

| Check | Result |
|---|---|
| Native/settings compiler | PASS, BrighterScript 0.73.8 |
| Package, artwork and tracking checks | PASS, 28 Python tests |
| Production behavior/timing | PASS, 32 checks, including a rerun after arrival/hover adjustments |
| Fish animation | PASS, every fish/body/fin phase at Low/Medium/High density |
| Coral collision | PASS, 30 simulated seconds with 18 fish; safe spawns, swept contact, clear physics/interpolated poses and no position jumps |
| Draw ordering | PASS, production renderer interleaves rear/middle/front fish with eight formations and blends reflected body/fin views |
| Turn smoothness | PASS, bounded angular speed/acceleration/jerk, cubic endpoint velocities, continuous widths and fractional pitched/mirrored centers |
| Settings | PASS, HD/FHD layout, labels, navigation and Back/Done |
| Waves/pacing | PASS, interpolated effects, shared wave phase and simulated 60/30Hz presentation |
| Pan placement | PASS, float32 HD/FHD transforms and GPU-probe classifier |
| Browser inspection | PASS, 27 images, four lighting modes, play/pause/seek and no page errors |
| Extended scene soak | Canceled at the user's request; no completed soak claimed for this final build |
| Actual Roku GPU/FPS | Not measured in this environment |

The controlled host yaw sweep reduces peak frame-to-frame image changes to 15–30% of nearest-view snapping for the same 64-view data. Float32 fish-transform center error is at most 0.000586px in the tested HD/FHD pitched/mirrored cases. The existing pan test remains below 0.004px placement error with a maximum 0.03125px frame step. These are host math/raster checks, not measurements of device presentation or FPS.

Active Sunset textures are approximately 98.0 MiB decoded RGBA: 62.5 MiB body atlases and 13.4 MiB fins, plus scenery/effects. FHD double buffers bring the estimate to 113.8 MiB; HD to 105.0 MiB, before driver/interpreter overhead. Bilateral view reuse and cached regions avoid a separate decoded texture for every full-circle view.

Photographic sand grain and defined ridges remain; the restrained lighting overlay changes with the same wave phase as the surface. The sunset palette, larger slim fish, independent pectoral animation and slow four-minute camera sweep are retained. No dapple asset is shipped.

The browser preview records 601 production-world snapshots. It illustrates the current artwork, formation ordering, view reflection/blending and width interpolation; it is an inspection aid rather than a Roku GPU reference. Its capture preceded the final small arrival-radius/hover-state adjustment. Earlier scene-soak logs are historical, not final-build evidence.

Tracked installation ZIP: **3,872,032 bytes**. SHA-256: `d190ee5044981a99b80efa57c5b5b078616555f47b9ca9a642b0dd7d443fd2bf`.

Still requires the user's Roku: startup probe outcomes, visible smoothness, sustained FPS/memory, native settings rendering, remote dismissal and activation/persistence across sessions.
