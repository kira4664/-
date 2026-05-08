"""ElevenLabs TTS 모듈"""

import re
from pathlib import Path
from typing import Optional

from config.settings import (
    ELEVENLABS_API_KEY,
    ELEVENLABS_VOICE_ID,
    TTS_MODEL_ID,
    TTS_STABILITY,
    TTS_SIMILARITY,
    AUDIO_DIR,
)
from modules.utils import logger


def _split_sentences(text: str) -> list[str]:
    """텍스트를 문장 단위로 분리"""
    sentences = re.split(r'(?<=[.!?。])\s+', text.strip())
    return [s.strip() for s in sentences if s.strip()]


def generate_tts(
    text: str,
    job_id: str,
    voice_id: Optional[str] = None,
    output_path: Optional[Path] = None,
) -> Path:
    """
    ElevenLabs TTS로 텍스트를 음성 파일로 변환

    Args:
        text: 내레이션 텍스트
        job_id: 작업 ID
        voice_id: ElevenLabs Voice ID (없으면 설정에서 읽음)
        output_path: 저장 경로 (없으면 자동 생성)

    Returns:
        생성된 mp3 파일 경로
    """
    if not ELEVENLABS_API_KEY:
        raise ValueError(
            "ELEVENLABS_API_KEY가 설정되지 않았습니다.\n"
            ".env 파일에 ELEVENLABS_API_KEY를 입력하세요.\n"
            "API 키 발급: https://elevenlabs.io/"
        )

    used_voice_id = voice_id or ELEVENLABS_VOICE_ID
    if not used_voice_id:
        raise ValueError(
            "ELEVENLABS_VOICE_ID가 설정되지 않았습니다.\n"
            ".env 파일에 ELEVENLABS_VOICE_ID를 입력하세요.\n"
            "ElevenLabs 대시보드에서 사용할 Voice ID를 확인하세요."
        )

    if output_path is None:
        output_path = AUDIO_DIR / f"{job_id}.mp3"

    output_path.parent.mkdir(parents=True, exist_ok=True)

    logger.info(f"TTS 생성 시작 | Voice: {used_voice_id} | 글자 수: {len(text)}")

    try:
        from elevenlabs import ElevenLabs, VoiceSettings

        client = ElevenLabs(api_key=ELEVENLABS_API_KEY)

        audio_generator = client.text_to_speech.convert(
            voice_id=used_voice_id,
            text=text,
            model_id=TTS_MODEL_ID,
            voice_settings=VoiceSettings(
                stability=TTS_STABILITY,
                similarity_boost=TTS_SIMILARITY,
                style=0.3,
                use_speaker_boost=True,
            ),
        )

        with open(output_path, "wb") as f:
            for chunk in audio_generator:
                if chunk:
                    f.write(chunk)

    except ImportError:
        raise ImportError(
            "elevenlabs 패키지가 설치되지 않았습니다.\n"
            "pip install elevenlabs 를 실행하세요."
        )
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "unauthorized" in error_msg.lower():
            raise ValueError("ElevenLabs API 키가 올바르지 않습니다.")
        elif "voice_not_found" in error_msg.lower():
            raise ValueError(f"Voice ID '{used_voice_id}'를 찾을 수 없습니다.")
        else:
            raise RuntimeError(f"TTS 생성 실패: {error_msg}")

    logger.info(f"TTS 생성 완료: {output_path}")
    return output_path


def list_available_voices() -> list[dict]:
    """사용 가능한 ElevenLabs 목소리 목록 반환"""
    if not ELEVENLABS_API_KEY:
        return []

    try:
        from elevenlabs import ElevenLabs

        client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
        response = client.voices.get_all()
        return [
            {
                "voice_id": v.voice_id,
                "name": v.name,
                "labels": v.labels or {},
            }
            for v in response.voices
        ]
    except Exception as e:
        logger.warning(f"목소리 목록 조회 실패: {e}")
        return []
