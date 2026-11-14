# Deep Reef 1.0.8 — targeted verification

The fish renderer now draws one coherent body/tail pose and one fin image. Ghost-producing anatomy overlays, coral-view crossfades and repeated per-layer pixel blends are removed. Native-resolution reef layers use exact 1:1 copies. The touching, reference-aligned reef rests on a shared foundation; water/sand backgrounds were recreated after fixing that layout.

The sea fan and anemone use fish-style closed, UV-textured 3D volumes with stitched edges, curvature/thickness and seven rendered viewing angles. Their actual NPZ geometry and source Blender scenes are included. The renderer selects one sharp marine view at a time. This is the same family of hybrid 3D/2D technique as the fish, not a runtime shader or anatomical scan.

| Check | Result |
|---|---|
| Native/settings compiler | PASS, BrighterScript 0.73.8 |
| Package/artwork/tracking | PASS, 30 Python tests |
| Single anatomy image | PASS, one full-alpha body/tail and one fin per fish |
| Upright turning | PASS, full-circle pitched draw calls use positive scales |
| Marine geometry | PASS, actual mesh vertex counts, nonzero depth, seven-view atlas bounds |
| Reef layout | PASS, dominant connected assemblage, shared root line and registered layers |
| Every-fish animation | PASS at Low/Medium/High density with native shared-cursor semantics |
| Targeted collision | PASS, 60 physics ticks, 18 fish, whole physical/interpolated footprints clear |
| Settings/waves/pacing | PASS, existing menu closure/labels and simulated display timing |
| Pan geometry | PASS, production adjacent-pixel offsets; centroid error below 0.002px in tested segment |
| Browser inspection | PASS, 23 images, lighting/play/pause/seek, no page errors |
| Extended soaks | Not run; short validation requested |
| Actual Roku GPU/FPS | Not measured |

The graph has 255 connected nodes and 558 bidirectional edges with precomputed next hops. Collision reserves the union of marine view silhouettes. Wave-driven sand light is rebuilt from the new background and excluded from coral footprints.

Estimated active Sunset textures occupy about 96.7 MiB decoded RGBA. Including the 8.44 MiB canvas and FHD double buffers gives about 120.96 MiB; HD gives about 112.17 MiB before driver/interpreter overhead. These are dimension-based estimates, not measured device residency. Exact release bytes and SHA-256 are in dist/build-report.json.

Current short-gate logs are package, compiler, movement-regression, collision, settings, wave-smoothness, render-depth, upright-present, turn-smoothness, pan-precision and browser results. Earlier long simulation/raster/soak logs are historical, not current-build evidence. Check actual upright appearance, sharpness, smoothness and sustained FPS on the user's Roku.
