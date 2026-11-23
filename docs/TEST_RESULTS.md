# Deep Reef 1.0.28 — faster swimming updates and attached body sections

Hardware baseline from the user: Roku Ultra, normal/Medium fish density, 11 FPS, U44 / D30 / S0 / E0 ms after v27. New device FPS is pending installation.

The 60-tick/eight-fish production fixture retains its reference end poses and every physics/collision check while helper calls fall 26,268 → 17,136. The 120-frame renderer fixture retains all 2,160 transforms while Sin/Cos calls fall 17,113 → 5,957. These are source call counts, not native timings. [swim-performance-audit.json](swim-performance-audit.json) contains the complete counts.

The pitch regression checks 864 cached bends and attached pivots at ordinary and clamped angles; it fails against v27's clamped-rotation/unclamped-placement mismatch. The native region/transform capture checks all ten species, both directions, twelve swim phases and HD/FHD. All 11,481,120 sampled seam-neighborhood points have a two-output-pixel filter guard with the new overlap. V27 lacked that guard at 1,497,365 points. This is a conservative geometric/filter-margin test, not a GPU frame capture.

Validation: BrighterScript compilation; 52 Python package/material/geometry/release checks; native activity/shared-cursor movement, traffic, route recovery and collision equivalence; CPU reference poses; clam events and contents; floor/cave/surface clearance; body sway and pivot geometry; marine appendages; HD/FHD pan and smooth turns; settings and draw ordering. `tools/test.py --quick` includes the new seam check. No extended soak was run. Rasterized production-transform body previews were inspected locally.

High resolution, eight body sections, smooth two-view yaw interpolation, texture detail, fish density and 30 Hz physics are retained. The sideload ZIP/build report remain tracked and match the current source. Actual Roku FPS and GPU filtering still require the user's short follow-up sample.
