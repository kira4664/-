"""Streamlit 웹 앱: streamlit run app.py"""
import os
import sys
from pathlib import Path
import streamlit as st
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")
load_dotenv(Path(__file__).parent / ".env")

from src.generate_cards import generate

st.set_page_config(
    page_title="인스타 카드뉴스 자동생성기",
    page_icon="📱",
    layout="wide"
)

st.title("📱 인스타 카드뉴스 자동생성기")
st.caption("본문을 붙여넣으면 1080×1080 카드뉴스 이미지를 자동으로 만들어드립니다.")

st.divider()

col_input, col_options = st.columns([3, 1])

with col_input:
    text = st.text_area(
        "본문 입력",
        height=300,
        placeholder="뉴스 기사, 정책 안내, 블로그 글 등을 붙여넣어 주세요...",
        help="복지 정책, 지원금, 뉴스, 상품 정보 등 어떤 글이든 OK"
    )

with col_options:
    card_count = st.selectbox("카드 수", [6, 7, 8, 9, 10], index=2)
    st.markdown("**카드 구성**")
    st.markdown("🎯 1장: 후킹 제목")
    st.markdown("❓ 2장: 문제 제기")
    st.markdown("ℹ️ 3장: 핵심 정보")
    st.markdown("✅ 4장: 조건/대상")
    st.markdown("📋 5장: 신청 방법")
    st.markdown("⚠️ 6장: 주의사항")
    st.markdown("📝 7장: 요약")
    st.markdown("📣 8장: CTA")

generate_btn = st.button("🚀 카드뉴스 생성하기", type="primary", use_container_width=True)

if generate_btn:
    if not text.strip():
        st.error("본문을 입력해주세요.")
        st.stop()

    progress_bar = st.progress(0)
    status = st.empty()

    def update_progress(pct: float, msg: str):
        progress_bar.progress(pct)
        status.info(msg)

    try:
        result = generate(text.strip(), card_count=card_count, progress_cb=update_progress)
        progress_bar.progress(1.0)
        status.success("✅ 카드뉴스 생성 완료!")

        st.divider()
        st.subheader("🖼️ 생성된 카드뉴스")

        cols = st.columns(4)
        for i, png_path in enumerate(result["png_paths"]):
            with cols[i % 4]:
                st.image(png_path, caption=f"카드 {i+1}", use_container_width=True)

        st.divider()
        col_dl, col_caption = st.columns([1, 2])

        with col_dl:
            st.subheader("📦 다운로드")
            zip_path = result["zip_path"]
            with open(zip_path, "rb") as f:
                st.download_button(
                    "⬇️ ZIP 다운로드",
                    data=f,
                    file_name="cards.zip",
                    mime="application/zip",
                    use_container_width=True
                )

        with col_caption:
            st.subheader("✍️ 인스타 캡션")
            caption_full = f"{result['caption']}\n\n{result['hashtags']}"
            st.text_area("복사해서 사용하세요", value=caption_full, height=180)

    except Exception as e:
        progress_bar.empty()
        status.empty()
        st.error(f"오류 발생: {e}")
        st.exception(e)

st.divider()
with st.expander("📌 사용 방법"):
    st.markdown("""
1. 본문 텍스트를 위 입력창에 붙여넣기
2. 카드 수 선택 (기본 8장)
3. '카드뉴스 생성하기' 클릭
4. 미리보기 확인 후 ZIP 다운로드
5. 인스타 캡션 복사 후 업로드

**잘 어울리는 콘텐츠 유형**
- 정부 지원금 / 복지 정책 안내
- 뉴스 요약
- 제품/서비스 소개
- 생활 정보 / 꿀팁
""")
