# Source provenance

Original reef generated 2026-11-13 using the session's available image-generation tool. Source output identifier: `exec-75517e18-2b6e-49e2-bfaa-0e5bdacb0d4f`. Original 1672×941 RGB image is retained as `reef-original.png`.

Prompt:

> Create a photorealistic underwater photograph for a premium realistic saltwater reef aquarium screensaver, absolutely not an illustration or painting. Wide landscape 16:9, view straight through aquarium front glass. Empty of fish and animals that swim. Clear deep blue turquoise water filling upper 55 percent; subtle water surface at top; pale finely rippled white sand in the bottom quarter. Asymmetrical natural established live rock reef mounds at left and right, with swim-through arches and caves, branching muted purple Acropora, yellow-green brain coral, muted orange plate corals, small zoanthid colonies, delicate cream soft coral and small anemones at lower left. Broad central open sandy channel and ample open water. Natural restrained biologically plausible coral colors, crisp detailed porous rock textures, gentle mottled sunlight caustics from above, visually beautiful natural aquarium photography, no borders, no text, no logos, no screens, no diagram. Landscape photograph.

Empty aquarium edit identifier: `exec-e5881eaa-b98d-4775-add2-35a6aadb8d16`, retained as `empty-original.png`, same input image.

Edit prompt:

> Edit this exact aquarium photo: remove ALL rock formations, ALL coral, ALL plants, and ALL anemones. Fill the now empty aquarium naturally with the SAME clear blue turquoise water and rippled pale sand. Keep the camera perspective, existing sandy bottom depth and horizon, existing water surface, and exact same natural light colors and sun rays. The result is an EMPTY aquarium plate containing just clear water, delicate sunlight and a sandy bottom. No animals. No new rocks or plants. Preserve the original image dimensions and framing. Photorealistic.

The model's seed and underlying model version were not exposed. Regeneration from these prompts is not deterministic. Offline reconstruction from the supplied source pixels is fully implemented and needs no generation service. The sunset palette was subsequently requested by the user and implemented deterministically in `tools/art.py`, with matching occlusion/soft-coral colors. No third-party image reference was used for that original reef generation. The active 1.0.5 composition below uses the user-supplied reference.

The six licensed reference portraits originate from Paul Robello's MIT-licensed roku-fishtank revision `8560cf0d3cfd22e267cf2d7ecdd1cfd80554914c`. Original provenance and license notices are retained under `assets/licenses/`. Normalized texture PNGs and NPZ meshes are derived by fish_mesh.py and are rebuildable from those originals.

## Photographic fish refinement

The six licensed portraits were arranged into the 1800×1000 transparent `fish-studies.png` reference sheet. The session image tool edited that sheet into `fish-photographic-sheet.png`, output identifier `exec-2c2dcb0f-ef9b-4458-94d1-a71d8582edec`, 1683×935 RGBA. The derived portraits retain the MIT attribution. `tools/split_fish.py` reproduces the six source PNGs by cropping the 3-column/2-row grid; the mesh generator reads those PNGs. The complete source pixels are included, so later offline rebuilds require no generative tool.

Refinement prompt:

> Transform this six-fish reference sheet into SIX ACTUAL PHOTOGRAPHIC marine fish, looking absolutely like real saltwater aquarium macro photographs, not illustrations, not cartoon fish, not plastic or CGI. Preserve exactly the 3 columns by 2 rows arrangement and each fish entirely inside its original cell with generous empty transparent margins. Exactly six fish, all full-body right-facing side profiles. TOP ROW: ocellaris clownfish (real small black eye, natural orange, three irregular white black-edged bands); yellow tang (realistic pointed mouth and thin semi-translucent fins); royal gramma (purple front half, yellow rear half). BOTTOM ROW: adult emperor angelfish (real natural sinuous yellow blue stripes); Moorish idol (black white yellow bands, long dorsal streamer); blue-green chromis (slender small reef fish with iridescent blue green scales). Each subject must be a real anatomically plausible adult fish, with realistic wet scale texture, small natural eyes, subtle translucency in fins, photographed under the same soft aquarium light from above and slightly in front. Tone down excessive saturation to natural biological colors. Improve volume and lifelike appearance, reduce the big cartoon eyes. Keep entire tails and dorsal streamers visible without touching cell edges. Transparent background. No water, no bubbles, no shadows, no text, no border. All six fish isolated individually with clean transparent edges.

This is generated photorealistic artwork rather than photographs of real specimens. The fish meshes still use silhouette-derived volumes; no anatomical scan is implied.

## Active close-reef plate — 2026-11-14

`reef-close-reference.png` is the active source for version 1.0.5. It is a 1672×941 RGB generated image, output `exec-0b716c42-fda0-442b-ad1c-3e6cf5aee97f`. The user supplied a small aquarium image as a composition reference: larger fish, a closer full-width coral reef with no empty middle, and defined sand. The tool created a new fish-free photographic-style background with the established sunset palette; live fish are added by the renderer.

Prompt essentials: wide 16:9 straight-on aquarium photograph; continuous dense tropical coral across the entire width including the center; close-up scale; varied brain, branching, soft and plating corals; narrow foreground sand with clear shaded ripple ridges; warm pink/orange/red water light with natural distinct coral colors; no fish, bubbles, text, UI, logos, shafts or dappled spot overlay. The source file is retained exactly as generated, so subsequent builds use its pixels offline and need no image-generation service. This is generated artwork, not a documentary photograph of a real aquarium.

## Mid-ground reef isolation (1.0.6)

`reef-midground-cutout.png` is the unmodified 1752×900 RGBA output of the session image tool, identifier `exec-675b3241-9e8c-4655-b415-22e6440f7494`, edited from `reef-close-reference.png`. The prompt requested a precise transparent coral/rock/clam cutout, preserving the reference layout, photographic detail and sunset lighting; removing all sky, clouds, water and sandy ground; making every gap between antlers transparent; and adding no fish, text or new background. The source is generated artwork rather than a real aquarium photograph. Runtime layers, masks and navigation rebuild offline from these exact pixels. The original reference source continues to provide the sand and manifest artwork.

## Sparse coral collection (1.0.7)

`coral-islands-sheet.png` is the unmodified 1536×1024 RGBA output of the session image tool, identifier `exec-4ca4646f-3cdd-47b2-a9c3-103e706c0a4b`, referenced to reef-close-reference.png. The prompt requested six separated photorealistic objects in a 3×2 transparent grid: cream branching coral on a live-rock arch, orange antler coral, green cup coral, rounded red/mint brain coral, giant clam/zoanthids and purple fingers/orange plates. It requested preserved sunset lighting, shaded three-quarter volume and clean transparent gaps, with no fish, text, floor or sky. Source alpha is retained; preprocessing normalizes near-opaque cores and near-transparent fringe. Derived individual objects, silhouettes and render metadata are in coral-islands/. Runtime images are actual three-view height-field mesh renders from coral_render.py. All rebuilding is offline from checked-in pixels.

## Connected reef and marine volumes (1.0.8)

The user supplied a new aquarium image to specify a touching reef, common baseline and spacing. `reef-connected-reference.png` is the unmodified image-tool RGBA output `exec-c35594b6-bf75-4fc7-96f5-6c15b584e9a5`: a fish-free, connected live-rock reef with left green cup, center-left white crown/cave, right antler pillar, pink bubble and brain corals, small foreground clam, right plating coral and zoanthids. The prompt excluded fish, water, floor, framing, lettering and logos, and retained a nearly common foundation.

`render_marine.py` created the original sea-fan and anemone geometry and Cycles images (.blend and .png files under marine-renders). These two renders were references for the natural anatomy/material finishing sheet `organic-finish-sheet.png`, unmodified output `exec-1039f629-68d7-4e85-a941-d6879b05abe5`. The prompt requested separated transparent objects, natural dense gorgonian branches/polyps and fleshy green/cream anemone tentacles with pink tips, photographic detail and no defocus/ghosting. Extracted finished PNGs retain their alpha. They are art inputs to the fish-style closed volumes in marine_views.py, not a claim that the final pixels are untouched Cycles output. NPZ meshes and seven-view render metadata are included. The fan uses shared sheet curvature plus front/back thickness; the anemone uses a thicker rounded volume. Both are depth-tested in ModernGL and packed as single-view selections with no pose crossfade.

The reef and rendered-object placement was fixed before creating `background-matched-sunset.png`, unmodified output `exec-9628305d-eb2e-4d2e-850f-20e94c9f1ba7`. Its reference guide is retained as reef-layout-guide-geometry.png. The prompt removed every coral/rock/fan/anemone while retaining camera framing, the shared foundation height, matching warm underwater lighting, subtle contact shadowing and crisp fine sand/ridges. Daylight is derived from those same pixels. All runtime rebuilding is offline from checked-in source artwork.

## Four additional species and improved fish volumes (1.0.9)

`fish-additional-sheet.png` is the unmodified RGBA image-tool output `exec-f9bfa87c-53be-4667-ae75-a8a7b0030a62`, using fish-photographic-sheet.png as a photographic-style reference. The prompt requested four separated, full, right-facing side profiles on transparency: regal blue tang, copperband butterflyfish, Banggai cardinalfish and mandarin dragonet, with realistic scales, gill covers, eyes and fin rays, no text or scenery. These are illustrative generated portraits, not scientific anatomical scans. `tools/extract_additional_fish.py` reproducibly extracts the four checked-in source portraits, removes almost-transparent fringe and normalizes near-opaque alpha. Existing portrait licenses remain unchanged. New original artwork is covered by the project's CC0 art dedication.

`fish_mesh.py` builds denser closed textured volumes with rounded body cross-sections, thinner peripheral fins and per-vertex normals. The complete face set is partitioned into disjoint body and caudal-tail sets; independently bent tail poses are depth-tested against the body. Source NPZ files preserve the full mesh, partitioned faces, normals and pectoral geometry. Rendering remains entirely offline.

## Adaptive rotation and marine animation (1.0.10)

No new source photographs or generated artwork are introduced. `dense_turns.py` renders additional angles from the existing NPZ body faces, vertex normals and UV textures. Runtime marine bending acts on immutable bands of the existing closed-volume renders; their source geometry, texture provenance and licenses remain unchanged.

## Tunnel moray and complete marine motion (1.0.11)

`cave-eel-original.png` is the unmodified transparent image-tool output `exec-6c17a462-be5b-4dd9-829b-e4ab0239254b`. The prompt requested a single photorealistic olive/gold honeycomb moray head and upper neck, three-quarter view toward the viewer and left, slightly oversized inquisitive eyes, a crooked friendly grin, warm underwater light, and no rocks, water, text or props. Its anatomy is illustrative and its expression deliberately exaggerated. `cave_and_net.py` extracts/resizes the fixed source offline; original art follows the project's CC0 dedication. The tunnel matte is derived from the user's existing approved reef layout.

Marine animation uses the existing NPZ volumes and finished textures, with complete deformed poses rendered offline by `marine_animation.py`. No new coral artwork is generated. The cellular net shadow is original procedural art with periodic sites and coordinate warping. Existing portrait/reef licenses are retained.

## Modeled moray, reef volumes and soft surface lighting (1.0.12)

`eel-model/zany-moray.blend` and its NPZ/pose files are original procedural 3D artwork generated by `render_eel_3d.py`. Every visible part is mesh geometry; skin uses procedural Voronoi/noise, with no portrait image input. The earlier generated portrait remains historical source material and is absent from runtime assets. Model and rendered artwork follow the project's CC0 art dedication; application/generator code retains the project license.

`reef-model/` contains the approved reef image's UV colour projection, individual closed-volume NPZ meshes and the packed Blender scene. Geometry is reconstructed from the existing reef silhouettes with anatomically shaped depth fields, shared touching boundaries and a separate tapered hollow tunnel. The Blender scene also includes the existing marine volumes and the actual articulated eel. Existing texture licenses and provenance remain unchanged. This preserves the established frontal composition with editable 3D geometry.

Projected wave shading is original procedural art, applied through conservative surface masks and object material tints. No new generated reef image or third-party 3D asset is used.

## Photographic marine materials and shell occlusion (1.0.18)

No new external artwork is introduced. `marine_materials.py` extracts tissue/shell maps from `marine-renders/sea-anemone-finished.png` and `coral-islands/central-clam.png`, preserving their existing art provenance and license. The maps are attached to individual tube/valve UVs, and included in the packed Blender source. Original procedural geometry is retained. `clam_occlusion.py` derives foreground masks from the depth-rendered shell and reuses the main atlas pixels. `compact_marine.py` packages photographic poses, preserves 80% tentacle opacity, and creates small original branded menu/splash images to reserve package space for the scene.


## Recessed anemone and illuminated clam lining (1.0.19)

No new external artwork is introduced. `anemone_pocket.py` builds an original closed U-shaped rock rim, with photographic colour projected from the existing approved reef and a matching depression in the reef/foundation volumes. The anemone's original photographic tissue maps and 80% tentacle opacity are preserved. The clam lining uses the existing photographic interior material, fitted to a shallower pale mantle. Foreground shell masks exclude the lining, so contents exist at full opacity behind the shell and are progressively uncovered by opening geometry. Source meshes, colour projection and the packed Blender scene are included. Existing artwork licenses remain unchanged.
