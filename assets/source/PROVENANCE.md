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
