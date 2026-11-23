# Deep Reef 1.0.29 — continuous fish bodies

Hardware baseline reported by the user: Roku Ultra, 15 FPS, U36 / D29 / S0 / E0 ms, with splits still visible after v28. Resulting v29 device FPS and filtering remain pending.

Body rendering now uses complete curved/neutral/inverse-curved images. All 112 mesh-view angles, texture resolution and visible source colors are preserved. There are no runtime body slices. The 120-frame native fixture uses 707 transforms versus 2,160 previously, with correct normalized phase/yaw weights, an opaque base, common body pitch, and one tail/fin submission each.

The independent pixel test covers 1,710 view/pose combinations across ten species. Every column retains its original alpha profile and visible RGBA sequence; neutral poses retain their anchor alignment. No new internal gaps or color changes are introduced. Original rest atlases and metadata are preserved in `assets/source/fish-rest`; the offline generator is `tools/whole_swim.py`.

The fixed-tick anatomy cache reduces object field reads 530,121 → 462,656 in the two-second/eight-fish fixture. Both versions retain 60 ticks, 480 fish updates, 1,645 reef sweeps, 3,360 pair sweeps and the same reference end poses. These are source work counts, not hardware timings. [continuous-body-audit.json](continuous-body-audit.json) contains the full data and texture-memory tradeoff.

Validation: BrighterScript compilation; 54 Python package/geometry/material/pixel/release checks; native activity, shared-cursor movement, traffic, route recovery, collision equivalence and reference poses; clam events/contents; floor/cave/surface clearance; whole-body blending; 1,728 traveling/standing attachment/pivot cases; appendage animation; draw ordering; upright turns; unchanged head-on image-change metrics; HD/FHD subpixel pan; settings; source-matching ZIP verification. `tools/test.py --quick` passed. No extended soak was run.

Every runtime texture stays within 2048×2048, and the package remains below the 4 MiB ceiling. High resolution, fish density, 30 Hz physics and heading interpolation remain. The ZIP and build report are tracked with the source. A short updated native FPS/U/D/S/E sample is the remaining device check.
