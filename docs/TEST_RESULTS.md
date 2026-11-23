# Deep Reef 1.0.31 — copperband tail bend

The copperband butterflyfish now bends at the narrow tail stalk, farther back and behind its dorsal and anal fins. Its caudal cut moved from source U=0.21 to U=0.15; the existing mesh was repartitioned, the tail and complete-body views rebaked, and the shared attachment recomputed. Geometry, source photographs and pectoral fins are retained. Other species are unchanged. Runtime draw count and animation logic are unchanged.

Attachment validation covers ten species × eight headings × eight phases × HD/FHD × fractional/integer placement: 2,560 production-command captures. Maximum fractional root error is 0.018040 px; maximum integer-path error is 0.695813 px. Every sampled side-view collar retains overlap, and every tail draws before the body. See [results](tail-attachment-results.json). The [copperband close-up](previews/copperband-rear-bend.png) is a host composite of the rebuilt textures, not a Roku screenshot.

Validation: BrighterScript compilation; 56 Python package, geometry, source-pixel and mesh-binding checks; native movement, traffic and recovery; collision equivalence and swept reef/fish/cave/floor clearance; complete-body phase/yaw weights; tail pivots; turn smoothness; HD/FHD pan; settings; clam, wave and appendage animation. `tools/test.py --quick` passed. No extended soak was run.

The tracked ZIP and build report match source and remain below the 4 MiB package limit. Actual Roku appearance and FPS were not measured; the latest supplied baseline remains 15 FPS / U36 / D29 / S0 / E0 ms from v28.
