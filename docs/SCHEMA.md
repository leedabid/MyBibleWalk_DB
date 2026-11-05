# 파일 형식 (schema 1)

## index.json
```json
{
  "schema": 1,
  "updated": "2026-11-04",
  "books": [
    { "book": 2, "name": "출애굽기", "file": "books/02_출애굽기.json", "status": "draft", "updated": "2026-11-04" }
  ]
}
```
- `book`: 앱의 권 번호(창세기=1 … 요한계시록=66)
- `status`: `draft`(초안·검증 중) 또는 `verified`(문장별 검증 완료)

## books/NN_이름.json
```json
{
  "schema": 1,
  "book": 2,
  "name": "출애굽기",
  "status": "draft",
  "updated": "2026-11-04",
  "framework": "보스 4분과(넓은 의미의 주경신학 안에 성경개론·성경신학·본문 주해)",
  "sections": [
    {
      "id": "overview",
      "heading": "한눈에 보기",
      "discipline": "성경개론",
      "sentences": [
        { "text": "문장.", "refs": [1, 2] },
        { "text": "근거 없는 정리 문장.", "refs": [], "unsourced": true }
      ]
    }
  ],
  "refs": [
    {
      "n": 1,
      "cite": "저자, 제목, 출판 정보",
      "where": "쪽·장·절·글 안의 소제목",
      "url": "https://…",
      "accessed": "2026-11-04",
      "level": "full",
      "evidence": ["근거 확인용 짧은 발췌(원문 언어, 15단어 이내)", "필요하면 여러 개"]
    }
  ]
}
```
- `sentences[].refs`: 그 문장을 뒷받침하는 `refs[].n` 목록. 비어 있으면 `unsourced: true`를 함께 둡니다.
- `refs[].level`: `full` / `abstract` / `secondary`
- 성경 구절 자체를 근거로 쓸 때는 `cite`에 구절을 적고 `where`에 장:절을 적습니다. (예: 본문 확인용 `출 12:37`)
- 앱은 문장의 번호를 눌렀을 때 맨 아래 `refs`의 같은 번호 항목으로 이동합니다.

## 추가 필드
- `notes`: 파일 전체에 대한 주의 문구 목록(검증 범위, 출처의 관점 등).
- `route`(선택): 여정 순서. `{order, name, verses, refs, lat, lng, locationNote}`. 좌표는 근거 자료를 확인한 것만 넣고, 확인 못 하면 `null`로 둡니다.
- `sections[].discipline`: 그 섹션이 속하는 분과(예: 성경개론, 성경 배경(지리), 성경신학).
- 가독용 미리보기는 `preview/NN_이름.md`에 같은 내용을 마크다운으로 둡니다(번호·참고 목록 포함).

## limits.json (AI 한도 기본값)
앱이 AI 설정 화면에서 모델별 한도의 **기본값**으로 읽습니다. 구글이 한도를 바꾸면 이 파일만 고쳐 올립니다(앱을 다시 설치할 필요 없음).
```json
{ "schema": 1, "updated": "2026-11-04", "tier": "free",
  "models": [ { "match": "3.5-flash-lite", "rpm": 15, "tpm": 250000, "rpd": 500 } ] }
```
- `match`: 모델 이름에 이 글자가 들어 있으면 해당 값을 씁니다. 위에서부터 처음 맞는 항목이 적용되므로 `2.5-flash-lite`를 `2.5-flash`보다 위에 둡니다.
- `rpm`(분당 요청), `tpm`(분당 입력 토큰), `rpd`(하루 요청). 사용자가 앱에서 직접 적은 값이 있으면 그 값이 우선합니다.
- 값은 Google AI Studio의 '비율 제한' 화면에서 확인한 숫자를 적습니다(무료 등급과 유료 등급은 다름).

## 여러 권이 함께 쓰는 자료 (shared/)
`index.json`의 `shared: [{id, file, updated}]`에 나열합니다. 앱은 책을 받을 때 함께 받아 둡니다.
- `shared/geo.json`: `{ refs[], places[], unlockedOther[], journeys[] }`. `refs`의 번호는 이 파일 안에서만 씁니다.
  - `places[]`: `{id, name, nameEn, kind, verses, mapped, primary, candidates[{label, lat, lng, score, tier, precision, refs}], refs}`. `score`는 OpenBible best_path_score, `tier`(높음 400 이상·보통 150–399·낮음 150 미만)는 이 앱의 구분.
  - `journeys[]`: `{id, title, period, note, color, lineStyle, lineMinScore, books[], stops[{order, placeId, name, time, event, verses, refs}]}`. `lineMinScore` 이상인 지점만 선으로 잇는다.
  - 이동 순서가 없는 권의 '주요 지명 목록'도 같은 모양의 여정으로 둡니다. `lineStyle: "none"`, `lineMinScore: 1001`(점수는 최대 1000대 초반이라 어떤 지점도 선에 들지 않음)로 두면 선 없이 점만 찍힙니다. 앱이 `lineStyle: "none"`을 모르더라도 1001 때문에 선은 그려지지 않습니다.
- 책 파일의 `geo`는 `{ "shared": "geo", "journeys": ["id", ...], "focus": "id" }`로 가리키기만 합니다. (예전처럼 책 안에 `places`·`routes`를 직접 둘 수도 있으나 새 책은 공용 파일을 씁니다.)

## links (다른 권과의 연결)
`tools/crossref_links.py`가 만든 수치. `links: {source, total, ot, nt, byBook[], topChapters[], topPairs[], todo}`. 같은 내용을 문장으로 풀어 `sections`의 "다른 권과의 연결" 섹션에 넣습니다. 해석(영향·인용)은 이 수치와 섞지 않고 별도 섹션에 각주와 함께 씁니다. 자세한 원칙은 `docs/BOOK_OVERVIEW_GUIDE.md`.

## refs[].level 추가 값
- `reference`: 성경 구절의 위치만 제시했고 본문을 직접 열어 확인하지 못함. 상태를 `verified`로 올리기 전에 본문과 대조해야 합니다.
