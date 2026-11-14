# Performance and stability

**Target:** 60 FPS in Auto/High, stable 30 FPS fallback in Auto/Performance on a modern Roku Ultra, particularly 4850X. **Measured on Roku:** not available; no device was configured in this environment. Local interpreter throughput and preview frame rate do not establish Roku performance.

The renderer uses double buffering, a fixed 33.33 ms simulation schedule with 16.67 ms presentation, fish/bubble interpolation, continuous effect timing and overdue-frame recovery, immutable cached image pages, cached atlas regions and two neighboring body views and two small fin views per fish. The 60Hz mode relies on native double-buffered SwapBuffers pacing without an extra wait. The 30Hz frame scheduler waits before SwapBuffers with a 8 ms submission margin for 30Hz; it does not sleep after a blocking swap. Static scenery, effects and pitched fish use fractional placement through cached pretranslated regions and floating-point scale, verified by a startup GPU pixel probe. The same pan period and amplitude are retained. Performance mode requests 720p; High/Auto try 1080p and fall back if display construction fails. It renders native graphics, not 4K video.

Cropped body atlases use about **62.5 MiB**, and the separate fin atlases **13.4 MiB**. Active Sunset textures total approximately **98.0 MiB** decoded RGBA; including double buffers gives **113.8 MiB** at FHD or **105.0 MiB** at HD, before driver, interpreter and metadata overhead. These are calculations from image dimensions, not measured device residency. The 64-view animation reuses 33 unique angles through bilateral reflection and reversed tail bends. Region caches deduplicate reflected frames and keep normal/fractional regions on the same bitmap.

Runtime collections are bounded: 12/18/24 fish, six body/fin image pairs, eight formations, 72 effect slots, a connected 185-node/400-edge route graph and a reusable render-reference list. Images decode once. A display pose is computed once per fish per frame and reused for sorting/drawing. Paths use BFS only at destination changes, with local waypoint visibility and swept collision checks during movement. Smooth filtering and opaque-base view blending provide finer turning transitions without a new decoded texture for each intermediate angle. Some small steering/projection objects remain temporary; actual GC and draw throughput require profiling on the Roku.

Auto quality computes average FPS in four-second windows. Twelve accumulated seconds below 45 FPS locks the session to an even 30 FPS target, avoiding repeated frame-cap switches. High keeps a 60 FPS target; Performance starts at 30 FPS. Sustained output below 25 FPS reduces optional effect quality in gradual steps, culls particles after fading them, and attenuates caustics sand highlights. A bounded recovery path restores quality after stable throughput. Principal fish and reef occlusion remain intact. Memory warnings reduce optional quality and request garbage collection. Show FPS is off by default.

The monotonic millisecond source is reset daily, before signed 32-bit overflow. Simulation/effect phases are bounded; a stalled timestep caps at 100 ms. The PRNG uses double arithmetic with a bounded modulus. Fish do not teleport at camera edges; particles/bubbles recycle out of view.

## Device profiling procedure

1. Install the release ZIP, select Deep Reef, set Medium density, Auto quality and Show FPS On.
2. Open the screensaver debugger on TCP 8087 and capture the four-second FPS/quality reports. If available, use Roku Resource Monitor/`free` to record script and graphics memory at startup, five minutes, 30 minutes and one hour.
3. Run 10 minutes in Sunset at Medium, then High density; compare 1080p Auto against 720p Performance. Repeat under Daylight and Moonlight.
4. Run an overnight soak, verify fish return from occlusion, and inspect memory trend and draw warnings.
5. Dismiss with several remote buttons and reactivate at least ten times. Verify settings across two activations and a full reboot. Confirm idle activation from the normal Roku UI and from another idle app.
6. Disable Show FPS afterward. Record model, Roku OS version, output mode, settings, average FPS, memory trend and any logs.

A 60 FPS target is implemented; sustained device output and a successful hardware soak have not been measured. If actual 1080p performance is below target, the first shipped fallback is 720p Performance plus reduced optional effects; species count is preserved.

## Pan precision gate

`tests/pan_precision.brs` exports real production transforms for 720p/1080p. `tools/pan_check.py` applies float32 drawing precision and requires sub-0.009px error, sub-0.04px frame increments at the tested 60Hz camera segment, and less than 0.032px stretch over a 2048px layer. The current maxima are 0.003886px error and 0.031250px frame increments. These are math checks; `pan.brs` separately verifies a fractional drawing path against actual GPU readback at startup. Unsupported paths retain ordinary drawing. Check `Deep Reef fractional pan=` in the screensaver debug log when validating on a TV.

## Fish turn precision

`tests/turn_smoothness.brs` checks bounded angular acceleration/jerk and continuous endpoint display velocities. `tools/turn_check.py` quantizes rotated/mirrored center placement to float32 at HD/FHD; the current host maximum center error is 0.000586px. Host raster comparisons reduce peak frame-to-frame changes during a controlled yaw sweep to 15–30% of nearest-view snapping for the same 64-view data. These measurements describe transforms and image transitions; they do not establish device FPS or shader/GPU behavior. The startup `Deep Reef fractional fish=` log reports the actual device drawing-path probe.
