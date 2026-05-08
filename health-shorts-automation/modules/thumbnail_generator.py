"""썸네일 생성 모듈 - Pillow 기반"""

from pathlib import Path
from typing import Optional

from PIL import Image, ImageDraw, ImageFont, ImageFilter

from config.settings import (
    VIDEO_WIDTH, VIDEO_HEIGHT,
    FONTS_DIR, THUMBNAIL_DIR,
)
from modules.utils import logger, split_text_lines


_THUMBNAIL_PRESETS = {
    "vertical": (1080, 1920),
    "horizontal": (1280, 720),
}

_TONE_GRADIENTS = {
    "warning":     {"top": (140, 15, 15),   "bottom": (30, 0, 0),   "accent": (255, 90, 90)},
    "informative": {"top": (15, 50, 120),   "bottom": (5, 15, 60),  "accent": (100, 180, 255)},
    "warm":        {"top": (25, 90, 50),    "bottom": (8, 30, 20),  "accent": (100, 230, 140)},
    "news":        {"top": (35, 35, 50),    "bottom": (10, 10, 25), "accent": (210, 210, 230)},
}


def _make_gradient_bg(width: int, height: int, top_color: tuple, bottom_color: tuple) -> Image.Image:
    img = Image.new("RGB", (width, height))
    for y in range(height):
        ratio = y / height
        r = int(top_color[0] * (1 - ratio) + bottom_color[0] * ratio)
        g = int(top_color[1] * (1 - ratio) + bottom_color[1] * ratio)
        b = int(top_color[2] * (1 - ratio) + bottom_color[2] * ratio)
        for x in range(width):
            img.putpixel((x, y), (r, g, b))
    return img


def _get_font(size: int) -> ImageFont.FreeTypeFont:
    candidates = [
        FONTS_DIR / "Pretendard-Bold.ttf",
        FONTS_DIR / "NanumGothicBold.ttf",
        "/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    ]
    for p in candidates:
        if Path(p).exists():
            try:
                return ImageFont.truetype(str(p), size)
            except Exception:
                continue
    return ImageFont.load_default()


def _draw_title_centered(
    img: Image.Image,
    title: str,
    accent_color: tuple,
    is_vertical: bool = True,
) -> Image.Image:
    """제목 텍스트를 중앙에 렌더링"""
    width, height = img.size
    draw = ImageDraw.Draw(img)

    font_size = 110 if is_vertical else 80
    font = _get_font(font_size)
    sub_font = _get_font(int(font_size * 0.45))

    max_chars = 10 if is_vertical else 16
    lines = split_text_lines(title, max_chars=max_chars)

    line_height = font_size + 20
    total_text_height = len(lines) * line_height

    # 반투명 박스
    max_line_w = 0
    for line in lines:
        lw = draw.textlength(line, font=font)
        max_line_w = max(max_line_w, lw)

    box_w = int(max_line_w) + 80
    box_h = total_text_height + 60
    box_x = (width - box_w) // 2
    box_y = height // 2 - box_h // 2 - 40

    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ov_draw = ImageDraw.Draw(overlay)
    ov_draw.rounded_rectangle(
        [box_x, box_y, box_x + box_w, box_y + box_h],
        radius=24,
        fill=(0, 0, 0, 190),
    )
    img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
    draw = ImageDraw.Draw(img)

    # 텍스트 렌더링
    y = box_y + 30
    for i, line in enumerate(lines):
        lw = draw.textlength(line, font=font)
        x = (width - lw) // 2
        # 외곽선
        for dx, dy in [(-3, -3), (3, -3), (-3, 3), (3, 3)]:
            draw.text((x + dx, y + dy), line, font=font, fill=(0, 0, 0, 200))
        # 첫 줄은 액센트 색, 나머지는 흰색
        color = accent_color if i == 0 else (255, 255, 255)
        draw.text((x, y), line, font=font, fill=color)
        y += line_height

    # 하단 면책 문구
    disclaimer = "※ 일반 건강정보 제공 목적 · 전문 진단 대체 불가"
    dw = draw.textlength(disclaimer, font=sub_font)
    dx = (width - dw) // 2
    dy = height - 120 if is_vertical else height - 60
    draw.text((dx + 2, dy + 2), disclaimer, font=sub_font, fill=(0, 0, 0, 160))
    draw.text((dx, dy), disclaimer, font=sub_font, fill=(180, 180, 180))

    return img


def generate_thumbnail(
    title: str,
    job_id: str,
    tone: str = "informative",
    background_image: Optional[Path] = None,
    sizes: Optional[list[str]] = None,
) -> dict[str, Path]:
    """
    썸네일 생성

    Args:
        title: 영상 제목
        job_id: 작업 ID
        tone: 영상 톤
        background_image: 배경 이미지 경로 (없으면 그라데이션 사용)
        sizes: 생성할 크기 목록 ["vertical", "horizontal"]

    Returns:
        {"vertical": Path, "horizontal": Path} 형태
    """
    if sizes is None:
        sizes = ["vertical"]

    colors = _TONE_GRADIENTS.get(tone, _TONE_GRADIENTS["informative"])
    result = {}

    for size_key in sizes:
        width, height = _THUMBNAIL_PRESETS.get(size_key, _THUMBNAIL_PRESETS["vertical"])
        is_vertical = size_key == "vertical"

        # 배경 생성
        if background_image and Path(background_image).exists():
            bg = Image.open(background_image).convert("RGB")
            bg = bg.resize((width, height), Image.LANCZOS)
            # 어두운 오버레이
            overlay = Image.new("RGBA", bg.size, (0, 0, 0, 120))
            bg = Image.alpha_composite(bg.convert("RGBA"), overlay).convert("RGB")
        else:
            bg = _make_gradient_bg(width, height, colors["top"], colors["bottom"])

        # 제목 삽입
        thumb = _draw_title_centered(bg, title, colors["accent"], is_vertical)

        # 저장
        ext = "jpg"
        out_path = THUMBNAIL_DIR / f"{job_id}_thumb_{size_key}.{ext}"
        thumb.save(str(out_path), "JPEG", quality=92)
        result[size_key] = out_path
        logger.info(f"썸네일 저장: {out_path}")

    return result
