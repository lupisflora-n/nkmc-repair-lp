#!/usr/bin/env python3
"""Package the project handoff without internal-only founder context."""
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT.parent / 'NKMC-repair-LP-production-kit.zip'
PRIVATE_FILES = {Path('docs/BRAND_CONTEXT_PRIVATE.md')}


def main():
    with zipfile.ZipFile(ARCHIVE, 'w', compression=zipfile.ZIP_DEFLATED) as bundle:
        for path in sorted(ROOT.rglob('*')):
            if not path.is_file() or '.git' in path.parts or '__pycache__' in path.parts:
                continue
            relative = path.relative_to(ROOT)
            if relative in PRIVATE_FILES:
                continue
            bundle.write(path, Path(ROOT.name) / relative)
    with zipfile.ZipFile(ARCHIVE) as bundle:
        assert bundle.testzip() is None
        assert all(str(Path(ROOT.name) / path) not in bundle.namelist() for path in PRIVATE_FILES)
        print(f'制作データ一式: {len(bundle.namelist())}ファイル。内部限定の創業背景は含めていません。')
    print(ARCHIVE)


if __name__ == '__main__':
    main()
