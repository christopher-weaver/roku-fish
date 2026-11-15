# Deep Reef 1.0.12 — targeted verification

The moray is an original articulated 3D model with procedural skin, moving neck/jaw, spherical eyes/pupils and teeth. Twenty-five rendered poses replace the portrait. The existing eased emergence and tunnel occlusion remain. Editable source models and a combined Blender reef scene are included.

All coral/live-rock groups now have real UV-textured volume meshes. The static reef uses 19 structural parts, totaling 597,226 vertices and 1,193,912 triangles: eighteen closed parts and an open-ended tapered tunnel bore. The tunnel follows the original irregular opening and samples stone from its rim. Existing fan/anemone models keep their coherent sixty-five-pose animation. Original reef colour supplies the frontal UV projection; Roku displays offline mesh renders.

Broad caustic bands replace the tiled screen net. Projective cell sizes grow toward the foreground, with smooth dark-to-light transitions. Conservative receiver masks keep every upsampled coral-shadow pixel inside opaque reef coverage. Sand uses a separate mask; fish and animated objects receive matching continuous wave lighting. Open-water pixels are untouched by this shadow pass.

| Check | Result |
|---|---|
| Native compiler | PASS, BrighterScript 0.73.8 |
| Package/artwork/tracking | PASS, 38 Python tests |
| Static reef topology | PASS, every edge of all eighteen closed mesh parts has two incident triangles |
| Tunnel geometry | PASS, receding/tapered front/back rings with real depth |
| Eel geometry | PASS, non-flat mesh, jaw/eye/pupil parts, 25 bounded render poses, no portrait texture |
| Water exclusion | PASS, all 32 phases per reef receiver have zero alpha outside opaque coral after upsampling |
| Shadow perspective/softness | PASS, depth-scaled cell periods and bounded spatial gradients |
| Native object lighting | PASS, bounded intensity, continuous time and periodic/projective sampling |
| Native drawing | PASS, water plate untinted, surface overlays ordered with their geometry, one coherent marine draw |
| Fish behavior/traffic | PASS, lateral/home-depth behavior and swept/interpolated encounter clearance |
| Coral collision | PASS, targeted physical/interpolated footprints against rebuilt masks |
| Eel/marine animation | PASS, eased emergence and coherent pose selection |
| Settings/waves/pan | PASS, labels, Back/Done, wave timing, positive transforms and pan precision |
| Browser inspection | PASS, all 52 runtime images, lighting/play/pause/seek, no page errors |
| Extended soaks | Not run; short checks requested |
| Actual Roku GPU/FPS | Not measured |

The navigation graph has 251 connected nodes. Estimated active Sunset image textures occupy 85.71 MiB at default density and 93.14 MiB at High. Add 8.44 MiB for the canvas and 15.82 MiB for FHD double buffers (6.25 MiB at HD), before driver/interpreter overhead. These are estimates. Mesh construction and rendering occur offline; the native runtime remains a cached 2D compositor.

The tracked ZIP is below 4,000,000 bytes. Exact bytes and SHA-256 are in dist/build-report.json. Current evidence includes model/receiver unit tests, native movement/traffic/profile, lighting, marine, collision, settings, render order, upright turns, raster, pan and browser logs. Earlier extended-soak reports remain historical.
