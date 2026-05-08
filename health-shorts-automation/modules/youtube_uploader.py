"""YouTube Data API v3 업로드 모듈 (선택 기능)"""

import json
import pickle
from pathlib import Path
from typing import Optional

from config.settings import YOUTUBE_CLIENT_SECRET_FILE, YOUTUBE_TOKEN_FILE, YOUTUBE_SCOPES
from modules.utils import logger


def _get_authenticated_service():
    """Google OAuth2 인증 및 YouTube 서비스 생성"""
    try:
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from google.auth.transport.requests import Request
        from googleapiclient.discovery import build
    except ImportError:
        raise ImportError(
            "YouTube 업로드 기능을 사용하려면 아래 패키지가 필요합니다:\n"
            "pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib"
        )

    secret_file = Path(YOUTUBE_CLIENT_SECRET_FILE)
    token_file = Path(YOUTUBE_TOKEN_FILE)

    if not secret_file.exists():
        raise FileNotFoundError(
            f"YouTube OAuth 클라이언트 시크릿 파일이 없습니다: {secret_file}\n"
            "Google Cloud Console에서 OAuth 2.0 클라이언트 ID를 생성하고\n"
            f"'{secret_file}' 이름으로 저장하세요."
        )

    creds = None

    # 저장된 토큰 로드
    if token_file.exists():
        try:
            creds = Credentials.from_authorized_user_file(str(token_file), YOUTUBE_SCOPES)
        except Exception:
            pass

    # 토큰 갱신 또는 새 인증
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                str(secret_file), YOUTUBE_SCOPES
            )
            creds = flow.run_local_server(port=0)

        token_file.write_text(creds.to_json())

    return build("youtube", "v3", credentials=creds)


def upload_to_youtube(
    video_path: Path,
    title: str,
    description: str,
    hashtags: Optional[list[str]] = None,
    thumbnail_path: Optional[Path] = None,
    category_id: str = "26",  # 26 = Howto & Style
    privacy_status: str = "private",
) -> str:
    """
    유튜브에 영상 업로드

    Args:
        video_path: 업로드할 mp4 파일 경로
        title: 영상 제목
        description: 영상 설명
        hashtags: 해시태그 목록
        thumbnail_path: 썸네일 이미지 경로
        category_id: 유튜브 카테고리 ID
        privacy_status: "private" / "unlisted" / "public"

    Returns:
        업로드된 영상 URL
    """
    try:
        from googleapiclient.http import MediaFileUpload
    except ImportError:
        raise ImportError("pip install google-api-python-client 를 먼저 실행하세요.")

    if not video_path.exists():
        raise FileNotFoundError(f"영상 파일이 없습니다: {video_path}")

    tags = []
    if hashtags:
        tags = [tag.lstrip("#") for tag in hashtags]

    disclaimer = (
        "\n\n※ 이 영상은 일반 건강정보 제공을 목적으로 하며, "
        "전문 의료 진단을 대체하지 않습니다. "
        "증상이 지속되거나 심한 경우 반드시 의료 전문가와 상담하시기 바랍니다."
    )
    full_description = description + disclaimer

    body = {
        "snippet": {
            "title": title[:100],
            "description": full_description[:5000],
            "tags": tags[:500],
            "categoryId": category_id,
        },
        "status": {
            "privacyStatus": privacy_status,
            "selfDeclaredMadeForKids": False,
        },
    }

    logger.info(f"유튜브 업로드 시작: {title}")

    youtube = _get_authenticated_service()

    media = MediaFileUpload(
        str(video_path),
        mimetype="video/mp4",
        resumable=True,
        chunksize=1024 * 1024 * 8,  # 8MB chunks
    )

    request = youtube.videos().insert(
        part=",".join(body.keys()),
        body=body,
        media_body=media,
    )

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            logger.info(f"업로드 진행: {int(status.progress() * 100)}%")

    video_id = response.get("id", "")
    video_url = f"https://www.youtube.com/watch?v={video_id}"

    # 썸네일 설정
    if thumbnail_path and thumbnail_path.exists() and video_id:
        try:
            from googleapiclient.http import MediaFileUpload as MFU
            youtube.thumbnails().set(
                videoId=video_id,
                media_body=MFU(str(thumbnail_path)),
            ).execute()
            logger.info("썸네일 설정 완료")
        except Exception as e:
            logger.warning(f"썸네일 설정 실패: {e}")

    logger.info(f"유튜브 업로드 완료: {video_url}")
    return video_url
