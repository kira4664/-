#!/usr/bin/env python3
"""CLI: python generate.py [--input path] [--count N]"""
import argparse
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")  # 루트 .env
load_dotenv(Path(__file__).parent / ".env")         # card_news/.env (우선)

from src.generate_cards import generate

def progress(pct: float, msg: str):
    bar = "#" * int(pct * 30)
    print(f"\r[{bar:<30}] {int(pct*100):3d}% {msg}", end="", flush=True)

def main():
    parser = argparse.ArgumentParser(description="인스타 카드뉴스 자동생성기")
    parser.add_argument("--input", "-i", default="input/content.txt", help="입력 텍스트 파일 경로")
    parser.add_argument("--count", "-n", type=int, default=8, help="카드 수 (기본 8)")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"오류: 입력 파일 없음 → {input_path}")
        sys.exit(1)

    text = input_path.read_text(encoding="utf-8").strip()
    if not text:
        print("오류: 입력 파일이 비어 있습니다.")
        sys.exit(1)

    print(f"입력 파일: {input_path}")
    print(f"카드 수: {args.count}장")
    print()

    result = generate(text, card_count=args.count, progress_cb=progress)
    print()
    print()
    print("=" * 50)
    print(f"✓ 카드 {len(result['png_paths'])}장 생성 완료")
    print(f"✓ 출력 폴더: output/")
    print(f"✓ ZIP: {result['zip_path']}")
    print(f"✓ 캡션: {result['caption_path']}")
    print()
    print("[인스타 캡션]")
    print(result["caption"])
    print()
    print(result["hashtags"])

if __name__ == "__main__":
    main()
