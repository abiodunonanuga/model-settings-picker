"""Regression tests for the privacy boundary, using dummy private-file fixtures."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
import zipfile
from unittest.mock import patch

import build_release
import package_files
import picker

ROOT = Path(__file__).resolve().parents[1]


class PackageBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='picker boundary ')
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.sentinel = os.urandom(24).hex()
        self.source = self.base / 'source'
        # Create a clean source checkout without Git, so selection cannot depend
        # on Git availability, tracked state, ignored state or a developer home.
        for name in package_files.RELEASE_FILES:
            target = self.source / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, target)

    def extras(self):
        names = ['.env', '.env.production', 'private.json', 'nested/client-notes.txt',
                 'skills/model-settings-picker/personal.json', '.venv/credentials.txt',
                 'dist/private.zip', 'sessions/private.json', '.codex/auth.json']
        for name in names:
            p = self.source / name
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(self.sentinel, encoding='utf-8')
        return names

    def test_release_uses_exact_manifest_not_source_extras(self):
        self.extras()
        with patch.object(build_release, 'ROOT', self.source):
            result = build_release.build(self.base / 'release')
        with zipfile.ZipFile(self.base / 'release' / result['archive']) as archive:
            names = {n.removeprefix('model-settings-picker/') for n in archive.namelist()}
            self.assertEqual(names, set(package_files.RELEASE_FILES))
            self.assertTrue(all(self.sentinel.encode() not in archive.read(n) for n in archive.namelist()))
        self.assertEqual(set(result['files']), set(package_files.RELEASE_FILES))

    def test_install_uses_exact_runtime_manifest_not_extras(self):
        self.extras()
        target = self.base / 'target'
        with patch.object(picker, 'ROOT', self.source):
            picker.install(target)
        package = target / picker.OWNER / 'package'
        names = {p.relative_to(package).as_posix() for p in package.rglob('*') if p.is_file()}
        self.assertEqual(names, set(package_files.INSTALL_FILES))
        skill = target / 'skills' / picker.OWNER
        self.assertEqual({p.name for p in skill.iterdir()}, {'SKILL.md'})
        self.assertNotIn(self.sentinel, json.dumps(picker.read(target / picker.OWNER / 'install.json')))

    def test_manifest_contains_only_expected_unique_paths(self):
        for manifest in (package_files.INSTALL_FILES, package_files.RELEASE_FILES):
            self.assertEqual(len(manifest), len(set(manifest)))
            self.assertFalse(any(Path(n).name.startswith('.env') for n in manifest))
        self.assertTrue(set(package_files.INSTALL_FILES) <= set(package_files.RELEASE_FILES))

    def test_upgrade_retires_old_owned_builder_and_preserves_preferences(self):
        target = self.base / 'target'
        with patch.object(picker, 'ROOT', self.source):
            picker.install(target)
            old_builder = target / picker.OWNER / 'package' / 'build_release.py'
            old_builder.write_text('legacy recursive builder')
            marker = target / picker.OWNER / 'install.json'
            owned = picker.read(marker)
            owned['files'][str(old_builder.relative_to(target))] = picker.digest(old_builder)
            picker.write(marker, owned)
            picker.write(target / picker.OWNER / 'config.json', picker.SUGGESTED)
            picker.install(target)
        self.assertFalse(old_builder.exists())
        self.assertEqual(picker.read(target / picker.OWNER / 'config.json'), picker.SUGGESTED)

    def test_missing_required_file_stops_before_release_or_install_writes(self):
        (self.source / 'providers/openai.json').unlink()
        output, target = self.base / 'output', self.base / 'target'
        with patch.object(build_release, 'ROOT', self.source), self.assertRaises(OSError):
            build_release.build(output)
        with patch.object(picker, 'ROOT', self.source), self.assertRaises(OSError):
            picker.install(target)
        self.assertFalse(output.exists())
        self.assertFalse(target.exists())

    def link(self, target, destination, directory=False):
        try:
            destination.symlink_to(target, target_is_directory=directory)
        except (OSError, NotImplementedError) as error:
            self.skipTest('Native symlink creation unavailable: ' + str(error))

    def test_listed_symlink_is_rejected_before_output(self):
        private = self.base / 'private.txt'
        private.write_text(self.sentinel)
        (self.source / 'README.md').unlink()
        self.link(private, self.source / 'README.md')
        with patch.object(build_release, 'ROOT', self.source), self.assertRaises(ValueError):
            build_release.build(self.base / 'release')
        with patch.object(picker, 'ROOT', self.source), self.assertRaises(ValueError):
            picker.install(self.base / 'target')
        self.assertFalse((self.base / 'release').exists())
        self.assertFalse((self.base / 'target').exists())

    def test_linked_parent_directory_is_rejected(self):
        external = self.base / 'outside-policies'
        shutil.move(str(self.source / 'policies'), external)
        self.link(external, self.source / 'policies', directory=True)
        with self.assertRaises(ValueError):
            package_files.source_bytes(self.source, package_files.INSTALL_FILES)

    def test_unlisted_symlink_is_never_followed(self):
        private = self.base / 'private.txt'
        private.write_text(self.sentinel)
        self.link(private, self.source / 'private-link.txt')
        result = package_files.source_bytes(self.source, package_files.RELEASE_FILES)
        self.assertNotIn('private-link.txt', result)
        self.assertTrue(all(self.sentinel.encode() not in v for v in result.values()))

    @unittest.skipUnless(os.name == 'nt', 'Windows junction boundary')
    def test_windows_junction_parent_rejected(self):
        command = shutil.which('cmd.exe')
        if not command:
            self.skipTest('cmd.exe unavailable for junction fixture')
        external = self.base / 'outside-policies'
        shutil.move(str(self.source / 'policies'), external)
        junction = self.source / 'policies'
        result = subprocess.run([command, '/d', '/c', 'mklink', '/J', str(junction), str(external)],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        with self.assertRaises(ValueError):
            package_files.source_bytes(self.source, package_files.INSTALL_FILES)

    def test_unsafe_manifest_paths_rejected(self):
        for name in ('../private.txt', '/private.txt', 'C:/private.txt', 'nested\\private.txt'):
            with self.subTest(name=name), self.assertRaises(ValueError):
                package_files.source_bytes(self.source, [name])

    def test_directory_cannot_replace_listed_file(self):
        (self.source / 'README.md').unlink()
        (self.source / 'README.md').mkdir()
        with self.assertRaises(ValueError):
            package_files.source_bytes(self.source, package_files.RELEASE_FILES)

    def test_build_is_repeatable_with_unrelated_files(self):
        with patch.object(build_release, 'ROOT', self.source):
            first = build_release.build(self.base / 'first')
            self.extras()
            second = build_release.build(self.base / 'second')
        self.assertEqual(first['sha256'], second['sha256'])


if __name__ == '__main__':
    unittest.main()
