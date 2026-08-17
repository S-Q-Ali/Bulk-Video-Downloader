"""Asynchronous Verification Engine for Facebook and Instagram Page/Profile Existence."""

import asyncio
import logging

import httpx

from s_q_ali_media_downloader.agent.schema import (
    SocialPlatform,
    SocialPresence,
    SocialStatus,
)

logger = logging.getLogger(__name__)

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

FB_NOT_FOUND_SIGNATURES = [
    "this page isn't available",
    "the link you followed may be broken",
    "page not found",
    "content not found",
    "this content isn't available right now",
    "login/?next=",
]

IG_NOT_FOUND_SIGNATURES = [
    "sorry, this page isn't available",
    "the link you followed may be broken",
    "page not found",
    "user not found",
]


class SocialVerifierTool:
    """Probes Facebook and Instagram profile existence asynchronously."""

    def __init__(self, delay_between_requests: float = 2.0, timeout: float = 10.0):
        self.delay = delay_between_requests
        self.timeout = timeout

    async def verify_facebook_presence(
        self, candidate_url: str | None, channel_handle: str | None = None
    ) -> SocialPresence:
        """Verifies if a Facebook page exists."""
        presence = SocialPresence(platform=SocialPlatform.FACEBOOK)

        target_url = candidate_url
        is_fallback_handle = False

        if not target_url and channel_handle:
            clean_handle = channel_handle.lstrip("@")
            target_url = f"https://www.facebook.com/{clean_handle}/"
            is_fallback_handle = True

        if not target_url:
            return presence

        presence.verified_url = target_url
        presence.handle = target_url.rstrip("/").split("/")[-1]

        try:
            async with httpx.AsyncClient(
                follow_redirects=True, timeout=self.timeout, headers=DEFAULT_HEADERS
            ) as client:
                response = await client.get(target_url)
                body = response.text.lower()

                if response.status_code == 200:
                    # Check for "Page not found" DOM signature
                    if any(sig in body for sig in FB_NOT_FOUND_SIGNATURES):
                        presence.status = SocialStatus.NOT_FOUND
                        presence.confidence_score = 0.0
                    else:
                        presence.status = (
                            SocialStatus.VERIFIED
                            if not is_fallback_handle
                            else SocialStatus.UNVERIFIED_HANDLE
                        )
                        presence.confidence_score = 0.95 if not is_fallback_handle else 0.60
                else:
                    presence.status = SocialStatus.NOT_FOUND
                    presence.confidence_score = 0.0
        except Exception as e:
            logger.warning(f"FB probe failed for {target_url}: {e}")
            presence.status = SocialStatus.NOT_FOUND
            presence.confidence_score = 0.0

        return presence

    async def verify_instagram_presence(
        self, candidate_url: str | None, channel_handle: str | None = None
    ) -> SocialPresence:
        """Verifies if an Instagram profile exists."""
        presence = SocialPresence(platform=SocialPlatform.INSTAGRAM)

        target_url = candidate_url
        is_fallback_handle = False

        if not target_url and channel_handle:
            clean_handle = channel_handle.lstrip("@")
            target_url = f"https://www.instagram.com/{clean_handle}/"
            is_fallback_handle = True

        if not target_url:
            return presence

        presence.verified_url = target_url
        presence.handle = target_url.rstrip("/").split("/")[-1]

        try:
            async with httpx.AsyncClient(
                follow_redirects=True, timeout=self.timeout, headers=DEFAULT_HEADERS
            ) as client:
                response = await client.get(target_url)
                body = response.text.lower()

                if response.status_code == 200:
                    if any(sig in body for sig in IG_NOT_FOUND_SIGNATURES):
                        presence.status = SocialStatus.NOT_FOUND
                        presence.confidence_score = 0.0
                    else:
                        presence.status = (
                            SocialStatus.VERIFIED
                            if not is_fallback_handle
                            else SocialStatus.UNVERIFIED_HANDLE
                        )
                        presence.confidence_score = 0.95 if not is_fallback_handle else 0.60
                elif response.status_code == 404:
                    presence.status = SocialStatus.NOT_FOUND
                    presence.confidence_score = 0.0
                else:
                    # Try oEmbed verification fallback if redirected to login
                    oembed_status = await self._verify_instagram_oembed(client, target_url)
                    if oembed_status:
                        presence.status = SocialStatus.VERIFIED
                        presence.confidence_score = 0.90
                    else:
                        presence.status = SocialStatus.NOT_FOUND
                        presence.confidence_score = 0.0
        except Exception as e:
            logger.warning(f"IG probe failed for {target_url}: {e}")
            presence.status = SocialStatus.NOT_FOUND
            presence.confidence_score = 0.0

        return presence

    async def _verify_instagram_oembed(self, client: httpx.AsyncClient, url: str) -> bool:
        """Fallback check using Instagram oEmbed endpoint."""
        try:
            oembed_url = f"https://api.instagram.com/oembed?url={url}"
            resp = await client.get(oembed_url)
            return resp.status_code == 200
        except Exception:
            return False

    async def verify_channel_socials(
        self,
        candidate_fb: str | None,
        candidate_ig: str | None,
        channel_handle: str | None = None,
    ) -> tuple[SocialPresence, SocialPresence]:
        """Probes both Facebook and Instagram in parallel."""
        fb_task = self.verify_facebook_presence(candidate_fb, channel_handle)
        ig_task = self.verify_instagram_presence(candidate_ig, channel_handle)

        fb_res, ig_res = await asyncio.gather(fb_task, ig_task)
        return fb_res, ig_res
