# Deep Reef 1.0.5 — verification results

The camera's four-minute Slow cycle and ±56px amplitude are unchanged. Scenery/effects now retain fractional placement instead of whole-pixel stepping. The composition uses a close, continuous reef, 60% larger fish and photographic sand ridges with subtle wave-linked lighting.

| Check | Result |
|---|---|
| Native/settings compiler | PASS, BrighterScript 0.73.8 |
| Package, artwork, detail and tracking checks | PASS, 26 Python tests |
| Production behavior/timing | PASS, 32 native-cursor checks |
| Fish update/animation regression | PASS, every fish/body/fin phase at Low/Medium/High density |
| Coral collision | PASS, safe spawns, swept body/tail contact and clear physics/interpolated poses for 18 enlarged fish |
| Scene soak | PASS, 600 simulated seconds, six enlarged principal fish, zero boundary or coral intersections |
| Settings | PASS, HD/FHD layout, readable row data, navigation, Back/Done, defaults |
| Pan geometry | PASS, production transforms quantized to float32 at HD/FHD |
| GPU-probe classifier | PASS, fractional samples accepted, flipped/channel-varied readback accepted, integer-only samples rejected |
| Wave/display timing | PASS, shared 32-frame/eight-second wave cycle, interpolated bubbles and 60/30Hz scheduling |
| Browser inspection | PASS, 601 production-world snapshots, 22 images, four lighting modes and play/pause/seek; no page errors |
| Actual Roku GPU/FPS | Not measured in this environment |

The float32 transform gate measured maximum placement error **0.003886px**, maximum frame increment **0.031250px**, and maximum stretch across a 2048px layer **0.031006px** in the tested 60Hz camera segment. The old whole-pixel draw placement stepped by 1px. A startup readback probe checks the actual device's scaled/transformed path before enabling fractional drawing; unsupported paths retain ordinary placement. The math test does not establish native GPU precision or sustained device frame rate.

The new reference-inspired source fills the center and both sides with coral. Shared photographic reef layers have recorded crop bounds, and conservative per-plane occupancy includes the crown sway envelope. The 32-yaw/eight-tail/nine-fin animation remains; larger species use 224×196 canvases and others 208×182, with improved source contrast/sharpness and clean palettes. The 60% display-length increase is covered by the collision tests.

The sand photo is preserved. Tests compare grain energy against its source and limit the animated lighting alpha to 48/255. The low-resolution light overlay contains only subtle brightness variation, not replacement sand texture. Its phase comes from the same periodic field as the surface waves. No dapple layer is present.

Estimated decoded storage: **62.5 MiB** body atlases, **12.9 MiB** fins, **99.5 MiB** active Sunset textures; about **115.3 MiB** with FHD double buffers or **106.6 MiB** with HD buffers, before driver/interpreter overhead. Two cached regions share each scenery bitmap; fractional placement does not allocate another image. These are dimension-based estimates, not measured residency.

Current logs: compiler, package, simulation, movement-regression, collision, settings, wave-smoothness, pan-precision, scene-soak and browser results under `docs/`. The older one-hour soak/Blender logs are historical checks, not new hardware results.

Still requires the user's Roku: startup probe result, visible pan smoothness, sustained FPS, graphics memory, native menu rendering/remote behavior, repeated activation and registry persistence.

Tracked install ZIP: **3,990,704 bytes**. SHA-256: `ac8e6619cf5f3561b58cfedd2891ddded691f693ea5cac5a7dd43843dc7105fb`.
