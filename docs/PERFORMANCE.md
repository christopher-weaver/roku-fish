# FPS investigation — 1.0.26

The reported device is a Roku Ultra, with normal/Medium fish density and about 7–8 FPS in both High and Performance. There is no Roku connection configured in this workspace, so the dominant hardware stage and the resulting device FPS remain unmeasured. These findings are source measurements and production-code regression checks.

## Confirmed longstanding costs

- **Performance still rendered a full-resolution scene.** The 2048×1080 offscreen canvas was fixed in size regardless of the 1280×720 output request. That canvas code dates to commit `8ab67df`, version 1.0.7. Performance now uses a 1365×720 overscan canvas and presents it directly at native output size. Canvas pixels fall from 2,211,840 to 982,800 (56% fewer). High remains 2048×1080 with the same smooth adjacent-pixel pan.
- **Receiver shadows submitted unnecessary full-scene rectangles.** Each receiver drew two scaled 2048×1152 regions. The current rock-border receiver was completely transparent but still submitted both passes. That extra receiver is recent; the full-scene receiver design is older. Empty receivers are now omitted and the others are cropped with transparent filter padding. Submitted shadow source area falls from 14,155,776 to 4,788,224 pixels/frame (66% less). These are source-area counts, not measured GPU time. All 96 old receiver frames reconstruct exactly, including alpha and every visible colour.
- **Fish body bending repeated expensive math.** Two heading views × eight body sections, plus a tail and fin, can submit 18 transforms/fish—144 for eight fish. The draw count and heading blends are retained. Common rotation bases and wave terms are reused, and equivalent tangent identities replace repeated trigonometry. In the same 120-frame production-render fixture, Sin/Cos calls fall from 23,321 to 12,761 (45% fewer); all 2,160 transform draws remain. An independent 864-case regression preserves original rounded positions and angles.
- **Auto did not reduce most of that work.** Its existing fallback changes the frame cap, particle count and light opacity, but leaves the canvas, fish sections and shadow rectangles intact. Changing alpha alone does not eliminate a draw. This release reduces avoidable work in every quality mode without lowering High's resolution or fish motion detail.

## What is not yet proven

7–8 FPS corresponds to roughly 125–143 ms/frame. The source audit cannot tell whether update/collision work, draw submission/driver stalls, GPU work, or memory/garbage collection dominates on this Ultra. Eight unique species also create about 12,960 fish regions; this is a working-set concern, not proof of a leak. Clam births can raise the bounded fish count and pairwise collision work. Those possibilities must be checked against native timings rather than inferred from host execution speed.

## Native diagnostic build

Every four seconds the Roku console now prints a `Deep Reef PERF` JSON line with actual FPS, selected mode, canvas dimensions, fish count, simulation ticks/frame, average and maximum stage times, and memory-warning count. FPS sampling now includes the completed swap and message processing.

With **FPS → On**, a second on-screen line shows average milliseconds:

- **U**: update, physics and lighting.
- **D**: drawing and presentation calls, including any driver blocking.
- **S**: SwapBuffers, including queued graphics work and refresh waiting; it is not an isolated GPU timer.
- **E**: event processing and explicit garbage collection.

The console also includes intentional pacing wait time and peaks, which help separate sustained cost from occasional stalls. A normal vsync wait is expected; a swap taking around 100 ms is different from a 16.7 ms refresh wait.

Install the updated ZIP, keep High and normal density initially, turn FPS on, and wait for the first four-second sample. Report the FPS plus the U/D/S/E line, or paste one `Deep Reef PERF` console line. A second short sample in Performance can then distinguish resolution-dependent rendering cost. No long soak is required.

## Validation

BrighterScript compilation; 49 Python package/geometry/material/render-cost/release checks; native diagnostics arithmetic, 864 transform equivalence cases, body sway, draw ordering, upright fish, HD/FHD pan precision, waves/pacing and continuous turns. The browser preview checks asset loading and lighting/control flows only. [performance-audit.json](performance-audit.json) records the measured source work and shadow reconstruction results. A desktop High-preview comparison differed by at most 2/255 in an RGB channel after cropped-texture resampling. Actual Roku GPU/FPS validation remains pending.
