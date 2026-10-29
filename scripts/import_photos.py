#!/usr/bin/env python3
"""Copy received originals byte-for-byte and register their SHA-256 values."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--case', choices=['case-01', 'case-02', 'case-03'], required=True)
    parser.add_argument('--before', type=Path, required=True)
    parser.add_argument('--after', type=Path, required=True)
    args = parser.parse_args()
    config = ROOT / 'site/content.json'
    data = json.loads(config.read_text(encoding='utf-8'))
    case = next(item for item in data['cases']['items'] if item['id'] == args.case)
    planned = []
    for side in ('before', 'after'):
        source = getattr(args, side).resolve(strict=True)
        if source.suffix.lower() not in {'.jpg', '.jpeg', '.png', '.webp', '.avif', '.gif'}:
            raise SystemExit('受領したブラウザ対応の元写真を指定してください。変換は行いません。')
        relative = f'assets/cases/{args.case}-{side}{source.suffix.lower()}'
        target = ROOT / 'site' / relative
        digest = hashlib.sha256(source.read_bytes()).hexdigest()
        if target.exists() and hashlib.sha256(target.read_bytes()).hexdigest() != digest:
            raise SystemExit(f'既存の元写真を上書きできません: {relative}')
        planned.append((side, source, target, relative, digest))
    for side, source, target, relative, digest in planned:
        target.parent.mkdir(parents=True, exist_ok=True)
        if source != target:
            shutil.copy2(source, target)
        if hashlib.sha256(target.read_bytes()).hexdigest() != digest:
            raise SystemExit('複製後の写真が元ファイルと一致しません。')
        case[side] = relative
        case[side + 'Sha256'] = digest
    config.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(args.case + ': 元ファイルを無加工で複製し、SHA-256を記録しました。内容・掲載条件の確認フラグは変更していません。')


if __name__ == '__main__':
    main()
