#!/usr/bin/env python3
"""
웹 자료 수집 기반 블로그 자동 포스팅 도구
키워드를 입력하면 웹을 검색해 자료를 취합하고, 블로그 글을 작성한 뒤
워드프레스에 자동으로 포스팅합니다.
"""

import os
import json
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import anthropic
import requests
from dotenv import load_dotenv

load_dotenv()

MODEL = "claude-opus-5"

BLOG_POST_SCHEMA = {
    "type": "object",
    "properties": {
        "title": {"type": "string", "description": "블로그 글 제목"},
        "content_html": {
            "type": "string",
            "description": "워드프레스에 그대로 게시할 수 있는 HTML 본문 (h2/h3, p, ul/li 등 사용)",
        },
        "excerpt": {"type": "string", "description": "1~2문장 요약(발췌문)"},
        "tags": {
            "type": "array",
            "items": {"type": "string"},
            "description": "블로그 태그 목록 (3~8개)",
        },
        "meta_description": {"type": "string", "description": "SEO용 메타 설명 (150자 내외)"},
    },
    "required": ["title", "content_html", "excerpt", "tags", "meta_description"],
    "additionalProperties": False,
}


class BlogPoster:
    """웹 리서치 -> 블로그 글 작성 -> 워드프레스 포스팅 파이프라인"""

    def __init__(self, config_path: str = "config.json"):
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

        self.blog_config = self.config.get("blog", {})

    def _load_config(self, config_path: str) -> Dict:
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)

    # ------------------------------------------------------------------
    # 1) 웹 자료 수집
    # ------------------------------------------------------------------
    def research_topic(self, keyword: str) -> str:
        """키워드에 대해 웹 검색을 수행하고 취합된 자료를 반환합니다."""
        num_searches = self.blog_config.get("num_search_queries", 5)

        tools = [{"type": "web_search_20260209", "name": "web_search", "max_uses": num_searches}]

        system = (
            "당신은 블로그 글 작성을 위한 리서치 담당자입니다. "
            "주어진 주제에 대해 웹을 검색하여 최신이고 정확한 정보를 폭넓게 수집하세요. "
            "여러 출처를 확인하고, 상반되는 정보가 있다면 함께 언급하세요."
        )
        user_prompt = (
            f"주제: '{keyword}'\n\n"
            "이 주제에 대해 블로그 글을 쓸 수 있도록 웹에서 자료를 조사해주세요. "
            "다음을 포함해 정리해주세요:\n"
            "1. 핵심 개념/배경 설명\n"
            "2. 최신 동향이나 뉴스\n"
            "3. 구체적인 수치, 통계, 사례\n"
            "4. 서로 다른 관점이나 의견\n"
            "5. 참고한 출처(가능하면 URL 포함)\n\n"
            "취합한 자료를 구조화된 텍스트로 요약해서 알려주세요."
        )

        messages = [{"role": "user", "content": user_prompt}]
        response = self.client.messages.create(
            model=MODEL,
            max_tokens=8000,
            system=system,
            tools=tools,
            messages=messages,
        )

        # 서버 사이드 도구 호출이 10회 제한에 걸리면 pause_turn으로 멈추므로 이어서 진행
        continuations = 0
        while response.stop_reason == "pause_turn" and continuations < 5:
            messages = [
                {"role": "user", "content": user_prompt},
                {"role": "assistant", "content": response.content},
            ]
            response = self.client.messages.create(
                model=MODEL,
                max_tokens=8000,
                system=system,
                tools=tools,
                messages=messages,
            )
            continuations += 1

        research_text = "\n".join(
            block.text for block in response.content if block.type == "text"
        )

        if not research_text.strip():
            raise RuntimeError(
                "웹 리서치 결과가 비어 있습니다. 키워드를 바꾸거나 다시 시도해주세요."
            )

        return research_text

    # ------------------------------------------------------------------
    # 2) 블로그 글 작성
    # ------------------------------------------------------------------
    def write_blog_post(self, keyword: str, research: str, lang: str) -> Dict:
        """취합된 자료를 바탕으로 블로그 글(JSON)을 생성합니다."""
        tone = self.blog_config.get("tone", "친근하고 신뢰감 있는")
        min_words = self.blog_config.get("min_word_count", 800)
        custom_style = self.blog_config.get("custom_style", "")

        lang_name = {"ko": "한국어", "en": "영어", "ja": "일본어"}.get(lang, lang)

        system = (
            "당신은 전문 블로그 작가입니다. 주어진 리서치 자료를 바탕으로 "
            "정확하고 읽기 좋은 블로그 글을 작성합니다. 리서치에 없는 사실을 "
            "지어내지 마세요."
        )
        user_prompt = f"""
【주제】
{keyword}

【리서치 자료】
{research}

【작성 요구사항】
- 언어: {lang_name}
- 톤: {tone}
- 최소 분량: {min_words}자 내외
- 도입부에서 흥미를 끌고, 소제목(h2/h3)으로 구조화
- 리서치 자료에 기반한 사실만 사용 (근거 없는 내용 금지)
- content_html은 워드프레스에 바로 게시 가능한 HTML로 작성 (p, h2, h3, ul/li, strong 등)
{f'【커스텀 스타일】{custom_style}' if custom_style else ''}
""".strip()

        response = self.client.messages.create(
            model=MODEL,
            max_tokens=8000,
            system=system,
            output_config={"format": {"type": "json_schema", "schema": BLOG_POST_SCHEMA}},
            messages=[{"role": "user", "content": user_prompt}],
        )

        text = next(block.text for block in response.content if block.type == "text")
        return json.loads(text)

    # ------------------------------------------------------------------
    # 3) 워드프레스 포스팅
    # ------------------------------------------------------------------
    def _wp_auth(self):
        wp_user = os.getenv("WP_USERNAME")
        wp_app_password = os.getenv("WP_APP_PASSWORD")
        if not wp_user or not wp_app_password:
            raise ValueError(
                "WP_USERNAME / WP_APP_PASSWORD가 설정되지 않았습니다. "
                ".env 파일에 워드프레스 인증 정보를 입력하세요."
            )
        return (wp_user, wp_app_password)

    def _wp_base_url(self) -> str:
        wp_url = os.getenv("WP_URL")
        if not wp_url:
            raise ValueError("WP_URL이 설정되지 않았습니다. .env 파일에 워드프레스 사이트 주소를 입력하세요.")
        return wp_url.rstrip("/")

    def _get_or_create_term(self, taxonomy: str, name: str) -> int:
        """워드프레스 태그/카테고리를 이름으로 찾고, 없으면 생성 후 ID를 반환합니다."""
        base_url = self._wp_base_url()
        auth = self._wp_auth()
        endpoint = f"{base_url}/wp-json/wp/v2/{taxonomy}"

        resp = requests.get(endpoint, params={"search": name}, auth=auth, timeout=15)
        resp.raise_for_status()
        for term in resp.json():
            if term["name"].strip().lower() == name.strip().lower():
                return term["id"]

        resp = requests.post(endpoint, json={"name": name}, auth=auth, timeout=15)
        resp.raise_for_status()
        return resp.json()["id"]

    def post_to_wordpress(
        self,
        post: Dict,
        status: str = "draft",
        category: Optional[str] = None,
    ) -> Dict:
        """생성된 블로그 글을 워드프레스에 포스팅합니다."""
        base_url = self._wp_base_url()
        auth = self._wp_auth()
        endpoint = f"{base_url}/wp-json/wp/v2/posts"

        payload = {
            "title": post["title"],
            "content": post["content_html"],
            "excerpt": post.get("excerpt", ""),
            "status": status,
        }

        tag_names = post.get("tags") or []
        if tag_names:
            payload["tags"] = [self._get_or_create_term("tags", t) for t in tag_names]

        category_name = category or self.blog_config.get("default_category")
        if category_name:
            payload["categories"] = [self._get_or_create_term("categories", category_name)]

        resp = requests.post(endpoint, json=payload, auth=auth, timeout=30)
        resp.raise_for_status()
        return resp.json()

    # ------------------------------------------------------------------
    # 전체 파이프라인
    # ------------------------------------------------------------------
    def run(
        self,
        keyword: str,
        status: Optional[str] = None,
        category: Optional[str] = None,
        lang: Optional[str] = None,
        dry_run: bool = False,
    ) -> Dict:
        status = status or self.blog_config.get("default_status", "draft")
        lang = lang or self.blog_config.get("language", "ko")

        print(f"\n🔍 '{keyword}' 관련 자료를 웹에서 수집하는 중...")
        research = self.research_topic(keyword)
        print("✅ 자료 수집 완료!")

        print("\n✍️  취합한 자료로 블로그 글을 작성하는 중...")
        post = self.write_blog_post(keyword, research, lang)
        print(f"✅ 블로그 글 작성 완료! (제목: {post['title']})")

        result = {
            "keyword": keyword,
            "research": research,
            "post": post,
            "status": status,
            "wordpress_response": None,
        }

        if dry_run:
            print("\n🧪 dry-run 모드: 워드프레스에는 게시하지 않습니다.")
        else:
            print(f"\n📤 워드프레스에 '{status}' 상태로 포스팅하는 중...")
            wp_response = self.post_to_wordpress(post, status=status, category=category)
            result["wordpress_response"] = {
                "id": wp_response.get("id"),
                "link": wp_response.get("link"),
                "status": wp_response.get("status"),
            }
            print(f"✅ 포스팅 완료! (ID: {wp_response.get('id')}, 링크: {wp_response.get('link')})")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.output_dir / f"blog_{keyword}_{timestamp}.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"\n💾 결과가 저장되었습니다: {output_file}")

        return result


def main():
    parser = argparse.ArgumentParser(
        description="웹 자료 수집 기반 블로그 자동 포스팅 도구",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
사용 예시:
  python blog_poster.py --keyword "2026년 AI 트렌드" --dry-run
  python blog_poster.py --keyword "홈트레이닝 루틴 추천" --status draft
  python blog_poster.py --keyword "제주도 여행 코스" --status publish --category "여행"
        """,
    )

    parser.add_argument("--keyword", "-k", required=True, help="블로그 글 주제 키워드")
    parser.add_argument(
        "--status",
        "-s",
        choices=["draft", "publish", "pending"],
        default=None,
        help="워드프레스 게시 상태 (기본값: config.json의 blog.default_status, 미설정 시 draft)",
    )
    parser.add_argument("--category", "-c", default=None, help="워드프레스 카테고리 이름")
    parser.add_argument("--lang", "-l", default=None, help="글 작성 언어 코드 (예: ko, en, ja)")
    parser.add_argument("--config", default="config.json", help="설정 파일 경로")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="워드프레스에 게시하지 않고 리서치 및 글 작성 결과만 저장",
    )

    args = parser.parse_args()

    try:
        poster = BlogPoster(config_path=args.config)
        poster.run(
            keyword=args.keyword,
            status=args.status,
            category=args.category,
            lang=args.lang,
            dry_run=args.dry_run,
        )
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
