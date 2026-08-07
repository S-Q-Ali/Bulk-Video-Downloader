# Security Policy

## Reporting a vulnerability

Please report security issues privately instead of opening a public issue.

Use GitHub's **private vulnerability reporting**:

1. Go to https://github.com/S-Q-Ali/Bulk-Video-Downloader/security/advisories
2. Click **New draft security advisory**
3. Describe the issue, the affected version, and a minimal reproduction.

You'll get an acknowledgment within a few days. Please do not disclose the
issue publicly until it has been addressed.

## Scope

In scope:

- Remote code execution or arbitrary file write from a crafted URL or filename.
- Credential/key leakage in the shipped application or repository.
- Unexpected network behaviour that exposes user data.

Out of scope:

- Downloading copyrighted content (this tool is a download client; users are
  responsible for respecting platform terms and copyright).
- Design choices about retry pacing or worker count.

## Notes for maintainers

- The legacy activation secret (`legacy/licensing.py`) is gitignored and must
  never be re-added to the repository or the installer.
- Do not commit secrets, tokens, or the GitHub credential material to the repo.
