# Deep Reef 1.0.9 — targeted verification

The scene now displays 6/8/10 fish drawn from ten species, with a seeded shuffled roster and no repeated species. New portraits cover regal blue tang, copperband butterflyfish, Banggai cardinalfish and mandarin dragonet. Denser meshes, rounded body cross-sections, thinner peripheral fins, vertex-normal lighting, larger canvases and richer palettes improve model detail. The caudal-tail face set is disjoint from the body; exactly one body, one tail and one pectoral part are drawn. Bilateral view reuse fills 64 upright heading slots from 33 actual views without negative scales or anatomy crossfades.

Variable dark wave bands cross the existing sand highlights. Their curvature, width and strength vary with the same periodic field as the surface. The floor mask excludes coral and preserves photographed sand ridges. Reef composition, marine geometry and background plates remain unchanged.

| Check | Result |
|---|---|
| Native/settings compiler | PASS, BrighterScript 0.73.8 |
| Package/artwork/tracking | PASS, 32 Python tests |
| Fish geometry | PASS, disjoint body/tail faces, finite normals, higher mesh density and atlas bounds |
| Single anatomy image | PASS, one full-alpha body, tail and pectoral part per fish |
| Upright turning | PASS, full-circle pitched draw calls use positive scales |
| Reef layout/marine geometry | PASS, connected common foundation, registered seven-view marine volumes |
| Roster/animation | PASS, 6/8/10 unique species; every fish advances with native shared-cursor semantics |
| Targeted collision | PASS, 60 physics ticks, 8 fish, physical/interpolated footprints clear |
| Settings/waves/pacing | PASS, settings text/Back/Done and synchronized smooth wave timing |
| Sand shadows | PASS, changing floor-only atlas, bounded opacity, exclusion from coral |
| Pan geometry | PASS, production adjacent-pixel offsets; centroid error below 0.002px in tested segment |
| Browser inspection | PASS, all 48 runtime images, lighting/play/pause/seek, no page errors |
| Extended soaks | Not run; short validation requested |
| Actual Roku GPU/FPS | Not measured |

The refreshed conservative navigation graph has 252 connected nodes and 547 bidirectional edges. The install ZIP is below the four-million-byte budget; exact bytes and SHA-256 are in dist/build-report.json.

Roku loads only the species present. Estimated active Sunset image textures occupy 62.55 MiB at the default density and 68.53 MiB at High. Add 8.44 MiB for the scene canvas and 15.82 MiB for FHD double buffers (6.25 MiB at HD), before driver/interpreter overhead. These are dimension-based estimates, not measured residency.

Current short-gate logs are compiler, movement-regression, collision, settings, wave-smoothness, render-depth, upright-present, turn-smoothness, pan-precision and browser results. Earlier long simulation/raster/soak logs are historical. Check sustained smoothness and FPS on an actual Roku.
