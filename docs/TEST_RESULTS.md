# Deep Reef 1.0.27 — CPU update optimization

User hardware evidence: Roku Ultra, normal/Medium density, High and Performance both around 7–8 FPS, U101 / D31 / S0 / E0 ms. Update CPU is the dominant measured cost.

The actual production update fixture retains all 60 physics ticks, 480 fish updates, 1,645 swept reef checks, 3,360 fish-pair checks and all eight reference trajectories. Helper calls fall 106,147 → 26,268; occupancy searches fall 16,359 → 1,372. These are call counts, not device FPS measurements. See [cpu-performance-audit.json](cpu-performance-audit.json).

Validation includes BrighterScript compilation; 52 Python checks; independent v26 collision oracle (1,260 rectangle queries, 600 reef sweeps, 1,200 fish-pair sweeps, 600 cache refreshes); reference trajectories; movement/activity, traffic and recovery; floor/cave/surface clearance; clam contents and births; smooth turns, pan, waves and appendages; body sway; render ordering; settings and matching tracked ZIP. Native tests use the Roku single-cursor adapter. No extended soak was run.

The sideload ZIP and build report remain tracked with the source. Updated on-device FPS/U/D/S/E after installation is pending; High's resolution and all artwork remain unchanged. [PERFORMANCE.md](PERFORMANCE.md) details the diagnosis and short device check.
