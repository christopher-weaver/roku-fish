# Deep Reef 1.0.19 — movement and scene verification

The three-minute baseline runs the production BrightScript for 5,400 ticks at 30 Hz, with the shipped Medium population, seed 47831, collision volumes and clam births. It reproduced 27 six-second low-progress windows and a longest stationary episode of 12.47 seconds. No reef/floor/fish intersections were recorded. Full output is in [three-minute-before.txt](three-minute-before.txt).

Two causes were identified: the front depth lane conflicted with the old wall force/brake, and a clearance-tested recovery goal could not be followed while propulsion remained tied to a slowly turning body. Recovery now follows a short clear 3D segment with eased velocity and endpoint slowing. A nearly vertical recovery retains propulsion. Every physical candidate still passes swept reef/floor/fish guards; positions are never teleported. Cubic display positions stay within the physical endpoints, while single-image tail/fin envelopes change continuously across pose boundaries.

A one-minute follow-up observed 1,800 production 30 Hz ticks with zero six-second low-progress windows and a longest stationary episode of 1.27 seconds; output is in [movement-followup.txt](movement-followup.txt). Its progress detector also counts nearby goals, a stricter criterion than the baseline. The additional follow-up was stopped after one minute; the requested three-minute baseline completed in full. Swept collision safety is covered separately by the native traffic, reef, floor and cave regressions. These host simulations exercise production logic; their execution speed is not a measurement of Roku frame rate.

The anemone is seated in a depressed 3D foundation with a matching textured rock rim in front of its base. Tentacle opacity remains 0.8 and the approved fan is unchanged. The clam has a pale photographic mantle, with pearl, bubbles and a baby present behind its closed foreground shell. A partial opening reveals contents before the shell is fully open. The same bubble objects rise without a release-position jump, and the same baby object exits into normal swimming. Surface waves are twice their previous width and height, with a protected full-body fish clearance.

| Check | Result |
|---|---|
| Compiler | PASS |
| Python package, geometry, materials and release checks | PASS, 48 tests |
| Native simulation | PASS, 32 checks |
| Lateral activity | PASS, all eight fish span about 227–562 design pixels over 12 simulated seconds |
| Turns and position interpolation | PASS, bounded angular motion, velocity endpoints and physical position envelope |
| Appendage transitions | PASS, 1,060 fin/tail pose boundaries with continuous envelope dimensions and anchors |
| Clam contents | PASS, full-opacity pearl and prepared bubbles behind the closed shell, continuous release |
| Shell geometry | PASS, all ten baby species fit inside closed shell; partial opening reveals contents; visible mantle |
| Reef pocket | PASS, closed rim and depressed 3D foundation; photo colour matches surrounding reef |
| Traffic, routes, floor, cave and waves | PASS, production regressions |
| Browser preview | PASS, all lighting modes, assets, play/pause/seek; no page errors |
| Release package | PASS, tracked fresh ZIP below the 4 MB limit |
| Ten-minute soak | Not run |
| Actual Roku GPU/FPS | Not measured |

The editable Blender scene includes the recessed foundation, rock rim, photographic anemone, articulated clam and resident moray. Screenshots of closed, partially open, occupied and emerging clam states are included under `docs/previews/`.
