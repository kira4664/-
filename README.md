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

---

# 검색엔진 노출 확인 도구 (SEO Exposure Checker)

워드프레스에 올린 글이 구글/빙/네이버/다음(카카오) 검색 결과에 실제로 노출되는지 확인하는 도구입니다. 각 검색엔진의 검색결과 화면을 직접 크롤링하지 않고(봇 차단·캡차로 금방 막히고 이용약관에도 어긋남), **각 사가 공식 제공하는 검색 API**를 사용해 글 제목으로 검색해본 뒤 결과 안에 내 글 URL이 있는지, 몇 위인지 확인합니다.

## 동작 방식

1. 워드프레스 REST API(`/wp-json/wp/v2/posts`)로 최근 발행된 글 목록(제목/URL)을 가져옵니다.
2. 각 글 제목을 검색어로 구글/빙/네이버/다음 검색 API를 호출합니다.
3. 검색 결과 URL 목록에 내 글 URL이 있는지 비교해 노출 여부와 순위를 판정합니다.
4. 결과를 콘솔에 출력하고 `output/seo_check_<타임스탬프>.json`에 저장합니다.

키를 설정하지 않은 검색엔진은 자동으로 건너뛰고 "확인 불가"로 표시되므로, 필요한 엔진만 선택적으로 설정해도 됩니다.

## API 키 발급 방법

| 검색엔진 | 필요한 키 | 발급처 |
|---|---|---|
| 구글 | `GOOGLE_API_KEY`, `GOOGLE_CSE_ID` | [Programmable Search Engine](https://programmablesearchengine.google.com/)에서 검색엔진 생성 시 "전체 웹 검색"으로 설정 후, [Custom Search API](https://developers.google.com/custom-search/v1/overview)용 API 키 발급 (무료 할당량 100건/일, 초과 시 유료) |
| 빙 | `BING_API_KEY` | Azure Portal에서 Bing Search v7 리소스 발급 (Microsoft 정책 변경으로 신규 발급이 제한/중단될 수 있으니, Azure Portal에서 현재 가입 가능 여부를 먼저 확인하세요) |
| 네이버 | `NAVER_CLIENT_ID`, `NAVER_CLIENT_SECRET` | [네이버 개발자센터](https://developers.naver.com/apps/#/register) → 애플리케이션 등록 → "검색" API 사용 설정 |
| 다음(카카오) | `KAKAO_REST_API_KEY` | [카카오 디벨로퍼스](https://developers.kakao.com/) → 애플리케이션 등록 → REST API 키 확인 (다음 검색은 카카오 검색 API로 제공됩니다) |

`.env` 파일에 필요한 키를 추가하세요 (`.env.example` 참고).

## 사용 방법

```bash
# 최근 발행 글 5개를 전체 검색엔진으로 확인 (기본값)
python seo_exposure_checker.py

# 최근 10개 글 확인
python seo_exposure_checker.py --limit 10

# 특정 검색엔진만 확인
python seo_exposure_checker.py --engines google,naver

# 워드프레스 목록 조회 없이, 특정 URL 하나만 확인
python seo_exposure_checker.py --url "https://your-wordpress-site.com/2026/09/02/my-post/" --title "글 제목"
```

## 참고 및 한계

- 네이버/다음(카카오)의 "검색 API" 결과는 실제 통합검색 화면 노출 순서와 완전히 같지 않을 수 있습니다 (오픈API는 웹문서 검색 결과 기준). 참고용 지표로 활용하세요.
- 구글 Custom Search API, 빙 Search API는 모두 일별 무료 할당량이 있고 초과 시 과금되거나 제한됩니다.
- 갓 발행한 글은 검색엔진이 아직 색인(크롤링)하지 않아 당연히 미노출로 나올 수 있습니다. 보통 몇 시간~며칠 후 다시 확인해보세요.
- 구글의 경우 [Google Search Console](https://search.google.com/search-console)에 사이트를 등록하면 특정 URL의 실제 색인 상태(크롤링 여부, 색인 제외 사유 등)를 훨씬 정확하게 확인할 수 있습니다. 이 도구는 "검색 노출 여부"를 빠르게 훑어보는 용도이고, 정확한 색인 진단은 각 검색엔진의 웹마스터 도구(네이버 서치어드바이저, 빙 웹마스터 도구 포함)를 함께 활용하는 것을 권장합니다.
