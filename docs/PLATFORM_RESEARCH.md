# Platform and reference review — 2026-11-13

Official pages inspected before implementation:

- https://developer.roku.com/dev/docs/screensavers
- https://developer.roku.com/dev/docs/channel-manifest
- https://developer.roku.com/dev/docs/roscreen
- https://developer.roku.com/dev/docs/ifdraw2d
- https://developer.roku.com/dev/docs/ifscreen
- https://developer.roku.com/dev/docs/robitmap
- https://developer.roku.com/dev/docs/roregion
- https://developer.roku.com/dev/docs/developer-setup
- https://developer.roku.com/dev/docs/hardware
- https://developer.roku.com/dev/docs/samples
- https://developer.roku.com/dev/docs/static-analysis-tool

The current standalone screensaver entry point, settings entry point, manifest registration and system dismissal behavior are implemented. Video/audio player components and normal-channel entry points are excluded. The manifest uses rsg_version=1.3 in keeping with the current certification guidance (the 2026-10-01 cutoff); personal sideloading is the delivery target, not a claim of store certification. The current publishing guidance also requires minimum firmware 15.1.0 or later; that value is selected on the Developer Dashboard package upload page, not invented as a manifest flag. This personal sideload build targets OS 16 and has not been submitted for certification. The contemporary UI ceiling is treated as 1080p, separately from 4K video playback.

roBitmap's 2048-pixel limit governs every atlas and reef tile. OS 16 draw-source immutability is respected. The screen's graphics feature query controls arbitrary pitch rotation; a supported scaled-drawing fallback remains available. PNG/JPEG are used throughout the package, avoiding WebP version gating and preserving ordinary manifest art requirements.

Reference review:

| Reference | Architecture / assets / installation | License decision |
|---|---|---|
| Reef Glass | Native double-buffered roScreen at 30 FPS; multi-view 3D body/tail atlases, coral occupancy, panorama, cached regions and guarded memory monitor; separate SG settings and ZIP helpers | Apache-2.0 code, CC0 images. Small memory-monitor pattern adapted with notice. LFS art could not be downloaded, so none is shipped. |
| AquariumTV | SG scene, photo cutouts, generated effects and configuration, image processing and package/deploy helpers | Terms withhold modification/redistribution rights; reviewed only. |
| roku-fishtank | SG layered reef, species brains, segmented photo rigs, schooling, data-driven scenes, host BrightScript and browser tests, native settings and sideload workflow | MIT root license; six source portraits reused with full notices and source provenance. Own runtime/projection/atlas mesh pipeline used here. |

Source code and license files were inspected locally. Review of reference implementations is not a claim that their hardware tests were rerun. No private Roku APIs, Unity/Unreal runtime, arbitrary runtime shaders or proprietary Roku assets are used.

## Native iteration rule

Roku objects maintain one `ifEnum` cursor. Nested enumeration of the same fish array, even through a neighbor function, can end the outer loop after its first item. The fish update and neighbor scan now use numeric indices. The test adapter explicitly reproduces this rule; the unmodified JavaScript-backed interpreter did not. References: [Roku developer discussion of shared enumeration](https://forum.developer.roku.com/t/for-each-bug-one-iteration-breaks-another/5160) and [nested-loop behavior](https://forum.developer.roku.com/t/nested-for-each-loops-behavior/7289).
