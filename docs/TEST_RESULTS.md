# Deep Reef 1.0.15 — targeted verification

The eel stays lower within a widened chamber, reaches farther outside, and lifts only late in emergence. Its smaller eyes are retained. Fully-emerged head depth is now 280, with brighter exposed-face lighting. It occasionally opens its articulated jaw and makes a squint/grin, with neutral pauses. There are 97 total states: 65 emergence and 32 expression states. The artificial cave-floor highlight is suppressed. Every one of the 65 rendered emergence states is checked vertex-by-vertex against the cave walls; the rear ring remains anchored and the final head is wholly beyond the lip.

All ten fish shells now have closed, rounded joins and smooth normals. Overlapping/open perimeter faces are removed. Opaque body colour extends through the original photograph fringe, so the two sides meet without a dark alpha belt. Independent tail/fin rigs and adaptive heading spacing remain.

A ridged, textured 3D floor and solid reef footings prevent under-reef and sand entry. Swept native body envelopes include pitch, fins, tail and depth thickness. Routes use conservative clearance. The approved lacy fan is restored exactly. The anemone has one hundred curled 3D tentacles, peach bulbs, a visible recessed mouth and reference surface colors; its individual fingers move in three axes before offline rendering. Bubble and brain coral have additional sculpted, textured meshes.

| Check | Result |
|---|---|
| Native compiler | PASS |
| Python package, topology, materials and release checks | PASS, 44 tests |
| Fish joins | PASS, every edge of every complete fish shell has exactly two incident faces |
| Cave clipping | PASS, all vertices at all 65 states remain inside the chamber until emergence |
| Eel motion | PASS, lower entry, late lift, longer depth travel, bounded adjacent states |
| Ground and reef footings | PASS, all ten species; buried poses/swept entry blocked; clear front lanes retained |
| Cave exclusion | PASS, all ten species, spawn and swept entry checks |
| Fan restoration | PASS, exact approved atlas bytes and complete formation metadata |
| Anemone anatomy | PASS, closed curled tentacles and bulbs with anchored roots and 3D displacement |
| Eel expressions | PASS, articulated mouth and squint/grin geometry, occasional timing and neutral pauses |
| Fish movement and traffic | PASS, all fish advance; predictive separation and swept/interpolated clearance |
| Lighting and water exclusion | PASS, conservative receiver masks and continuous wave sampling |
| Render ordering | PASS, textured ground, reef, joint cave actor and swimmers use correct depth order |
| Settings, pan, turns and pacing | PASS, targeted native checks |
| Browser preview | PASS, runtime assets, lighting modes, play/pause/seek and no page errors |
| Extended soaks | Not run |
| Actual Roku GPU/FPS | Not measured |

All rendering of the source meshes occurs offline. The native Roku compositor still uses cached atlases. The updated Blender scene contains the reef sculptures, floor, closed rock footings, marine anatomy and articulated moray. Texture-memory totals include unused species/lighting variants; actual device memory and FPS require hardware measurement.

The tracked install ZIP stays below 4,000,000 bytes. Exact bytes and SHA-256 are recorded in dist/build-report.json. Geometry, native collision/motion, material, render order, browser and release logs accompany this version. Historical soaks are not fresh evidence for this release.
