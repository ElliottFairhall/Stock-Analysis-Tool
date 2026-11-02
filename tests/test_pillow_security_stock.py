"""Regression guard for the Pillow 13 upgrade.

Pillow < 13.0.0 has known high-severity TIFF and PDF-parser advisories
(GHSA-c6hw-5grf-ff96, GHSA-q45j-58j2-45rg, GHSA-p4wg-p73j-c528). The fix is only
available in 13.0.0, which needs Python 3.11+, so an upper cap of ``<13`` or a
``requires-python`` of 3.10 silently keeps the vulnerable release installable.
These tests fail if either constraint creeps back.
"""

from __future__ import annotations

import tomllib
from pathlib import Path

import pytest
from packaging.requirements import Requirement
from packaging.specifiers import SpecifierSet
from packaging.version import Version

ROOT = Path(__file__).resolve().parent.parent
FIXED = Version("13.0.0")
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp", ".tif", ".tiff"}
SKIP_DIRS = {".venv", "venv", "node_modules", ".git", "__pycache__", "backup"}


def _walk(patterns: tuple[str, ...]) -> list[Path]:
    found: list[Path] = []
    for pattern in patterns:
        for path in ROOT.rglob(pattern):
            if not SKIP_DIRS.intersection(path.relative_to(ROOT).parts):
                found.append(path)
    return sorted(found)


def _pillow_requirements() -> list[tuple[Path, Requirement]]:
    """Every Pillow requirement declared in a requirements file or pyproject."""
    found: list[tuple[Path, Requirement]] = []
    for path in _walk(("requirements*.txt",)):
        for raw in path.read_text(encoding="utf-8").splitlines():
            line = raw.split("#", 1)[0].strip()
            if line and not line.startswith("-"):
                req = Requirement(line)
                if req.name.lower() == "pillow":
                    found.append((path, req))
    for path in _walk(("pyproject.toml",)):
        data = tomllib.loads(path.read_text(encoding="utf-8"))
        project = data.get("project", {})
        deps = list(project.get("dependencies", []))
        for extra in project.get("optional-dependencies", {}).values():
            deps.extend(extra)
        for dep in deps:
            req = Requirement(dep)
            if req.name.lower() == "pillow":
                found.append((path, req))
    return found


PILLOW_REQS = _pillow_requirements()


def _rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def _label(item: tuple[Path, Requirement]) -> str:
    return str(item[0].relative_to(ROOT))


def test_pillow_is_declared() -> None:
    """Pillow must stay a declared dependency so the pin below is enforced."""
    assert PILLOW_REQS, "Pillow is no longer declared anywhere in this repository"


@pytest.mark.parametrize("item", PILLOW_REQS, ids=_label)
def test_pillow_requirement_excludes_vulnerable_releases(
    item: tuple[Path, Requirement],
) -> None:
    """Each Pillow spec must allow 13.0.0 and reject every vulnerable release."""
    path, req = item
    spec: SpecifierSet = req.specifier
    assert spec.contains(FIXED), f"{path.name}: '{req}' does not allow Pillow 13.0.0"
    assert spec.contains("99.0.0"), (
        f"{path.name}: '{req}' caps Pillow; a cap is how the fix was kept out"
    )
    for vulnerable in ("12.3.0", "12.0.0", "11.0.0", "10.3.0"):
        assert not spec.contains(vulnerable), (
            f"{path.name}: '{req}' still allows vulnerable Pillow {vulnerable}"
        )


@pytest.mark.parametrize("path", _walk(("pyproject.toml",)), ids=_rel)
def test_python_floor_matches_pillow_13(path: Path) -> None:
    """Python 3.10 cannot install Pillow 13, so the floor must exclude it."""
    project = tomllib.loads(path.read_text(encoding="utf-8")).get("project", {})
    requires = project.get("requires-python")
    if requires is None:
        pytest.skip("no requires-python declared")
    assert not SpecifierSet(requires).contains("3.10"), (
        f"requires-python '{requires}' allows 3.10, where pip falls back to Pillow 12"
    )


def test_installed_pillow_is_fixed_release() -> None:
    """The Pillow in the test environment is the fixed release."""
    import PIL

    assert Version(PIL.__version__) >= FIXED, f"Pillow {PIL.__version__} is installed"


def _bundled_images() -> list[Path]:
    return [
        path
        for path in sorted(ROOT.rglob("*"))
        if path.suffix.lower() in IMAGE_SUFFIXES
        and path.is_file()
        and not SKIP_DIRS.intersection(path.relative_to(ROOT).parts)
    ]


@pytest.mark.parametrize("image_path", _bundled_images(), ids=_rel)
def test_bundled_images_decode_with_installed_pillow(image_path: Path) -> None:
    """Every bundled image still decodes under the installed Pillow."""
    from PIL import Image

    with Image.open(image_path) as image:
        image.load()
        assert image.width > 0
        assert image.height > 0
