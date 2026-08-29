"""Unit tests for the TikTok discovery pipeline (offline, faked responses)."""

from s_q_ali_media_downloader.agent.schema import SocialStatus, TikTokProfileMetadata
from s_q_ali_media_downloader.agent.tools.tiktok_search import (
    TikTokSearchTool,
    format_followers,
)
from s_q_ali_media_downloader.agent.tools.youtube_existence import (
    YouTubeExistenceTool,
    name_similarity,
)

# ---------------------------------------------------------------------------
# TikTokSearchTool
# ---------------------------------------------------------------------------


def test_format_followers():
    assert format_followers(1_500_000) == "1.5M"
    assert format_followers(24_000) == "24.0K"
    assert format_followers(733) == "733"


def test_handle_from_entry_url():
    entry = {"webpage_url": "https://www.tiktok.com/@clip_machine/video/73123"}
    assert TikTokSearchTool._handle_from_entry(entry) == "clip_machine"


def test_handle_from_entry_uploader():
    entry = {"uploader": "@daily_edits"}
    assert TikTokSearchTool._handle_from_entry(entry) == "daily_edits"


def test_handle_from_entry_garbage_uploader():
    entry = {"uploader": "Some Creator Name!"}
    assert TikTokSearchTool._handle_from_entry(entry) is None


def test_search_profiles_dedupes_and_excludes():
    tool = TikTokSearchTool()
    handles = ["creator_a", "creator_a", "tiktok", "creator_b", "x", "creator_c"]
    # Fake both discovery tiers to return the same handle list.
    tool._discover_via_ytdlp = lambda query: list(handles)
    profiles = tool.search_profiles("query", max_profiles=50)
    names = [p.handle for p in profiles]
    assert names.count("creator_a") == 1
    assert "tiktok" not in names
    assert "x" not in names  # too short
    assert all(p.profile_url.startswith("https://www.tiktok.com/@") for p in profiles)


# ---------------------------------------------------------------------------
# name_similarity
# ---------------------------------------------------------------------------


def test_name_similarity_exact():
    assert name_similarity("speed edits", "SpeedEdits") == 1.0


def test_name_similarity_token_overlap():
    assert name_similarity("speed_edits", "Speed Edits Official") >= 0.8


def test_name_similarity_disjoint():
    assert name_similarity("cooking_stuff", "car_reviews") < 0.5


# ---------------------------------------------------------------------------
# YouTubeExistenceTool — bio link path (no network needed)
# ---------------------------------------------------------------------------


def _profile(bio: str) -> TikTokProfileMetadata:
    return TikTokProfileMetadata(
        profile_id="tester",
        handle="tester",
        nickname="Tester",
        bio=bio,
        profile_url="https://www.tiktok.com/@tester/",
    )


def test_youtube_bio_link_is_verified():
    tool = YouTubeExistenceTool()
    presence = tool.check_youtube_presence(
        _profile("daily edits! youtube.com/@testerclips check it")
    )
    assert presence.status == SocialStatus.VERIFIED
    assert presence.source == "bio_link"
    assert presence.confidence_score == 0.95
    assert presence.verified_url is not None


def test_no_bio_link_and_no_candidates_is_not_found(monkeypatch):
    tool = YouTubeExistenceTool()
    monkeypatch.setattr(
        tool.search_tool,
        "search_channels",
        lambda query, max_results=10, min_subscribers=0: [],
    )
    presence = tool.check_youtube_presence(_profile("just vibing, no links"))
    assert presence.status == SocialStatus.NOT_FOUND


def test_weak_name_match_is_not_found(monkeypatch):
    from s_q_ali_media_downloader.agent.schema import ChannelMetadata

    tool = YouTubeExistenceTool()
    far_channel = ChannelMetadata(
        channel_id="UC1",
        title="Completely Different Channel",
        youtube_url="https://www.youtube.com/channel/UC1",
    )
    monkeypatch.setattr(
        tool.search_tool,
        "search_channels",
        lambda query, max_results=10, min_subscribers=0: [far_channel],
    )
    presence = tool.check_youtube_presence(_profile("no links here"))
    assert presence.status == SocialStatus.NOT_FOUND


def test_strong_name_match_flags_unverified(monkeypatch):
    from s_q_ali_media_downloader.agent.schema import ChannelMetadata

    tool = YouTubeExistenceTool()
    near_channel = ChannelMetadata(
        channel_id="UC2",
        title="Tester",
        handle="@tester",
        youtube_url="https://www.youtube.com/channel/UC2",
    )
    monkeypatch.setattr(
        tool.search_tool,
        "search_channels",
        lambda query, max_results=10, min_subscribers=0: [near_channel],
    )
    monkeypatch.setattr(
        YouTubeExistenceTool, "_channel_links_to_tiktok", lambda self, url, handle: False
    )
    presence = tool.check_youtube_presence(_profile("no links in bio"))
    assert presence.status == SocialStatus.UNVERIFIED_HANDLE
    assert presence.source == "name_match"


def test_bidirectional_backlink_confirms_verified(monkeypatch):
    from s_q_ali_media_downloader.agent.schema import ChannelMetadata

    tool = YouTubeExistenceTool()
    near_channel = ChannelMetadata(
        channel_id="UC3",
        title="Tester Clips",
        handle="@tester",
        youtube_url="https://www.youtube.com/channel/UC3",
    )
    monkeypatch.setattr(
        tool.search_tool,
        "search_channels",
        lambda query, max_results=10, min_subscribers=0: [near_channel],
    )
    monkeypatch.setattr(
        YouTubeExistenceTool, "_channel_links_to_tiktok", lambda self, url, handle: True
    )
    presence = tool.check_youtube_presence(_profile("bio without youtube link"))
    assert presence.status == SocialStatus.VERIFIED
    assert presence.confidence_score == 0.90