# Repo Professionalization Plan — Q-S-Ali Media Downloader

Goal: turn the current flat, mixed-source repo into a clean, conventional,
CI-ready Python project that is easy to contribute to, release, and rebuild.

Current layout (informal, has build/deploy artifacts mixed in at root):

```
Anas Media Downloader.exe_extracted/   # old artifact
_internal/                            # deployed runtime (release artifact)
_internal.old/                        # backup
Anas Media Downloader.exe.old         # backup
Q-S-Ali Media Downloader.exe          # deployed release artifact
source/
  venv/ build/ dist/                 # local, gitignored
  main.py engine.py theme.py licensing.py icon.ico
  *.spec
.gitignore
```

## Target structure

```
Bulk-Video-Downloader/
├── .github/
│   └── workflows/
│       ├── ci.yml                    # lint + tests on push/PR
│       └── release.yml               # build EXE + installer, publish on tag
│   └── PULL_REQUEST_TEMPLATE.md, ISSUE_TEMPLATE.md
├── src/
│   └── qsali_media_downloader/
│       ├── __init__.py               # __version__ = "2.0.0"
│       ├── __main__.py               # entry: python -m qsali_media_downloader
│       ├── app.py                    # QApplication bootstrap (was main() bottom)
│       ├── engine.py                 # download engine (moved as-is)
│       ├── theme.py                  # palette + stylesheet (moved as-is)
│       ├── ui/
│       │   ├── main_window.py        # MainWindow + queue/cards/chips
│       │   ├── widgets.py            # Job, JobCard, Chip, glyph_icon, shield_pixmap
│       │   └── resources.py          # resource()/storage_dir() helpers
│       └── resources/
│           └── icon.ico
├── tests/
│   ├── test_urls.py                  # is_tiktok/is_youtube/platform_of
│   ├── test_engine.py                # base_opts platform behavior, sanitize, keygen
│   ├── test_theme.py                 # palette/status color invariants
│   └── conftest.py                   # offscreen QApplication fixture
├── tools/
│   ├── make_icon.py                  # regenerate icon.ico (font-free)
│   └── mint_keys.py                  # legacy licensing tool (optional)
├── packaging/
│   ├── Q-S-Ali-Media-Downloader.spec # PyInstaller spec (checked in)
│   ├── installer.iss                 # Inno Setup script
│   └── ffmpeg/                       # ignored; staging for bundling
├── docs/
│   └── (usage, build, release guide)
├── .gitignore
├── .editorconfig
├── LICENSE                            # MIT (pick one)
├── README.md                          # badges, quickstart, screenshots, links
├── CONTRIBUTING.md
├── CHANGELOG.md
├── SECURITY.md
├── pyproject.toml                     # metadata, deps, ruff config
└── requirements.txt / requirements-dev.txt
```

## Phased execution

### Phase A — Hygiene ✅ DONE (2026-08-06)
1. Deleted `_internal.old`, `Anas Media Downloader.exe.old`,
   `Anas Media Downloader.exe_extracted`, stale `source\Anas Media Downloader.spec`.
2. Deployed EXE + `_internal` moved to `release/portable/`; installer.iss
   re-pointed to `release\portable\` and recompiled + re-verified.
3. Plan + SESSION_NOTES.md committed (`8620b84`).

### Phase B — Package restructure ✅ DONE (2026-08-06)
4. Created `src/qsali_media_downloader/`; `engine.py`, `theme.py` moved as-is;
   `main.py` split into `app.py` + `ui/main_window.py` + `ui/widgets.py`
   (behaviour-identical; verified by offscreen smoke + engine checks).
5. Absolute imports (`from qsali_media_downloader.engine import ...`).
6. Added `pyproject.toml`, `requirements.txt`, `requirements-dev.txt`.
7. Added `__main__.py` → `python -m qsali_media_downloader`.
8. Full verification passed; EXE rebuilt from the package; installer
   recompiled (icon path updated to `src\...\resources\icon.ico`) and
   install/uninstall round-trip verified. Commit `bf1b220`.
   - NOTE: `legacy/licensing.py` replaces `source/licensing.py`.
   - Installer script lives at `release/installer.iss` (not `packaging/`).

### Phase C — Tests & lint
9. Add `tests/` (URL detection, engine opt-building, theme invariants,
   offscreen GUI smoke). `conftest.py` sets `QT_QPA_PLATFORM=offscreen`.
10. Configure ruff + a simple `ci.yml` (install deps → pytest → build EXE).

### Phase D — Docs & community
11. `README.md`: what it is, features, install (portable + installer),
    build-from-source, tech stack, GitHub/LinkedIn links.
12. `LICENSE` (MIT), `CONTRIBUTING.md`, `CHANGELOG.md`, `SECURITY.md`.
13. Issue/PR templates.

### Phase E — Release automation
14. `packaging/Q-S-Ali-Media-Downloader.spec` committed; a
    `tools/build_release.ps1` that runs PyInstaller → Inno Setup → zip.
15. `release.yml`: on tag `v*`, build on windows-latest, run tests, publish
    the EXE/installer as a GitHub Release.
16. First tag: `v2.0.0`.

## Rules for future sessions
- Keep release artifacts (EXE, `_internal`, installers) out of git; publish
  via GitHub Releases only.
- Source stays under `src/`; no build outputs in the repo.
- Preserve the curl_cffi==0.15.0 pin and the onedir/windowed build flags.
- Re-run SESSION_NOTES §6 checks after any structural change.

## Open questions
- License choice (MIT proposed) — confirm before Phase D.
- Keep `licensing.py`/`tools/mint_keys.py` as legacy, or delete?
- Rename `master` → `main` branch?
