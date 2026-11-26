# Performance and stability

**Target:** 60 FPS in Auto/High, stable 30 FPS fallback in Auto/Performance on a modern Roku Ultra, particularly 4850X. **Measured on Roku:** not available; no device was configured in this environment. Local interpreter throughput and preview frame rate do not establish Roku performance.

The renderer uses a fixed 30Hz simulation with interpolated 60Hz presentation. An opaque 2048×1080 overscan canvas costs 8.44 MiB and is presented with two adjacent integer offsets, avoiding changing large-anchor transforms. At most four complete body regions, one caudal region and one fin region draw per fish; static reef layers use exact 1:1 copies. Marine objects select from 65 mesh poses without crossfading. Fin texture memory is reduced by about 70%; no runtime reflection is used.

Projection/probe/candidate and display objects are reused. The route graph includes precomputed next-hop data, avoiding frame-loop BFS allocations. Waypoint visibility is checked at 5Hz, and fixed effect depth buckets avoid repeated scans. These changes reduce known sources of stalls; only real-device profiling can establish achieved FPS.

Decoded texture/buffer estimates for this release are recorded in docs/TEST_RESULTS.md. They are dimension-based estimates, not measured GPU residency. The 60Hz target relies on SwapBuffers; 30Hz waiting still happens before presentation, with an 8ms submission margin. Performance requests HD; High/Auto try FHD.

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

## Short validation

Use `python tools/test.py --quick` for routine changes. The pan gate measures actual adjacent-pixel weights, and tests/upright_present.brs captures production draw calls across a full fish turn and HD/FHD presentation. Extended soaks remain optional and were not run for this release.

On the Roku, enable Show FPS briefly and inspect screensaver debug output on port 8087. Check the `opaque pan canvas` startup line, pan continuity, turn orientation and sustained output. Hardware results are not available in this environment.

## Version 1.0.8 sharpness

The renderer now draws one body/tail and one fin per fish. Marine meshes select one of seven views. Connected reef layers use exact 1:1 image copies, with no repeated layer pixel blends or view/pose crossfades. Only final camera presentation interpolates neighboring pixels. Estimated active Sunset texture storage is 96.7 MiB; with the canvas and FHD buffers about 120.96 MiB before overhead (HD 112.17 MiB). These are not hardware measurements.

## 1.0.34 motion budget

Raised eyes and S/C deformation are baked offline. Both straight swimming and turning keep the existing ceiling of four body region draws plus one tail and one fin. Fewer redundant profile views retain all 25 dense frontal angles and native canvas resolution. One cached C-view record and its attachment table are added per loaded species/fish; no per-frame bitmap construction is introduced. Near-contact escape changes run only after the exact swept collision test reaches its numerical buffer. Pure vertical and shorter corner probes are confined to route recovery. Native FPS and GPU residency still require device measurements.
