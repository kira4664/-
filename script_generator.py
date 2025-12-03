#!/usr/bin/env python3
"""
음식 숏폼 대본 생성기
키워드를 입력하면 팩트체크를 거쳐 일본어/영어 대본을 생성합니다.
"""

import os
import json
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import anthropic
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()


class ScriptGenerator:
    """음식 숏폼 대본 생성기 클래스"""

    def __init__(self, config_path: str = "config.json"):
        """초기화"""
        self.config = self._load_config(config_path)
        self.api_key = os.getenv("ANTHROPIC_API_KEY")

        if not self.api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY가 설정되지 않았습니다. "
                ".env 파일을 생성하고 API 키를 입력하세요."
            )

        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.output_dir = Path(self.config.get("output_directory", "output"))
        self.output_dir.mkdir(exist_ok=True)

        # 스타일 가이드 로드
        self.japanese_style = self._load_style_guide("prompts/japanese_style.txt")
        self.english_style = self._load_style_guide("prompts/english_style.txt")

    def _load_config(self, config_path: str) -> Dict:
        """설정 파일 로드"""
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _load_style_guide(self, path: str) -> str:
        """스타일 가이드 파일 로드"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            return ""

    def research_keyword(self, keyword: str) -> str:
        """
        키워드에 대한 리서치 및 팩트체크

        실제 구현에서는 웹 검색 API를 사용하여 정보를 수집합니다.
        여기서는 Claude에게 팩트체크를 요청합니다.
        """
        prompt = f"""
음식 관련 키워드 '{keyword}'에 대해 숏폼 콘텐츠에 활용할 수 있는
흥미롭고 정확한 정보를 조사해주세요.

다음 정보를 포함해주세요:
1. 기본 정보 (역사, 유래, 특징)
2. 흥미로운 사실이나 일화
3. 구체적인 수치나 데이터
4. 의외의 사실이나 오해
5. 문화적 배경이나 현지인의 시각

정보는 팩트 기반으로 정확해야 하며, 출처가 불분명한 내용은 제외해주세요.
"""

        message = self.client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )

        return message.content[0].text

    def generate_script(
        self,
        keyword: str,
        research_data: str,
        language: str,
        duration: int
    ) -> str:
        """
        대본 생성

        Args:
            keyword: 음식 키워드
            research_data: 리서치된 정보
            language: 'ja' (일본어) 또는 'en' (영어)
            duration: 대본 길이 (초)

        Returns:
            생성된 대본
        """
        # 언어별 설정
        if language == "ja":
            lang_name = "일본어"
            style_guide = self.japanese_style
            native_instruction = "현지 일본인 유튜버가 말하는 것처럼 자연스럽게"
            style_config = self.config["style"]["japanese"]
        else:  # en
            lang_name = "영어"
            style_guide = self.english_style
            native_instruction = "Write like a native English-speaking content creator"
            style_config = self.config["style"]["english"]

        # 커스텀 프롬프트 스타일 적용
        custom_style = self.config.get("custom_prompt_style", "")

        prompt = f"""
당신은 음식 숏폼 콘텐츠 전문 작가입니다.
다음 정보를 바탕으로 {lang_name} 대본을 작성해주세요.

【키워드】
{keyword}

【리서치 정보】
{research_data}

【대본 요구사항】
- 길이: 약 {duration}초 분량
- 언어: {lang_name}
- 톤: {style_config['tone']}
- {native_instruction}

【스타일 가이드】
{style_guide}

{f'【커스텀 스타일】{custom_style}' if custom_style else ''}

【대본 구성】
1. Hook (첫 3초): 강렬한 시작으로 시청자 잡기
2. Main Content: 팩트 기반 정보를 재미있게 전달
3. Closing: 간단한 CTA

중요:
- 현지인이 실제로 사용하는 자연스러운 표현 사용
- 감탄사와 리액션 포함
- 캐주얼하고 친근한 톤
- 팩트는 정확하게, 표현은 재미있게

대본만 작성해주세요. 설명이나 주석은 제외하고 순수 대본만 출력하세요.
"""

        message = self.client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=3000,
            messages=[{"role": "user", "content": prompt}]
        )

        return message.content[0].text

    def generate(
        self,
        keyword: str,
        language: str = "both",
        duration: int = None
    ) -> Dict[str, str]:
        """
        전체 생성 프로세스 실행

        Args:
            keyword: 음식 관련 키워드
            language: 'ja', 'en', 또는 'both'
            duration: 대본 길이 (초)

        Returns:
            생성된 대본들을 담은 딕셔너리
        """
        if duration is None:
            duration = self.config.get("default_duration", 60)

        print(f"\n🔍 '{keyword}'에 대한 리서치를 시작합니다...")
        research_data = self.research_keyword(keyword)
        print("✅ 리서치 완료!")

        results = {
            "keyword": keyword,
            "duration": duration,
            "research_data": research_data,
            "scripts": {}
        }

        # 언어별 대본 생성
        languages = []
        if language == "both":
            languages = ["ja", "en"]
        else:
            languages = [language]

        for lang in languages:
            lang_name = "일본어" if lang == "ja" else "영어"
            print(f"\n✍️  {lang_name} 대본을 생성 중...")

            script = self.generate_script(keyword, research_data, lang, duration)
            results["scripts"][lang] = script

            print(f"✅ {lang_name} 대본 생성 완료!")
            print(f"\n{'='*50}")
            print(f"【{lang_name} 대본】")
            print(f"{'='*50}")
            print(script)
            print(f"{'='*50}\n")

        # 결과 저장
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.output_dir / f"{keyword}_{timestamp}.json"

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

        print(f"\n💾 결과가 저장되었습니다: {output_file}")

        return results


def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(
        description="음식 숏폼 대본 생성기",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
사용 예시:
  python script_generator.py --keyword "라면의 역사"
  python script_generator.py --keyword "스시" --lang ja --duration 30
  python script_generator.py --keyword "kimchi" --lang en --duration 60
        """
    )

    parser.add_argument(
        "--keyword",
        "-k",
        required=True,
        help="음식 관련 키워드"
    )

    parser.add_argument(
        "--lang",
        "-l",
        choices=["ja", "en", "both"],
        default="both",
        help="생성할 언어 (ja: 일본어, en: 영어, both: 둘 다)"
    )

    parser.add_argument(
        "--duration",
        "-d",
        type=int,
        help="대본 길이 (초)"
    )

    parser.add_argument(
        "--config",
        "-c",
        default="config.json",
        help="설정 파일 경로"
    )

    args = parser.parse_args()

    try:
        generator = ScriptGenerator(config_path=args.config)
        generator.generate(
            keyword=args.keyword,
            language=args.lang,
            duration=args.duration
        )
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
