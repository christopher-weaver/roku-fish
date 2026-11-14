# Native architecture

`RunScreenSaver()` owns the standalone roScreen aquarium. `RunScreenSaverSettings()` opens the separate SceneGraph settings context. There is no Main/RunUserInterface, video, runtime download or ordinary channel launch flow. Settings validate against one schema and persist in `deep-reef-v1`; Back/Done explicitly save and close. XML system fonts and HD/FHD layout scaling keep all options readable.

## Composition and registration

`tools/scene.py` builds the active 2048×1152 close-reef composition from `assets/source/reef-close-reference.png`. Coral spans the center and both sides, with a narrow strip of defined sandy foreground. The active source follows the user-supplied composition reference and keeps the established sunset colors.

Gradient-guided watershed segmentation and reviewed silhouette seeds produce opaque coral masks. The mid/front textures are cropped to their alpha bounds; `tank.json.layers` records exact origins and dimensions. They share one photographic color source rather than duplicating all reef textures for each lighting mode. Daylight uses cooler water and reef tint; Sunset uses the warm source. Night/dusk overlays and automatic local-time transitions remain.

The rear plate contains sky/water and the actual photographed sand. Hidden reef pixels are replaced by ambient water, avoiding a second full copy of the coral photo. Sand grain and ridges are retained, including their shaded grooves. `waves.py` adds a low-opacity light modulation using the same eight-second height field as the surface waves. The floor overlay stays within its floor mask and below foreground fish; it does not replace or smear the base sand texture.

The white coral crown has one separately masked texture. A tiny continuous horizontal sway and width change anchor it to its mid-depth position, avoiding repeated copies of the same detailed crown. Regions and bitmaps remain immutable once drawing starts.

## Fractional panning

The design-space camera is unchanged: Off fixes 64px; Subtle uses ±40px over 180 seconds; Slow uses ±56px over 240 seconds. Horizontal overscan remains 128px, with smooth cosine reversals.

Whole-pixel output placement caused visible stepping at this slow rate. `ReefLayer` now caches two regions sharing the same bitmap. Its fractional region has a 65536px pretranslation. `ReefLayerTransform` combines integer draw coordinates with floating-point scale to retain the desired fractional origin; the scale correction changes the width of a 2048px layer by less than 1/32px. A persistent transform object avoids per-draw allocation.

At startup `pan.brs` draws a hidden stripe probe into the back buffer and reads its pixels. It checks that a fractional placement changes the filtered stripe centroid. It tries scaled and, when available, transformed drawing, tolerates readback channel/row layouts, and falls back to the ordinary region if neither path works. The test pattern is cleared before the first presented aquarium frame. This is a runtime capability check, not an off-device assertion about the user's GPU.

The host float32 test at 720p/1080p finds less than 0.004px placement error and a maximum 0.03125px frame increment near the fastest point of the 60Hz pan. Actual presentation and GPU output still need device testing. Fractional placement also covers coral sway, wave overlays, bubbles, motes and shafts. Fish retain their separately interpolated poses, yaw atlases and pitch rendering.

## Fish and collision

`aquarium.brs` owns seeded state, fixed 30Hz simulation and display-time interpolation. `fish.brs` steers forward-swimming fish with limited heading acceleration, eased turn-speed reductions and gradual avoidance. `schooling.brs` supplies separation/alignment/cohesion. All fish/neighbor visits use indexed loops because Roku has a single enumeration cursor per object.

The six species retain 32 yaw views, eight tail bends and nine independent pectoral strokes. Larger fish textures use 224×196 canvases; smaller species use 208×182. The nominal physical display lengths increase by 60%, and source contrast/sharpness improve texture detail. Clownfish now explore around the central clam/coral area.

Both reef planes have conservative 8px occupancy maps. Swept projected rectangles include the full body, tail, fins, pitch and complete camera sweep. Safe spawn lanes, predictive avoidance and sliding movement prevent entering the reef; density remains 12/18/24. The crown's sway envelope is included at the correct mid-depth plane. This is conservative 2.5D occlusion, not a sculpted reef physics mesh.

## Drawing and pacing

Order: water/sand plate, rear particles/fish, mid reef/crown, mid fish, front reef, subtle floor lighting, front fish/particles, shafts, surface waves, global lighting and optional clock/FPS. Depth affects fish scale, tint and parallax.

The 60Hz target uses double-buffered SwapBuffers pacing without an extra sleep. Performance uses 30Hz with a pre-swap wait and GPU submission headroom. Auto settles at 30Hz after sustained output below 45 fps. Optional effect quality adapts gradually; principal fish remain. Previous/current bubble endpoints interpolate and reset together on recycling. A continuous display clock drives environmental animation between physics ticks.

Texture loads occur once. Missing decorations are skipped, memory warnings reduce optional quality and request GC, and failed display construction falls back from FHD to HD. The millisecond timer restarts daily; simulation/effect phases remain bounded. Native graphics use documented [draw interfaces](https://developer.roku.com/dev/docs/ifdraw2d) and [region pretranslation/scaling](https://developer.roku.com/dev/docs/ifregion).
