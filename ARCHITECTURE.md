# Native architecture

RunScreenSaver owns the double-buffered native roScreen. RunScreenSaverSettings owns the separate SceneGraph settings context. There is no ordinary Main/RunUserInterface, video or runtime networking. Existing settings persistence, labels and Back/Done closure remain.

## Sharp, coherent rendering

Each fish draws exactly one upright body/tail view and one pectoral view, both at full modulation alpha. Nearest mesh pose selection replaces the previous four-pose source-over blend, which could expose multiple tails. Movement/heading interpolation and continuous width matching remain. No negative-scale reflection is used.

Static reef layers are native-resolution crops and draw at 1:1. A common camera registration keeps their shared foundation joined. Each marine volume selects one of seven camera-angle images; no coral or anatomy images are crossfaded. Exact 1:1 copies use DrawObject, avoiding unnecessary scaling. The only whole-scene interpolation is the final adjacent-pixel pan; wave/light fields retain their own low-opacity temporal blending.

The aquarium composes into an opaque 2048×1080 overscan canvas, presented at adjacent integer pixel offsets. Camera progress follows the monotonic display clock. Slow remains a four-minute cycle. This pan path has no large pretranslation anchors or changing scale. Clock/FPS text draws after presentation. The canvas is modified again only after SwapBuffers; allocation failure retains direct drawing.

## Reference-aligned reef

The source reef is one connected assemblage, with low rock touching across the frame and a shared foundation around y=1025 (small natural staggering). Its two complementary, registered masks provide mid-ground and foreground occlusion without duplicating the same coral across different positions. A back sea fan and front anemone add real mesh-derived volume. Their stems/bases remain registered to that foundation; hidden fan root pixels are omitted from its atlas because the fixed reef occludes them.

The sea fan and anemone use the same family of technique as the fish: silhouette-derived, closed front/back surfaces, stitched rims, photographic UV texture and offscreen depth-tested rendering. Fan sheet curvature and anemone thickness produce actual view-dependent perspective/occlusion. Seven views span -8 to +8 degrees; one is selected from camera position. These are photo-derived volumes rather than anatomical scans or runtime 3D shaders. Source NPZ meshes, Blender curve models, renders and the finished material sheet are included.

The initial Blender geometry was surface/anatomy-refined with the image tool; the resulting RGBA artwork textures the closed-volume meshes. The touching reef layout was fixed first, then a new empty water/sand plate was created from its composition guide. A cooler background is derived from the same matched pixels. Sand illumination is rebuilt from this new background and masked outside coral footprints.

## Movement, collision and pacing

Fixed 30Hz simulation, interpolated XYZ and cubic headings are retained. Turn speed/acceleration/jerk are bounded. All fish/neighbor loops are indexed for Roku's shared ifEnum cursor. Cached display/projection/probe/candidate objects, effect depth bands, offline next-hop paths and 5Hz waypoint visibility checks reduce frame-loop work.

Collision uses conservative swept full-fish footprints against finite-depth masks, reserving the union of every marine view. Native 60Hz presentation and the existing stable 30Hz fallback remain. Textures and regions load once. Host math and draw-call checks do not establish actual Roku GPU precision, sustained FPS or memory residency.
