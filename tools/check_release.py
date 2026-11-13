"""Check that the versioned, non-LFS sideload ZIP matches the current Roku sources."""
from pathlib import Path
import hashlib
import subprocess
import sys
import build

ROOT = Path(__file__).resolve().parents[1]
RELEASE_FILES = ('dist/deep-reef-screensaver.zip', 'dist/build-report.json')


def check_release():
    expected = {}
    for name in RELEASE_FILES:
        result = subprocess.run(
            ['git', 'ls-files', '--error-unmatch', '--', name],
            cwd=ROOT, capture_output=True, text=True,
        )
        if result.returncode:
            raise ValueError(f'{name} must be tracked in Git; rebuild and git add both release files')
        path = ROOT / name
        if not path.is_file():
            raise ValueError(f'{name} is missing; run python tools/build.py')
        expected[name] = path.read_bytes()
    if not expected[RELEASE_FILES[0]].startswith(b'PK\x03\x04'):
        raise ValueError('The sideload ZIP must contain real ZIP bytes, not a Git LFS pointer')
    build.build()
    stale = [name for name in RELEASE_FILES if (ROOT / name).read_bytes() != expected[name]]
    if stale:
        raise ValueError(
            'Release files were stale and have been rebuilt: ' + ', '.join(stale)
            + '. Stage the regenerated ZIP and report with the source changes.'
        )
    digest = hashlib.sha256(expected[RELEASE_FILES[0]]).hexdigest()
    print(f'Tracked sideload ZIP matches the current source: {digest}')


if __name__ == '__main__':
    try:
        check_release()
    except (ValueError, OSError) as error:
        sys.exit(f'Release check failed: {error}')
