# Native architecture

`RunScreenSaver()` owns the standalone double-buffered roScreen. `RunScreenSaverSettings()` opens the separate SceneGraph settings context. There is no Main/RunUserInterface, video playback, runtime download or ordinary channel launch flow. Settings and Back/Done behavior are retained.

## Stable camera presentation

The renderer composes the aquarium into one opaque 2048×1080 roBitmap. World draws add the camera offset inside that overscan canvas, preserving each fish/formation's relative depth parallax. `ReefPresent` draws the canvas at floor(-camera × outputScale), then overlays it one output pixel to the right with the fractional weight. Since both sources are opaque copies of the completed scene, the result is an ordinary linear interpolation with no layer opacity dip.

The primary camera transform uses integer draw positions and constant scale. There are no 65536px pretranslations or changing scales in the pan path. Scale quantization therefore cannot amplify a subpixel remainder into a multi-pixel jump. HD/FHD alpha weights have less than 0.002px centroid error in host checks. This establishes the draw geometry, not actual Roku FPS.

The canvas is rendered once, used as an immutable source for presentation, and modified again only after SwapBuffers. If allocation fails, the renderer retains direct drawing with neighboring-pixel layer blending. Clock/FPS text draws on the output screen after presentation. The camera uses the monotonic display clock rather than a capped physics catch-up clock. Slow remains ±56px over 240 seconds; Subtle ±40px over 180 seconds.

## Fish orientation and articulation

All 64 fish views are real upright offline renders. Both scale axes remain positive; pitch stays within a small natural tilt. The previous bilateral runtime reflection path is removed. Four source tail bends and five source pectoral strokes interpolate with the two neighboring yaw views. Ordered source-over weights preserve opaque body interiors. Dense views and continuous width matching limit silhouette fringe differences.

Fin textures use half-resolution crops with a 2× draw scale, reducing their decoded memory by about 70%. Fractional crop anchors are retained explicitly so pose interpolation does not shift the fin hinge. The existing short-anchor positive-scale fish placement is enabled only after a startup pixel check; it is independent of camera presentation.

Fixed 30Hz simulation, interpolated XYZ and cubic heading interpolation remain. Turn speed, acceleration and jerk are bounded. Indexed fish/neighbor loops preserve Roku's shared ifEnum semantics.

## Layered reef and navigation

Six independent coral/rock islands replace the continuous wall. White coral sits on a porous swim-through arch; branching coral rises at the rear right; a green cup, round brain coral, central clam and smaller garden sit at different depths. Each has three actual offline relief-mesh views, blended over camera travel. These are photo-textured depth fields, not anatomical scans or runtime 3D shaders. Stronger parallax, rounded shading, open channels and contact shadows reinforce depth.

Collision masks reserve the union of the three silhouettes at each formation's finite depth interval. Full fish footprints include fins, tail, pitch and the entire camera sweep. The graph is built offline against these masks. A precomputed next-hop table replaces per-destination BFS; waypoint visibility checks run at 5Hz. Projection/probe/candidate objects are reused, display poses are cached, and effects are assigned to fixed depth bands rather than rescanned for each formation. A final swept-volume guard still prevents entering coral.

## Rendering and limits

The canvas draws water/sand, contact shadows, depth-interleaved fish/effects/coral views, restrained floor lighting, shafts, surface waves and global lighting. The output screen then presents the interpolated opaque canvas and optional UI. Source textures/regions load once and stay immutable. The existing Auto 60→30Hz fallback and Performance mode remain.

Native graphics use documented roBitmap/roRegion/roScreen APIs. Actual device frame time, memory residency and activation/settings behavior require Roku validation.
