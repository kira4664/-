"""영상 렌더링 모듈 - FFmpeg + Pillow 기반"""

import json
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import Optional

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

from config.settings import (
    VIDEO_WIDTH, VIDEO_HEIGHT, VIDEO_FPS,
    VIDEO_BITRATE, AUDIO_BITRATE,
    BGM_VOLUME, FONTS_DIR, BGM_DIR, VIDEO_DIR,
    SUBTITLE_FONT_SIZE,
)
from modules.utils import logger, require_ffmpeg, split_text_lines


# ─── 배경 이미지 생성 ─────────────────────────────────────────

def _create_gradient_bg(
    width: int, height: int,
    color_top: tuple, color_bottom: tuple
) -> Image.Image:
    """수직 그라데이션 배경 생성"""
    img = Image.new("RGB", (width, height))
    for y in range(height):
        ratio = y / height
        r = int(color_top[0] * (1 - ratio) + color_bottom[0] * ratio)
        g = int(color_top[1] * (1 - ratio) + color_bottom[1] * ratio)
        b = int(color_top[2] * (1 - ratio) + color_bottom[2] * ratio)
        for x in range(width):
            img.putpixel((x, y), (r, g, b))
    return img


def _load_or_create_background(
    bg_path: Optional[Path],
    scene_index: int,
    tone: str = "informative",
) -> Image.Image:
    """배경 이미지 로드 또는 그라데이션 생성"""
    if bg_path and bg_path.exists():
        img = Image.open(bg_path).convert("RGB")
        img = img.resize((VIDEO_WIDTH, VIDEO_HEIGHT), Image.LANCZOS)
        return img

    # 톤별 기본 그라데이션 색상
    gradients = {
        "warning":     ((100, 10, 10), (20, 0, 0)),
        "informative": ((15, 40, 90), (5, 10, 40)),
        "warm":        ((20, 70, 40), (5, 25, 15)),
        "news":        ((25, 25, 35), (8, 8, 18)),
    }
    colors = gradients.get(tone, gradients["informative"])
    return _create_gradient_bg(VIDEO_WIDTH, VIDEO_HEIGHT, colors[0], colors[1])


# ─── Ken Burns 효과 ────────────────────────────────────────────

def _apply_ken_burns(
    img: Image.Image,
    frame_idx: int,
    total_frames: int,
    zoom_start: float = 1.0,
    zoom_end: float = 1.08,
) -> Image.Image:
    """Ken Burns 줌인 효과 적용"""
    progress = frame_idx / max(total_frames - 1, 1)
    zoom = zoom_start + (zoom_end - zoom_start) * progress

    new_w = int(VIDEO_WIDTH * zoom)
    new_h = int(VIDEO_HEIGHT * zoom)

    zoomed = img.resize((new_w, new_h), Image.LANCZOS)

    # 중앙 크롭
    left = (new_w - VIDEO_WIDTH) // 2
    top = (new_h - VIDEO_HEIGHT) // 2
    return zoomed.crop((left, top, left + VIDEO_WIDTH, top + VIDEO_HEIGHT))


# ─── 자막 오버레이 ─────────────────────────────────────────────

def _get_font(size: int) -> ImageFont.FreeTypeFont:
    """Pretendard Bold 폰트 로드. 없으면 기본 폰트"""
    font_candidates = [
        FONTS_DIR / "Pretendard-Bold.ttf",
        FONTS_DIR / "NanumGothicBold.ttf",
        FONTS_DIR / "malgun.ttf",
    ]
    for font_path in font_candidates:
        if font_path.exists():
            try:
                return ImageFont.truetype(str(font_path), size)
            except Exception:
                continue

    # 시스템 폰트 시도 (Linux)
    system_fonts = [
        "/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    ]
    for sf in system_fonts:
        if Path(sf).exists():
            try:
                return ImageFont.truetype(sf, size)
            except Exception:
                continue

    return ImageFont.load_default()


def _draw_caption_on_frame(
    frame: Image.Image,
    text: str,
    font_size: int = SUBTITLE_FONT_SIZE,
    y_ratio: float = 0.55,
) -> Image.Image:
    """프레임에 중앙 자막 오버레이"""
    if not text:
        return frame

    draw = ImageDraw.Draw(frame.copy())
    img = frame.copy()
    draw = ImageDraw.Draw(img)

    font = _get_font(font_size)
    lines = split_text_lines(text, max_chars=13)

    line_height = font_size + 12
    total_height = len(lines) * line_height + 24

    # 자막 중앙 Y 위치
    y_center = int(VIDEO_HEIGHT * y_ratio)
    y_start = y_center - total_height // 2

    # 반투명 검은 박스
    max_line_width = max(
        draw.textlength(line, font=font) for line in lines
    ) if lines else 0
    box_w = int(max_line_width) + 60
    box_h = total_height
    box_x = (VIDEO_WIDTH - box_w) // 2

    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    overlay_draw.rounded_rectangle(
        [box_x, y_start - 10, box_x + box_w, y_start + box_h + 10],
        radius=16,
        fill=(0, 0, 0, 160),
    )
    img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
    draw = ImageDraw.Draw(img)

    # 텍스트 렌더링
    for i, line in enumerate(lines):
        y = y_start + i * line_height
        lw = draw.textlength(line, font=font)
        x = (VIDEO_WIDTH - lw) // 2

        # 외곽선
        for dx in [-3, -2, 2, 3]:
            for dy in [-3, -2, 2, 3]:
                draw.text((x + dx, y + dy), line, font=font, fill=(0, 0, 0, 220))

        # 흰색 본문
        draw.text((x, y), line, font=font, fill=(255, 255, 255, 255))

    return img


# ─── 메인 렌더링 ───────────────────────────────────────────────

def render_video(
    script_data: dict,
    job_id: str,
    audio_path: Path,
    captions_json_path: Optional[Path] = None,
    background_images: Optional[list[Path]] = None,
    bgm_path: Optional[Path] = None,
    bgm_volume: float = BGM_VOLUME,
    progress_callback=None,
) -> Path:
    """
    최종 영상 렌더링

    Args:
        script_data: 대본 데이터
        job_id: 작업 ID
        audio_path: TTS 오디오 파일 경로
        captions_json_path: 캡션 JSON 파일 경로
        background_images: 장면별 배경 이미지 경로 목록
        bgm_path: 배경음악 파일 경로
        bgm_volume: BGM 볼륨 (0.0~1.0)
        progress_callback: 진행률 콜백 (0.0~1.0)

    Returns:
        최종 mp4 파일 경로
    """
    require_ffmpeg()

    scenes = script_data.get("scenes", [])
    tone = script_data.get("tone", "informative")

    if not scenes:
        raise ValueError("렌더링할 장면 데이터가 없습니다.")

    if not audio_path.exists():
        raise FileNotFoundError(f"오디오 파일이 없습니다: {audio_path}")

    # 캡션 로드
    captions = []
    if captions_json_path and captions_json_path.exists():
        captions = json.loads(captions_json_path.read_text(encoding="utf-8"))

    output_path = VIDEO_DIR / f"{job_id}_final.mp4"

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp = Path(tmp_dir)
        frame_files = []

        total_scenes = len(scenes)
        for scene_idx, scene in enumerate(scenes):
            duration = float(scene.get("duration", 5))
            n_frames = int(duration * VIDEO_FPS)
            scene_no = scene.get("scene_no", scene_idx + 1)

            # 배경 이미지 선택
            bg_img = None
            if background_images and scene_idx < len(background_images):
                bg_img = background_images[scene_idx]

            base_frame = _load_or_create_background(bg_img, scene_idx, tone)

            # 현재 장면에 해당하는 캡션 찾기
            scene_start_time = sum(
                float(s.get("duration", 5)) for s in scenes[:scene_idx]
            )
            active_captions = [
                c for c in captions
                if c.get("scene_no") == scene_no
            ]
            caption_text = active_captions[0]["text"] if active_captions else ""

            for frame_i in range(n_frames):
                frame = _apply_ken_burns(base_frame.copy(), frame_i, n_frames)

                # 현재 시간의 자막 결정
                current_time = scene_start_time + frame_i / VIDEO_FPS
                current_caption = ""
                for cap in captions:
                    if cap["start"] <= current_time < cap["end"]:
                        current_caption = cap["text"]
                        break

                if not current_caption:
                    current_caption = caption_text

                frame = _draw_caption_on_frame(frame, current_caption)

                frame_path = tmp / f"frame_{len(frame_files):06d}.png"
                frame.save(str(frame_path), "PNG")
                frame_files.append(frame_path)

            if progress_callback:
                progress_callback((scene_idx + 1) / total_scenes * 0.7)

        # 프레임 목록 파일 생성
        concat_file = tmp / "frames.txt"
        with open(concat_file, "w") as f:
            for fp in frame_files:
                f.write(f"file '{fp}'\n")
                f.write(f"duration {1/VIDEO_FPS}\n")

        # 무음 영상 생성
        silent_video = tmp / "silent.mp4"
        _run_ffmpeg([
            "ffmpeg", "-y",
            "-f", "concat", "-safe", "0",
            "-i", str(concat_file),
            "-vf", f"fps={VIDEO_FPS},scale={VIDEO_WIDTH}:{VIDEO_HEIGHT}",
            "-c:v", "libx264", "-preset", "medium",
            "-pix_fmt", "yuv420p",
            str(silent_video),
        ])

        if progress_callback:
            progress_callback(0.85)

        # 오디오 + BGM 믹싱 및 최종 합성
        if bgm_path and Path(bgm_path).exists():
            _merge_with_bgm(
                silent_video, audio_path, Path(bgm_path),
                bgm_volume, output_path
            )
        else:
            _merge_audio_only(silent_video, audio_path, output_path)

    if progress_callback:
        progress_callback(1.0)

    logger.info(f"영상 렌더링 완료: {output_path}")
    return output_path


def _run_ffmpeg(cmd: list):
    """FFmpeg 명령 실행. 실패 시 로그와 함께 예외 발생"""
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        logger.error(f"FFmpeg 오류:\n{result.stderr[-2000:]}")
        raise RuntimeError(
            f"FFmpeg 렌더링 실패 (코드 {result.returncode}).\n"
            "FFmpeg 설치 여부와 입력 파일을 확인하세요."
        )


def _merge_audio_only(video_path: Path, audio_path: Path, output_path: Path):
    """영상 + TTS 오디오 합성"""
    _run_ffmpeg([
        "ffmpeg", "-y",
        "-i", str(video_path),
        "-i", str(audio_path),
        "-c:v", "copy",
        "-c:a", "aac", "-b:a", AUDIO_BITRATE,
        "-shortest",
        str(output_path),
    ])


def _merge_with_bgm(
    video_path: Path,
    tts_path: Path,
    bgm_path: Path,
    bgm_volume: float,
    output_path: Path,
):
    """영상 + TTS + BGM 믹싱"""
    _run_ffmpeg([
        "ffmpeg", "-y",
        "-i", str(video_path),
        "-i", str(tts_path),
        "-stream_loop", "-1", "-i", str(bgm_path),
        "-filter_complex",
        f"[1:a]volume=1.0[tts];[2:a]volume={bgm_volume}[bgm];[tts][bgm]amix=inputs=2:duration=first[aout]",
        "-map", "0:v",
        "-map", "[aout]",
        "-c:v", "copy",
        "-c:a", "aac", "-b:a", AUDIO_BITRATE,
        "-shortest",
        str(output_path),
    ])
