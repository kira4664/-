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
