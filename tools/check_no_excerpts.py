# -*- coding: utf-8 -*-
"""저작권 검사: books/*.json, shared/geo.json의 refs[].evidence가 모두 비어 있는지 확인합니다.
사용: python3 tools/check_no_excerpts.py            (작업 폴더 검사)
      python3 tools/check_no_excerpts.py <커밋>      (그 커밋의 내용 검사)
발췌가 있으면 목록을 보여 주고 종료 코드 1을 돌려줍니다."""
import json, sys, subprocess, glob, os
rev = sys.argv[1] if len(sys.argv) > 1 else None
def files():
    if rev:
        out = subprocess.check_output(['git', 'ls-tree', '-r', '-z', '--name-only', rev]).decode('utf-8').split('\0')
        return [f for f in out if (f.startswith('books/') and f.endswith('.json')) or f == 'shared/geo.json']
    return sorted(glob.glob('books/*.json')) + (['shared/geo.json'] if os.path.exists('shared/geo.json') else [])
def load(f):
    if rev: return json.loads(subprocess.check_output(['git', 'show', f'{rev}:{f}']).decode('utf-8'))
    return json.load(open(f, encoding='utf-8'))
bad = []
for f in files():
    for r in load(f).get('refs', []):
        if r.get('evidence'): bad.append((f, r.get('n')))
if bad:
    print('원문 발췌(evidence)가 남아 있습니다:', len(bad), '건'); [print(' ', b) for b in bad[:20]]; sys.exit(1)
print('OK: 원문 발췌 없음')
