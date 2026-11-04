"""Reviewed distribution boundaries, shared by the installer and release builder.

Adding a source file requires an intentional update here. Git status, ignored
files and arbitrary files alongside a checkout never expand either package.
"""
from pathlib import Path, PurePosixPath
import stat

VERSION = '0.1.1'
PLUGIN_FILES = (
    'LICENSE',
    'README.md',
    'INSTALL.md',
    'picker.py',
    'package_files.py',
    'policies/runtime.md',
    'providers/openai.json',
    'skills/model-settings-picker/SKILL.md',
    'plugin.json',
    '.codex-plugin/plugin.json',
    '.agents/plugins/marketplace.json',
    'hooks/hooks.json',
    'hooks/run-hook.sh',
    'hooks/run-hook.ps1',
)
RELEASE_FILES = PLUGIN_FILES + (
    '.gitattributes',
    '.gitignore',
    '.github/workflows/test.yml',
    'build_release.py',
    'tests/test_picker.py',
    'tests/test_package_files.py',
    'tests/test_native_plugin.py',
)


def source_bytes(root, names):
    """Snapshot only explicitly named regular files; reject links before reading.

    Validate the entire selected set before any consumer writes output. Check every
    component so a linked parent directory cannot bypass a leaf-only symlink check.
    Windows junctions/reparse points are rejected, including on Python 3.10.
    """
    root = Path(root).resolve(strict=True)
    result = {}
    for name in names:
        relative = PurePosixPath(name)
        if relative.is_absolute() or '..' in relative.parts or '\\' in name or ':' in name:
            raise ValueError('Unsafe package manifest entry: ' + name)
        path = root
        for component in relative.parts:
            path = path / component
            info = path.lstat()
            if stat.S_ISLNK(info.st_mode) or getattr(info, 'st_file_attributes', 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT:
                raise ValueError('Linked package source is forbidden: ' + name)
        if not stat.S_ISREG(info.st_mode) or root not in path.resolve(strict=True).parents:
            raise ValueError('Package source must be a contained regular file: ' + name)
        result[name] = path.read_bytes()
    return result
