"""공통 유틸리티 함수 모음"""

import uuid
import logging
import subprocess
import shutil
from datetime import datetime
from pathlib import Path


def generate_job_id() -> str:
    """영문/숫자로만 구성된 고유 job ID 생성"""
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    uid = uuid.uuid4().hex[:6].upper()
    return f"JOB_{ts}_{uid}"


def setup_logger(name: str, log_file: Path = None) -> logging.Logger:
    """표준 로거 설정"""
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    fmt = logging.Formatter(
        "[%(asctime)s] %(levelname)s %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(fmt)
    logger.addHandler(ch)

    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        fh = logging.FileHandler(log_file, encoding="utf-8")
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(fmt)
        logger.addHandler(fh)

    return logger


def check_ffmpeg() -> bool:
    """FFmpeg 설치 여부 확인"""
    return shutil.which("ffmpeg") is not None


def require_ffmpeg():
    """FFmpeg 없으면 사용자 친화적 오류 발생"""
    if not check_ffmpeg():
        raise EnvironmentError(
            "FFmpeg가 설치되어 있지 않습니다.\n"
            "설치 방법:\n"
            "  Windows: https://ffmpeg.org/download.html 에서 다운로드 후 PATH에 추가\n"
            "  또는: winget install ffmpeg\n"
            "  Mac: brew install ffmpeg\n"
            "  Ubuntu: sudo apt install ffmpeg"
        )


def get_audio_duration(audio_path: Path) -> float:
    """ffprobe로 오디오 파일 길이(초) 반환"""
    require_ffmpeg()
    result = subprocess.run(
        [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(audio_path)
        ],
        capture_output=True, text=True
    )
    try:
        return float(result.stdout.strip())
    except ValueError:
        return 0.0


def seconds_to_srt_time(seconds: float) -> str:
    """초를 SRT 타임코드 형식으로 변환 (HH:MM:SS,mmm)"""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds - int(seconds)) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def split_text_lines(text: str, max_chars: int = 14) -> list[str]:
    """텍스트를 최대 글자 수 기준으로 줄 나누기"""
    words = text.split()
    lines = []
    current = ""
    for word in words:
        if len(current) + len(word) + (1 if current else 0) <= max_chars:
            current = f"{current} {word}".strip() if current else word
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines or [""]


def safe_filename(text: str, max_len: int = 40) -> str:
    """한글 등 특수문자를 포함한 텍스트를 안전한 파일명으로 변환"""
    import re
    safe = re.sub(r'[^\w\s-]', '', text, flags=re.UNICODE)
    safe = re.sub(r'[\s]+', '_', safe.strip())
    return safe[:max_len] if safe else "output"


logger = setup_logger("health_shorts")
