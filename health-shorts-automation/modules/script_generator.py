"""건강정보 쇼츠 대본 생성 모듈 (Claude API 사용)"""

import json
import re
from pathlib import Path
from typing import Optional

import anthropic

from config.settings import ANTHROPIC_API_KEY, SCRIPT_DIR
from modules.utils import logger

# 의료 안전 기준 시스템 프롬프트
_SYSTEM_PROMPT = """당신은 건강정보 유튜브 쇼츠 전문 대본 작가입니다.

[절대 준수 의료 안전 기준]
- 질병을 확정 진단하는 표현 금지 (예: "이 증상이 있으면 ○○병입니다" 금지)
- "무조건 낫는다", "완치된다", "100% 효과" 같은 단정 표현 금지
- 민간요법을 의학적 치료법처럼 단정하지 않기
- 특정 약품 복용 지시 금지
- 증상이 지속되거나 심하면 반드시 의료진 상담 권장
- 건강정보는 일반 정보 제공 목적임을 명시

[대상 시청자]
- 40대~70대 한국인
- 이해하기 쉬운 일상 언어 사용
- 전문 의학 용어는 쉬운 말로 풀어서 설명

[콘텐츠 스타일]
- 생활정보 중심
- 공감할 수 있는 증상이나 상황으로 시작
- 짧고 명확한 문장
- 친근하면서도 신뢰감 있는 톤"""

_SCENE_DURATIONS = {
    30: [4, 5, 5, 5, 5, 6],
    45: [5, 7, 7, 7, 7, 7, 5],
    60: [5, 8, 8, 8, 8, 8, 8, 7],
}

_TONE_DESCRIPTIONS = {
    "warning":     "시청자에게 주의를 환기시키는 긴박하고 경각심을 주는 톤",
    "informative": "차분하고 신뢰감 있게 정보를 전달하는 톤",
    "warm":        "따뜻하고 친근하게 설명하는 톤",
    "news":        "객관적이고 뉴스처럼 간결하게 전달하는 톤",
}


def _build_user_prompt(topic: str, duration: int, tone: str) -> str:
    durations = _SCENE_DURATIONS.get(duration, _SCENE_DURATIONS[45])
    scene_count = len(durations)
    tone_desc = _TONE_DESCRIPTIONS.get(tone, _TONE_DESCRIPTIONS["informative"])

    return f"""주제: {topic}
영상 길이: {duration}초
톤: {tone_desc}
장면 수: {scene_count}개
장면별 재생 시간(초): {durations}

위 주제로 유튜브 건강정보 쇼츠 대본을 생성하세요.

[대본 구조]
1. 강한 후킹 문장 (첫 {durations[0]}초)
2. 공감 문제 제기 ({durations[1]}초)
3. 핵심 정보 {scene_count - 3}가지 (각 {durations[2]}초 내외)
4. 주의사항 / 병원 권장 안내 ({durations[-2]}초)
5. CTA 마무리 ({durations[-1]}초)

[필수 출력 형식 - 반드시 아래 JSON만 출력]
{{
  "title": "영상 제목 (30자 이내)",
  "hook": "첫 후킹 문장",
  "script": "전체 내레이션 텍스트 (연속된 하나의 문자열)",
  "scenes": [
    {{
      "scene_no": 1,
      "duration": {durations[0]},
      "narration": "이 장면에서 읽을 내레이션",
      "caption": "화면 중앙 자막 (8~14자)",
      "image_prompt": "영어 이미지 생성 프롬프트 (realistic, Korean person, 9:16 vertical, no text)"
    }}
  ],
  "hashtags": ["#건강정보", "#건강관리"]
}}

장면 수는 정확히 {scene_count}개여야 합니다.
JSON 외 다른 텍스트는 절대 출력하지 마세요."""


def generate_script(
    topic: str,
    duration: int = 45,
    tone: str = "informative",
    job_id: Optional[str] = None,
) -> dict:
    """
    건강정보 쇼츠 대본 생성

    Args:
        topic: 건강 주제 (예: "무릎 통증", "혈압 관리")
        duration: 영상 길이 (30 / 45 / 60)
        tone: 톤 (warning / informative / warm / news)
        job_id: 작업 ID (결과 저장용)

    Returns:
        대본 딕셔너리 (JSON 형식)
    """
    if not ANTHROPIC_API_KEY:
        raise ValueError(
            "ANTHROPIC_API_KEY가 설정되지 않았습니다.\n"
            ".env 파일에 ANTHROPIC_API_KEY를 입력하세요.\n"
            "API 키 발급: https://console.anthropic.com/"
        )

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    logger.info(f"대본 생성 시작 | 주제: {topic} | 길이: {duration}초 | 톤: {tone}")

    try:
        message = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=4096,
            system=_SYSTEM_PROMPT,
            messages=[
                {"role": "user", "content": _build_user_prompt(topic, duration, tone)}
            ],
        )
    except anthropic.AuthenticationError:
        raise ValueError("API 키가 올바르지 않습니다. .env 파일의 ANTHROPIC_API_KEY를 확인하세요.")
    except anthropic.RateLimitError:
        raise RuntimeError("API 사용 한도를 초과했습니다. 잠시 후 다시 시도해주세요.")
    except Exception as e:
        raise RuntimeError(f"대본 생성 중 오류 발생: {e}")

    raw = message.content[0].text.strip()

    # JSON 파싱
    try:
        # 코드블록 제거
        cleaned = re.sub(r"```(?:json)?|```", "", raw).strip()
        script_data = json.loads(cleaned)
    except json.JSONDecodeError:
        logger.error(f"JSON 파싱 실패. 원본:\n{raw[:500]}")
        raise RuntimeError(
            "대본 생성 결과를 파싱하는 데 실패했습니다. 다시 시도해주세요."
        )

    # 필수 필드 검증
    required = ["title", "hook", "script", "scenes", "hashtags"]
    missing = [f for f in required if f not in script_data]
    if missing:
        raise RuntimeError(f"대본 데이터에 누락된 필드: {missing}")

    # 면책 문구 추가
    disclaimer = (
        "※ 이 영상은 일반 건강정보 제공을 목적으로 하며, "
        "전문 의료 진단을 대체하지 않습니다. "
        "증상이 지속되면 반드시 의료 전문가와 상담하세요."
    )
    script_data["disclaimer"] = disclaimer
    script_data["topic"] = topic
    script_data["duration"] = duration
    script_data["tone"] = tone

    # 결과 저장
    if job_id:
        out_path = SCRIPT_DIR / f"{job_id}_script.json"
        out_path.write_text(
            json.dumps(script_data, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
        logger.info(f"대본 저장 완료: {out_path}")

    logger.info(f"대본 생성 완료 | 제목: {script_data.get('title')}")
    return script_data
