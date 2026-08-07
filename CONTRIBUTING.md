# Contributing

Thanks for helping out! This project is small but open to everyone. Here's how to get going.

## Setup

```powershell
git clone https://github.com/S-Q-Ali/Bulk-Video-Downloader.git
cd Bulk-Video-Downloader
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements-dev.txt
```

## Running checks

```powershell
pytest                # 25+ tests, includes an offscreen GUI smoke test
ruff check src tests  # lint
```

Everything must pass before a PR is merged. CI runs the same checks on Windows.

## Code layout

- `src/qsali_media_downloader/engine.py` — download engine and URL helpers (no UI code).
- `src/qsali_media_downloader/theme.py` — palette and stylesheet.
- `src/qsali_media_downloader/app.py` — application entry point.
- `src/qsali_media_downloader/ui/` — `main_window.py` (window + wiring) and `widgets.py` (cards, chips, drawing helpers).
- `tests/` — pytest suite. Keep it green; add tests alongside new behaviour.

## Guidelines

- Keep engine logic free of UI imports so it stays unit-testable.
- Preserve the `curl_cffi==0.15.0` pin in `requirements.txt` — yt-dlp only
  supports up to 0.15.x, and that pin is what keeps TikTok impersonation working.
- Do not commit build artifacts (`dist/`, `_internal/`, `release/*`,
  installer outputs) or virtual environments — see `.gitignore`.
- Do not commit secrets, API keys, or the legacy licensing secret.
- Use the same dark-theme palette from `theme.py` for any UI work.

## Pull requests

1. Fork the repo and create a branch (`feature/…` or `fix/…`).
2. Make your change and add/update tests.
3. Run `pytest` and `ruff check src tests`.
4. Open a PR from the template. Reference the issue it fixes, if any.

## Releases

Maintainers cut releases by tagging (`v2.0.1`, …). The tag triggers the CI
release pipeline; the portable build and Inno installer are produced and
published as a GitHub Release asset. See `REPO_IMPROVEMENT_PLAN.md` Phase E.
