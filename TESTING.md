# Verification

Routine iteration uses short targeted checks:

```sh
npm install
python -m pip install -r tools/requirements.txt
python tools/build.py
python tools/test.py --quick
python tools/check_release.py
```

BSC_BIN and BRS_BIN can point to installed tool binaries. The default run without --quick retains longer simulation/raster gates; --scene-soak and --soak are optional extended checks and are not required for routine delivery.

## Current targeted coverage

The quick suite compiles native/settings sources and runs 59 Python package, artwork and Git-tracking checks. Production BrightScript tests cover every fish and body/fin phase at Low/Medium/High density, 60 simulation ticks with physical/interpolated whole-body coral footprints, readable settings and Back/Done, wave/display timing, drawing order, turn acceleration/jerk and cubic heading interpolation.

pan_precision.brs exports real production adjacent-pixel weights at HD/FHD. pan_check.py verifies centroid error under 0.002px and frame increments under 0.04px in the tested 60Hz camera segment. upright_present.brs exercises pitched body/fin drawing over a full circle, requires positive scales, and captures actual ReefPresent calls to check opaque base frames and adjacent offsets. These tests do not simulate a Roku GPU.

All native tests use roku_runner.cjs, whose compatibility adapter reproduces Roku's single shared ifEnum cursor. Fish and neighbor loops are indexed to avoid the prior one-moving-fish bug. Renderer tests use draw-call recorders; settings tests use node/registry adapters rather than actual SceneGraph rendering.

The browser gate checks the short native-world recording, current image loading, lighting, play/pause/seek and JavaScript errors. Single-body/single-fin draw counts and full modulation alpha are required; mixed marine atlases are checked against actual mesh files and camera views. Foundation continuity/common root height are checked against the reef masks. The recording samples the fastest section of the unchanged camera cycle. Current logs are in docs/TEST_RESULTS.md. Earlier long-soak and raster comparison logs are historical, not evidence for this release.

Actual Roku orientation, native pixel output, sustained FPS/memory, registration/idle activation, remote dismissal and reboot persistence require device validation. No Roku IP or developer password was configured here.

The 1.0.34 quick suite also reproduces the three-species coral pileup, verifies safe contact-buffer escape, tests signed C bends within the existing draw budget, and checks continuous projected tilt through front/rear views. The optional `--three-minute` test now uses High density and reports per-fish travel, stationary intervals and low-progress windows. Current results are recorded in `docs/TEST_RESULTS.md`.

The 1.0.35 quick suite replays actual C-turn draw captures on both sides of each critical atlas boundary, in both turn directions for all ten species. It limits centroid, coverage and color discontinuities, checks advancing swim phase during steady steering, and verifies the reference-facing copperband proportions. See `docs/turn-boundaries-results.json`.
