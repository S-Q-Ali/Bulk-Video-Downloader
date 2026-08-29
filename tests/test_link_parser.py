"""Unit tests for LinkParserTool."""

from s_q_ali_media_downloader.agent.tools.link_parser import LinkParserTool


def test_extract_facebook_url():
    text = "Check out my Facebook page at https://www.facebook.com/speededitsfx/ and subscribe!"
    fb, ig, tk = LinkParserTool.extract_social_links(text)
    assert fb == "https://www.facebook.com/speededitsfx/"
    assert ig is None
    assert tk is None


def test_extract_instagram_url():
    text = "Follow my Instagram: https://instagram.com/speededitsdaily/"
    fb, ig, _tk = LinkParserTool.extract_social_links(text)
    assert fb is None
    assert ig == "https://www.instagram.com/speededitsdaily/"


def test_extract_both_social_links():
    text = (
        "Main Channel Bio\n"
        "Facebook: https://facebook.com/mycreatorpage/\n"
        "IG: https://www.instagram.com/creator_ig/"
    )
    fb, ig, _tk = LinkParserTool.extract_social_links(text)
    assert fb == "https://facebook.com/mycreatorpage/"
    assert ig == "https://www.instagram.com/creator_ig/"


def test_extract_handle_from_text():
    text = "Follow me on IG: @speed_edits_official for daily shorts!"
    _fb, ig, _tk = LinkParserTool.extract_social_links(text)
    assert ig == "https://www.instagram.com/speed_edits_official/"


def test_handle_from_url_helper():
    handle = LinkParserTool.extract_handle_from_url("https://www.facebook.com/pages/tech/123456")
    assert handle == "123456"


# ---------------------------------------------------------------------------
# Precision regression tests
# ---------------------------------------------------------------------------


def test_profile_php_query_param_preserved():
    """profile.php?id= links must keep their numeric id, not be query-stripped."""
    text = "FB: https://www.facebook.com/profile.php?id=100087654321&ref=x"
    fb, _ig, _tk = LinkParserTool.extract_social_links(text)
    assert fb == "https://www.facebook.com/profile.php?id=100087654321"
    assert LinkParserTool.extract_handle_from_url(fb) == "100087654321"


def test_word_boundary_prevents_config_match():
    """'config:' must not be read as an IG handle prefix."""
    text = "config: myname | here is my setup"
    _fb, ig, _tk = LinkParserTool.extract_social_links(text)
    assert ig is None


def test_group_link_never_shadows_vanity_page():
    """A groups/ link must lose to a vanity page link."""
    text = (
        "Join the group https://www.facebook.com/groups/somegroup/ "
        "or visit https://www.facebook.com/mycreatorpage/"
    )
    fb, _ig, _tk = LinkParserTool.extract_social_links(text)
    assert fb == "https://www.facebook.com/mycreatorpage/"


def test_excluded_ig_segments():
    text = "See https://www.instagram.com/explore/ for more"
    _fb, ig, _tk = LinkParserTool.extract_social_links(text)
    assert ig is None


def test_extract_tiktok_url():
    text = "My TikTok: https://www.tiktok.com/@speededits daily uploads!"
    fb, ig, tk = LinkParserTool.extract_social_links(text)
    assert tk == "https://www.tiktok.com/@speededits/"
    assert fb is None and ig is None


def test_extract_tiktok_text_handle():
    text = "tiktok: @daily_clips official"
    _fb, _ig, tk = LinkParserTool.extract_social_links(text)
    assert tk == "https://www.tiktok.com/@daily_clips/"


def test_tiktok_handle_extraction_strips_at():
    handle = LinkParserTool.extract_handle_from_url("https://www.tiktok.com/@creator_x/")
    assert handle == "creator_x"
