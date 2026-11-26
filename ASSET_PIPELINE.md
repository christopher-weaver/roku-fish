# Offline artwork pipeline

All runtime artwork and source pixels are included. No generation service, model weights, paid API, download or runtime server is required to rebuild.

```sh
python -m venv .venv
python -m pip install -r tools/requirements.txt
python tools/generate_assets.py
python tools/build.py
```

Activate the venv using the normal command for your shell. Full artwork regeneration also requires Blender 4.3+ on PATH. The headless mesh renderer uses ModernGL/EGL with Mesa on Linux; `LIBGL_ALWAYS_SOFTWARE=1` is supported. Windows/macOS can use a suitable EGL environment or Linux, and the optional Blender exporter remains available.

## Active inputs

- `assets/source/reef-connected-reference.png`: active connected RGBA reef; `background-matched-sunset.png` is its newly matched environment.
- `assets/source/marine-renders/`: Blender sources, finished textures, closed-volume NPZ meshes and seven-view metadata.
- `assets/source/reef-close-reference.png`: historical 1672×941 reference-inspired close reef. It preserves the requested sunset palette, full-width coral and defined sand ridges. Provenance and prompt notes are in `assets/source/PROVENANCE.md`.
- `assets/source/reef-midground-cutout.png`: historical generated RGBA isolation retained from version 1.0.6. The exact source pixels are checked in.
- `reef-original.png` and `empty-original.png`: retained historical sources used by earlier releases.
- Six licensed/refined photographic fish portraits and four new generated portraits, plus source sheets. The Paul Robello MIT notices and provenance remain in `assets/licenses/` and CREDITS.
- `*-texture.png`, `*-pectoral.png` and NPZ volumes are derived from those portraits and rebuildable offline.

## Connected reef and matched environment

`reef-connected-reference.png` is a generated RGBA reef based on the user's updated composition reference. `connected_scene.py` registers it to a common foundation and creates complementary mid-ground/foreground masks. These are native-resolution crops, not enlarged 448px island images. Coral color uses WebP quality 88 with preserved alpha. The guide used to recreate the environment is retained as reef-layout-guide-geometry.png.

`background-matched-sunset.png` was generated after fixing object positions, retaining matching water/sand perspective, lighting and contact darkening while removing the reef. Sunset and cooler Daylight runtime plates derive from these pixels. `waves.py` uses the new sand texture and excludes coral footprints from the animated floor-light mask.

## Fish-style 3D marine objects

`render_marine.py`, run with Blender, produces actual curved sea-fan and tentacle geometry and transparent Cycles renders. The original .blend/.png files are retained under marine-renders. An image-tool finishing pass adds natural anatomy and surface detail; its original sheet and extracted RGBA objects are included.

`marine_views.py` turns the finished textures into closed front/back volumes with stitched edges, fan curvature and anemone thickness, following the fish's textured-volume approach. It exports NPZ geometry and seven sharp, depth-tested camera angles from -8 to +8 degrees. Hidden fan pixels behind the fixed reef are cropped before packing. A 128-color, lossless WebP container compacts the view atlas without spatial blur. Metadata records frames, columns, origins, root height and mesh sizes. The runtime chooses one view, never a view crossfade.

`art.py` invokes the connected scene and waves; `generate_assets.py` rebuilds runtime art from checked-in source pixels and meshes without a generation service. To recreate the initial procedural Blender models separately, run `blender --background --python tools/render_marine.py`; the finished material sheet remains a fixed art input.

## Fish

`fish_mesh.py` fills 64 heading slots from 33 upright bilateral views with positive scales. The reverse half reuses matching body/fin views and reverses caudal-bend phase; it never reflects a runtime sprite. Each direction has one body image, four independently bent caudal-tail poses and five hinged pectoral-fin poses. Body and tail face sets partition the complete mesh without duplicating any tail geometry. Tail and pectoral passes are depth-tested against the body. Rounded anatomical cross-sections, thin peripheral fins and vertex-normal lighting replace the older uniformly inflated relief. Source grids are 384 samples wide, canvases are 240×210 or 224×196, and renders use 4× supersampling. Fin crops remain half resolution with explicit 2× scale and fractional anchors. Only species actually present are loaded on Roku.

`extract_additional_fish.py` extracts the four new portraits from the fixed source sheet; it does not require a generation service. `optimize.py` quantizes fresh raw atlases without dithering into lossless WebP. Body palettes use 144 colors, tails 112, fins 80. Coral and backgrounds are unchanged from 1.0.8. `waves.py` adds a 32-frame dark shadow atlas using the same periodic field as the surface and sand light; the photographic highlights and grain remain beneath it. `catalog.py` records dimensions/checksums and `build.py` checks all three fish-part atlases and the four-million-byte ZIP budget. Raw atlases are cached under ignored work/fish-raw; never repeatedly quantize delivered images.

## Preview and editing

```sh
node tests/roku_runner.cjs --root roku roku/source/math.brs roku/source/camera.brs roku/source/settings-model.brs roku/source/aquarium.brs roku/source/fish.brs roku/source/schooling.brs roku/source/effects.brs tests/export_preview.brs > work/frames.log
python tools/preview.py
python -m http.server 8000
```

Create `work/` first. The export records the production brain, not a separate fish simulator. The preview reads current layer and wave metadata, so cropped registration matches the native renderer. Open `http://localhost:8000/docs/preview.html` for lighting/seek/play inspection. It does not establish Roku GPU output.

Optional Blender editing:

```sh
blender --background --python tools/blender_render.py -- --species yellow_tang --output work/blender
```

The exporter reads the same NPZ rig and photo textures, supports fin poses 0–8, and saves an editable blend. These remain inspection/replacement renders; the production atlas build uses ModernGL. The meshes are silhouette-derived textured volumes rather than anatomical scans.

## Adaptive turns and continuous marine bending (1.0.10)

`dense_turns.py` follows the base fish build and renders 53 unique body views from the checked-in mesh/texture sources. Mirrored heading coverage fills 104 positive-scale slots. Sampling reaches 1.40625° between 78.75° and 101.25°, and 0.703125° immediately around 90°; equivalent backside slots are reused without runtime reflection. `ReefBodyView` searches the nonuniform angles and continuously matches the body silhouette width. Tail/pectoral atlases remain separately articulated. No anatomy crossfade is added.

Marine bitmaps retain their seven photographic 3D-volume views. Immutable eight-pixel bands share each bitmap; a continuous two-frequency displacement/stretch field bends branches and tentacles without generating a frame atlas or modifying bitmap pixels at runtime. Vertical band boundaries share positions and roots remain pinned. Performance mode uses sixteen-pixel bands. Native fractional placement provides motion between integer pixels. Conservative occupancy reserves the entire tip excursion before navigation is rebuilt.

`turn_check.py` compares actual adaptive body rasters with the 64-angle subset using single-pose rendering in both cases. It checks peak frame changes around head-on turns. Native tests also cover nonuniform width continuity, fish encounters, interpolated collision clearance and marine roots/band boundaries.

## Coherent marine poses, tunnel eel and cellular shadow (1.0.11)

`marine_animation.py` deforms the original closed NPZ volumes offline and bakes 65 complete poses along a continuous signed current parameter. The roots remain fixed, while branch/tentacle tips bend in different directions. Runtime chooses the nearest signed pose from a sinusoidal display clock and draws exactly one complete object at a fixed position and scale. There are no runtime strip transforms, oversized anchors, camera-yaw switches or anatomy crossfades. Dense spatial poses limit tip changes to a fraction of a design pixel; source texture sizes are compacted to stay within practical texture memory. The fan uses half design resolution and the anemone about three quarters, rendered offline with supersampling.

`formation_frames.py` reads static/animated pages and rebuilds conservative occupancy/navigation from the union of all poses. The existing rigid reef and background plates retain their resolution and pixels. Fish bodies now use 112 heading slots, including finer sampling across 84.375°–95.625°. Body palettes are 80 colors for the two small chromis/gramma portraits and 96 for the others; tail/fin palettes are 80/64 colors in lossless WebP, with no spatial blur; keep their original RGBA renders in the ignored work cache when tuning compression. Marine palettes use 64/80 colors with near-opaque alpha normalized.

`cave_and_net.py` derives a small moray sprite from the checked-in generated source and a recessed matte from the actual enclosed reef tunnel. The eel uses quintic easing and a slow 31-second cycle with pauses; existing rock pixels occlude the head. The plate below the tunnel is restored before fish/coral rendering to hide the neck. A seamless, padded 32-frame cellular wave-net shadow tile casts softly across the whole scene. Its 16 alpha levels are temporally interpolated, and periodic padding prevents tile seams.

The full offline build runs the base art, additional fish directions, coherent marine poses, navigation, waves and cave/net generation before packaging. No runtime network or image generation is required.

## All-reef geometry and receiver lighting (1.0.12)

`reef_geometry.py` partitions the approved reef colour projection into named coral/live-rock groups and builds closed front/back volumes with anatomical curvature: cup concavity/fluting, rounded bubble/brain forms, clam folds, plating relief and branching silhouettes. Shared boundary coordinates preserve the touching composition. Checkerboard corner contacts have separate vertex pairs, and topology checks require exactly two incident triangles at every closed-volume edge. There are eighteen closed static mesh parts across ten anatomical/support groups, plus a separate open-ended hollow bore. The tunnel follows the actual irregular opening, tapers/recedes in depth and maps stone from the surrounding rim onto its inner walls. The existing fan/anemone retain their 3D volumes and coherent animation.

NPZ geometry, UVs and normals are in `assets/source/reef-model/`; `save_reef_blend.py` creates the packed, editable `reef-scene.blend`, including the marine objects and the actual moray positioned in the tunnel. The original frontal reef image supplies UV colour. Current native-resolution renders preserve the approved composition; the Roku runtime composites these pre-rendered mesh views.

`render_eel_3d.py` creates the moray in Blender from closed meshes: swept neck with shape keys, head/snout, jaw hinge, eyeballs, irises, pupils, nostrils and teeth. Skin is a procedural Voronoi/noise material. No portrait image is used. The model, animation and geometry exports are in `assets/source/eel-model/`. `pack_eel_3d.py` packages twenty-five lit poses, while the existing eased emergence controls the character's movement through the tunnel.

`surface_lighting.py` replaces the screen-wide net with broad, smoothly blended wave bands in a projective coordinate system. Cell size increases toward the foreground. Two compact static reef receiver atlases use conservative opaque-coverage masks; their upsampled alpha must be exactly zero outside the receiving geometry. Sand has a separate receiver mask. Thin/animated objects and fish use the same continuous wave field for material lighting. This avoids darkening open water and removes the previous tiling overlay.

The complete generator now runs Blender for the eel/source scene and ModernGL for the volume renders before rebuilding masks, navigation and lighting. Checked-in runtime assets let `tools/build.py` package the screensaver with Python's standard library alone.

## Shared cave scene and fish exclusion (1.0.13)

`cave_geometry.py` defines the common photo-world coordinates for the five-ring bending chamber, closed rear wall, pinned moray body, moving head/jaw and reserved fish volume. The mouth is the only open mesh boundary. The rear body ring remains fixed while the head travels from Z=-124 to Z=120, through the front lip at Z=90. Original rounded head, eyes, jaw and teeth remain volumetric geometry.

`cave_stage.py` renders 65 emergence states with a shared depth buffer. Surrounding reef meshes are depth holdouts: recessed body parts disappear behind the lip, while emerged parts can pass in front. The cave is rendered at the connected-reef depth, before foreground swimmers and coral. It uses neither a translated portrait nor a background repair patch. Tight shared cropping keeps the atlas within device texture limits. `pack_eel_3d.py` now invokes this joint renderer. The complete Blender reef scene contains the identical pinned body poses as editable shape keys.

`formation_frames.reserve_navigation()` records the cave volume in occupancy. Runtime `ReefCaveBlocked` tests continuous swept fish envelopes against it before the coral-plane checks, including maximum pitch, fins and camera margins. The offline navigation graph reserves a slightly larger envelope. Spawns, destinations, routes and final movement guards therefore agree. The resident eel is separate from the free-swimming roster.

Wave field alpha increases from 60 to 72 on ground/reef receivers; fish use 0.30 of the new field, making their modulation 0.36 of the previous release. The background-exclusion masks and soft perspective projection are preserved. This section supersedes the earlier portrait/matte and open-ended-bore workflows.

## Closed fish joins, solid ground and sculpted marine anatomy (1.0.14)

`fish_mesh.closed_shell` joins the two sampled body surfaces with five intermediate curved perimeter rings. Every shell edge has exactly two incident faces, including checkerboard corner splits. Area-weighted normals smooth the join. `wrap_texture` extends interior RGB through the old cutout fringe, while geometry supplies body alpha. This prevents the central dark belt/gap in head-on turns. Body, tail and pectoral atlases are regenerated for all ten species; the 112 adaptive body heading slots are retained.

The moray head follows `head_pose`: Y=875 while inside, followed by a 27-pixel quintic lift after 62% emergence. Head depth travels from -124 to 230. Smaller, inset eyes retain real eyeball/iris/pupil geometry. The curved blind chamber is wider behind its mouth. All vertices of every one of the 65 emergence states are checked against its actual interpolated walls, and the final head lies beyond the lip. A matte interior replaces the bright rim sample. The reserved cave volume extends forward to cover the longer exposed head as well as the entrance. The rear body stays anchored.

`seafloor.py` creates a textured 16,705-vertex ridged floor spanning actual depth, with matching native ground-plane collision data. The water plate no longer supplies the foreground sand. A shared sand image receives a cool material tint outside Sunset. The projected sand ridges, wave highlights and shadows are retained. Closed `grounded-footings.npz` geometry extends the low reef into the floor; conservative depth slabs prevent free fish from traveling below the reef. The same body/pitch/fin envelopes constrain spawn, routes, sweeps and final movement checks. The 3D source scene includes the floor and footings.

`living_reef.py` models an anemone with 84 independently bending closed tentacle tubes and a solid oral base. The fan has a trunk, 18 primary branches and 108 smaller tubular branches. Their animation displaces actual 3D vertices before depth rendering; no source picture or image ripple supplies their anatomy. Sixty-five coherent states remain cached on Roku. Additional closed bubble and brain coral sculptures use detailed source colours as opaque wrapped textures with smooth edge extension. The other reference-aligned reef forms retain their closed phototextured volumes. Material texture detail stays distinct from the actual modeled surface.

The source Blender scene includes these meshes, floor, structural footings, tentacle/branch deformation keys and the pinned moray. GPU mesh rendering remains offline; Roku presents the resulting cached images. The 4,000,000-byte package limit remains enforced.

## Reference-matched marine life and eel expressions (1.0.15)

`approved_fan.restore` copies the approved 1.0.13 fan atlas, footprint, mesh and exact formation metadata from `assets/source/marine-renders/approved-fan/`. A regression test compares the runtime atlas byte-for-byte and the complete formation data. The replacement tubular fan is removed. The offline generator restores the approved fan on every run.

The anemone has a closed, recessed oral disc and one hundred separately curved, capped 3D tentacle tubes with spherical peach bulbs. A radial 3D arrangement, varied S-curves, visible mouth, low body and short foreground fingers follow the earlier picture. Each finger has pinned roots and its own three-axis displacement. Original surface color is wrapped over the geometry with opaque RGB extension through cutout gaps; alpha comes from the mesh, not from the reference picture. Sixty-five complete poses preserve smooth motion. The full anatomy and deformation keys are present in the Blender source.

The moray's exposed head depth increases from 230 to 280 and receives a smoothly stronger warm key light outside the cave. The 65 emergence states remain. Sixteen additional articulated jaw poses and sixteen squint/grin poses share the same cave depth test, producing 97 cached states in total. Jaw opening rotates real lower-jaw geometry around its hinge, and the cavity changes volume to fill the mouth. The funny expression squints one smaller eye, shifts the pupils and tilts the jaw. Native and preview selectors match: a brief gape during each fully-emerged hold, a funny expression on alternate holds, and neutral intervals between them. No expression overlay or pose crossfade is used.

The cave reservation covers the exposed head. If neither usual spawn depth is clear, `ReefSafeSpawn` selects the nearest safe navigation node. Existing fish envelopes, ground, reef and cave checks still apply. Packaging continues to enforce the tracked ZIP and the 4,000,000-byte limit.

## Thicker anatomy, natural skin and route recovery (1.0.16)

The anemone now has 64 closed tentacle tubes. Root radii are 5.2–7.4 design pixels, with fuller middle sections and tapered rounded ends. Separate spherical tip decorations are removed. Cream, pink and muted violet tissue bands follow the new reference. Geometry tests count the connected components and measure actual root-ring diameters; the approved fan is still restored byte-for-byte.

The moray shader replaces the sine-product lattice with domain-warped 3D value noise at multiple scales. The material uses rest-position coordinates from the original mesh, so its irregular olive-brown mottling and fine pore variation follow the animal during emergence and expressions. The Blender materials also use organic noise; the former honeycomb shader is removed.

`ReefSwimPose` adds a small 3D yaw oscillation and gentle bank around an approximate head pivot, synchronized with the existing caudal phase and scaled with swimming effort. Body, tail and fins use the same continuous display pose. Physical positions are untouched; existing yaw/pitch envelopes and clearance margins cover the small display offsets. There are still exactly three draws per fish, with no new textures, anatomy crossfades or slice seams. Preview exports now include the real swaying display pose.

Obstacle lookahead follows stopping distance rather than always projecting five seconds ahead. Avoidance preserves steering propulsion and neighbor separation while the swept guard remains authoritative. Routed goals expire, and arrival tolerances no longer leave fish circling an unreachable final point. Every six seconds, staggered progress checks detect a distant goal with less than 28 pixels of net movement. Recovery chooses a visible, unoccupied navigation node or a smaller locally swept escape. A tighter recovery arrival radius keeps the fish moving far enough to leave the obstruction. No recovery directly changes position or heading.

Passing lanes are tested against the reef and ground. When one preferred lane is blocked, one fish holds its lane while the other uses clear water; fish do not turn back into an already separated neighbor because the floor blocks further separation. Targeted regressions cover three stalled reef routes, five encounter patterns including the actual floor/reef, and production body/tail/fin transform continuity.

## 1.0.34 fish motion and eyes

`python tools/lateral_swim.py` bakes stronger lateral S/inverse-S poses and separate signed C-turn mesh poses. It also attaches two ellipsoidal eyeballs per fish, using iris/pupil crops from the existing photographs. Geometry and eye textures are checked in under `assets/source`. `fish_anatomy.py` defines the S/C curves; `fish_eyes.py` defines anatomical eye anchors. The native body retains 25 dense frontal samples, with fewer redundant side views, at unchanged per-fish pixel resolution. C-turn poses share the body atlas. Straight swimming and turning each need at most four body submissions, plus one attached caudal tail and one fin image. The caudal root follows the blended model deformation.

`compact_swim.py` can repack an older denser atlas without changing retained pixels. `compact_fish_palette.py` reduces colors without resizing or spatial filtering, retains every alpha pixel, and reports visible RGB error before updating the asset catalog. Packaging still enforces the 4 MiB sideload limit.

## 1.0.35 continuous C silhouettes

The curved bank retains the same 25 frontal samples as straight swimming and adds entrance/exit views. Broadside slots reuse neutral projections. `turn_cores.py` builds small masks inside both neighboring silhouettes; `lateral_swim.py` invokes it after baking. Their per-frame reference widths/anchors let the compositor keep an opaque interior while the outgoing outline fades. Only masks are quarter resolution. No skin image is downsampled.

`compact_fish_palette.py --part body|tail|fin --colors N` compacts RGB while preserving alpha exactly and recording per-pass error. Selected palette sizes are retained in species metadata for later bakes. The source-matched package remains under the 4 MiB limit. `turn_capture_check.py` evaluates the actual tilted C-turn submissions across every critical boundary in both directions; it catches the v34 outline handoff that neutral-view checks missed.
