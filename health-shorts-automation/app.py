"""건강정보 쇼츠 자동화 - Streamlit 웹 UI"""

import sys
import json
from pathlib import Path

import streamlit as st

# 프로젝트 루트를 sys.path에 추가
sys.path.insert(0, str(Path(__file__).parent))

from config.settings import (
    ELEVENLABS_VOICE_ID, BGM_DIR, VIDEO_DIR, THUMBNAIL_DIR,
)
from modules.utils import check_ffmpeg, logger
from modules.job_manager import list_jobs


# ── 페이지 설정 ─────────────────────────────────────────────────
st.set_page_config(
    page_title="건강정보 쇼츠 자동화",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    .main-title { font-size: 2rem; font-weight: 700; color: #1a73e8; }
    .step-badge {
        background: #1a73e8; color: white;
        border-radius: 50%; width: 28px; height: 28px;
        display: inline-flex; align-items: center; justify-content: center;
        font-weight: bold; margin-right: 8px;
    }
    .info-box {
        background: #f0f4ff; border-left: 4px solid #1a73e8;
        padding: 12px 16px; border-radius: 4px; margin: 8px 0;
    }
    .warning-box {
        background: #fff8e1; border-left: 4px solid #f9a825;
        padding: 12px 16px; border-radius: 4px; margin: 8px 0;
    }
    .success-box {
        background: #e8f5e9; border-left: 4px solid #2e7d32;
        padding: 12px 16px; border-radius: 4px; margin: 8px 0;
    }
</style>
""", unsafe_allow_html=True)


# ── 사이드바 ────────────────────────────────────────────────────
def sidebar():
    with st.sidebar:
        st.markdown("## ⚙️ 설정")

        st.markdown("### 영상 기본 설정")
        duration = st.select_slider(
            "영상 길이",
            options=[30, 45, 60],
            value=45,
            format_func=lambda x: f"{x}초",
        )
        tone = st.selectbox(
            "영상 톤",
            options=["informative", "warning", "warm", "news"],
            format_func=lambda x: {
                "informative": "📋 정보형",
                "warning": "⚠️ 경고형",
                "warm": "💚 따뜻한 설명형",
                "news": "📰 뉴스형",
            }[x],
        )

        st.markdown("### TTS 설정")
        voice_id = st.text_input(
            "ElevenLabs Voice ID",
            value=ELEVENLABS_VOICE_ID or "",
            placeholder="ElevenLabs 대시보드에서 복사",
            help="ElevenLabs 대시보드 > Voices 에서 원하는 목소리의 Voice ID를 복사하세요.",
        )

        st.markdown("### BGM 설정")
        bgm_files = list(BGM_DIR.glob("*.mp3")) + list(BGM_DIR.glob("*.wav"))
        bgm_options = ["없음"] + [f.name for f in bgm_files]
        selected_bgm = st.selectbox("배경음악", bgm_options)
        bgm_volume = st.slider("BGM 볼륨", 0.0, 0.3, 0.10, 0.01)

        st.markdown("### 썸네일 설정")
        thumb_sizes = st.multiselect(
            "생성할 썸네일 크기",
            options=["vertical", "horizontal"],
            default=["vertical"],
            format_func=lambda x: "세로형 (1080×1920)" if x == "vertical" else "가로형 (1280×720)",
        )

        # 환경 체크
        st.markdown("---")
        st.markdown("### 환경 상태")
        ffmpeg_ok = check_ffmpeg()
        st.markdown(
            "✅ FFmpeg 설치됨" if ffmpeg_ok else "❌ FFmpeg 없음 → [설치 방법](https://ffmpeg.org/download.html)"
        )

        from config.settings import ANTHROPIC_API_KEY, ELEVENLABS_API_KEY
        st.markdown("✅ Claude API 키 설정됨" if ANTHROPIC_API_KEY else "❌ ANTHROPIC_API_KEY 미설정")
        st.markdown("✅ ElevenLabs API 키 설정됨" if ELEVENLABS_API_KEY else "❌ ELEVENLABS_API_KEY 미설정")

    return {
        "duration": duration,
        "tone": tone,
        "voice_id": voice_id if voice_id else None,
        "bgm_path": BGM_DIR / selected_bgm if selected_bgm != "없음" else None,
        "bgm_volume": bgm_volume,
        "thumb_sizes": thumb_sizes or ["vertical"],
    }


# ── 메인 탭 ─────────────────────────────────────────────────────
def main():
    st.markdown('<div class="main-title">🏥 건강정보 쇼츠 자동화</div>', unsafe_allow_html=True)
    st.markdown("건강 주제를 입력하면 유튜브 쇼츠 영상을 자동으로 생성합니다.")
    st.markdown(
        '<div class="warning-box">⚠️ 이 프로그램이 생성하는 콘텐츠는 일반 건강정보 제공 목적이며, '
        '전문 의료 진단을 대체하지 않습니다.</div>',
        unsafe_allow_html=True,
    )

    settings = sidebar()

    tab1, tab2, tab3 = st.tabs(["🎬 영상 생성", "📂 작업 기록", "📖 사용 방법"])

    # ── 탭 1: 영상 생성 ─────────────────────────────────────────
    with tab1:
        col1, col2 = st.columns([2, 1])

        with col1:
            st.markdown("### 주제 입력")
            topic = st.text_input(
                "건강 주제",
                placeholder="예: 무릎 통증 완화법, 혈압 낮추는 생활습관, 수면 개선 방법",
                label_visibility="collapsed",
            )
            topic_examples = [
                "무릎 통증 완화법", "혈압 낮추는 생활습관", "수면 개선 방법",
                "당뇨 예방 식단", "허리 통증 자세 교정", "눈 피로 회복법",
            ]
            st.caption("예시: " + " · ".join(f"`{t}`" for t in topic_examples))

        with col2:
            st.markdown("### 이미지 업로드 (선택)")
            uploaded_images = st.file_uploader(
                "장면별 배경 이미지",
                type=["jpg", "jpeg", "png"],
                accept_multiple_files=True,
                help="업로드하지 않으면 자동으로 그라데이션 배경이 생성됩니다.",
            )

        start_btn = st.button(
            "🚀 영상 자동 생성 시작",
            type="primary",
            use_container_width=True,
            disabled=not topic.strip(),
        )

        if start_btn and topic.strip():
            _run_generation(topic.strip(), settings, uploaded_images)

        # 생성 결과 표시
        if "result" in st.session_state and st.session_state.result:
            _show_result(st.session_state.result)

    # ── 탭 2: 작업 기록 ─────────────────────────────────────────
    with tab2:
        st.markdown("### 최근 작업 기록")
        jobs = list_jobs(20)
        if not jobs:
            st.info("아직 생성된 영상이 없습니다.")
        else:
            for job in jobs:
                status_icon = {
                    "completed": "✅",
                    "failed": "❌",
                    "running": "⏳",
                }.get(job["status"], "⏳")

                with st.expander(
                    f"{status_icon} [{job['created_at'][:16]}] {job['topic']} — {job['title'] or '제목 없음'}"
                ):
                    col_a, col_b, col_c = st.columns(3)
                    col_a.metric("상태", job["status"])
                    col_b.metric("길이", f"{job['duration']}초")
                    col_c.metric("톤", job["tone"])

                    if job.get("video_path") and Path(job["video_path"]).exists():
                        with open(job["video_path"], "rb") as f:
                            st.download_button(
                                "📥 영상 다운로드",
                                data=f,
                                file_name=Path(job["video_path"]).name,
                                mime="video/mp4",
                                key=f"dl_video_{job['job_id']}",
                            )

                    if job.get("error_msg"):
                        st.error(f"오류: {job['error_msg']}")

    # ── 탭 3: 사용 방법 ─────────────────────────────────────────
    with tab3:
        st.markdown("""
### 사용 방법

1. **API 키 설정**: `.env` 파일에 `ANTHROPIC_API_KEY`, `ELEVENLABS_API_KEY`, `ELEVENLABS_VOICE_ID` 입력
2. **FFmpeg 설치**: [ffmpeg.org](https://ffmpeg.org/download.html) 또는 `winget install ffmpeg`
3. **주제 입력**: 건강 관련 주제를 입력
4. **설정 조정**: 왼쪽 사이드바에서 길이, 톤, 목소리 선택
5. **생성 시작**: '영상 자동 생성 시작' 버튼 클릭
6. **다운로드**: 생성 완료 후 영상/썸네일 다운로드

### ElevenLabs Voice ID 찾는 방법
1. [ElevenLabs](https://elevenlabs.io/) 로그인
2. Voices 메뉴에서 원하는 목소리 선택
3. 목소리 이름 옆 ID를 복사해서 `.env`의 `ELEVENLABS_VOICE_ID`에 붙여넣기

### 자주 묻는 오류

| 오류 | 해결 방법 |
|------|----------|
| FFmpeg 없음 | `winget install ffmpeg` 또는 공식 사이트에서 설치 |
| API 키 오류 | `.env` 파일 확인, 따옴표 없이 키만 입력 |
| Voice ID 오류 | ElevenLabs 대시보드에서 Voice ID 재확인 |
| 렌더링 실패 | FFmpeg PATH 환경변수 설정 확인 |
        """)


def _run_generation(topic: str, settings: dict, uploaded_images):
    """영상 생성 파이프라인 실행"""
    from modules.pipeline import run_pipeline
    import tempfile

    # 업로드된 이미지 저장
    bg_images = []
    if uploaded_images:
        tmp_dir = Path(tempfile.mkdtemp())
        for i, img_file in enumerate(uploaded_images):
            img_path = tmp_dir / f"bg_{i:02d}{Path(img_file.name).suffix}"
            img_path.write_bytes(img_file.read())
            bg_images.append(img_path)

    # 진행 상태 UI
    st.markdown("---")
    st.markdown("### 생성 진행 상황")

    progress_bar = st.progress(0)
    status_text = st.empty()
    step_statuses = {
        "대본 생성": st.empty(),
        "TTS 음성 생성": st.empty(),
        "자막 생성": st.empty(),
        "영상 렌더링": st.empty(),
        "썸네일 생성": st.empty(),
    }
    step_order = list(step_statuses.keys())
    step_progress = {s: 0.0 for s in step_order}

    def _on_progress(step_name: str, ratio: float):
        step_progress[step_name] = ratio

        # 전체 진행률
        total = sum(step_progress.values()) / len(step_progress)
        progress_bar.progress(min(total, 1.0))
        status_text.markdown(f"**{step_name}** 진행 중... {int(ratio*100)}%")

        # 스텝별 아이콘
        for s, placeholder in step_statuses.items():
            p = step_progress[s]
            if p == 0:
                placeholder.markdown(f"⬜ {s}")
            elif p < 1.0:
                placeholder.markdown(f"🔄 {s} ({int(p*100)}%)")
            else:
                placeholder.markdown(f"✅ {s}")

    try:
        result = run_pipeline(
            topic=topic,
            duration=settings["duration"],
            tone=settings["tone"],
            voice_id=settings["voice_id"],
            bgm_path=settings["bgm_path"],
            background_images=bg_images or None,
            generate_thumb_sizes=settings["thumb_sizes"],
            progress_callback=_on_progress,
        )

        progress_bar.progress(1.0)
        status_text.success("✅ 영상 생성 완료!")
        st.session_state.result = result
        st.rerun()

    except ValueError as e:
        st.error(f"설정 오류: {e}")
    except RuntimeError as e:
        st.error(f"생성 오류: {e}")
    except Exception as e:
        st.error(f"예상치 못한 오류가 발생했습니다: {e}")
        logger.exception("파이프라인 예외")


def _show_result(result: dict):
    """생성 결과 표시"""
    st.markdown("---")
    st.markdown("## 생성 결과")
    st.markdown(
        '<div class="success-box">✅ 영상이 성공적으로 생성되었습니다!</div>',
        unsafe_allow_html=True,
    )

    script = result.get("script", {})

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 대본 미리보기")
        if script:
            st.markdown(f"**제목:** {script.get('title', '')}")
            st.markdown(f"**후킹 문장:** {script.get('hook', '')}")

            with st.expander("전체 대본 보기"):
                st.text(script.get("script", ""))

            with st.expander("장면별 자막 보기"):
                for scene in script.get("scenes", []):
                    st.markdown(
                        f"**장면 {scene['scene_no']}** ({scene['duration']}초): "
                        f"{scene['caption']}"
                    )
                    st.caption(scene['narration'])

            if script.get("hashtags"):
                st.markdown("**해시태그:** " + " ".join(script["hashtags"]))

    with col2:
        st.markdown("### 다운로드")

        # 영상 다운로드
        video_path = result.get("video_path")
        if video_path and Path(video_path).exists():
            st.video(str(video_path))
            with open(video_path, "rb") as f:
                st.download_button(
                    "📥 영상 다운로드 (MP4)",
                    data=f,
                    file_name=Path(video_path).name,
                    mime="video/mp4",
                    use_container_width=True,
                )

        # 썸네일 다운로드
        thumbnails = result.get("thumbnails", {})
        for size_key, thumb_path in thumbnails.items():
            if thumb_path and Path(thumb_path).exists():
                label = "세로형" if size_key == "vertical" else "가로형"
                with open(thumb_path, "rb") as f:
                    st.download_button(
                        f"🖼️ 썸네일 다운로드 ({label})",
                        data=f,
                        file_name=Path(thumb_path).name,
                        mime="image/jpeg",
                        use_container_width=True,
                        key=f"thumb_{size_key}",
                    )
                st.image(str(thumb_path), caption=f"썸네일 ({label})", use_container_width=True)

        # 자막 다운로드
        subtitles = result.get("subtitle_paths", {})
        srt_path = subtitles.get("srt")
        if srt_path and Path(srt_path).exists():
            with open(srt_path, "rb") as f:
                st.download_button(
                    "📄 자막 다운로드 (SRT)",
                    data=f,
                    file_name=Path(srt_path).name,
                    mime="text/plain",
                    use_container_width=True,
                )


if __name__ == "__main__":
    main()
