# Deep Reef 1.0.30 — anatomical tail attachment

The user located the remaining visible texture joint at the tail/body boundary. Each caudal patch now binds to its actual shared mesh joint after width interpolation, keeps neck height fixed, and sits underneath the complete body. Integer placement follows the body's rounded origin. Texture files and the maximum six fish draw calls are unchanged.

Joint captures cover ten species × eight headings × eight phases × HD/FHD × fractional/integer placement: 2,560 cases. Maximum fractional root error is 0.016702 px, compared with 2.156544 px in the matching v29 subset. Maximum integer-path error is 0.695813 px, within single-pixel rounding. Every sampled side-view collar retains overlap, and the tail is drawn before the body. See [audit](tail-attachment-audit.json) and [matching reconstructed close-ups](previews/tail-joint-comparison.png). These are host reconstructions of production commands, not Roku screenshots.

Validation: BrighterScript compilation; 56 Python package/geometry/material/source-pixel/mesh-bind checks; native motion, fish traffic and recovery; swept reef/fish/cave/floor/surface collision; reference positions; complete-body phase/yaw weights; upright rendering and depth order; clam/appendage animation; attachment pivots; head-on turn metrics; HD/FHD pan and settings. `tools/test.py --quick` passed, with the extended integer-path checks also passing after the fallback-origin correction. No extended soak was run.

The package and build report remain tracked and source-matched below the 4 MiB limit. Actual Roku appearance and performance remain to be confirmed; the latest supplied performance baseline is 15 FPS / U36 / D29 / S0 / E0 ms from v28.
