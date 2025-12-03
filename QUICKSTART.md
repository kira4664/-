# 빠른 시작 가이드

## 5분 안에 시작하기

### 1단계: API 키 설정 ⚙️

```bash
# 1. .env 파일 생성
cp .env.example .env

# 2. .env 파일을 편집기로 열기
nano .env  # 또는 vim, code 등

# 3. API 키 입력
ANTHROPIC_API_KEY=sk-ant-api03-여기에입력
```

💡 API 키는 https://console.anthropic.com/ 에서 발급받을 수 있습니다.

### 2단계: 패키지 설치 📦

```bash
pip install -r requirements.txt
```

### 3단계: 대본 스타일 설정 ✏️

`config.json` 파일을 열고 `custom_prompt_style`을 수정하세요:

```json
{
  "custom_prompt_style": "친구에게 얘기하듯 편하고 재미있게, 중간중간 리액션 섞어서"
}
```

### 4단계: 첫 대본 생성! 🎬

```bash
python script_generator.py --keyword "김치"
```

실행하면 다음과 같이 진행됩니다:

```
🔍 '김치'에 대한 리서치를 시작합니다...
✅ 리서치 완료!

✍️  일본어 대본을 생성 중...
✅ 일본어 대본 생성 완료!

==================================================
【일본어 대본】
==================================================
[일본어 대본 내용]
==================================================

✍️  영어 대본을 생성 중...
✅ 영어 대본 생성 완료!

==================================================
【영어 대본】
==================================================
[영어 대본 내용]
==================================================

💾 결과가 저장되었습니다: output/김치_20231203_153045.json
```

## 자주 사용하는 명령어

```bash
# 일본어만
python script_generator.py --keyword "라멘" --lang ja

# 영어만
python script_generator.py --keyword "sushi" --lang en

# 30초 짧은 버전
python script_generator.py --keyword "타코야키" --duration 30

# 3분 긴 버전
python script_generator.py --keyword "한식의 역사" --duration 180
```

## 문제 해결

### ❌ "ANTHROPIC_API_KEY가 설정되지 않았습니다"
→ `.env` 파일을 확인하고 API 키를 올바르게 입력했는지 확인

### ❌ "ModuleNotFoundError: No module named 'anthropic'"
→ `pip install -r requirements.txt` 실행

### ❌ 대본이 마음에 안 듦
→ `config.json`의 `custom_prompt_style`을 더 구체적으로 수정

## 다음 단계

- 📖 [상세 사용 가이드](USAGE_EXAMPLES.md) 읽기
- ⚙️ `prompts/` 폴더의 스타일 가이드 커스터마이징
- 🎯 여러 키워드로 시리즈 콘텐츠 제작

Happy creating! 🎉
