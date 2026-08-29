"""Unit tests for SocialVerifierTool using asyncio.run."""

import asyncio

from s_q_ali_media_downloader.agent.schema import SocialStatus
from s_q_ali_media_downloader.agent.tools.social_verifier import SocialVerifierTool


def test_social_verifier_none_input():
    verifier = SocialVerifierTool()

    async def _test():
        return await verifier.verify_channel_socials(candidate_fb=None, candidate_ig=None)

    fb, ig, tk = asyncio.run(_test())
    assert fb.status == SocialStatus.NOT_FOUND
    assert ig.status == SocialStatus.NOT_FOUND
    assert tk.status == SocialStatus.NOT_FOUND


def test_social_verifier_valid_format():
    verifier = SocialVerifierTool()

    async def _test():
        return await verifier.verify_facebook_presence(
            candidate_url="https://www.facebook.com/nonexistent_dummy_page_99999"
        )

    presence = asyncio.run(_test())
    assert presence.verified_url == "https://www.facebook.com/nonexistent_dummy_page_99999"


def test_bio_link_never_downgrades_to_not_found(monkeypatch):
    """A bio-sourced URL that hits a network failure must stay UNVERIFIED_HANDLE."""
    verifier = SocialVerifierTool(timeout=0.1)
    import httpx

    class FakeClient:
        def __init__(self, *a, **kw):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *a):
            return False

        async def get(self, *a, **kw):
            raise httpx.ConnectError("blocked")

    monkeypatch.setattr(httpx, "AsyncClient", FakeClient)

    async def _test():
        return await verifier.verify_instagram_presence(
            candidate_url="https://www.instagram.com/real_creator/"
        )

    presence = asyncio.run(_test())
    assert presence.status == SocialStatus.UNVERIFIED_HANDLE
    assert presence.confidence_score >= 0.5
    assert presence.source == "bio_link"


def test_handle_guess_network_failure_is_inconclusive(monkeypatch):
    """A guessed handle that hits a network failure must NOT be NOT_FOUND."""
    verifier = SocialVerifierTool(timeout=0.1)
    import httpx

    class FakeClient:
        def __init__(self, *a, **kw):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *a):
            return False

        async def get(self, *a, **kw):
            raise httpx.ConnectError("blocked")

    monkeypatch.setattr(httpx, "AsyncClient", FakeClient)

    async def _test():
        return await verifier.verify_facebook_presence(
            candidate_url=None, channel_handle="@somebody"
        )

    presence = asyncio.run(_test())
    assert presence.status == SocialStatus.INCONCLUSIVE
    assert presence.source == "handle_guess"
