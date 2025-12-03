# 사용 예시 및 가이드

## 설정하기

### 1. API 키 설정

`.env` 파일을 생성하고 Anthropic API 키를 입력하세요:

```bash
cp .env.example .env
# .env 파일을 열고 API 키를 입력하세요
```

`.env` 파일 내용:
```
ANTHROPIC_API_KEY=sk-ant-api03-...
```

### 2. 패키지 설치

```bash
pip install -r requirements.txt
```

### 3. 스타일 커스터마이징 (선택사항)

`config.json` 파일의 `custom_prompt_style` 필드에 원하는 대본 스타일을 입력하세요.

예시:
```json
{
  "custom_prompt_style": "친구에게 말하듯 편하게, 그리고 약간 과장된 리액션으로 재미있게 전달하는 스타일"
}
```

## 실행 예시

### 기본 사용 (일본어 + 영어)

```bash
python script_generator.py --keyword "타코야키"
```

출력:
```
🔍 '타코야키'에 대한 리서치를 시작합니다...
✅ 리서치 완료!

✍️  일본어 대본을 생성 중...
✅ 일본어 대본 생성 완료!

==================================================
【일본어 대본】
==================================================
[생성된 일본어 대본]
==================================================

✍️  영어 대본을 생성 중...
✅ 영어 대본 생성 완료!

==================================================
【영어 대본】
==================================================
[생성된 영어 대본]
==================================================

💾 결과가 저장되었습니다: output/타코야키_20231203_153045.json
```

### 일본어만 생성

```bash
python script_generator.py --keyword "라멘" --lang ja
```

### 영어만 생성

```bash
python script_generator.py --keyword "korean fried chicken" --lang en
```

### 대본 길이 지정

```bash
# 30초 대본
python script_generator.py --keyword "김치찌개" --duration 30

# 1분 대본 (기본값)
python script_generator.py --keyword "비빔밥" --duration 60

# 3분 대본
python script_generator.py --keyword "한국의 발효음식" --duration 180
```

## 출력 파일 구조

생성된 JSON 파일 예시:

```json
{
  "keyword": "타코야키",
  "duration": 60,
  "research_data": "타코야키에 대한 리서치 정보...",
  "scripts": {
    "ja": "일본어 대본 내용...",
    "en": "English script content..."
  }
}
```

## 활용 팁

### 1. 여러 키워드 일괄 처리

```bash
# keywords.txt 파일에 키워드 목록 작성
for keyword in $(cat keywords.txt); do
  python script_generator.py --keyword "$keyword"
  sleep 2  # API 호출 간격
done
```

### 2. 시리즈 콘텐츠 제작

```bash
# 한국 음식 시리즈
python script_generator.py --keyword "김치" --duration 60
python script_generator.py --keyword "된장찌개" --duration 60
python script_generator.py --keyword "불고기" --duration 60

# 일본 음식 시리즈
python script_generator.py --keyword "스시" --duration 60 --lang ja
python script_generator.py --keyword "라멘" --duration 60 --lang ja
```

### 3. 트렌드 키워드 활용

최신 음식 트렌드를 키워드로 활용하세요:
- "탕후루"
- "크로플"
- "마라탕"
- "밀키트"
- "비건 디저트"

### 4. 비교/대결 콘텐츠

```bash
python script_generator.py --keyword "일본 라멘 vs 한국 라면 차이점"
python script_generator.py --keyword "authentic pizza vs american pizza"
```

## 고급 설정

### config.json 커스터마이징

```json
{
  "default_duration": 45,  // 기본 대본 길이를 45초로 변경
  "style": {
    "japanese": {
      "tone": "엔터테이닝하고 유머러스한",  // 톤 변경
      "use_casual_speech": true,
      "include_reactions": true
    },
    "english": {
      "tone": "educational but fun",  // 교육적이면서 재미있게
      "use_casual_speech": true,
      "include_reactions": true
    }
  },
  "custom_prompt_style": "MZ세대가 좋아할 만한 밈과 유행어를 적절히 섞어서"
}
```

## 문제 해결

### API 키 오류
```
ValueError: ANTHROPIC_API_KEY가 설정되지 않았습니다.
```
→ `.env` 파일을 확인하고 올바른 API 키를 입력했는지 확인하세요.

### 생성 속도가 느림
- 대본 생성은 약 30초~1분 정도 소요됩니다
- `duration` 값을 줄이면 더 빠르게 생성됩니다

### 대본 품질 개선
1. `config.json`의 `custom_prompt_style` 수정
2. `prompts/` 폴더의 스타일 가이드 수정
3. 더 구체적인 키워드 사용 (예: "라면" → "일본 돈코츠 라멘의 역사")

## 다음 단계

생성된 대본을 활용하여:
1. 영상 촬영 스크립트로 활용
2. 자막 제작
3. 보이스오버 녹음
4. 썸네일 문구 추출

Happy scripting! 🎬🍜
