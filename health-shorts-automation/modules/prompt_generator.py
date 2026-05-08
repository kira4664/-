"""장면별 이미지 프롬프트 보강 모듈"""

# 기본 이미지 스타일 접미사
_BASE_STYLE = (
    "realistic photo, Korean person, bright clean lighting, "
    "4K resolution, vertical 9:16 aspect ratio, "
    "medical information style, no text overlay, no watermark"
)

# 장면 번호별 권장 배경 힌트
_SCENE_BACKGROUNDS = {
    1: "close-up face showing concern, indoor background",
    2: "Korean person in daily life situation, home or outdoors",
    3: "Korean person demonstrating health action, clean environment",
    4: "medical or hospital related scene, professional setting",
    5: "Korean elderly person smiling, positive health outcome",
    6: "Korean family or community, warm atmosphere",
    7: "close-up motivational scene, bright positive lighting",
    8: "Korean person looking healthy and active, natural setting",
}

# 나이대별 인물 설명
_AGE_DESCRIPTIONS = {
    "40s": "Korean person in their 40s",
    "50s": "Korean person in their 50s",
    "60s": "Korean elderly person in their 60s",
    "70s": "Korean elderly person in their 70s",
}


def enhance_image_prompt(
    narration: str,
    base_prompt: str,
    scene_no: int,
    tone: str = "informative",
    age_group: str = "60s",
) -> str:
    """
    장면 내레이션과 기본 프롬프트를 기반으로 이미지 생성 프롬프트 보강

    Args:
        narration: 해당 장면 내레이션
        base_prompt: 스크립트 생성 시 만들어진 기본 이미지 프롬프트
        scene_no: 장면 번호
        tone: 영상 톤 (warning / informative / warm / news)
        age_group: 주요 인물 나이대

    Returns:
        강화된 이미지 프롬프트 문자열
    """
    tone_mood = {
        "warning": "dramatic lighting, concerned expression",
        "informative": "calm neutral expression, informative setting",
        "warm": "soft warm lighting, gentle smile",
        "news": "clean professional setting, neutral expression",
    }.get(tone, "clean lighting")

    age_desc = _AGE_DESCRIPTIONS.get(age_group, _AGE_DESCRIPTIONS["60s"])
    bg_hint = _SCENE_BACKGROUNDS.get(scene_no, _SCENE_BACKGROUNDS[2])

    # 기본 프롬프트가 비어 있으면 내레이션에서 키워드 추출
    if not base_prompt or len(base_prompt.strip()) < 10:
        keywords = _extract_keywords_from_narration(narration)
        base_prompt = f"{keywords}, {bg_hint}"

    enhanced = f"{base_prompt}, {age_desc}, {tone_mood}, {_BASE_STYLE}"
    return enhanced


def _extract_keywords_from_narration(narration: str) -> str:
    """
    내레이션에서 이미지 생성에 유용한 키워드 추출 (간단한 규칙 기반)
    """
    health_keywords = {
        "무릎": "person touching knee",
        "허리": "person holding lower back",
        "혈압": "blood pressure measurement",
        "당뇨": "healthy food diet",
        "심장": "person touching chest",
        "위": "person touching stomach",
        "수면": "person sleeping peacefully",
        "눈": "person with eye concern",
        "두통": "person holding head",
        "관절": "person joint pain",
        "피로": "tired looking person",
        "운동": "person exercising gently",
        "식단": "healthy Korean food",
        "병원": "doctor patient consultation",
        "약": "medication pills",
    }

    for kor, eng in health_keywords.items():
        if kor in narration:
            return eng

    return "Korean person health lifestyle daily routine"


def generate_thumbnail_prompt(title: str, topic: str, tone: str = "informative") -> str:
    """썸네일용 이미지 프롬프트 생성"""
    tone_style = {
        "warning": "dramatic red lighting, urgency",
        "informative": "clean blue professional background",
        "warm": "warm sunset tones, friendly",
        "news": "dark professional studio look",
    }.get(tone, "clean professional")

    return (
        f"YouTube health information thumbnail background for '{topic}', "
        f"{tone_style}, Korean health content style, "
        f"no text, gradient background, 4K quality, "
        f"suitable for health information channel"
    )
