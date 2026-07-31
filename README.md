# 음식 숏폼 대본 생성기 (Food Script Generator)

음식 관련 키워드를 입력하면 자동으로 팩트체크를 거쳐 일본어와 영어로 현지인 스타일의 숏폼 대본을 생성하는 도구입니다.

## 주요 기능

- 🔍 **자동 팩트체크**: 입력한 키워드로 웹 검색을 수행하여 정확한 정보 수집
- 🇯🇵 **일본어 대본**: 현지인이 사용하는 자연스러운 일본어 표현
- 🇺🇸 **영어 대본**: 네이티브 스피커 스타일의 영어 표현
- 🎬 **숏폼 최적화**: 짧고 임팩트 있는 대본 구성

## 설치 방법

```bash
pip install -r requirements.txt
```

## 사용 방법

### 기본 사용

```bash
python script_generator.py --keyword "라면의 역사"
```

### 언어 선택

```bash
# 일본어만 생성
python script_generator.py --keyword "김치찌개" --lang ja

# 영어만 생성
python script_generator.py --keyword "bibimbap" --lang en

# 둘 다 생성 (기본값)
python script_generator.py --keyword "스시" --lang both
```

### 대본 길이 설정

```bash
python script_generator.py --keyword "타코야키" --duration 30  # 30초
python script_generator.py --keyword "라멘" --duration 60      # 1분
```

## 초기 설정

### 1. API 키 설정

```bash
# .env 파일 생성
cp .env.example .env

# .env 파일을 열고 Anthropic API 키 입력
# ANTHROPIC_API_KEY=your_api_key_here
```

### 2. 커스텀 대본 스타일 설정 (중요!)

`config.json` 파일의 `custom_prompt_style` 필드에 **"클로드 입숏대본쓰기"에서 사용하던 프롬프트 스타일**을 입력하세요.

```json
{
  "custom_prompt_style": "여기에 기존 프롬프트의 말투/스타일을 입력하세요. 예: 친구에게 말하듯 편하게, 약간 과장된 리액션으로 재미있게 전달"
}
```

예시:
- "MZ세대 감성으로 밈과 유행어를 섞어서"
- "전문가처럼 깊이 있게, 하지만 쉽게 설명하는 스타일"
- "재치있고 위트있는 표현으로 웃음을 주면서"

### 3. 세부 설정 조정

`config.json`에서 대본 스타일, 톤, 포맷을 커스터마이징할 수 있습니다:

- `default_duration`: 기본 대본 길이 (초)
- `style.japanese.tone`: 일본어 대본의 톤
- `style.english.tone`: 영어 대본의 톤

## 프로젝트 구조

```
.
├── README.md
├── requirements.txt
├── config.json              # 설정 및 프롬프트 스타일
├── script_generator.py      # 메인 스크립트
├── prompts/
│   ├── japanese_style.txt   # 일본어 대본 스타일 가이드
│   └── english_style.txt    # 영어 대본 스타일 가이드
└── output/                  # 생성된 대본 저장 폴더
```

## 출력 예시

생성된 대본은 `output/` 폴더에 JSON 형식으로 저장됩니다.

---

# 블로그 자동 포스팅 도구 (Blog Auto Poster)

키워드를 입력하면 웹에서 자료를 검색·취합하고, 그 자료를 바탕으로 블로그 글을 작성한 뒤 워드프레스에 자동으로 포스팅하는 도구입니다.

## 동작 방식

1. **웹 리서치**: Claude의 웹 검색 도구로 키워드 관련 최신 자료를 여러 출처에서 수집·취합
2. **글 작성**: 취합된 자료를 근거로 제목/본문(HTML)/발췌문/태그/메타 설명을 생성
3. **자동 포스팅**: 워드프레스 REST API로 지정한 상태(초안/발행 등)로 게시

## 초기 설정

### 1. 워드프레스 Application Password 발급

워드프레스 관리자 페이지 → 사용자 → 프로필 → **Application Passwords**에서 새 비밀번호를 발급받으세요. 일반 로그인 비밀번호가 아니라 이 전용 비밀번호를 사용해야 합니다.

### 2. `.env` 파일에 정보 입력

```bash
cp .env.example .env
```

```
ANTHROPIC_API_KEY=your_api_key_here
WP_URL=https://your-wordpress-site.com
WP_USERNAME=your_wp_username
WP_APP_PASSWORD=xxxx xxxx xxxx xxxx xxxx xxxx
```

### 3. `config.json`의 `blog` 섹션 설정 (선택)

```json
{
  "blog": {
    "language": "ko",
    "default_status": "draft",
    "default_category": "",
    "num_search_queries": 5,
    "min_word_count": 800,
    "tone": "친근하고 신뢰감 있는",
    "custom_style": ""
  }
}
```

- `default_status`: `draft`(초안) / `publish`(즉시 발행) / `pending`(검토 대기) — 기본값은 안전하게 `draft`
- `num_search_queries`: 웹 검색 최대 횟수
- `custom_style`: 원하는 문체/톤을 자유롭게 지정

## 사용 방법

```bash
# 초안으로만 생성 (실제 게시 없이 결과만 확인)
python blog_poster.py --keyword "2026년 AI 트렌드" --dry-run

# 워드프레스에 초안으로 저장
python blog_poster.py --keyword "홈트레이닝 루틴 추천"

# 카테고리 지정 + 즉시 발행
python blog_poster.py --keyword "제주도 여행 코스" --status publish --category "여행"

# 영어로 작성
python blog_poster.py --keyword "best coffee brewing methods" --lang en
```

기본값은 `--status draft`로, 실수로 바로 공개 발행되지 않도록 안전하게 초안 상태로 저장됩니다. 확인 후 워드프레스 관리자 페이지에서 직접 발행하거나, `--status publish`를 명시적으로 지정하세요.

리서치 자료와 생성된 글, 워드프레스 게시 결과는 `output/blog_<키워드>_<타임스탬프>.json`에 저장됩니다.

## 주제 자동 선정

`--keyword`를 생략하고 실행하면, 웹 검색으로 최근 화제/트렌드를 확인해 블로그 글감이 될 만한 구체적인 주제를 자동으로 하나 고릅니다.

```bash
python blog_poster.py --status draft
```

- 이미 다룬 주제는 `data/used_topics.json`에 기록되어, 다음 자동 선정 시 중복을 피하는 데 사용됩니다.
- `config.json`의 `blog.topic_category`에 값을 넣으면 특정 분야(예: `"IT/테크"`, `"여행"`) 안에서만 주제를 고릅니다. 비워두면 분야 제한 없이 폭넓게 고릅니다.

## 자동 반복 실행 (GitHub Actions)

`.github/workflows/blog-auto-post.yml`에 **3시간마다(하루 8회)** 자동으로 실행되는 워크플로가 포함되어 있습니다. 매 실행마다 키워드 없이 `blog_poster.py --status draft`를 호출해 주제를 자동으로 고르고, 초안으로 워드프레스에 저장합니다.

### 설정 방법

1. GitHub 저장소 **Settings → Secrets and variables → Actions**에서 다음 시크릿을 등록하세요:
   - `ANTHROPIC_API_KEY`
   - `WP_URL`
   - `WP_USERNAME`
   - `WP_APP_PASSWORD`
2. 이 워크플로 파일이 **저장소의 기본 브랜치**에 병합되어야 스케줄이 실제로 동작합니다 (GitHub는 기본 브랜치에 있는 워크플로만 `schedule` 트리거로 실행합니다). PR이 머지되기 전까지는 **Actions 탭에서 수동 실행(`workflow_dispatch`)** 으로 미리 테스트할 수 있습니다.
3. 주제 중복을 피하기 위해 매 실행 후 `data/used_topics.json`을 저장소에 자동으로 커밋합니다.

### 안전장치

- 게시 상태는 항상 `draft`(초안)입니다. 자동 생성된 글이 검수 없이 바로 공개되지 않도록 하기 위함이며, 품질을 확인한 뒤 워드프레스 관리자 페이지에서 직접 발행하는 것을 권장합니다.
- 실행 주기나 게시 상태를 바꾸려면 워크플로 파일의 `cron` 값과 `--status` 옵션을 수정하세요.
