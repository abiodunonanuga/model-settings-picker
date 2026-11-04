"""Build a release from the explicit reviewed file manifest, never a directory scan."""
import argparse
import hashlib
import json
from pathlib import Path
import zipfile
from package_files import RELEASE_FILES, VERSION, source_bytes

ROOT = Path(__file__).resolve().parent

def build(output):
    output = Path(output).resolve()
    if output == ROOT or ROOT in output.parents:
        raise ValueError('Release output must be outside the source tree')
    files = source_bytes(ROOT, RELEASE_FILES)
    output.mkdir(parents=True, exist_ok=True)
    manifest = {name: hashlib.sha256(content).hexdigest() for name, content in sorted(files.items())}
    archive = output / ('model-settings-picker-' + VERSION + '.zip')
    with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED) as z:
        for relative, content in sorted(files.items()):
            name = 'model-settings-picker/' + relative
            info = zipfile.ZipInfo(name, date_time=(2026, 11, 3, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            z.writestr(info, content)
    result = {'archive': archive.name, 'sha256': hashlib.sha256(archive.read_bytes()).hexdigest(), 'files': manifest}
    (output / 'release-manifest.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    return result

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True)
    print(json.dumps(build(parser.parse_args().output), indent=2))
