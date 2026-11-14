# Performance and stability

**Target:** 60 FPS in Auto/High, stable 30 FPS fallback in Auto/Performance on a modern Roku Ultra, particularly 4850X. **Measured on Roku:** not available; no device was configured in this environment. Local interpreter throughput and preview frame rate do not establish Roku performance.

The renderer uses double buffering, a fixed 33.33 ms simulation schedule with 16.67 ms presentation, fish/bubble interpolation, continuous effect timing and overdue-frame recovery, immutable cached image pages, cached atlas regions and one body and one small fin draw per fish. The 60Hz mode relies on native double-buffered SwapBuffers pacing without an extra wait. The 30Hz frame scheduler waits before SwapBuffers with a 8 ms submission margin for 30Hz; it does not sleep after a blocking swap. Native draw coordinates are integers, which remains a platform limit on very slow movement. Performance mode requests 720p; High/Auto try 1080p and fall back if display construction fails. It renders native graphics, not 4K video.

Cropped body atlases use about **50.8 MiB**, and six separate cropped fin atlases about **10.9 MiB**. The denser 32-view animation increases texture memory. All active Sunset textures total approximately **97.4 MiB** decoded RGBA; adding the 1080p double buffers gives **113.3 MiB** before driver, interpreter and metadata overhead (about 104.5 MiB with 720p buffers). These are calculations from image dimensions, not measured device residency. Cropping offsets retain the 192×168 registration canvas without storing its empty margins. Only one color variant of each large reef surface is loaded.

Runtime collections are bounded: 12/18/24 fish, six body pages with 256 regions each, six fin pages with 288 regions each, 72 effect slots, one bounded render-reference list. Images are never decoded in the frame loop. Smooth region scaling is enabled outside Performance mode. The simulation does make small temporary steering/projection objects; they are collectable, and actual collector behavior must be profiled on the target. The fixed pools do not prove absence of driver or interpreter memory leaks.

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
