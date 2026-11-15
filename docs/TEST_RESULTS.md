# Deep Reef 1.0.13 — targeted verification

Wave shading is 20% stronger on ground/reef receivers. Fish receive 30% of the new field (36% of the previous release). Conservative receiver masks still exclude open water; sand ridges remain visible.

The cave now has five bending depth rings and a closed rear wall. Its opening is the only mesh boundary. The eel and chamber share coordinates and depth tests, with surrounding reef geometry used as holdouts. The rear body ring remains anchored inside while the head moves through the entrance. Sixty-five complete rendered states replace the vertical sliding/repair trick. The combined Blender scene contains the same body poses as editable geometry.

The reserved cave volume is shared by offline route generation and native swept collision checks. Tests cover all ten species at maximum size, initial cave occupancy, forward/reverse crossing, depth crossing and safe spawn correction. Clear front/rear lanes remain available.

| Check | Result |
|---|---|
| Native compiler | PASS, BrighterScript 0.73.8 |
| Package/artwork/tracking | PASS, 38 Python tests |
| Static reef topology | PASS, all eighteen closed parts have two triangles at every edge |
| Cave geometry | PASS, rear cap closed; only the 192-edge mouth is open; 270 design-pixel depth |
| Eel geometry | PASS, pinned rear ring, head moves from inside to beyond lip, 65 bounded atlas states |
| Cave fish exclusion | PASS, all ten species; spawn, swept horizontal/depth entry and lane clearance |
| Water exclusion | PASS, all 32 reef-shadow phases have zero alpha outside opaque receiver coverage |
| Lighting | PASS, bounded soft projective field and continuous cycle |
| Fish motion/traffic | PASS, all fish advance; swept/interpolated encounter clearance and lateral behavior |
| Coral collision | PASS, 60 physics ticks with physical/interpolated footprints |
| Rendering | PASS, joint cave stage between connected reef and foreground fish; one body/tail/fin per fish |
| Marine/eel timing | PASS, coherent poses and bounded adjacent emergence-state changes |
| Settings/waves/pan/turns | PASS, readable labels, Back/Done, wave timing, smooth positive-scale transforms |
| Browser preview | PASS, all runtime assets and four lighting modes load; play/pause/seek; no page errors |
| Extended soaks | Not run |
| Actual Roku GPU/FPS | Not measured |

The navigation graph has 246 connected nodes and 528 edges. The 19 static structural pieces total 597,803 vertices and 1,195,256 triangles. The jointly rendered cave/eel uses a tightly cropped atlas. Estimated active Sunset image textures occupy 87.58 MiB at default density and 95.01 MiB at High. Add 8.44 MiB for the canvas and 15.82 MiB for FHD double buffers (6.25 MiB at HD), before driver/interpreter overhead. These are estimates. Mesh rendering occurs offline; Roku uses the cached 2D compositor.

The tracked install ZIP stays below 4,000,000 bytes. Exact bytes and SHA-256 appear in dist/build-report.json. Logs and short visual fixtures accompany the source; historical extended-soak reports are not fresh evidence for this version.
