"""전역 설정 및 경로 관리"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ── 프로젝트 루트 ──────────────────────────────────────────────
BASE_DIR = Path(__file__).parent.parent

# ── 출력 디렉토리 ──────────────────────────────────────────────
OUTPUT_DIR       = BASE_DIR / "output"
AUDIO_DIR        = OUTPUT_DIR / "audio"
SUBTITLE_DIR     = OUTPUT_DIR / "subtitles"
VIDEO_DIR        = OUTPUT_DIR / "videos"
THUMBNAIL_DIR    = OUTPUT_DIR / "thumbnails"
SCRIPT_DIR       = OUTPUT_DIR / "scripts"

# ── 에셋 디렉토리 ──────────────────────────────────────────────
ASSETS_DIR       = BASE_DIR / "assets"
FONTS_DIR        = ASSETS_DIR / "fonts"
BGM_DIR          = ASSETS_DIR / "bgm"
BACKGROUNDS_DIR  = ASSETS_DIR / "backgrounds"
IMAGES_DIR       = ASSETS_DIR / "images"

# ── 데이터 디렉토리 ────────────────────────────────────────────
DATA_DIR         = BASE_DIR / "data"
DB_PATH          = DATA_DIR / "jobs.sqlite"

# ── 디렉토리 생성 ──────────────────────────────────────────────
for _d in [AUDIO_DIR, SUBTITLE_DIR, VIDEO_DIR, THUMBNAIL_DIR,
           SCRIPT_DIR, FONTS_DIR, BGM_DIR, BACKGROUNDS_DIR,
           IMAGES_DIR, DATA_DIR]:
    _d.mkdir(parents=True, exist_ok=True)

# ── API Keys ───────────────────────────────────────────────────
ANTHROPIC_API_KEY     = os.getenv("ANTHROPIC_API_KEY", "")
ELEVENLABS_API_KEY    = os.getenv("ELEVENLABS_API_KEY", "")
ELEVENLABS_VOICE_ID   = os.getenv("ELEVENLABS_VOICE_ID", "")
OPENAI_API_KEY        = os.getenv("OPENAI_API_KEY", "")

# ── 영상 스펙 ──────────────────────────────────────────────────
VIDEO_WIDTH       = 1080
VIDEO_HEIGHT      = 1920
VIDEO_FPS         = 30
VIDEO_BITRATE     = "4000k"
AUDIO_BITRATE     = "192k"

# ── 기본값 ────────────────────────────────────────────────────
DEFAULT_DURATION  = int(os.getenv("DEFAULT_DURATION", "45"))
BGM_VOLUME        = float(os.getenv("BGM_VOLUME", "0.10"))
RENDER_QUALITY    = os.getenv("RENDER_QUALITY", "medium")

# ── 자막 스타일 ────────────────────────────────────────────────
SUBTITLE_FONT_SIZE    = 72
SUBTITLE_COLOR        = "white"
SUBTITLE_STROKE_COLOR = "black"
SUBTITLE_STROKE_WIDTH = 4
SUBTITLE_Y_POSITION   = 0.55   # 화면 높이 비율 (0=상단, 1=하단)

# ── ElevenLabs 설정 ────────────────────────────────────────────
TTS_MODEL_ID   = "eleven_multilingual_v2"
TTS_STABILITY  = 0.5
TTS_SIMILARITY = 0.75

# ── YouTube ────────────────────────────────────────────────────
YOUTUBE_CLIENT_SECRET_FILE = os.getenv("YOUTUBE_CLIENT_SECRET_FILE", "client_secret.json")
YOUTUBE_TOKEN_FILE         = os.getenv("YOUTUBE_TOKEN_FILE", "token.json")
YOUTUBE_SCOPES             = ["https://www.googleapis.com/auth/youtube.upload"]
