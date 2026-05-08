"""전체 영상 생성 파이프라인"""

from pathlib import Path
from typing import Optional, Callable

from modules.utils import logger, generate_job_id, get_audio_duration
from modules.script_generator import generate_script
from modules.tts_elevenlabs import generate_tts
from modules.subtitle_generator import generate_subtitles
from modules.video_renderer import render_video
from modules.thumbnail_generator import generate_thumbnail
from modules.job_manager import create_job, update_job


def run_pipeline(
    topic: str,
    duration: int = 45,
    tone: str = "informative",
    voice_id: Optional[str] = None,
    bgm_path: Optional[Path] = None,
    background_images: Optional[list[Path]] = None,
    generate_thumb_sizes: Optional[list[str]] = None,
    progress_callback: Optional[Callable[[str, float], None]] = None,
) -> dict:
    """
    전체 쇼츠 제작 파이프라인 실행

    Args:
        topic: 건강 주제
        duration: 영상 길이 (30 / 45 / 60)
        tone: 톤 (warning / informative / warm / news)
        voice_id: ElevenLabs Voice ID
        bgm_path: BGM 파일 경로
        background_images: 장면별 배경 이미지 목록
        generate_thumb_sizes: 썸네일 크기 목록 ["vertical", "horizontal"]
        progress_callback: (step_name, ratio) 형태의 진행률 콜백

    Returns:
        결과 딕셔너리 {job_id, script, audio_path, video_path, thumbnails, ...}
    """
    def _progress(step: str, ratio: float):
        logger.info(f"[{step}] {int(ratio*100)}%")
        if progress_callback:
            progress_callback(step, ratio)

    job_id = generate_job_id()
    logger.info(f"파이프라인 시작 | job_id: {job_id} | topic: {topic}")

    create_job(job_id, topic, duration, tone)
    update_job(job_id, status="running")

    result = {"job_id": job_id}

    try:
        # ── Step 1: 대본 생성 ─────────────────────────────────
        _progress("대본 생성", 0.0)
        script_data = generate_script(topic, duration, tone, job_id)
        result["script"] = script_data
        update_job(job_id, title=script_data.get("title"), status="script_done")
        _progress("대본 생성", 1.0)

        # ── Step 2: TTS 생성 ──────────────────────────────────
        _progress("TTS 음성 생성", 0.0)
        audio_path = generate_tts(
            text=script_data["script"],
            job_id=job_id,
            voice_id=voice_id,
        )
        result["audio_path"] = audio_path
        update_job(job_id, audio_path=str(audio_path), status="tts_done")
        _progress("TTS 음성 생성", 1.0)

        # ── Step 3: 자막 생성 ─────────────────────────────────
        _progress("자막 생성", 0.0)
        audio_dur = get_audio_duration(audio_path)
        subtitle_paths = generate_subtitles(script_data, job_id, audio_dur)
        result["subtitle_paths"] = subtitle_paths
        update_job(job_id, status="subtitle_done")
        _progress("자막 생성", 1.0)

        # ── Step 4: 영상 렌더링 ───────────────────────────────
        _progress("영상 렌더링", 0.0)

        def _render_progress(ratio: float):
            _progress("영상 렌더링", ratio)

        video_path = render_video(
            script_data=script_data,
            job_id=job_id,
            audio_path=audio_path,
            captions_json_path=subtitle_paths.get("captions_json"),
            background_images=background_images,
            bgm_path=bgm_path,
            progress_callback=_render_progress,
        )
        result["video_path"] = video_path
        update_job(job_id, video_path=str(video_path), status="video_done")
        _progress("영상 렌더링", 1.0)

        # ── Step 5: 썸네일 생성 ───────────────────────────────
        _progress("썸네일 생성", 0.0)
        sizes = generate_thumb_sizes or ["vertical"]
        bg_img = background_images[0] if background_images else None
        thumbnails = generate_thumbnail(
            title=script_data.get("title", topic),
            job_id=job_id,
            tone=tone,
            background_image=bg_img,
            sizes=sizes,
        )
        result["thumbnails"] = thumbnails
        if "vertical" in thumbnails:
            update_job(job_id, thumb_path=str(thumbnails["vertical"]))
        update_job(job_id, status="completed")
        _progress("썸네일 생성", 1.0)

        logger.info(f"파이프라인 완료 | job_id: {job_id}")

    except Exception as e:
        err = str(e)
        logger.error(f"파이프라인 오류 | job_id: {job_id} | {err}")
        update_job(job_id, status="failed", error_msg=err)
        result["error"] = err
        raise

    return result
