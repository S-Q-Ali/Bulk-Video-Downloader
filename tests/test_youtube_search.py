"""Unit tests for YouTubeSearchTool and YouTube channel URL normalization."""

from s_q_ali_media_downloader.agent.tools.youtube_search import YouTubeSearchTool
from s_q_ali_media_downloader.engine import is_youtube_channel_url, normalize_youtube_channel_url


def test_format_subs_helper():
    assert YouTubeSearchTool.format_subs(1820000) == "1.8M"
    assert YouTubeSearchTool.format_subs(64500) == "64.5K"
    assert YouTubeSearchTool.format_subs(450) == "450"


def test_youtube_search_initialization():
    tool_no_key = YouTubeSearchTool()
    assert tool_no_key.api_key is None

    tool_with_key = YouTubeSearchTool(api_key="  AIzaSyTESTKEY123  ")
    assert tool_with_key.api_key == "AIzaSyTESTKEY123"


def test_youtube_channel_shorthand_urls():
    shorthand_url = "https://youtube.com/UCisZ2efLJn1Dxvn4th6mwlA"
    assert is_youtube_channel_url(shorthand_url) is True

    normalized = normalize_youtube_channel_url(shorthand_url)
    assert normalized == "https://www.youtube.com/channel/UCisZ2efLJn1Dxvn4th6mwlA"


def test_youtube_channel_standard_urls():
    standard_url = "https://www.youtube.com/channel/UCisZ2efLJn1Dxvn4th6mwlA"
    assert is_youtube_channel_url(standard_url) is True
    assert normalize_youtube_channel_url(standard_url) == standard_url
