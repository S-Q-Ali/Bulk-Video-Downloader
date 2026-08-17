"""Unit tests for LinkParserTool."""

from s_q_ali_media_downloader.agent.tools.link_parser import LinkParserTool


def test_extract_facebook_url():
    text = "Check out my Facebook page at https://www.facebook.com/speededitsfx/ and subscribe!"
    fb, ig = LinkParserTool.extract_social_links(text)
    assert fb == "https://www.facebook.com/speededitsfx/"
    assert ig is None


def test_extract_instagram_url():
    text = "Follow my Instagram: https://instagram.com/speededitsdaily/"
    fb, ig = LinkParserTool.extract_social_links(text)
    assert fb is None
    assert ig == "https://www.instagram.com/speededitsdaily/"


def test_extract_both_social_links():
    text = (
        "Main Channel Bio\n"
        "Facebook: https://facebook.com/mycreatorpage/\n"
        "IG: https://www.instagram.com/creator_ig/"
    )
    fb, ig = LinkParserTool.extract_social_links(text)
    assert fb == "https://facebook.com/mycreatorpage/"
    assert ig == "https://www.instagram.com/creator_ig/"


def test_extract_handle_from_text():
    text = "Follow me on IG: @speed_edits_official for daily shorts!"
    _fb, ig = LinkParserTool.extract_social_links(text)
    assert ig == "https://www.instagram.com/speed_edits_official/"


def test_handle_from_url_helper():
    handle = LinkParserTool.extract_handle_from_url("https://www.facebook.com/pages/tech/123456")
    assert handle == "123456"
