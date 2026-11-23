# FPS investigation — 1.0.27

The Roku Ultra reports **U 101 / D 31 / S 0 / E 0 ms**, at normal/Medium fish density, with the same performance in High and Performance modes. Update plus draw is approximately 132 ms/frame, consistent with 7–8 FPS. This identifies CPU simulation/update work as the dominant measured stage. Draw submission is also substantial; the negligible swap/event readings do not point to a long swap wait or explicit event/GC work. These averages cannot exclude internal automatic garbage collection or occasional stalls.

## CPU fixes in this release

- **Exact indexed reef queries.** Previously every rectangle walked occupancy rows and searched each string. An offline sparse table now ORs consecutive rows in power-of-two bands. Any rectangle is covered exactly by at most two overlapping bands, so its result takes at most two native string searches. Shared mask strings keep the index about 166 KB uncompressed, with only a few KB added to the ZIP. It is loaded once, validated against the actual grid, and reused. Custom grids retain the original exact row-scan fallback. The build regenerates the index from current occupancy data.
- **Shared swept geometry.** A reef sweep computes world bounds, depth radius, body envelope and projected rectangle once, sharing them across the floor, surface and depth planes. All formations with matching parallax share a rectangle. Distant cave volumes are rejected before invoking the exact segment/slab test. This removes thousands of repeated helper calls and duplicate projections while retaining conservative body/tail/fin clearance.
- **Cached fish envelopes and exact pair rejection.** Body dimensions are cached for each size/species, with invalidation for a resized fish, changed species or cloned clam baby. A pair wholly outside an axis slab cannot collide and exits before the closest-approach calculation. Passing-lane steering and the final continuous pair guards remain active.
- **Bounded particle phases.** A phase that advances by less than a turn needs a single conditional subtraction when it wraps, rather than a generic modulo helper on all 72 particles every physics tick.

Slow frames above 100 ms currently require three 30 Hz catch-up ticks. Repeating the former expensive update amplified the slowdown. This release reduces the cost of each tick; it retains the fixed 30 Hz dynamics, interpolation, swimming speeds, fish count and collision checks. It does not discard simulation steps to manufacture a higher frame count.

## Measured production work

The same seeded fixture runs actual production BrightScript for 60 fixed ticks with eight fish, excluding initialization. Its v1.0.26 reference is commit `0cad87f`. The host adapter enforces Roku's shared enumeration cursor.

| Work in the two-second simulation window | v1.0.26 | v1.0.27 |
| --- | ---: | ---: |
| BrightScript helper calls | 106,147 | 26,268 (75% fewer) |
| All observed calls, including native built-ins | 165,320 | 56,048 (66% fewer) |
| Reef occupancy string searches | 16,359 | 1,372 (92% fewer) |
| Physics ticks / individual fish updates | 60 / 480 | 60 / 480 |
| Swept reef / fish-pair tests | 1,645 / 3,360 | 1,645 / 3,360 |
| Sin / Cos calls | 5,337 / 1,137 | 5,337 / 1,137 |

All eight reference x/y/z/heading trajectories are retained within 1e-7 design units. Counts demonstrate work removed, **not a measured native FPS increase**. [cpu-performance-audit.json](cpu-performance-audit.json) records full counts and the user-supplied hardware evidence. `tools/profile_updates.cjs` and `tests/cpu_workload.brs` reproduce the current count using the production sources; the baseline run substitutes the four v26 source files changed by this update.

## Validation and the next device sample

Independent frozen v26 collision guards match 1,260 indexed rectangles, 600 swept reef paths and 1,200 swept/static fish-pair paths. Another 600 size/species changes validate cache refresh. The offline index is also checked against every rectangle on an irregular small grid and every query height in the shipping grids. Native movement, traffic, route recovery, floor/cave/surface clearance, clam births, turns, pan, appendage animation, settings and package checks exercise the same production code.

Install the tracked **1.0.27** ZIP, select **High / normal density / FPS On**, and report the FPS and U/D/S/E after about ten seconds. No long soak is required. There is no configured connection to the actual Roku in this workspace, so the resulting device FPS still needs that sample. The previous drawing optimizations remain in place, and D=31 ms is still a separate remaining cost.

## Diagnostic meanings

Every four seconds the console prints `Deep Reef PERF` JSON with actual FPS, selected mode, canvas size, fish count, ticks/frame, average/maximum stage times and memory warnings. The FPS overlay's second line shows average milliseconds:

- **U**: physics, simulation and lighting.
- **D**: drawing and presentation calls, including any driver blocking.
- **S**: SwapBuffers, including refresh waiting and queued graphics work; not an isolated GPU timer.
- **E**: event processing and explicit garbage collection.

The console includes intentional pacing wait time separately. FPS includes the completed swap and message processing.

## Earlier render fixes retained from v1.0.26

- **Performance still rendered a full-resolution scene.** The 2048×1080 offscreen canvas was fixed in size regardless of the 1280×720 output request. That canvas code dates to commit `8ab67df`, version 1.0.7. Performance now uses a 1365×720 overscan canvas and presents it directly at native output size. Canvas pixels fall from 2,211,840 to 982,800 (56% fewer). High remains 2048×1080 with the same smooth adjacent-pixel pan.
- **Receiver shadows submitted unnecessary full-scene rectangles.** Each receiver drew two scaled 2048×1152 regions. The current rock-border receiver was completely transparent but still submitted both passes. That extra receiver is recent; the full-scene receiver design is older. Empty receivers are now omitted and the others are cropped with transparent filter padding. Submitted shadow source area falls from 14,155,776 to 4,788,224 pixels/frame (66% less). These are source-area counts, not measured GPU time. All 96 old receiver frames reconstruct exactly, including alpha and every visible colour.
- **Fish body bending repeated expensive math.** Two heading views × eight body sections, plus a tail and fin, can submit 18 transforms/fish—144 for eight fish. The draw count and heading blends are retained. Common rotation bases and wave terms are reused, and equivalent tangent identities replace repeated trigonometry. In the same 120-frame production-render fixture, Sin/Cos calls fall from 23,321 to 12,761 (45% fewer); all 2,160 transform draws remain. An independent 864-case regression preserves original rounded positions and angles.
- **Auto did not reduce most of that work.** Its existing fallback changes the frame cap, particle count and light opacity, but leaves the canvas, fish sections and shadow rectangles intact. Changing alpha alone does not eliminate a draw. This release reduces avoidable work in every quality mode without lowering High's resolution or fish motion detail.


The earlier source-area and transform counts remain documented in [performance-audit.json](performance-audit.json). All 96 receiver frames reconstruct with zero alpha or visible-colour error. The native-sized Performance canvas and High's smooth pan/body transforms remain unchanged by the CPU update.
