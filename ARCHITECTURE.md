# Native architecture

`RunScreenSaver()` owns the standalone roScreen aquarium. `RunScreenSaverSettings()` opens the separate SceneGraph settings context. There is no Main/RunUserInterface, video, runtime download or ordinary channel launch flow. Settings validate against one schema and persist in `deep-reef-v1`; Back/Done explicitly save and close. XML system fonts and HD/FHD layout scaling keep all options readable.

## Composition and registration

`tools/scene.py` builds the active 2048×1152 close-reef composition from `assets/source/reef-close-reference.png`. Coral spans the center and both sides, with a narrow strip of defined sandy foreground. The active source follows the user-supplied composition reference and keeps the established sunset colors.

`reef-midground-cutout.png` supplies clean RGBA coral, including transparent gaps between antlers. The original reference source supplies the photographic sand and manifest art. The cutout is registered over the sand and separated into sea fan, white crown, branching coral, green cup, center rock, brain coral, right garden and central clam. Overlapping seam underpainting prevents gaps during parallax. `tank.json.formations` records image origins, depth, thickness and parallax; `occupancy.json` uses the same silhouettes and depths. All lighting modes share the coral textures.

The background contains only ambient water and the original defined sand ridges. Reef pixels are drawn solely as the depth-sorted formations. The white crown retains a tiny continuous sway within the collision safety margin. The same eight-second wave phase drives surface motion and restrained floor brightness changes. No dapple layer is present.
## Fractional panning

The design-space camera is unchanged: Off fixes 64px; Subtle uses ±40px over 180 seconds; Slow uses ±56px over 240 seconds. Horizontal overscan remains 128px, with smooth cosine reversals.

Whole-pixel output placement caused visible stepping at this slow rate. `ReefLayer` now caches two regions sharing the same bitmap. Its fractional region has a 65536px pretranslation. `ReefLayerTransform` combines integer draw coordinates with floating-point scale to retain the desired fractional origin; the scale correction changes the width of a 2048px layer by less than 1/32px. A persistent transform object avoids per-draw allocation.

At startup `pan.brs` draws a hidden stripe probe into the back buffer and reads its pixels. It checks that a fractional placement changes the filtered stripe centroid. It tries scaled and, when available, transformed drawing, tolerates readback channel/row layouts, and falls back to the ordinary region if neither path works. The test pattern is cleared before the first presented aquarium frame. This is a runtime capability check, not an off-device assertion about the user's GPU.

The host float32 test at 720p/1080p finds less than 0.004px placement error and a maximum 0.03125px frame increment near the fastest point of the 60Hz pan. Actual presentation and GPU output still need device testing. Fractional placement also covers coral sway, wave overlays, bubbles, motes and shafts. Fish have a separate 4096px anchored transform that solves the rotated, mirrored fractional center. A second startup readback probe verifies that drawing path; unsupported paths use ordinary placement. Cached normal/fractional regions share each bitmap, with repeated mirrored views reusing the same region objects.

## Fish and collision

`aquarium.brs` owns seeded state, fixed 30Hz simulation and interpolated display time. XYZ endpoints interpolate; headings use cubic Hermite interpolation with endpoint yaw velocities. `fish.brs` bounds turn speed, angular acceleration and jerk, and ramps speed acceleration. Separation/alignment/cohesion remain in `schooling.brs`. Every nested fish visit is indexed for Roku's shared `ifEnum` cursor.

Fish use 64 yaw views, eight tail bends and nine independent fin strokes. A bilateral rig needs only 33 unique views for a full circle: opposite-facing views reflect horizontally and reverse the body bend, preserving which end faces the camera. Neighboring view widths interpolate continuously. Rendering draws an opaque base view and overlays the adjacent view by the fractional yaw weight; this retains opaque body interiors during the transition. Dense views and width matching limit silhouette fringe differences. This is sprite interpolation, not a runtime shader or anatomical mesh deformation.

Each formation has an 8px occupancy mask extruded over a finite depth interval. Swept projected rectangles include the body, tail, fins, maximum pitch and full camera sweep, using that formation's parallax. This is a conservative 2.5D collision representation rather than a sculpted physics mesh.

`scene.py` builds a small connected navigation graph offline. Nodes and edges must clear every species at maximum size, including pitch and camera travel. Runtime BFS runs only when choosing a destination. Visible waypoints are string-pulled to round open-water corners; local predictive braking and a final swept-volume sliding guard cover curved approaches. Front/rear destinations create reef exploration and sheltering. Open water above the crests allows side changes without passing through coral. Clownfish favor the clam, grammas favor rear shelter, and hovering/schooling remain.
## Drawing and pacing

Order: water/sand plate; fish, particles and eight formations interleaved by display depth; subtle floor lighting and remaining front fish; shafts, surface waves, global lighting and optional clock/FPS. Depth affects fish scale, tint and parallax.

The 60Hz target uses double-buffered SwapBuffers pacing without an extra sleep. Performance uses 30Hz with a pre-swap wait and GPU submission headroom. Auto settles at 30Hz after sustained output below 45 fps. Optional effect quality adapts gradually; principal fish remain. Previous/current bubble endpoints interpolate and reset together on recycling. A continuous display clock drives environmental animation between physics ticks.

Texture loads occur once. Missing decorations are skipped, memory warnings reduce optional quality and request GC, and failed display construction falls back from FHD to HD. The millisecond timer restarts daily; simulation/effect phases remain bounded. Native graphics use documented [draw interfaces](https://developer.roku.com/dev/docs/ifdraw2d) and [region pretranslation/scaling](https://developer.roku.com/dev/docs/ifregion).
