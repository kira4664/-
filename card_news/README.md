# 인스타 카드뉴스 자동생성기

본문 텍스트를 넣으면 1080×1350 PNG 카드뉴스 8장을 자동으로 만들어주는 프로그램입니다.

## 폴더 구조

```
card_news/
├── input/
│   └── content.txt       ← 입력 본문
├── output/
│   ├── card_01.png ~ card_08.png
│   ├── cards.zip
│   └── caption.txt
├── templates/
│   ├── card_hook.html
│   ├── card_content.html
│   ├── card_summary.html
│   └── card_cta.html
├── styles/
│   └── card.css
├── src/
│   ├── analyze_text.py   ← Claude API로 카드 문구 생성
│   ├── render_image.py   ← HTML → PNG (Playwright)
│   └── generate_cards.py ← 전체 파이프라인
├── generate.py           ← CLI 실행 파일
├── app.py                ← Streamlit 웹 앱
└── requirements.txt
```

## 설치

```bash
cd card_news
pip install -r requirements.txt
playwright install chromium
```

## API 키 설정

프로젝트 루트의 `.env` 파일에 Anthropic API 키를 입력하세요:

```
ANTHROPIC_API_KEY=sk-ant-...
```

## 실행 방법

### CLI

```bash
# 기본 실행 (input/content.txt 사용, 8장 생성)
python generate.py

# 파일 지정
python generate.py --input my_article.txt

# 카드 수 지정
python generate.py --count 6
```

### 웹 앱 (Streamlit)

```bash
streamlit run app.py
```

브라우저에서 `http://localhost:8501` 접속

## 출력물

| 파일 | 설명 |
|------|------|
| `output/card_01.png` ~ `card_08.png` | 카드뉴스 이미지 |
| `output/cards.zip` | 전체 이미지 압축 파일 |
| `output/caption.txt` | 인스타 업로드용 캡션 + 해시태그 |

## 카드 구성

| 장 | 유형 | 내용 |
|----|------|------|
| 1장 | hook | 강한 후킹 제목 |
| 2장 | problem | 문제 제기 / 배경 |
| 3장 | info | 핵심 정보 (금액/기간 등) |
| 4장 | condition | 대상자 조건 |
| 5장 | method | 신청 방법 / 절차 |
| 6장 | caution | 주의사항 |
| 7장 | summary | 전체 요약 |
| 8장 | cta | 저장 / 공유 유도 |
