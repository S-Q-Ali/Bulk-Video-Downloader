"""TikTok Creator Discovery Engine (yt-dlp flat extraction + HTML fallback, zero keys).

Two-tier strategy:
1. yt-dlp flat extraction of the TikTok search page (benefits from the same
   curl_cffi impersonation pin that powers the app's TikTok downloads).
2. HTTPX scrape of the search page HTML, harvesting "uniqueId" fields from the
   embedded SIGI_STATE / __UNIVERSAL_DATA JSON blobs.
"""

import logging
import re

import yt_dlp

from s_q_ali_media_downloader.agent.schema import TikTokProfileMetadata

logger = logging.getLogger(__name__)

SEARCH_URL = "https://www.tiktok.com/search?q={query}"
PROFILE_URL = "https://www.tiktok.com/@{handle}"

# Handles harvested from embedded JSON (works even without yt-dlp).
UNIQUE_ID_PATTERN = re.compile(r'"uniqueId"\s*:\s*"([A-Za-z0-9\._]{2,30})"')
AT_HANDLE_PATTERN = re.compile(r'tiktok\.com/@([A-Za-z0-9\._]{2,30})/')

# Non-profile handles that appear in embedded payloads.
EXCLUDED_HANDLES = {
    "tiktok",
    "foryou",
    "following",
    "explore",
    "live",
    "upload",
    "login",
    "signup",
    "discover",
}


def format_followers(count: int) -> str:
    if count >= 1_000_000:
        return f"{count / 1_000_000:.1f}M"
    if count >= 1_000:
        return f"{count / 1_000:.1f}K"
    return str(count)


class TikTokSearchTool:
    """Discovers TikTok creator profiles by niche keyword, tag, or name."""

    def __init__(self, timeout: float = 20.0):
        self.timeout = timeout

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def search_profiles(
        self, query: str, max_profiles: int = 50
    ) -> list[TikTokProfileMetadata]:
        """Entry point: yt-dlp first, HTML harvest fallback."""
        handles = self._discover_via_ytdlp(query)
        if not handles:
            logger.info("yt-dlp TikTok search empty; trying HTML harvest fallback...")
            handles = self._discover_via_html(query)

        # Dedupe, filter, cap
        seen: set[str] = set()
        profiles: list[TikTokProfileMetadata] = []
        for handle in handles:
            handle = handle.strip(".").lower()
            if handle in seen or handle in EXCLUDED_HANDLES or len(handle) < 2:
                continue
            seen.add(handle)
            profiles.append(
                TikTokProfileMetadata(
                    profile_id=handle,
                    handle=handle,
                    profile_url=PROFILE_URL.format(handle=handle),
                )
            )
            if len(profiles) >= max_profiles:
                break

        # Enrich each profile with bio / follower data (best effort)
        for idx, profile in enumerate(profiles):
            try:
                self.enrich_profile(profile)
            except Exception as e:
                logger.warning(f"TikTok profile enrichment failed for @{profile.handle}: {e}")

        return profiles

    # ------------------------------------------------------------------
    # Tier 1: yt-dlp
    # ------------------------------------------------------------------
    def _discover_via_ytdlp(self, query: str) -> list[str]:
        """Flat-extracts the TikTok search page, collecting uploader handles."""
        handles: list[str] = []
        ydl_opts = {
            "extract_flat": True,
            "skip_download": True,
            "quiet": True,
            "no_warnings": True,
            "ignoreerrors": True,
            "socket_timeout": self.timeout,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(SEARCH_URL.format(query=query), download=False)
            except Exception as e:
                logger.warning(f"yt-dlp TikTok search failed: {e}")
                return handles

            entries = (info or {}).get("entries") or []
            for entry in entries:
                if not isinstance(entry, dict):
                    continue
                handle = self._handle_from_entry(entry)
                if handle:
                    handles.append(handle)

        return handles

    @staticmethod
    def _handle_from_entry(entry: dict) -> str | None:
        """Pulls the creator handle out of a flat TikTok video entry."""
        url = str(entry.get("webpage_url") or entry.get("url") or "")
        match = re.search(r"tiktok\.com/@([A-Za-z0-9\._]{2,30})", url)
        if match:
            return match.group(1)

        uploader = str(entry.get("uploader") or entry.get("creator") or "")
        uploader = uploader.lstrip("@").replace(" ", "")
        if re.fullmatch(r"[A-Za-z0-9\._]{2,30}", uploader):
            return uploader
        return None

    # ------------------------------------------------------------------
    # Tier 2: HTML harvest
    # ------------------------------------------------------------------
    def _discover_via_html(self, query: str) -> list[str]:
        """Scrapes uniqueId / @handle tokens from the search page HTML."""
        import httpx

        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
            ),
            "Accept-Language": "en-US,en;q=0.9",
        }
        try:
            with httpx.Client(
                timeout=self.timeout, follow_redirects=True, headers=headers
            ) as client:
                resp = client.get(SEARCH_URL.format(query=query))
                if resp.status_code != 200:
                    return []
                html = resp.text
        except Exception as e:
            logger.warning(f"TikTok HTML harvest failed: {e}")
            return []

        handles = UNIQUE_ID_PATTERN.findall(html)
        handles += AT_HANDLE_PATTERN.findall(html)
        return handles

    # ------------------------------------------------------------------
    # Profile enrichment
    # ------------------------------------------------------------------
    def enrich_profile(self, profile: TikTokProfileMetadata) -> TikTokProfileMetadata:
        """Best-effort enrichment of bio, follower count, and video count."""
        ydl_opts = {
            "skip_download": True,
            "quiet": True,
            "no_warnings": True,
            "ignoreerrors": True,
            "socket_timeout": self.timeout,
            "playlist_items": "1-5",
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(profile.profile_url, download=False)
        if not info or not isinstance(info, dict):
            return profile

        profile.nickname = info.get("uploader") or info.get("channel") or profile.nickname
        bio = info.get("description") or ""
        if bio:
            profile.bio = str(bio)[:500]
        count = info.get("channel_follower_count")
        if isinstance(count, int):
            profile.followers = count
            profile.followers_formatted = format_followers(count)
        entries = info.get("entries") or []
        if entries:
            profile.video_count = max(profile.video_count, len(entries))
        return profile