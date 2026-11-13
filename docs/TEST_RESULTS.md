# Test results — 2026-11-13

Release: Deep Reef 1.0.1 (manifest 1 / 0 / 1). Default lighting: Sunset.

| Gate | Result | Scope |
|---|---|---|
| BrighterScript 0.73.8 compilation | PASS, no reported diagnostics | Native sources and SG settings |
| Python package/asset suite | PASS, 12 tests | Real ZIP, manifest, images, atlas bounds/poses, notices, offline runtime, missing-device refusal |
| Production BrightScript simulation | PASS, 25 checks | Actual brain/projection/settings/lighting functions; OS registry adapter |
| Extended host simulation | PASS, 3,600 simulated seconds | 36,000 steps; six principal fish; 72 effect slots; zero tank-bound violations |
| Chromium inspection | PASS, no page errors | 25 preview textures, four palettes, seek/pause/resume and canvas screenshot |
| Blender optional pipeline | PASS, one transparent view + editable blend | Tested with --limit 1; default pipeline remains ModernGL |
| ZIP integrity and root structure | PASS | manifest is at archive root; no source-only art/tests/tools |
| Roku hardware/deployment | NOT RUN | No ROKU_IP or ROKU_DEV_PASSWORD configured |

Package: **3,340,478 bytes**, below the conservative 4,000,000-byte budget.

SHA-256: `7338e69ef887014eb5f9c42b34a3182821cb66f945e6b83587bec9bd37105548`.

All 31 image files and six species catalogs validate; textures are at most 2048 pixels per dimension. Each fish atlas contains 16 distinct yaw views × three actual mesh-bent swim poses; the package tests also compare the side-view pose pixels to detect a frozen tail.

The one-hour simulation's observed ranges were X 110.12–1912.04 and Z 0.05791–0.96760. Fish count remained six and effect count 72. It does not establish memory-leak freedom in the Roku interpreter/driver. The final camera projection adds depth-dependent parallax; the soak's collision projection uses camera zero and is algebraically unchanged by that display-only adjustment. The complete 25-check suite was rerun afterward, including a new assertion inside the existing perspective check for relative near/far camera motion.

Final visual review inspected the refined photographic fish sheet, default sunset, front/behind reef masking, close oblique fish, multiple lighting modes and compressed textures. The default sunset screenshot comes from an unmodified 20-second production-world snapshot. The occlusion/close-up fixtures deliberately place fish for inspection.

Remaining hardware checks: real screensaver discovery/registration, idle startup, actual native GPU output, stable 30 FPS, driver/script memory trend, settings persistence across power cycles, remote dismissal, and repeated activations. FHD/HD fallback is implemented but not device-verified. Silhouette-derived fish head geometry and limited registered-plate camera travel are documented fidelity tradeoffs.

See compiler-results.txt, package-results.txt, simulation-results.txt, soak-results.txt, browser-results.json and blender-smoke-results.txt for retained evidence.

## GitHub publication checks

All 16 Python package/release tests passed before the initial GitHub commit (the original 12 package tests plus four release-tracking tests). `python tools/check_release.py` confirmed that the tracked 3,340,478-byte ZIP reproduces from the source. `.gitattributes` disables LFS filtering for the ZIP, `.gitignore` explicitly retains it, and the Verify sideload ZIP workflow checks missing/stale package failures on future pushes and pull requests. The original device-verification limitations above remain unchanged.
