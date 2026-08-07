# Changelog

All notable changes are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [2.0.0] — 2026-08-06

### Added
- Open source release under the MIT license; activation keys removed entirely.
- Rebranded to **Q-S-Ali Media Downloader** with a new icon and dark cyan theme.
- YouTube support alongside TikTok — playlists and channels expand into
  individual videos automatically in the background.
- Per-platform download options (TikTok uses Chrome impersonation; YouTube
  uses native format selection).
- Audio-only preset (MP3) via bundled ffmpeg.
- Per-user Inno Setup installer (no admin required) that bundles ffmpeg.

### Changed
- Source reorganized into a proper `src/qsali_media_downloader` package.
- Added pytest suite, ruff linting, and a GitHub Actions CI pipeline.

### Fixed
- Impersonation failure label now shows the underlying error instead of a
  literal `{exc}` placeholder.

### Removed
- Legacy activation gate and ANAS license keys (kept in git history only).
- Old `Anas Media Downloader` branding and orphaned artifacts.
