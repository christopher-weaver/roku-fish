# Deep Reef 1.0.18 — targeted verification

Anemone and clam surfaces now use photographic maps extracted from the approved artwork, with UV coordinates attached to the actual modeled surfaces. Tentacle material opacity is exactly 0.8; the oral disc remains opaque. The clam is scaled to 70% and turned 55° sideways. Its front-shell mask reuses rectangles from the same color atlas, with drawing limited to the area overlapping a staged baby fish.

The same baby object exists behind the closed shell, follows a continuous eased emergence path behind the lip, then enters normal movement. Its size fits the shell for all ten parent species. Swept checks prevent it from entering the reef/floor or crossing another fish. A blocked exit holds the shell open.

Body-only interpolation between width-aligned 3D headings removes view snapping while retaining one tail and one pectoral image. Angular acceleration/jerk are reduced. Long visible crossings, earlier waypoint rounding, less stacked braking and rare brief pauses increase lateral swimming. Surface reflections are stronger and remain above the full fish envelope.

| Check | Result |
|---|---|
| Compiler | PASS |
| Python package, geometry, materials and release checks | PASS, 47 tests |
| Lateral activity | PASS, all eight fish span about 195–754 design pixels over 12 simulated seconds, without reef/floor entry |
| Turns | PASS, bounded velocity/acceleration/jerk, cubic display heading, continuous projected width and body-only interpolation |
| Turn raster comparison | PASS, peak image changes are 0.089–0.217 of the original 64-angle nearest-view reference |
| Shell occlusion | PASS, every parent species fits behind the closed shell; endpoint clears the shell before ordinary swimming |
| Baby lifecycle | PASS, same object starts inside, moves continuously through the opening, then uses ordinary AI; births remain bounded |
| Materials | PASS, 80% tentacle opacity and photographic variation; exact approved fan unchanged |
| Traffic, routes, floor and cave | PASS, predictive and swept encounters, progress recovery and full body clearance |
| Surface/pan/settings/render | PASS, protected waterline, continuous clocks, correct depth order and existing settings |
| Browser | PASS, all lighting modes, assets and play/pause/seek, no page errors |
| Package | PASS, tracked ZIP, fresh source, checksum and 4 MB limit |
| Extended soaks | Not run |
| Actual Roku GPU/FPS | Not measured |

The browser and host checks do not measure Roku GPU timing. The editable Blender scene includes the new photo UVs, per-vertex tissue opacity, smaller side-facing clam, and articulated opening geometry.
