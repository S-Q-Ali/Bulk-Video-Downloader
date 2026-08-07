# Q-S-Ali Media Downloader — Session Notes & Resume File

> Purpose: if the coding session is compacted, read this file to get back on
> track. It records the full project state, environment, decisions, verified
> facts, and next steps. Last updated: 2026-08-06.

## 1. Project at a glance

- **App:** Q-S-Ali Media Downloader (formerly *Anas Media Downloader*)
- **Version:** 2.0.0 — full rebrand + open source + YouTube support
- **What it does:** bulk-download TikTok and YouTube videos to a local folder.
  Queue-based GUI with a worker pool, inline retries, pacing delays, extra
  "passes", quality presets, TikTok account fetching, and automatic expansion
  of YouTube playlists/channels into video URLs.
- **Stack:** Python 3.14 + PySide6 GUI, yt-dlp engine, curl_cffi for TikTok
  browser impersonation. Built as a PyInstaller **onedir** app (no console).
- **Repo:** https://github.com/S-Q-Ali/Bulk-Video-Downloader (public, empty,
  pushed 2026-08-06). Branch `master`.
- **Open source:** the old activation/license gate is fully removed — no key
  prompt. `licensing.py` remains in `source/` only as source history; it is
  NOT imported or bundled.

## 2. Current status (DONE)

- Rebrand to Q-S-Ali complete and verified (no `Anas`/`ANAS`/`siddique`
  strings left in app source).
- Activation gate removed (`ActivationDialog`, `ensure_activated`, the
  `from licensing import ...` line, and the `ensure_activated` call in
  `main()` are all gone).
- Footer socials: only **GitHub** (`https://github.com/S-Q-Ali`) and
  **LinkedIn** (`https://linkedin.com/in/s-qasim-ali`).
- Theme recolored: dark ink-plum base, cyan accent `#22D3EE`,
  `accent_hi #67E8F9`, rail stripe cyan→teal gradient.
- New `icon.ico` generated (cyan→teal rounded square + navy download arrow;
  deliberately font-free — Qt text drawing crashes this offscreen build).
- YouTube bulk download implemented and verified (playlists/channels
  auto-expand in a background thread; `YOUTUBE`/`TIKTOK` card badges;
  per-platform download opts).
- EXE rebuilt as onedir/windowed and deployed; remote confirmed in sync.

## 3. Environment (exact, verified 2026-08-06)

- Workspace: `E:\Web App\Anas Media Downloader` (Windows, PowerShell 5.1)
- App venv (the working verification env): `E:\Web App\Anas Media Downloader\source\venv`
  - Python **3.14.6**
  - PySide6 **6.11.1**
  - yt-dlp **2026.07.04**
  - curl_cffi **0.15.0** (MUST stay 0.10.x–0.15.x; 0.16.0 breaks yt-dlp's
    request-handler registration and kills TikTok impersonation)
  - PyInstaller **6.21.0**
- Run GUI smoke tests with: `QT_QPA_PLATFORM=offscreen`, Python `-B` flag.
- System ffmpeg (used at runtime, not bundled): winget Gyan.FFmpeg 8.1.2 full
  build → `C:\Users\MuslimQasim\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1.2-full_build\bin\ffmpeg.exe` (ffmpeg.exe is 231 MB).
- Inno Setup: **not yet installed** (installer step pending, see §9).

## 4. File inventory & roles

Root:
- `Q-S-Ali Media Downloader.exe` — deployed app (8.7 MB); needs `_internal\` next to it.
- `_internal\` — deployed runtime (116.5 MB): PySide6, curl_cffi 0.15.0, certifi, icon.ico, etc.
- `_internal.old\`, `Anas Media Downloader.exe.old`, `Anas Media Downloader.exe_extracted\` — old-brand backups/artifacts (safe to delete once confirmed).
- `.gitignore` — excludes `source/venv`, `source/build`, `source/dist`, `*.spec`, `_internal/`, `*.exe_extracted/`, `/*.exe`, `*.old`, `unins000.exe`.

`source/` (tracked source):
- `main.py` — PySide6 GUI: `MainWindow`, `Job`, `JobCard`, `Chip`, rail/workspace/footer builders, `glyph_icon`, `shield_pixmap`, `resource/storage_dir/queue_file`, `main()`. Constants: `ORG='S-Q-Ali'`, `VERSION='2.0.0'`, `SETTINGS_VERSION='2.0'`, `MAX_SAVED_QUEUE=500`, `NOTICE`, `SOCIALS` (GitHub/LinkedIn).
- `engine.py` — download engine: `DownloadThread` (worker pool, inline retries, passes), `AccountFetchThread`, `YouTubeFetchThread`, `impersonate_target`/`impersonation_summary`, URL helpers (`is_tiktok_url`, `is_profile_url`, `is_youtube_url`, `is_youtube_playlist_url`, `is_youtube_channel_url`, `platform_of`), `QUALITY_OPTIONS`, `DELAY_PRESETS`, `RETRY_PASSES`, `PARALLEL_OPTIONS`, `sanitize_filename`, `find_ffmpeg`, `default_output_dir`, `tidy_error`, `is_permanent`. `APP_NAME='Q-S-Ali Media Downloader'`.
- `theme.py` — `C` palette dict, `STATUS_COLORS`, `STYLESHEET` (dark + cyan accent).
- `licensing.py` — LEGACY, unused by the app. Keep only as history.
- `icon.ico` — app/EXE icon (generated 2026-08-06).
- `Anas Media Downloader.spec`, `Q-S-Ali Media Downloader.spec` — PyInstaller build artifacts (gitignored).

Runtime storage (not in repo): `%LOCALAPPDATA%\Q-S-Ali Media Downloader\storage\` → `queue.json` + `downloads\`. QSettings org `S-Q-Ali`, app `Q-S-Ali Media Downloader` (registry `HKCU\Software\S-Q-Ali\Q-S-Ali Media Downloader`).

## 5. Architecture summary

- `add_links()` (main) → validates lines → TikTok/YouTube video URLs become
  `Job`s; YouTube playlist/channel links go to `_expand_queue` →
  `YouTubeFetchThread` resolves them to `watch?v=` URLs in the background
  (`on_youtube_found` adds jobs).
- `start_run()` → `DownloadThread(jobs, output_dir, quality, ...)`.
  - `_run_pool` spawns 1–3 worker threads (parallel setting) over a shared
    cursor; per-video inline retries (3×, 2–5s) then marked `Waiting`; extra
    passes sweep leftovers after a 20–35s cooldown.
  - `_download_one` computes `platform = platform_of(url) or 'TikTok'`;
    TikTok opts include `impersonate` (curl_cffi chrome target); YouTube
    skips impersonation. Format from `QUALITY_OPTIONS[quality]`; `Audio only`
    → mp3 via FFmpegExtractAudio. Files saved via `__amd_%(id)s` temp name
    then renamed to sanitized caption (unique_basename).
- Account tab → `AccountFetchThread` lists a public TikTok profile's newest
  videos (up to `MAX_ACCOUNT_VIDEOS`, default limit options 20–100) without
  downloading; found → added as jobs.
- Progress/state flows via signals: `job_started`, `job_meta`, `job_progress`,
  `job_retrying`, `job_result`, `log`, `countdown`, `finished_all`.

## 6. Verified facts (re-run to confirm health)

- `impersonate_target()` returns a chrome target (e.g. `chrome-146:macos-26`)
  in `source\venv`; `impersonation_summary()[0]` is True.
- `is_youtube_url('https://youtu.be/abc')`, playlist, channel, `platform_of`
  checks all pass.
- `DownloadThread._base_opts('YouTube')` has NO `impersonate`;
  `_base_opts('TikTok')` has it (with a mocked target).
- Offscreen GUI: window title `Q-S-Ali Media Downloader · 2.0.0`, wordmark
  `S-Q-Ali`, sub `MEDIA DOWNLOADER`, social buttons GitHub + LinkedIn.
- Built EXEs launch and stay running (Start-Process + 8s + kill).
- `py_compile` of all four modules passes; no leftover Anas strings.

## 7. Build & run commands

```powershell
# dev run (from source\)
$env:QT_QPA_PLATFORM="offscreen"   # optional for headless
& ".\venv\Scripts\python.exe" -B main.py

# rebuild EXE (source\)
& ".\venv\Scripts\pyinstaller.exe" --noconfirm --clean --onedir --windowed `
  --name "Q-S-Ali Media Downloader" --icon "icon.ico" --add-data "icon.ico;." main.py
# output: source\dist\Q-S-Ali Media Downloader\{exe, _internal}

# quick import/health check (source\)
& ".\venv\Scripts\python.exe" -B -c "import engine, main; print('OK')"
```

## 8. Git state

- Branch `master`; remote `origin` → https://github.com/S-Q-Ali/Bulk-Video-Downloader.git
- Commit `6da50b4` — "Rebrand to Q-S-Ali Media Downloader, remove license gate, add YouTube support"
- Push worked using a cached GitHub credential (VS Code/Git Credential Manager).
  No `gh` CLI, no SSH keys. For API calls, retrieve the token with
  `git credential fill` (host github.com) or ask the user for a PAT.

## 9. Next steps (in-flight)

1. **Installer (approved plan, NOT yet executed):**
   - Install Inno Setup 6: `winget install --id JRSoftware.InnoSetup -e --accept-package-agreements --accept-source-agreements`
   - Write `installer.iss`: per-user install
     (`{localappdata}\Programs\Q-S-Ali Media Downloader`, `PrivilegesRequired=lowest`),
     files = `Q-S-Ali Media Downloader.exe` + `_internal\**` + bundled
     `bin\ffmpeg.exe` (staged copy from the winget ffmpeg path into
     `release\staging\`); fresh AppId GUID; lzma2/ultra64; output
     `release\Q-S-Ali-Media-Downloader-Setup-2.0.0.exe`.
   - Build with ISCC; silent-install test to a temp dir; verify installed
     EXE launches and `bin\ffmpeg.exe` is found; uninstall to clean up.
   - Add `release/` to `.gitignore`; commit `installer.iss`.
   - Publish GitHub Release `v2.0.0` via REST API
     (`POST /repos/S-Q-Ali/Bulk-Video-Downloader/releases`) + upload the
     setup EXE. Fallback if token lacks scope: manual upload by user.
2. **Repo professionalization:** see `REPO_IMPROVEMENT_PLAN.md`.
3. **Optional cleanup:** delete `_internal.old`, `Anas Media Downloader.exe.old`,
   `Anas Media Downloader.exe_extracted`, old `.spec` files once the new
   installer is verified.

## 10. Known issues / caveats

- **curl_cffi must be 0.10.x–0.15.x.** 0.16.0 is unsupported by yt-dlp
  (handler silently fails to register → no impersonation → TikTok failures).
- **ffprobe not bundled** (only ffmpeg chosen). yt-dlp may log harmless
  "ffprobe not found" warnings; merging still works.
- **Qt text drawing crashes** on this build under offscreen/native in a bare
  QPainter script (0xC0000409). The app's own widget text is unaffected;
  only standalone QPainter `drawText` scripts are affected. Icon is font-free.
- **Full rename orphans old data:** old saved queue/settings live under
  `%LOCALAPPDATA%\Anas Media Downloader` and old ANAS keys are invalid — a
  clean relaunch by design.
- **New icon not visually confirmed** (model cannot view images); geometry is
  deterministic and the ICO loads as 256×256.
- **Offscreen smoke tests use `-B`** to avoid stale `__pycache__`.

## 11. Decisions log

| Date | Decision |
|------|----------|
| 2026-08-06 | Rebrand to Q-S-Ali Media Downloader; wordmark "S-Q-Ali"; open source (remove license gate); GitHub+LinkedIn footer; cyan theme; generate new icon |
| 2026-08-06 | curl_cffi pinned to 0.15.0 to restore impersonation |
| 2026-08-06 | YouTube support: playlists/channels auto-expand in background; native yt-dlp formats; no TikTok impersonation for YouTube |
| 2026-08-06 | Installer: per-user (no admin), bundle ffmpeg.exe, publish GitHub Release v2.0.0 |
