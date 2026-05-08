"""자막 생성 모듈 - SRT / JSON 출력"""

import json
import re
from pathlib import Path
from typing import Optional

from config.settings import SUBTITLE_DIR
from modules.utils import logger, seconds_to_srt_time


def _split_into_segments(script: str, scenes: list[dict]) -> list[dict]:
    """
    장면 목록 기반으로 자막 세그먼트 생성
    각 장면의 narration을 duration에 맞게 분배
    """
    segments = []
    current_time = 0.0

    for scene in scenes:
        duration = float(scene.get("duration", 5))
        narration = scene.get("narration", "").strip()
        caption = scene.get("caption", "").strip()

        # narration을 문장 단위로 분리
        sentences = re.split(r'(?<=[.!?。\s])', narration)
        sentences = [s.strip() for s in sentences if s.strip()]

        if not sentences:
            sentences = [narration] if narration else [caption]

        # 각 문장에 균등하게 시간 배분
        time_per_sentence = duration / max(len(sentences), 1)

        for i, sent in enumerate(sentences):
            start = current_time + i * time_per_sentence
            end = start + time_per_sentence - 0.1  # 약간의 간격
            segments.append({
                "scene_no": scene.get("scene_no", 1),
                "start": round(start, 3),
                "end": round(end, 3),
                "text": sent,
                "caption": caption if i == 0 else "",  # 장면 첫 번째 문장에만 캡션
            })

        current_time += duration

    return segments


def _fit_to_audio(segments: list[dict], audio_duration: float) -> list[dict]:
    """오디오 실제 길이에 맞춰 자막 타이밍 스케일 조정"""
    if not segments:
        return segments

    script_duration = segments[-1]["end"]
    if script_duration <= 0:
        return segments

    scale = audio_duration / script_duration
    for seg in segments:
        seg["start"] = round(seg["start"] * scale, 3)
        seg["end"] = round(seg["end"] * scale, 3)

    return segments


def generate_srt(
    script_data: dict,
    job_id: str,
    audio_duration: Optional[float] = None,
) -> Path:
    """
    대본 데이터에서 SRT 자막 파일 생성

    Args:
        script_data: script_generator.generate_script() 반환값
        job_id: 작업 ID
        audio_duration: 실제 오디오 길이(초). 있으면 타이밍 스케일 조정

    Returns:
        생성된 SRT 파일 경로
    """
    scenes = script_data.get("scenes", [])
    if not scenes:
        raise ValueError("대본에 장면 데이터가 없습니다.")

    segments = _split_into_segments(script_data.get("script", ""), scenes)

    if audio_duration and audio_duration > 0:
        segments = _fit_to_audio(segments, audio_duration)

    srt_lines = []
    for idx, seg in enumerate(segments, 1):
        srt_lines.append(str(idx))
        srt_lines.append(
            f"{seconds_to_srt_time(seg['start'])} --> {seconds_to_srt_time(seg['end'])}"
        )
        srt_lines.append(seg["text"])
        srt_lines.append("")

    srt_path = SUBTITLE_DIR / f"{job_id}.srt"
    srt_path.write_text("\n".join(srt_lines), encoding="utf-8")
    logger.info(f"SRT 자막 저장: {srt_path} ({len(segments)}개 자막)")

    return srt_path


def generate_caption_json(
    script_data: dict,
    job_id: str,
    audio_duration: Optional[float] = None,
) -> Path:
    """
    화면 중앙 오버레이용 캡션 JSON 생성 (영상 렌더러에서 사용)

    Returns:
        생성된 JSON 파일 경로
    """
    scenes = script_data.get("scenes", [])
    captions = []
    current_time = 0.0

    for scene in scenes:
        duration = float(scene.get("duration", 5))
        caption = scene.get("caption", "").strip()
        if caption:
            captions.append({
                "start": round(current_time, 3),
                "end": round(current_time + duration, 3),
                "text": caption,
                "scene_no": scene.get("scene_no", 1),
            })
        current_time += duration

    # 오디오 길이에 맞춰 스케일 조정
    if audio_duration and audio_duration > 0 and captions:
        script_duration = captions[-1]["end"] if captions else sum(
            s.get("duration", 5) for s in scenes
        )
        if script_duration > 0:
            scale = audio_duration / script_duration
            for cap in captions:
                cap["start"] = round(cap["start"] * scale, 3)
                cap["end"] = round(cap["end"] * scale, 3)

    json_path = SUBTITLE_DIR / f"{job_id}_captions.json"
    json_path.write_text(
        json.dumps(captions, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    logger.info(f"캡션 JSON 저장: {json_path} ({len(captions)}개 캡션)")

    return json_path


def generate_subtitles(
    script_data: dict,
    job_id: str,
    audio_duration: Optional[float] = None,
) -> dict:
    """
    SRT + 캡션 JSON 한 번에 생성

    Returns:
        {"srt": Path, "captions_json": Path}
    """
    srt_path = generate_srt(script_data, job_id, audio_duration)
    captions_path = generate_caption_json(script_data, job_id, audio_duration)
    return {"srt": srt_path, "captions_json": captions_path}
