"""Tool for extracting Facebook and Instagram URLs and handles from text/URLs."""

import re
from typing import ClassVar


class LinkParserTool:
    """Extracts Facebook and Instagram URLs and handles from channel metadata, descriptions, and link lists."""

    # FB Regex patterns
    FB_URL_PATTERN = re.compile(
        r"https?://(?:www\.|m\.|mobile\.)?(?:facebook\.com|fb\.com|fb\.watch)/(?:pages/[^/\s]+/\d+|groups/[^/\s]+|people/[^/\s]+/\d+|[A-Za-z0-9\._\-]+)/?",
        re.IGNORECASE,
    )
    FB_HANDLE_PATTERN = re.compile(
        r"(?:facebook|fb)\.com/([A-Za-z0-9\._\-]+)",
        re.IGNORECASE,
    )

    # IG Regex patterns
    IG_URL_PATTERN = re.compile(
        r"https?://(?:www\.)?(?:instagram\.com|instagr\.am)/([A-Za-z0-9\._\-]+)/?",
        re.IGNORECASE,
    )
    IG_TEXT_HANDLE_PATTERN = re.compile(
        r"(?:ig|instagram|insta)[:\s]*@?([A-Za-z0-9\._\-]{3,30})",
        re.IGNORECASE,
    )

    # Excluded common non-profile path segments for Facebook and Instagram
    EXCLUDED_SEGMENTS: ClassVar[set[str]] = {
        "sharer",
        "share",
        "dialog",
        "intent",
        "p",
        "reel",
        "reels",
        "stories",
        "explore",
        "direct",
        "tv",
        "developer",
        "legal",
        "about",
        "privacy",
        "help",
        "terms",
    }

    @classmethod
    def extract_social_links(
        r, text: str, links: list[str] | None = None
    ) -> tuple[str | None, str | None]:
        """Extracts primary (facebook_url, instagram_url) pair from raw text and link lists."""
        fb_url = None
        ig_url = None

        all_input = text + " " + " ".join(links or [])

        # 1. Check explicit URLs
        fb_matches = r.FB_URL_PATTERN.findall(all_input)
        for match in fb_matches:
            clean_url = r._clean_url(match)
            if clean_url and r._is_valid_fb_url(clean_url):
                fb_url = clean_url
                break

        ig_matches = r.IG_URL_PATTERN.findall(all_input)
        for match in ig_matches:
            # Match is either full URL or group 1 handle depending on regex search vs findall
            full_match = match if isinstance(match, str) else match[0]
            handle = full_match.strip("/").split("/")[-1]
            if handle.lower() not in r.EXCLUDED_SEGMENTS and len(handle) >= 3:
                ig_url = f"https://www.instagram.com/{handle}/"
                break

        # 2. Text handle fallback for IG (e.g. "Follow on IG: @myhandle")
        if not ig_url:
            ig_text_match = r.IG_TEXT_HANDLE_PATTERN.search(text)
            if ig_text_match:
                handle = ig_text_match.group(1).strip()
                if handle.lower() not in r.EXCLUDED_SEGMENTS and len(handle) >= 3:
                    ig_url = f"https://www.instagram.com/{handle}/"

        return fb_url, ig_url

    @classmethod
    def extract_handle_from_url(r, url: str) -> str | None:
        """Extracts handle string from a FB/IG URL."""
        if not url:
            return None
        clean = url.rstrip("/")
        parts = clean.split("/")
        if parts:
            last = parts[-1]
            if "?" in last:
                last = last.split("?")[0]
            if last.lower() not in r.EXCLUDED_SEGMENTS and len(last) >= 2:
                return last
        return None

    @classmethod
    def _clean_url(r, url: str) -> str:
        """Strips query params and trailing slashes."""
        url = url.strip()
        if "?" in url:
            url = url.split("?")[0]
        if not url.endswith("/"):
            url += "/"
        return url

    @classmethod
    def _is_valid_fb_url(r, url: str) -> bool:
        handle = r.extract_handle_from_url(url)
        if not handle:
            return False
        return handle.lower() not in r.EXCLUDED_SEGMENTS and len(handle) >= 3
