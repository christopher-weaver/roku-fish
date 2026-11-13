# Deep Reef repository instructions

The user requires the sideloadable ZIP to remain included on GitHub.

- Keep `dist/deep-reef-screensaver.zip` and `dist/build-report.json` tracked in Git. Do not ignore, delete, or replace the ZIP with a Git LFS pointer.
- After changing any file under `roku/` or changing packaging logic, run `python tools/build.py` and include the regenerated ZIP and build report in the same commit as the source change.
- Before committing, run `python tools/check_release.py`. It checks that the committed package paths are tracked and rebuilds the current source to detect a stale package.
- For a release version bump, use `python tools/build.py --increment`, then stage the updated manifest, ZIP, and report together.
- Native screensaver requirements remain authoritative: keep `RunScreenSaver()` and `RunScreenSaverSettings()`, no `Main()` or `RunUserInterface()`, no video playback or runtime network dependency.
