# Deep Reef 1.0.21 — small platform lip

Adds a small raised lip around the anemone foot and extends the ledge slightly forward. The complete anemone mesh and animation atlas are byte-for-byte unchanged from 1.0.20. The support is a separate closed rock platform with smaller side stones and a feathered photographic sand apron. The broad platform draws behind the anemone; a separate narrow front curb overlaps only the tip of the foot, preserving the complete pedal column. The platform, complete anemone and distinct sand material are included in the editable Blender scene.

Validation: 48 Python package/geometry/material/release checks; a targeted native collision regression covering physical and interpolated fish poses; matching source/ZIP release checks. The geometry test verifies the original base extent, closed support geometry, rear-to-front draw order and a translucent sand boundary. No fish movement code changed. The screenshot is from the desktop development preview; actual Roku hardware was not measured.

The prior release's movement investigation remains available in [three-minute-before.txt](three-minute-before.txt) and [movement-followup.txt](movement-followup.txt).
