"""Exercise ZIP freshness and tracking checks against a temporary Git repository."""
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class ReleaseTrackingChecks(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for name in ('roku', 'dist'):
            shutil.copytree(ROOT / name, self.root / name)
        (self.root / 'tools').mkdir()
        for name in ('build.py', 'check_release.py', 'collision_index.py'):
            shutil.copy2(ROOT / 'tools' / name, self.root / 'tools' / name)
        self.git('init', '--quiet')
        self.git('add', 'dist/deep-reef-screensaver.zip', 'dist/build-report.json')

    def git(self, *args):
        return subprocess.run(['git', *args], cwd=self.root, check=True, capture_output=True)

    def check_release(self):
        return subprocess.run(
            [sys.executable, 'tools/check_release.py'], cwd=self.root,
            capture_output=True, text=True,
        )

    def test_fresh_tracked_zip_passes(self):
        result = self.check_release()
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_stale_zip_fails_and_is_rebuilt(self):
        path = self.root / 'dist/deep-reef-screensaver.zip'
        expected = path.read_bytes()
        path.write_bytes(expected + b'stale')
        result = self.check_release()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('stale', result.stderr)
        self.assertEqual(path.read_bytes(), expected)

    def test_untracked_zip_fails(self):
        self.git('rm', '--cached', 'dist/deep-reef-screensaver.zip')
        result = self.check_release()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('must be tracked', result.stderr)

    def test_lfs_pointer_fails(self):
        (self.root / 'dist/deep-reef-screensaver.zip').write_text('version https://git-lfs.github.com/spec/v1\n')
        result = self.check_release()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('not a Git LFS pointer', result.stderr)


if __name__ == '__main__':
    unittest.main()
