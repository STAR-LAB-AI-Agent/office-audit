"""Compare local rule revisions without publishing document text or filenames."""
import argparse
import hashlib
import importlib.util
import json
import subprocess
import types
from collections import Counter
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sample-root', required=True)
    parser.add_argument('--baseline', default='2dcc5f3')
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    # --baseline is a trusted local Git revision selected by the operator.
    source = subprocess.run(['git', 'show', args.baseline + ':scripts/audit_docx.py'],
                            cwd=root, check=True, capture_output=True).stdout
    before_module = types.ModuleType('audit_baseline')
    exec(compile(source, '<trusted-git-baseline>', 'exec'), before_module.__dict__)
    spec = importlib.util.spec_from_file_location('audit_current', root / 'scripts/audit_docx.py')
    current = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(current)
    rows = []
    for ordinal, path in enumerate(sorted(Path(args.sample_root).glob('*.docx')), 1):
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        row = {'sample': f'{ordinal:02d}'}
        for label, module in [('before', before_module), ('after', current)]:
            result = module.audit_document(path)
            row[label] = {'rules': dict(Counter(f['rule_id'] for f in result['findings'])),
                          'summary': result['summary'],
                          'unsupported': len(result['unsupported_objects']),
                          'error_codes': [e['code'] for e in result['errors']]}
        row['source_unchanged'] = digest == hashlib.sha256(path.read_bytes()).hexdigest()
        rows.append(row)
    print(json.dumps({'baseline': args.baseline, 'samples': rows}, ensure_ascii=False, indent=2))
    return 0 if rows and all(r['source_unchanged'] and not r['before']['error_codes']
                            and not r['after']['error_codes'] for r in rows) else 1


if __name__ == '__main__':
    raise SystemExit(main())
