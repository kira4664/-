import os
import zipfile
from pathlib import Path
from .analyze_text import analyze_content
from .render_image import render_card_to_png

BASE_DIR = Path(__file__).parent.parent
OUTPUT_DIR = BASE_DIR / "output"


def generate(text: str, card_count: int = 8, progress_cb=None) -> dict:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    if progress_cb:
        progress_cb(0.1, "Claude가 카드뉴스 문구를 분석 중...")

    data = analyze_content(text, card_count)
    cards = data["cards"]
    brand = data.get("brand", "카드뉴스")
    total = len(cards)

    png_paths = []
    for i, card in enumerate(cards):
        if progress_cb:
            pct = 0.2 + (i / total) * 0.7
            progress_cb(pct, f"카드 {i+1}/{total} 이미지 생성 중...")

        out_path = OUTPUT_DIR / f"card_{i+1:02d}.png"
        render_card_to_png(card, i + 1, total, brand, out_path)
        png_paths.append(out_path)

    if progress_cb:
        progress_cb(0.95, "ZIP 파일 압축 중...")

    zip_path = OUTPUT_DIR / "cards.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for p in png_paths:
            zf.write(p, p.name)

    caption_path = OUTPUT_DIR / "caption.txt"
    caption_path.write_text(
        f"{data.get('caption', '')}\n\n{data.get('hashtags', '')}",
        encoding="utf-8"
    )

    if progress_cb:
        progress_cb(1.0, "완료!")

    return {
        "cards": cards,
        "brand": brand,
        "caption": data.get("caption", ""),
        "hashtags": data.get("hashtags", ""),
        "png_paths": [str(p) for p in png_paths],
        "zip_path": str(zip_path),
        "caption_path": str(caption_path)
    }
