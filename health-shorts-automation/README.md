# 건강정보 쇼츠 자동화 프로그램

건강 주제를 입력하면 유튜브 쇼츠용 9:16 세로형 영상을 자동으로 생성하는 프로그램입니다.

---

## 기능 요약

| 기능 | 설명 |
|------|------|
| 대본 생성 | Claude AI로 건강정보 쇼츠 대본 자동 생성 |
| TTS | ElevenLabs로 자연스러운 한국어 음성 생성 |
| 자막 | SRT 자막 + 화면 중앙 오버레이 자막 자동 생성 |
| 영상 렌더링 | Ken Burns 효과, 자막 오버레이, BGM 포함 MP4 생성 |
| 썸네일 | 세로형(1080×1920) + 가로형(1280×720) 썸네일 생성 |
| 작업 기록 | SQLite 기반 작업 이력 저장 |
| YouTube 업로드 | YouTube Data API v3 선택적 업로드 |

---

## 설치 방법

### 1. Python 설치

Python 3.11 이상이 필요합니다.
[python.org](https://www.python.org/downloads/)에서 다운로드하세요.

### 2. FFmpeg 설치

**Windows:**
```bash
winget install ffmpeg
# 또는 https://ffmpeg.org/download.html 에서 다운로드 후 PATH 추가
```

**Mac:**
```bash
brew install ffmpeg
```

**Ubuntu/Debian:**
```bash
sudo apt install ffmpeg
```

설치 확인:
```bash
ffmpeg -version
```

### 3. 프로젝트 설치

```bash
# 저장소 클론
git clone <repository-url>
cd health-shorts-automation

# 가상환경 생성 (Windows)
python -m venv .venv
.venv\Scripts\activate

# 가상환경 생성 (Mac/Linux)
python -m venv .venv
source .venv/bin/activate

# 패키지 설치
pip install -r requirements.txt
```

### 4. 환경변수 설정

`.env.example`을 복사해서 `.env` 파일을 만듭니다.

```bash
copy .env.example .env   # Windows
cp .env.example .env     # Mac/Linux
```

`.env` 파일을 열고 API 키를 입력합니다:

```env
ANTHROPIC_API_KEY=sk-ant-api03-...
ELEVENLABS_API_KEY=sk_...
ELEVENLABS_VOICE_ID=21m00Tcm4TlvDq8ikWAM
```

### 5. 폰트 설치 (권장)

`assets/fonts/` 폴더에 **Pretendard-Bold.ttf** 파일을 넣으세요.

[Pretendard 다운로드](https://github.com/orioncactus/pretendard/releases) → `Pretendard-1.x.x.zip` → `public/static/Pretendard-Bold.ttf`

폰트가 없어도 시스템 기본 폰트로 자동 대체됩니다.

### 6. 실행

```bash
streamlit run app.py
```

브라우저에서 `http://localhost:8501`이 자동으로 열립니다.

---

## API 키 발급 방법

### Anthropic (Claude) API 키
1. [console.anthropic.com](https://console.anthropic.com/) 접속
2. Settings → API Keys → Create Key
3. `.env`의 `ANTHROPIC_API_KEY`에 입력

### ElevenLabs API 키 + Voice ID
1. [elevenlabs.io](https://elevenlabs.io/) 회원가입
2. Profile Settings → API Key 복사 → `.env`의 `ELEVENLABS_API_KEY`에 입력
3. Voices 탭 → 원하는 목소리 선택 → Voice ID 복사 → `.env`의 `ELEVENLABS_VOICE_ID`에 입력

**한국어 지원 목소리 추천:**
- `eleven_multilingual_v2` 모델 사용 (자동 적용됨)
- ElevenLabs Voice Lab에서 한국어 지원 목소리 검색

---

## 폴더 구조

```
health-shorts-automation/
├── app.py                    # Streamlit 웹 UI
├── requirements.txt
├── .env.example
├── config/
│   ├── settings.py           # 전역 설정
│   └── templates.json        # 스타일 템플릿
├── modules/
│   ├── pipeline.py           # 전체 파이프라인
│   ├── script_generator.py   # 대본 생성 (Claude API)
│   ├── prompt_generator.py   # 이미지 프롬프트 생성
│   ├── tts_elevenlabs.py     # TTS 음성 생성
│   ├── subtitle_generator.py # 자막 생성
│   ├── video_renderer.py     # 영상 렌더링
│   ├── thumbnail_generator.py# 썸네일 생성
│   ├── youtube_uploader.py   # YouTube 업로드
│   ├── job_manager.py        # 작업 기록 관리
│   └── utils.py              # 공통 유틸리티
├── assets/
│   ├── fonts/                # Pretendard-Bold.ttf 여기에
│   ├── bgm/                  # 배경음악 mp3/wav 파일
│   └── backgrounds/          # 기본 배경 이미지
└── output/                   # 생성된 파일 저장
    ├── audio/
    ├── subtitles/
    ├── videos/
    ├── thumbnails/
    └── scripts/
```

---

## 사용 방법

1. 브라우저에서 `http://localhost:8501` 접속
2. 왼쪽 사이드바에서 영상 길이, 톤, 목소리 설정
3. 메인 화면에서 건강 주제 입력 (예: "무릎 통증 완화법")
4. "영상 자동 생성 시작" 버튼 클릭
5. 진행 상황 확인 후 완료되면 MP4 다운로드

---

## BGM 추가 방법

`assets/bgm/` 폴더에 MP3 또는 WAV 파일을 넣으면 사이드바에서 선택할 수 있습니다.

저작권 없는 BGM 추천:
- [pixabay.com/music](https://pixabay.com/music/) - 무료 음악
- [bensound.com](https://bensound.com) - 무료 음악

---

## YouTube 업로드 설정 (선택)

1. [Google Cloud Console](https://console.cloud.google.com/)에서 프로젝트 생성
2. YouTube Data API v3 활성화
3. OAuth 2.0 클라이언트 ID 생성 (데스크톱 앱)
4. `client_secret.json` 다운로드 후 프로젝트 루트에 저장
5. `.env`의 `YOUTUBE_CLIENT_SECRET_FILE=client_secret.json` 설정

---

## 오류 해결

| 오류 메시지 | 해결 방법 |
|------------|----------|
| `ANTHROPIC_API_KEY가 설정되지 않았습니다` | `.env` 파일에 API 키 입력 |
| `FFmpeg가 설치되어 있지 않습니다` | FFmpeg 설치 후 PATH 재설정 |
| `ELEVENLABS_VOICE_ID가 설정되지 않았습니다` | ElevenLabs 대시보드에서 Voice ID 확인 |
| `렌더링 실패` | `output/` 폴더 쓰기 권한 확인 |
| `JSON 파싱 실패` | Claude API 응답 이상 → 재시도 |
| 자막이 안 나옴 | `assets/fonts/`에 TTF 폰트 파일 추가 |

---

## 의료 정보 면책 조항

이 프로그램으로 생성되는 모든 콘텐츠는 **일반 건강정보 제공 목적**이며, 전문 의료 진단을 대체하지 않습니다.
증상이 지속되거나 심한 경우 반드시 의료 전문가와 상담하시기 바랍니다.

---

## 라이선스

MIT License
