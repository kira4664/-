import os
import json
from anthropic import Anthropic

client = Anthropic()

CARD_SCHEMA = {
    "type": "object",
    "properties": {
        "cards": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "type": {"type": "string", "enum": ["hook", "problem", "info", "condition", "method", "caution", "summary", "cta"]},
                    "emoji": {"type": "string"},
                    "tag": {"type": "string"},
                    "title": {"type": "string"},
                    "subtitle": {"type": "string"},
                    "bullets": {"type": "array", "items": {"type": "string"}},
                    "btn1": {"type": "string"},
                    "btn2": {"type": "string"}
                },
                "required": ["type", "title"]
            }
        },
        "brand": {"type": "string"},
        "caption": {"type": "string"},
        "hashtags": {"type": "string"}
    },
    "required": ["cards", "brand", "caption", "hashtags"]
}

SYSTEM_PROMPT = """당신은 인스타그램 카드뉴스 전문 편집자입니다.
사용자가 본문을 주면, 아래 규칙에 따라 JSON 형태로 카드뉴스 구성을 반환하세요.

카드 구성 규칙:
- 1장(hook): 강렬한 후킹 제목. 독자가 스크롤을 멈추게 만드는 문장. emoji 필드 필수.
- 2장(problem): 독자가 공감할 문제 제기나 배경 설명
- 3장(info): 핵심 정보 (금액, 기간, 조건 등 숫자가 있으면 반드시 포함)
- 4장(condition): 대상자 조건, 자격 요건
- 5장(method): 신청 방법, 절차, 주요 링크
- 6장(caution): 주의사항, 실수하기 쉬운 포인트
- 7장(summary): 전체 핵심을 3~5개 불릿으로 요약
- 8장(cta): 저장/공유/팔로우 유도. emoji, btn1, btn2 필드 필수.

작성 규칙:
- title은 20자 이내로 짧고 임팩트 있게
- subtitle(hook용)은 30자 이내
- bullets는 각 항목 30자 이내, 최대 5개
- tag는 카드 성격을 나타내는 3~5자 단어 (예: 지원금, 조건, 방법, 주의)
- brand는 콘텐츠 주제를 나타내는 2~4자 브랜드명 (예: 정책톡, 복지알림)
- caption은 인스타 업로드용 캡션 (150자 내외)
- hashtags는 공백으로 구분된 해시태그 10개 (#포함)
- 모든 텍스트는 한국어로 작성"""


def analyze_content(text: str, card_count: int = 8) -> dict:
    prompt = f"""다음 본문을 분석해서 인스타그램 카드뉴스 {card_count}장을 구성해주세요.

본문:
{text}

반드시 JSON 형식으로만 응답하세요."""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
        tools=[{
            "name": "create_card_news",
            "description": "카드뉴스 구성을 JSON으로 반환",
            "input_schema": CARD_SCHEMA
        }],
        tool_choice={"type": "tool", "name": "create_card_news"}
    )

    for block in response.content:
        if block.type == "tool_use" and block.name == "create_card_news":
            return block.input

    raise ValueError("카드뉴스 구성 생성 실패")
