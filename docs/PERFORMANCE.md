# FPS investigation — 1.0.32

## V32: density-dependent fish work

The user's latest Ultra measurements are **20–25 FPS at High fish density** and **about 45 FPS at Low density**. No new U/D split was supplied. These measurements support reducing work per fish and per pair; they do not isolate GPU time from script/driver time.

V32 rejects a distant fish pair using conservative swept X/Z slabs before entering the full cylinder function. Both endpoints include the other fish's previous/current positions; a tiny broad-phase margin retains near-boundary candidates. The full collision test still checks every candidate. Predictive steering compares squared distances first and only computes a square root for an interaction. Neither simulation frequency nor population settings are reduced.

The same 60-tick, eight-fish production fixture retains all reference end poses. Helper calls fall **17,136 → 13,896 (19%)**, square roots **5,608 → 2,576 (54%)**, and full pair-function calls **3,360 → 120 (96%)**. All original pair candidates are screened; rejected distant pairs cannot intersect. Field reads fall **462,656 → 427,736 (8%)**.

Drawing submits whole-body layers directly, shares tint setup, and reuses the quantized rotation basis across successive layers. The same 120-frame fixture retains **707 transforms**, the opaque base, and the normalized phase/yaw blend. Rendering helper calls fall **4,752 → 3,818 (20%)**, and Sin/Cos calls **3,338 → 2,628 (21%)**. The optimized renderer exactly matches 10240 body commands across 2,560 heading/phase/resolution/backend cases. These are host work counts, not native FPS gains.

The farther-back copperband attachment also exposed a subpixel-scale correction around the model origin. The correction now fixes the tail root itself. Maximum fractional joint error is **0.003062 px**, with no missing sampled side-view overlaps across 2,560 cases. The original 0.02 px gate is retained.

Clam openings now independently roll a **1/50 birth chance**; ordinary openings alternate pearls and bubbles. This avoids the former birth every third opening and its rapid increase in fish load. The roll happens once per opening on a separate random stream, preserving ordinary swimming randomness. Existing four-birth/twelve-fish caps and closed-shell baby preparation remain.

[The audit](density-performance-audit.json) records full counts. Actual v32 FPS remains unmeasured because no Roku is connected to this workspace.

## V30: caudal attachment correction

The user clarified that the remaining joint is **where the tail meets the body**. V30 keeps the complete-body renderer and corrects the separate caudal patch. The former crop-envelope transform resized/shifted the neck around its rectangle, and a generic .76 bend point did not match every species' actual attachment.

The root now comes from the vertices shared by the existing body and caudal meshes, including each baked tail pose. Cached projections track the blended body angle and flex. Width interpolation pivots around that anatomical point; neck height stays fixed. A small underlap is hidden by drawing the body after the tail. Integer-only rendering uses the same rounded body origin.

In the matching 1,280-case fractional subset, maximum projected root error falls **2.156544 → 0.016702 pixels**. Another 1,280 integer-backend cases stay within the expected rounding bound (maximum **0.695813 pixels**). No sampled visible side-view collar lacks overlap. All 2,560 cases paint the tail under the body. These are production-command and decoded-texture checks, not hardware screenshots. The texture files and maximum fish draw count are unchanged; joint tables are built once during asset loading.

[tail-attachment-audit.json](tail-attachment-audit.json) records the result; [matching close-ups](previews/tail-joint-comparison.png) reconstruct the old/new production submissions. Run `python tools/tail_rig.py` after changing the fish mesh or baked caudal poses. The on-device join still needs the user's confirmation; no new hardware FPS measurement is available.

## V29: complete body images and shared anatomy caches

The latest user measurement after v28 is **15 FPS, U36 / D29 / S0 / E0 ms**. The earlier 11 FPS / U44 / D30 result improved, but the user still sees splits. The v28 geometric overlap checks therefore did not establish that the on-device artifact was resolved.

V29 removes the body-slice renderer. Every species now has complete curved, neutral and inverse-curved body images for all **112** mesh-view angles. Opacity blends interpolate swim pose and heading, with a complete opaque base and normalized source-over weights. Tail and pectoral poses remain independent and attach to the same subtle body flex. All body images rotate together at the fish's pitch; there are no interior strip edges, overlap joins or independent section rotations. The images retain the approved texture resolution and exact visible source colors.

The 120-frame native fixture submits **707 transforms instead of 2,160 (67% fewer)**. A body needs at most four complete-image submissions instead of sixteen slice submissions. Source trigonometry also drops from 5,524 to 2,618 calls in that renderer-only fixture. The callbacks are host graphics stubs; these are work counts, not a Roku FPS prediction.

The physics update validates constant anatomy once for each fish at the start of a fixed tick. Projected coral extents/depth radii are cached, and pair/neighbor checks reuse the validated bounds during that tick. Standalone queries, resized fish, species changes and newborns retain validation. The same two-second/eight-fish fixture makes **462,656 object field reads instead of 530,121 (13% fewer)**, retaining every simulation tick, collision check and reference end pose. The simulation remains at 30 Hz.

An independent pixel check covers **1,710 mesh-view/body-pose combinations**. Each image column retains its entire source alpha profile and every visible RGBA value, including any legitimate source gaps; no new internal gaps or color changes appear. Neutral images keep their source alignment. Native tests verify complete-body submissions, common pitch, opaque base and the normalized two-axis blend weights. The obsolete strip-margin fixture has been removed. These checks are stronger than the earlier overlap test, though the actual Roku filtering/FPS still requires the user's sample.

Prebaking trades texture space for less script/driver work: the estimate for all variants rises from 128.43 to 172.23 MiB. The runtime loads only the present species and chosen scene, and creates substantially fewer body regions. The package stays below **4 MiB (4,194,304 bytes)**; this replaces the older conservative 4,000,000-byte guard. All atlas pages remain within 2048×2048. `assets/source/fish-rest` preserves the original neutral mesh views and metadata; `tools/whole_swim.py` regenerates the complete-body images without editing their source colors.

See [continuous-body-audit.json](continuous-body-audit.json) for counts and limitations. After installing v29, report FPS and U/D/S/E in High/normal density after about ten seconds, along with whether the splits remain. A full `Deep Reef PERF` line adds ticks/frame and memory events. No extended soak is required.

## V28 changes and earlier measurements


After v27 the user reports **11 FPS, U44 / D30 / S0 / E0 ms**, improved from U101 / D31. Updating is still the largest stage, and drawing remains significant. These are user-supplied averages; the new release has not yet been timed on the Ultra.

Version 1.0.28 removes another layer of physics helper dispatch without changing the 30 Hz step, steering limits, swept safety checks or reference end poses. Hot-path clamps use local comparisons with the same limits; the speed-factor local explicitly retains double precision. In the same 60-tick/eight-fish fixture, helper calls fall **26,268 → 17,136 (35%)**, and total observed calls fall **56,048 → 46,916 (16%)**. All 1,645 reef sweeps and 3,360 fish-pair sweeps remain.

Drawing caches immutable section phase offsets when the atlases load, shares the fish's phase/direction terms, and reuses the quantized rotation basis for half-pixel anchor compensation and fractional placement. In the same 120-frame production renderer fixture, **Sin/Cos calls fall 17,113 → 5,957 (65%)**, total calls fall 26%, and all **2,160 transform draws** remain. This includes identical fixture setup/assertions. The eight body sections, two-view rotation blend and separate fin/tail motion remain. Cached constants are allocated at load time, not on each displayed frame.

The segment fix has two parts. A pitched section previously clamped its submitted angle while placing its pivot with the unclamped angle; both now use the actual submitted rotation. A dedicated 864-case regression fails against v27 and passes with the correction. The source overlap also grows with section height, and pivots stay at their nominal section centers. Dense independent checks of captured native crops/transforms cover **11,481,120 seam-neighborhood points**, reserving two output pixels for filtering/placement error at HD/FHD. V27 lacks that margin at 1,497,365 points; v28 has no deficient samples. The margin test is geometric evidence, not a claim that every old deficient sample was a visible GPU hole.

[swim-performance-audit.json](swim-performance-audit.json) records the source counts and limitations. The renderer was also rasterized from its production transform captures for a visual check. No artwork, fish count, simulation rate or heading-blend detail was reduced. The subsequent user measurement was 15 FPS / U36 / D29, with splits still visible; v29 replaces this body renderer.

## Earlier v26 hardware baseline and v27 update fixes

The earlier Roku Ultra baseline reports **U 101 / D 31 / S 0 / E 0 ms**, at normal/Medium fish density, with the same performance in High and Performance modes. Update plus draw is approximately 132 ms/frame, consistent with 7–8 FPS. This identifies CPU simulation/update work as the dominant measured stage. Draw submission is also substantial; the negligible swap/event readings do not point to a long swap wait or explicit event/GC work. These averages cannot exclude internal automatic garbage collection or occasional stalls.

## CPU fixes introduced in v27

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

Install the tracked **1.0.29** ZIP, select **High / normal density / FPS On**, and report the FPS and U/D/S/E after about ten seconds. No long soak is required. There is no configured connection to the actual Roku in this workspace, so the resulting device FPS still needs that sample. The previous drawing optimizations remain in place, and D=31 ms is still a separate remaining cost.

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
