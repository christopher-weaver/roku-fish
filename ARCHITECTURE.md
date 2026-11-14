# Native architecture

`RunScreenSaver()` is the sole aquarium lifecycle entry point. `RunScreenSaverSettings()` creates a separate SceneGraph context for configuration. The manifest declares only `screensaver_title`, uses `rsg_version=1.3`, and includes real FHD/HD icons and FHD/HD/SD splash artwork.

## Platform decisions

The current official screensaver guide permits `roScreen`, forbids ordinary channel entry points and video, and delegates dismissal to the system. A double-buffered `roScreen` gives direct control over atlas regions, stable depth ordering and a 30 Hz loop. SceneGraph would also work, but updating many sprite nodes and region frames adds work without improving this renderer. SceneGraph is used only for the configuration screen, after which its context exits.

The OS 16 drawing rules prohibit modifying a bitmap after using it as a draw source until the buffer swap. All runtime textures and atlas regions are initialized once and remain immutable. This renderer does not depend on arbitrary OpenGL shaders, game engines, private native interfaces or 4K UI rendering. Offline OpenGL is used only in the desktop art pipeline.

Target output is 1920×1080. Performance mode and failed FHD creation fall back to 1280×720 using the same logical coordinates. The display scales the output to the TV's video mode. Every bitmap is at most 2048 pixels in each dimension. GPU rotation is queried; devices without arbitrary rotation omit small pitch rotations while retaining real yaw views.

## Simulation and data

`aquarium.brs` owns seeded state; `fish.brs` steers forward-swimming agents; `schooling.brs` supplies separation, alignment and cohesion. `camera.brs` handles perspective and occlusion occupancy. `effects.brs` handles fixed particle pools, lighting and adaptive quality. `assets.brs` caches textures; `renderer.brs` composites them.

X and Y are logical tank coordinates, Z is normalized depth from the rear wall (0) to front glass (1). Projection contracts distant fish toward the visual center and reduces their size and apparent speed. Fish have positions, targets, velocity and desired velocity, heading, pitch, state, timers, phase, per-species speed and independently randomized size and turn rate. Velocity follows the limited heading; a fish completes an arc instead of instantly reversing. Speed changes are acceleration-limited. Elapsed time caps at 100 ms after a stall. `ReefAdvance` feeds fixed 1/30-second ticks and interpolates the previous/current positions, heading, pitch, tail and fin phase for display. Angular acceleration is limited for gentle turns. Every fish and neighbor scan uses indexed loops: native Roku objects share one enumeration cursor, so nesting `for each` on the fish array used to end the outer update after fish zero.

Chromis use local alignment/cohesion and scatter slightly near large fish. Every species separates from close neighbors. Clownfish mostly visit the lower-left anemone area; grammas sometimes choose a cave target. Soft tank walls steer inward early, with acceleration-limited braking at the outer safety margin. Fish retain coherent world positions beyond the camera crop. They never wrap across the aquarium.

`scenes/species.json` defines 80 cropped body frames (20 yaw × four swim poses), 100 separate cropped pectoral-fin frames (20 yaw × five strokes), registration anchors, physical display length, body/fin beat and schooling behavior. `tank.json` defines the population order, density counts, occlusion planes and lighting thresholds. `occupancy.json` is generated from the actual reef masks, not invented obstacle rectangles. Adding a general cruising species needs artwork plus data; specialized behaviors can add a name-specific rule.

## Compositing order

1. Rear full reef/water photograph and sand.
2. Moving caustics and far particles.
3. Depth-sorted rear fish (Z < 0.48).
4. Transparent mid-reef surface, aligned with the rear plate.
5. Mid-depth fish (0.48 ≤ Z < 0.78).
6. Foreground reef and animated soft coral.
7. Near fish, independently timed pectoral overlays, particles, larger 13–28px bubbles, soft light shafts and surface wavelets.
8. Lighting overlays and optional clock/FPS.

The transparent reef copies have real cave/water holes. A rear fish disappears behind opaque coral; a near fish remains visible in front. A fish cannot cross a reef depth plane while projected over an occupied rock cell. It first seeks open water. This is conservative 2.5D collision handling rather than a complete rock mesh physics system.

The rear plate retains reef detail as a distant visual wall. Foreground surfaces share its registration, avoiding disconnected photographed layers. For this reason the reef planes share camera travel. Fish and particles have depth-dependent parallax; separate reef-plane parallax is intentionally restrained. The 2048×1152 art has 128 pixels of horizontal overscan: Off fixes the crop, Subtle uses ±40 pixels over three minutes and Slow uses ±56 pixels over four minutes. The cosine sweep starts left, eases into a rightward pan and smoothly returns; Slow is the default. No scene stretching, repeating panorama or border exposure is needed. This is the brief's supported fixed-view/limited-drift tradeoff.

## Settings and lighting

Preferences are validated against one shared schema before loading or saving to registry section `deep-reef-v1`. Invalid values fall back independently. The native configuration scene saves each change immediately, supports Back and Done, and restores defaults. No settings code runs as an input interface inside the aquarium.

Sunset is the user's requested default, using offline pink/amber/red plates and matching alpha layers. Daylight, Dusk and Moonlight use the daylight plate with efficient warm/dark overlays. Automatic reads local device time once a second, with configurable dawn 07:00 and dusk 18:30 thresholds in `tank.json`; continuous eased transitions and a 20-second filter avoid sudden changes. No location service is used.

## Timing, failure and memory

A double-precision simulation clock advances from capped deltas. The 32-bit host millisecond timer restarts daily before overflow; the camera's periods divide the daily phase window. Effects recycle fixed pools. Atlas pages load once; decorative load failures are skipped. If both display configurations fail, the entry point returns to the system. Missing essential scene metadata also returns instead of looping on a black display.

Auto quality measures four-second FPS windows, waits for sustained low throughput and fades optional particles and caustic opacity. Fish count and essential depth surfaces remain intact. Memory notifications request collection and reduce secondary effects. Actual throughput and resident GPU memory still require a Roku test.
