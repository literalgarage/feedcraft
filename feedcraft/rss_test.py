import pathlib
import typing as t

import pytest

from .rss import parse_rss

TEST_DIR = pathlib.Path(__file__).parent.parent / "testdata" / "feeds"


def test_pass():
    assert True


def _is_feed_any_rss(feed: str) -> bool:
    return "<rss" in feed


def _iter_all_test_feed_paths() -> t.Iterator[pathlib.Path]:
    for file_path in TEST_DIR.glob("*.xml"):
        yield file_path


def _iter_rss_test_feed_ids() -> t.Iterator[str]:
    for file_path in _iter_all_test_feed_paths():
        with open(file_path, "r", encoding="utf-8") as f:
            feed_content = f.read()
            if _is_feed_any_rss(feed_content):
                yield file_path.stem


@pytest.mark.parametrize("feed_id", _iter_rss_test_feed_ids())
def test_rss_20_feeds_parsing(feed_id: str):
    with open(TEST_DIR / f"{feed_id}.xml", "r", encoding="utf-8") as f:
        feed_content = f.read()
    feed = parse_rss(feed_content)
    assert feed is not None, f"Failed to parse RSS 2.0 feed: {feed_id}"
