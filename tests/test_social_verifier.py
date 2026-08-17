"""Unit tests for SocialVerifierTool using asyncio.run."""

import asyncio

from s_q_ali_media_downloader.agent.schema import SocialStatus
from s_q_ali_media_downloader.agent.tools.social_verifier import SocialVerifierTool


def test_social_verifier_none_input():
    verifier = SocialVerifierTool()

    async def _test():
        return await verifier.verify_channel_socials(candidate_fb=None, candidate_ig=None)

    fb, ig = asyncio.run(_test())
    assert fb.status == SocialStatus.NOT_FOUND
    assert ig.status == SocialStatus.NOT_FOUND


def test_social_verifier_valid_format():
    verifier = SocialVerifierTool()

    async def _test():
        return await verifier.verify_facebook_presence(
            candidate_url="https://www.facebook.com/nonexistent_dummy_page_99999"
        )

    presence = asyncio.run(_test())
    assert presence.verified_url == "https://www.facebook.com/nonexistent_dummy_page_99999"
