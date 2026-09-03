#!/usr/bin/env python3
"""
워드프레스 글의 검색엔진(구글/빙/네이버/다음) 노출 여부 확인 도구
워드프레스에서 최근 글 목록을 가져와, 각 글 제목으로 검색엔진 공식 검색 API를
호출해 내 글 URL이 검색 결과에 노출되는지(및 몇 위인지) 확인합니다.
"""

import os
import re
import sys
import html
import json
import argparse
from datetime import datetime
from pathlib import Path
from typing import Callable, Dict, List, Optional
from urllib.parse import urlparse, unquote

import requests
from dotenv import load_dotenv

load_dotenv()


def clean_title(raw_title: str) -> str:
    """워드프레스 title.rendered에 남아있는 HTML 엔티티/태그를 정리"""
    no_tags = re.sub(r"<[^>]+>", "", raw_title)
    return html.unescape(no_tags).strip()


def normalize_url(url: str) -> str:
    """검색결과 URL과 내 글 URL을 비교하기 위해 정규화 (스킴/www/트레일링 슬래시 무시)"""
    parsed = urlparse(unquote(url))
    netloc = parsed.netloc.lower()
    if netloc.startswith("www."):
        netloc = netloc[4:]
    path = parsed.path.rstrip("/")
    return f"{netloc}{path}"


def url_matches(target: str, candidate: str) -> bool:
    if not candidate:
        return False
    return normalize_url(target) == normalize_url(candidate)


def find_rank(target_url: str, links: List[str]) -> Optional[int]:
    for rank, link in enumerate(links, start=1):
        if url_matches(target_url, link):
            return rank
    return None


# ----------------------------------------------------------------------
# 워드프레스에서 최근 글 목록 가져오기
# ----------------------------------------------------------------------
def fetch_recent_posts(limit: int, wp_url: Optional[str] = None) -> List[Dict]:
    base_url = (wp_url or os.getenv("WP_URL") or "").rstrip("/")
    if not base_url:
        raise ValueError("WP_URL이 설정되지 않았습니다. .env 파일에 워드프레스 사이트 주소를 입력하세요.")

    endpoint = f"{base_url}/wp-json/wp/v2/posts"
    resp = requests.get(
        endpoint,
        params={"per_page": min(limit, 100), "orderby": "date", "order": "desc"},
        timeout=15,
    )
    resp.raise_for_status()

    posts = []
    for item in resp.json():
        posts.append(
            {
                "id": item["id"],
                "title": clean_title(item["title"]["rendered"]),
                "link": item["link"],
                "date": item.get("date"),
            }
        )
    return posts


# ----------------------------------------------------------------------
# 검색엔진별 체크 함수
# 각 함수는 {"checked": bool, "exposed": Optional[bool], "rank": Optional[int], "reason": str} 를 반환
# ----------------------------------------------------------------------
def check_google(title: str, url: str) -> Dict:
    """Google Programmable Search Engine (Custom Search JSON API)"""
    api_key = os.getenv("GOOGLE_API_KEY")
    cse_id = os.getenv("GOOGLE_CSE_ID")
    if not api_key or not cse_id:
        return {"checked": False, "reason": "GOOGLE_API_KEY / GOOGLE_CSE_ID 미설정"}

    resp = requests.get(
        "https://www.googleapis.com/customsearch/v1",
        params={"key": api_key, "cx": cse_id, "q": title, "num": 10},
        timeout=15,
    )
    resp.raise_for_status()
    items = resp.json().get("items", [])
    rank = find_rank(url, [item.get("link", "") for item in items])
    return {"checked": True, "exposed": rank is not None, "rank": rank}


def check_bing(title: str, url: str) -> Dict:
    """Bing Web Search API (Azure Cognitive Services)"""
    api_key = os.getenv("BING_API_KEY")
    if not api_key:
        return {"checked": False, "reason": "BING_API_KEY 미설정"}

    resp = requests.get(
        "https://api.bing.microsoft.com/v7.0/search",
        headers={"Ocp-Apim-Subscription-Key": api_key},
        params={"q": title, "count": 10, "mkt": "ko-KR"},
        timeout=15,
    )
    resp.raise_for_status()
    items = resp.json().get("webPages", {}).get("value", [])
    rank = find_rank(url, [item.get("url", "") for item in items])
    return {"checked": True, "exposed": rank is not None, "rank": rank}


def check_naver(title: str, url: str) -> Dict:
    """네이버 오픈API - 검색(웹문서)"""
    client_id = os.getenv("NAVER_CLIENT_ID")
    client_secret = os.getenv("NAVER_CLIENT_SECRET")
    if not client_id or not client_secret:
        return {"checked": False, "reason": "NAVER_CLIENT_ID / NAVER_CLIENT_SECRET 미설정"}

    resp = requests.get(
        "https://openapi.naver.com/v1/search/webkr.json",
        headers={"X-Naver-Client-Id": client_id, "X-Naver-Client-Secret": client_secret},
        params={"query": title, "display": 30},
        timeout=15,
    )
    resp.raise_for_status()
    items = resp.json().get("items", [])
    rank = find_rank(url, [item.get("link", "") for item in items])
    return {"checked": True, "exposed": rank is not None, "rank": rank}


def check_daum(title: str, url: str) -> Dict:
    """카카오(다음) 검색 API - 웹 문서 검색"""
    rest_api_key = os.getenv("KAKAO_REST_API_KEY")
    if not rest_api_key:
        return {"checked": False, "reason": "KAKAO_REST_API_KEY 미설정"}

    resp = requests.get(
        "https://dapi.kakao.com/v2/search/web",
        headers={"Authorization": f"KakaoAK {rest_api_key}"},
        params={"query": title, "size": 30},
        timeout=15,
    )
    resp.raise_for_status()
    items = resp.json().get("documents", [])
    rank = find_rank(url, [item.get("url", "") for item in items])
    return {"checked": True, "exposed": rank is not None, "rank": rank}


ENGINES: Dict[str, Callable[[str, str], Dict]] = {
    "google": check_google,
    "bing": check_bing,
    "naver": check_naver,
    "daum": check_daum,
}


def check_post(post: Dict, engine_names: List[str]) -> Dict:
    result = {"title": post["title"], "link": post["link"], "date": post.get("date"), "results": {}}
    for name in engine_names:
        try:
            result["results"][name] = ENGINES[name](post["title"], post["link"])
        except requests.RequestException as e:
            result["results"][name] = {"checked": False, "reason": f"요청 실패: {e}"}
    return result


def print_report(results: List[Dict]) -> None:
    for r in results:
        print(f"\n📄 {r['title']}")
        print(f"   🔗 {r['link']}")
        for engine, res in r["results"].items():
            label = f"{engine:6s}"
            if not res.get("checked"):
                print(f"   {label}: ⚠️  확인 불가 ({res.get('reason')})")
            elif res.get("exposed"):
                print(f"   {label}: ✅ 노출됨 (검색결과 {res.get('rank')}위 내)")
            else:
                print(f"   {label}: ❌ 미노출 (상위 검색결과에 없음)")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="워드프레스 글의 검색엔진(구글/빙/네이버/다음) 노출 여부 확인 도구",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
사용 예시:
  python seo_exposure_checker.py                          # 최근 5개 글 전체 엔진 확인
  python seo_exposure_checker.py --limit 10
  python seo_exposure_checker.py --engines google,naver
  python seo_exposure_checker.py --url "https://example.com/2026/09/02/my-post/" --title "내 글 제목"
        """,
    )
    parser.add_argument("--limit", type=int, default=5, help="확인할 최근 글 개수 (기본값: 5)")
    parser.add_argument("--wp-url", default=None, help="워드프레스 사이트 주소 (미지정 시 .env의 WP_URL 사용)")
    parser.add_argument("--url", default=None, help="워드프레스에서 목록을 가져오지 않고, 특정 글 URL 하나만 확인")
    parser.add_argument("--title", default=None, help="--url과 함께 사용. 검색에 사용할 글 제목 (미지정 시 URL 자체를 검색어로 사용)")
    parser.add_argument(
        "--engines",
        default=",".join(ENGINES.keys()),
        help=f"확인할 검색엔진 목록 (쉼표 구분, 기본값: 전체). 사용 가능: {', '.join(ENGINES.keys())}",
    )
    parser.add_argument("--output", default=None, help="결과 JSON 저장 경로 (기본값: output/seo_check_<타임스탬프>.json)")

    args = parser.parse_args()

    engine_names = [e.strip() for e in args.engines.split(",") if e.strip()]
    unknown = [e for e in engine_names if e not in ENGINES]
    if unknown:
        print(f"❌ 알 수 없는 검색엔진: {', '.join(unknown)} (사용 가능: {', '.join(ENGINES.keys())})")
        return 1

    try:
        if args.url:
            posts = [{"title": args.title or args.url, "link": args.url, "date": None}]
        else:
            posts = fetch_recent_posts(args.limit, wp_url=args.wp_url)
    except (ValueError, requests.RequestException) as e:
        print(f"❌ 워드프레스 글 목록을 가져오지 못했습니다: {e}")
        return 1

    if not posts:
        print("확인할 글이 없습니다.")
        return 0

    results = [check_post(post, engine_names) for post in posts]
    print_report(results)

    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = Path(args.output) if args.output else output_dir / f"seo_check_{timestamp}.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n💾 결과가 저장되었습니다: {output_file}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
