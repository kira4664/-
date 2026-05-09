import os
import asyncio
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
TEMPLATES_DIR = BASE_DIR / "templates"
STYLES_DIR = BASE_DIR / "styles"


def _build_bullets_html(bullets: list, color: str = "#333333", dot_color: str = "#2196f3") -> str:
    items = []
    for b in bullets:
        items.append(
            f'<div class="bullet-item" style="color:{color}">'
            f'<div class="bullet-dot" style="background:{dot_color}"></div>'
            f'<span>{b}</span></div>'
        )
    return "\n".join(items)


def _render_hook(card: dict, number: int, total: int, brand: str) -> str:
    tmpl = (TEMPLATES_DIR / "card_hook.html").read_text(encoding="utf-8")
    return (tmpl
            .replace("{{emoji}}", card.get("emoji", "📢"))
            .replace("{{title}}", card.get("title", ""))
            .replace("{{subtitle}}", card.get("subtitle", ""))
            .replace("{{total}}", str(total))
            .replace("{{brand}}", brand))


def _render_cta(card: dict, number: int, total: int, brand: str) -> str:
    tmpl = (TEMPLATES_DIR / "card_cta.html").read_text(encoding="utf-8")
    return (tmpl
            .replace("{{emoji}}", card.get("emoji", "🔔"))
            .replace("{{title}}", card.get("title", ""))
            .replace("{{btn1}}", card.get("btn1", "저장하기"))
            .replace("{{btn2}}", card.get("btn2", "공유하기"))
            .replace("{{number}}", str(number))
            .replace("{{total}}", str(total))
            .replace("{{brand}}", brand))


def _render_summary(card: dict, number: int, total: int, brand: str) -> str:
    tmpl = (TEMPLATES_DIR / "card_summary.html").read_text(encoding="utf-8")
    bullets_html = _build_bullets_html(
        card.get("bullets", []),
        color="#333333",
        dot_color="#ff9800"
    )
    return (tmpl
            .replace("{{title}}", card.get("title", ""))
            .replace("{{bullets}}", bullets_html)
            .replace("{{number}}", str(number))
            .replace("{{total}}", str(total))
            .replace("{{brand}}", brand))


THEME_MAP = {
    "problem":   ("theme-problem",  "light", "tag-problem",   "#ff7043", "#ff7043"),
    "info":      ("theme-info",     "light", "tag-info",      "#2196f3", "#2196f3"),
    "condition": ("theme-condition","light", "tag-condition",  "#4caf50", "#4caf50"),
    "method":    ("theme-method",   "light", "tag-method",    "#9c27b0", "#9c27b0"),
    "caution":   ("theme-caution",  "light", "tag-caution",   "#f44336", "#f44336"),
}


def _render_content(card: dict, number: int, total: int, brand: str) -> str:
    card_type = card.get("type", "info")
    theme, mode, tag_class, text_color, dot_color = THEME_MAP.get(
        card_type, ("theme-info", "light", "tag-info", "#2196f3", "#2196f3")
    )
    tmpl = (TEMPLATES_DIR / "card_content.html").read_text(encoding="utf-8")
    bullets_html = _build_bullets_html(
        card.get("bullets", []),
        color=text_color,
        dot_color=dot_color
    )
    return (tmpl
            .replace("{{theme}}", theme)
            .replace("{{mode}}", mode)
            .replace("{{tag}}", card.get("tag", ""))
            .replace("{{tag_class}}", tag_class)
            .replace("{{title}}", card.get("title", ""))
            .replace("{{bullets}}", bullets_html)
            .replace("{{number}}", str(number))
            .replace("{{total}}", str(total))
            .replace("{{brand}}", brand))


def build_html(card: dict, number: int, total: int, brand: str) -> str:
    card_type = card.get("type", "info")
    if card_type == "hook":
        return _render_hook(card, number, total, brand)
    elif card_type == "cta":
        return _render_cta(card, number, total, brand)
    elif card_type == "summary":
        return _render_summary(card, number, total, brand)
    else:
        return _render_content(card, number, total, brand)


async def _capture_with_playwright(html_content: str, output_path: Path, tmp_html: Path):
    from playwright.async_api import async_playwright

    tmp_html.write_text(html_content, encoding="utf-8")

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": 1080, "height": 1080})
        await page.goto(f"file://{tmp_html.resolve()}")
        await page.wait_for_timeout(800)
        await page.screenshot(path=str(output_path), full_page=False)
        await browser.close()

    tmp_html.unlink(missing_ok=True)


def render_card_to_png(card: dict, number: int, total: int, brand: str, output_path: Path):
    html = build_html(card, number, total, brand)
    tmp_html = output_path.parent / f"_tmp_card_{number:02d}.html"

    asyncio.run(_capture_with_playwright(html, output_path, tmp_html))
