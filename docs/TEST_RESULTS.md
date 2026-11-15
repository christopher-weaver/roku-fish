# Deep Reef 1.0.11 — targeted verification

Fish bodies now have 112 adaptive heading slots from 57 upright mesh views. The finest 0.703125° spacing covers more of the direct front/rear transition. Fish begin side-facing, choose predominantly lateral goals near their established depth and keep side-facing hover poses. Occasional depth excursions and natural turns remain.

The marine strip renderer is removed. Each fan/anemone draws once using one of 65 complete, root-pinned mesh-deformation poses. Fixed quad placement and scale eliminate moving strip boundaries, oversized-anchor jitter and camera-view switching. Pose spacing bounds geometric tip displacement to about 0.24 design pixels per state. Fish collision avoidance remains active.

A generated, deliberately slightly goofy moray peeks through the actual enclosed lower reef tunnel. Quintic easing gives a slow rise and retreat with pauses. Existing reef pixels hide the head/neck at the tunnel edges. Slow panning now takes three minutes, with the same sweep width. A periodic cellular wave-net shadow covers water, fish, reef and sand, with wrapped padding and display-clock interpolation.

| Check | Result |
|---|---|
| Native compiler | PASS, BrighterScript 0.73.8 |
| Package/artwork/tracking | PASS, 34 Python tests |
| Adaptive rotations | PASS, bounds, positive scales, continuous widths and host raster change reduction |
| Fish behavior | PASS, side-facing starts, mostly lateral/home-depth goals and side-facing hovering |
| Fish traffic | PASS, four spawning seeds and head-on/depth/overtaking/crossing encounters; swept/interpolated envelopes clear |
| Coherent marine animation | PASS, full-object states stay in range and do not skip geometry states at the tested 60Hz clock |
| Native marine drawing | PASS, exactly one draw per marine object, no runtime strip transforms |
| Tunnel eel | PASS, eased movement, visible and hidden pauses, bounded angles and correct draw order behind reef |
| Global shadow | PASS, padded cellular atlas, bounded alpha, scene-wide draw coverage |
| Faster pan | PASS, 180-second Slow cycle and unchanged amplitude |
| Coral clearance | PASS, targeted physical/interpolated footprint checks with all marine states reserved |
| Settings/waves/pacing | PASS, labels, Back/Done, wave phase and simulated display scheduling |
| Pan placement | PASS, existing adjacent-pixel presentation and centroid precision |
| Browser inspection | PASS, all 51 runtime images, lighting/play/pause/seek, no page errors |
| Extended soaks | Not run; short validation requested |
| Actual Roku GPU/FPS | Not measured |

The navigation graph has 251 connected nodes and 544 bidirectional edges. Estimated active Sunset image textures occupy 83.57 MiB at the default density and 91.00 MiB at High. Add 8.44 MiB for the scene canvas and 15.82 MiB for FHD double buffers (6.25 MiB at HD), before driver/interpreter overhead. These are dimension estimates. Marine drawing drops from roughly sixty moving strip draws to two coherent object draws; the new scene-wide shadow adds thirty small tile draws.

The tracked ZIP remains below 4,000,000 bytes. Exact bytes and SHA-256 are in dist/build-report.json. Source RGBA artwork and mesh files retain their detail; palettes, complete-pose texture sizes and startup splash compression keep the self-contained package within budget. No extra spatial filtering is applied to the fixed reef/background plates.

Current logs include compiler, fish profile/traffic, marine motion, collision, settings, waves, render depth, upright turns, adaptive raster, pan precision and browser results. Earlier extended-soak reports are historical. Inspect sustained motion and FPS on an actual Roku.
