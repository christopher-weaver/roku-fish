# Deep Reef 1.0.23 — natural reef attachment

The artificial rim and support slab are removed. The anemone uses the existing modeled foreground reef as its attachment. Outer front tentacles now curve down over the full pedal column and the rock-to-sand transition, preserving their pinned roots, three-axis motion and 80% opacity. The complete base remains in the closed mesh; it is no longer presented as an exposed potted stem. No new prop or decorative border surrounds it.

Validation: 48 Python package, geometry, material and release checks; a targeted native collision regression covering physical and interpolated fish poses; matching source/ZIP release checks; browser asset loading and screenshot capture without page errors. The attachment regression verifies that no rim/platform formation remains, the full pedal column is retained, and translucent moving front fingers reach down over it. No fish movement code changed. The screenshot is a desktop development preview; actual Roku hardware was not measured.

The earlier movement investigation remains available in [three-minute-before.txt](three-minute-before.txt) and [movement-followup.txt](movement-followup.txt).
