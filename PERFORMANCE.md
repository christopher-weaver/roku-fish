# Performance and stability

**Target:** stable 30 FPS on a modern Roku Ultra, particularly 4850X. **Measured on Roku:** not available; no device was configured in this environment. Local interpreter throughput and preview frame rate do not establish Roku performance.

The renderer uses double buffering, a fixed 33.33 ms schedule with overdue-frame recovery, immutable cached image pages, cached atlas regions and one native draw call per fish. Integer output coordinates avoid subpixel camera seams. Performance mode requests 720p; High/Auto try 1080p and fall back if display construction fails. It renders native graphics, not 4K video.

The six fish atlases are each 1536×1008, about 5.91 MiB decoded RGBA. All six total about 35.4 MiB. The active water plate is 9 MiB; two active reef surfaces total about 15.5 MiB; the coral strip is about 1.5 MiB. Effects, two output buffers (15.8 MiB at 1080p / 7 MiB at 720p), driver overhead, source strings and registry data add to this. The expected order of magnitude is **80–100 MiB**, not the compressed ZIP size. This is an estimate, not measured device residency. Only one color variant of each large surface is loaded.

Runtime collections are bounded: 12/18/24 fish, six atlas pages, 48 regions per page, 72 effect slots, one bounded render-reference list. Images are never decoded in the frame loop. The simulation does make small temporary steering/projection objects; they are collectable, and actual collector behavior must be profiled on the target. The fixed pools do not prove absence of driver or interpreter memory leaks.

Auto quality computes average FPS in four-second windows. Sustained output below 25 FPS reduces optional effect quality in gradual steps, culls particles after fading them, and attenuates caustics. A bounded recovery path restores quality after stable throughput. Principal fish and reef occlusion remain intact. Memory warnings reduce optional quality and request garbage collection. Show FPS is off by default.

The monotonic millisecond source is reset daily, before signed 32-bit overflow. Simulation/effect phases are bounded; a stalled timestep caps at 100 ms. The PRNG uses double arithmetic with a bounded modulus. Fish do not teleport at camera edges; particles/bubbles recycle out of view.

## Device profiling procedure

1. Install the release ZIP, select Deep Reef, set Medium density, Auto quality and Show FPS On.
2. Open the screensaver debugger on TCP 8087 and capture the four-second FPS/quality reports. If available, use Roku Resource Monitor/`free` to record script and graphics memory at startup, five minutes, 30 minutes and one hour.
3. Run 10 minutes in Sunset at Medium, then High density; compare 1080p Auto against 720p Performance. Repeat under Daylight and Moonlight.
4. Run an overnight soak, verify fish return from occlusion, and inspect memory trend and draw warnings.
5. Dismiss with several remote buttons and reactivate at least ten times. Verify settings across two activations and a full reboot. Confirm idle activation from the normal Roku UI and from another idle app.
6. Disable Show FPS afterward. Record model, Roku OS version, output mode, settings, average FPS, memory trend and any logs.

No 60 FPS mode or successful hardware soak is claimed. If actual 1080p performance is below target, the first shipped fallback is 720p Performance plus reduced optional effects; species count is preserved.
