# Deep Reef 1.0.26 — performance investigation

Confirmed and corrected avoidable render work: native-sized Performance canvas, no empty receiver draws, cropped shadow regions, and equivalent fish-sway math with cached common terms. High retains its canvas size, body sections, heading interpolation, textures and animation. No fish navigation or collision behavior changed.

Validation: compilation; 49 Python checks; native profiling arithmetic and canvas dimensions; 864 original/optimized transform comparisons; upright fish and presentation; body sway; draw ordering; wave/pacing and turn regressions; HD/FHD subpixel pan precision; matching source/ZIP release checks; browser preview. All 96 baseline shadow frames reconstruct with zero alpha or visible-colour error.

The measured source-area and call-count results are in [performance-audit.json](performance-audit.json). These are not device FPS measurements. The Roku Ultra needs to run this build and provide its native U/D/S/E timings to establish the dominant remaining bottleneck. [PERFORMANCE.md](PERFORMANCE.md) explains the findings, diagnostics and short on-device check.
