# Deep Reef 1.0.32 — density performance and rare births

The copperband tail joint moves farther back again, from source U=0.15 to U=0.11, with its mesh partition, body/tail views and binding rebuilt together. Fractional scale correction now anchors the tail attachment itself instead of the model origin. Other species' artwork and all population settings are retained.

The 60-tick/eight-fish production fixture retains all reference trajectories while using 19% fewer helper calls, 54% fewer square roots and 96% fewer full pair-function calls after conservative sweep screening. The 120-frame render fixture retains 707 transforms and uses 20% fewer helper calls and 21% fewer Sin/Cos calls. [Full audit](density-performance-audit.json).

Clam events roll a 2% birth chance once per opening on an independent random stream. Fifty controlled RNG buckets verify exactly one birth bucket; repeated frames do not reroll. The integration test still checks a closed-shell baby, one release, safe emergence, swimming, population caps, pearls and bubbles.

Validation covered compilation, 56 Python checks, native movement/activity/traffic/recovery, 1,200 full swept/static pair checks and 2,400 cached/uncached broad-phase comparisons against the frozen reference, reef/floor/cave clearance, phase/yaw blending, settings, appendages, clam/night/surface behavior, upright/depth rendering, turns and pan. All listed checks passed; attachment, swim-blend and turn checks were repeated after the final precision correction. No extended soak was run.

All 2,560 final joint cases pass the unchanged limits: maximum fractional error 0.003062 px, integer-path error 0.695864 px, zero missing sampled collar overlaps and zero draw-order failures. Optimized complete-body submissions exactly match the previous renderer with the same rebuilt artwork. The [close-up](previews/copperband-rear-bend.png) is a host texture composite, not a Roku screenshot.

The tracked ZIP and build report match source below 4 MiB. The user's current Ultra measurements are 20–25 FPS at High density and about 45 FPS at Low density. New native FPS is not measured; these work counts do not predict the device gain.
