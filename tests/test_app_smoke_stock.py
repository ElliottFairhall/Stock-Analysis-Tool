"""Smoke and design-guard tests for the Streamlit app.

These run the real ``app.py`` headlessly with Streamlit's ``AppTest`` harness, so
a dependency upgrade that breaks an import, a pandas or plotly call, or the
shipped theme fails here instead of in the browser. They also guard the design
rules the Data Flakes apps follow: native theming, light and dark modes, and no
decorative gradients or emoji headings.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parent.parent
APP = ROOT / "app.py"
CSS = ROOT / "styles" / "main.css"
CONFIG = ROOT / ".streamlit" / "config.toml"
EMOJI = re.compile("[\U0001f300-\U0001faff☀-➿⭐️]")


@pytest.fixture(scope="module")
def app() -> AppTest:
    """Run the app once and share the result across the assertions below."""
    return AppTest.from_file(str(APP), default_timeout=90).run()


def test_app_renders_without_exception(app: AppTest) -> None:
    """No uncaught exception is raised while the script runs."""
    assert not app.exception, [item.value for item in app.exception]


def test_app_has_a_title(app: AppTest) -> None:
    """The page shows a title."""
    assert app.title, "the app rendered no title"


def test_headings_have_no_emoji(app: AppTest) -> None:
    """Headings are plain text; emoji as decoration is a generated-UI giveaway."""
    headings = [item.value for item in (*app.title, *app.header, *app.subheader)]
    offenders = [text for text in headings if EMOJI.search(text)]
    assert not offenders, f"emoji in headings: {offenders}"


def test_stylesheet_is_valid_and_restrained() -> None:
    """The stylesheet balances its braces and avoids decorative effects."""
    css = CSS.read_text(encoding="utf-8")
    assert css.count("{") == css.count("}"), "unbalanced braces in main.css"
    assert "gradient" not in css, "no gradients: use solid palette colours"
    assert "text-fill-color" not in css, "no gradient text"
    if "@import" in css:
        assert css.index("@import") < css.index("{"), (
            "@import must come before any rule or the browser ignores it"
        )


def test_theme_is_native_and_supports_light_and_dark() -> None:
    """Fonts and colours live in the Streamlit theme, in both modes."""
    config = CONFIG.read_text(encoding="utf-8")
    assert "[theme.light]" in config
    assert "[theme.dark]" in config
    assert "Inter" in config
