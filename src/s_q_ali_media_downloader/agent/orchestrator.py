"""Agent Orchestrator controller for YouTube discovery and cross-platform social verification."""

import asyncio
import logging
import time
from collections.abc import Callable
from datetime import datetime, timezone

from s_q_ali_media_downloader.agent.schema import (
    AgentSearchResult,
    ChannelMetadata,
    SocialStatus,
)
from s_q_ali_media_downloader.agent.tools.metadata_extractor import MetadataExtractorTool
from s_q_ali_media_downloader.agent.tools.social_verifier import SocialVerifierTool
from s_q_ali_media_downloader.agent.tools.youtube_search import YouTubeSearchTool

logger = logging.getLogger(__name__)


class AgentOrchestrator:
    """Orchestrates multi-tool execution DAG for channel discovery & social presence verification."""

    def __init__(
        self,
        api_key: str | None = None,
        progress_callback: Callable[[int, str], None] | None = None,
    ):
        self.search_tool = YouTubeSearchTool(api_key=api_key)
        self.extractor_tool = MetadataExtractorTool()
        self.verifier_tool = SocialVerifierTool()
        self.progress_callback = progress_callback

    def _emit(self, percent: int, message: str) -> None:
        if self.progress_callback:
            try:
                self.progress_callback(percent, message)
            except Exception as e:
                logger.warning(f"Progress callback error: {e}")

    def run_discovery(
        self,
        query: str,
        max_channels: int = 50,
        min_subscribers: int = 0,
        check_facebook: bool = True,
        check_instagram: bool = True,
        only_no_socials: bool = False,
    ) -> AgentSearchResult:
        """Executes full autonomous agent pipeline."""
        start_time = time.time()
        self._emit(5, f"Initializing Agent... Searching YouTube for '{query}'...")

        # 1. YouTube Discovery
        raw_channels = self.search_tool.search_channels(
            query=query, max_results=max_channels, min_subscribers=min_subscribers
        )
        total_found = len(raw_channels)
        self._emit(25, f"Found {total_found} candidate channels. Extracting metadata...")

        if not raw_channels:
            self._emit(100, "Discovery complete. 0 channels found.")
            return AgentSearchResult(
                query=query,
                total_searched=0,
                channels_matching_filter=0,
                execution_time_seconds=round(time.time() - start_time, 2),
                timestamp=datetime.now(timezone.utc).isoformat(),
                channels=[],
            )

        # 2. Enrich channel metadata
        enriched_channels: list[ChannelMetadata] = []
        for idx, ch in enumerate(raw_channels):
            percent = 25 + int((idx / max(total_found, 1)) * 30)
            self._emit(percent, f"Parsing metadata for {ch.title} ({idx+1}/{total_found})...")
            enriched = self.extractor_tool.enrich_channel_metadata(ch)
            enriched_channels.append(enriched)

        # 3. Social Presence Verification
        self._emit(60, "Verifying Facebook & Instagram presences...")
        verified_channels = asyncio.run(
            self._verify_all_socials(
                enriched_channels, check_facebook, check_instagram
            )
        )

        # 4. Filter & Flag Opportunities
        final_channels: list[ChannelMetadata] = []
        no_socials_count = 0

        for ch in verified_channels:
            no_fb = ch.facebook.status == SocialStatus.NOT_FOUND
            no_ig = ch.instagram.status == SocialStatus.NOT_FOUND

            ch.has_no_socials = no_fb and no_ig
            if ch.has_no_socials:
                no_socials_count += 1
                ch.opportunity_flag = "TARGET_NO_SOCIALS"
            elif no_fb or no_ig:
                ch.opportunity_flag = "PARTIAL_SOCIALS"
            else:
                ch.opportunity_flag = "FULL_SOCIALS"

            if only_no_socials:
                if ch.has_no_socials:
                    final_channels.append(ch)
            else:
                final_channels.append(ch)

        elapsed = round(time.time() - start_time, 2)
        self._emit(
            100,
            f"Agent completed in {elapsed}s. {len(final_channels)} channels displayed ({no_socials_count} missing FB/IG).",
        )

        return AgentSearchResult(
            query=query,
            total_searched=total_found,
            channels_matching_filter=len(final_channels),
            execution_time_seconds=elapsed,
            timestamp=datetime.now(timezone.utc).isoformat(),
            channels=final_channels,
        )

    async def _verify_all_socials(
        self,
        channels: list[ChannelMetadata],
        check_facebook: bool,
        check_instagram: bool,
    ) -> list[ChannelMetadata]:
        """Runs async verification probes for list of channels."""
        total = len(channels)
        for idx, ch in enumerate(channels):
            percent = 60 + int((idx / max(total, 1)) * 35)
            self._emit(
                percent,
                f"Probing FB & IG for @{ch.handle or ch.title} ({idx+1}/{total})...",
            )

            candidate_fb = ch.facebook.verified_url if check_facebook else None
            candidate_ig = ch.instagram.verified_url if check_instagram else None

            fb_pres, ig_pres = await self.verifier_tool.verify_channel_socials(
                candidate_fb=candidate_fb,
                candidate_ig=candidate_ig,
                channel_handle=ch.handle,
            )

            if check_facebook:
                ch.facebook = fb_pres
            if check_instagram:
                ch.instagram = ig_pres

            # Pacing delay to prevent IP rate-limiting
            await asyncio.sleep(0.5)

        return channels
