"""Data schemas for YouTube Discovery and Social Presence Agent."""

from enum import Enum

from pydantic import BaseModel, Field


class SocialPlatform(str, Enum):
    FACEBOOK = "facebook"
    INSTAGRAM = "instagram"


class SocialStatus(str, Enum):
    VERIFIED = "verified"
    NOT_FOUND = "not_found"
    UNVERIFIED_HANDLE = "unverified_handle"


class SocialPresence(BaseModel):
    platform: SocialPlatform
    status: SocialStatus = SocialStatus.NOT_FOUND
    verified_url: str | None = None
    handle: str | None = None
    confidence_score: float = Field(default=0.0, ge=0.0, le=1.0)


class ChannelMetadata(BaseModel):
    channel_id: str
    title: str
    handle: str | None = None
    subscribers: int = 0
    subscribers_formatted: str = "0"
    youtube_url: str
    avatar_url: str | None = None
    description: str = ""
    banner_links: list[str] = Field(default_factory=list)
    facebook: SocialPresence = Field(
        default_factory=lambda: SocialPresence(platform=SocialPlatform.FACEBOOK)
    )
    instagram: SocialPresence = Field(
        default_factory=lambda: SocialPresence(platform=SocialPlatform.INSTAGRAM)
    )
    latest_video_url: str | None = None
    has_no_socials: bool = False
    opportunity_flag: str = "PROSPECT"


class AgentSearchResult(BaseModel):
    query: str
    total_searched: int = 0
    channels_matching_filter: int = 0
    execution_time_seconds: float = 0.0
    timestamp: str = ""
    channels: list[ChannelMetadata] = Field(default_factory=list)
