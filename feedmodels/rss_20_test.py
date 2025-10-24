import pathlib
import typing as t

import pytest

from .rss_20 import parse_rss


def test_pass():
    assert True


def _is_feed_rss_20(feed: str):
    return "<rss" in feed and 'version="2.0"' in feed


def _enumerate_all_test_feeds() -> t.Iterator[pathlib.Path]:
    test_dir = pathlib.Path(__file__).parent.parent / "testdata" / "feeds"
    for file_path in test_dir.glob("*.xml"):
        yield file_path


def _iter_rss_20_test_feeds() -> t.Iterator[t.Tuple[pathlib.Path, str]]:
    for file_path in _enumerate_all_test_feeds():
        with open(file_path, "r", encoding="utf-8") as f:
            feed_content = f.read()
            if _is_feed_rss_20(feed_content):
                yield file_path, feed_content


@pytest.mark.parametrize("file_path,feed_content", _iter_rss_20_test_feeds())
def test_rss_20_feeds_parsing(file_path: pathlib.Path, feed_content: str):
    feed = parse_rss(feed_content)
    assert feed is not None, f"Failed to parse RSS 2.0 feed: {file_path}"
