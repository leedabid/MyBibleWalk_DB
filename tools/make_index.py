# -*- coding: utf-8 -*-
"""DB를 고친 뒤 커밋하기 전에 한 번 실행: python3 tools/make_index.py
index.json의 각 파일에 rev(내용 지문)를 다시 계산해 넣습니다. 앱은 이 rev를 받은 파일과 비교해 '업데이트 있음'을 알립니다."""
import json, hashlib, os
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
p = os.path.join(root, 'index.json')
idx = json.load(open(p, encoding='utf-8'))
def rev(rel):
    b = open(os.path.join(root, rel), 'rb').read().replace(b'\r\n', b'\n')
    return hashlib.sha1(b).hexdigest()[:12]
n = 0
for key in ('books', 'shared'):
    for e in idx.get(key, []):
        f = e.get('file')
        if f and os.path.exists(os.path.join(root, f)):
            r = rev(f)
            if e.get('rev') != r:
                e['rev'] = r; n += 1
json.dump(idx, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('rev 갱신:', n)
