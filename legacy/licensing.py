"""Legacy installation-key generator for Q-S-Ali Media Downloader.

Q-S-Ali Media Downloader is now open source and no longer enforces an
activation key. This module is kept in the repo only as source history;
the shipped app does not import it.

Keys look like ANAS-7K2P-9XQM-4B3F. The first two blocks are random; the
last is a checksum of them plus a secret. Nothing is stored in a list, so
make_keys.py can mint as many as you like and every one of them
validates without the app ever being rebuilt.

The same check used to run in two places - the installer (installer.iss)
and the app on first launch. installer.iss carried a Pascal copy of the
function below; if you change SECRET or ALPHABET here, change it there
too.
"""

import hashlib
import random
import re

ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
PREFIX = "ANAS"
SECRET = "AnasMediaDownloader/2026/anas-siddique-online"
BLOCK = 4


def _checksum(block_one, block_two):
    raw = (block_one + block_two + SECRET).encode("ascii")
    digest = hashlib.sha256(raw).digest()
    return "".join(ALPHABET[byte % len(ALPHABET)] for byte in digest[:BLOCK])


def make_key(rng=None):
    if rng is None:
        rng = random.SystemRandom()
    one = "".join(rng.choice(ALPHABET) for _ in range(BLOCK))
    two = "".join(rng.choice(ALPHABET) for _ in range(BLOCK))
    return f"{PREFIX}-{one}-{two}-{_checksum(one, two)}"


def normalize_key(text):
    cleaned = re.sub(r"[^A-Za-z0-9]", "", text or "").upper()
    if len(cleaned) != BLOCK * 4:
        return None
    return "-".join(cleaned[i : i + BLOCK] for i in range(0, BLOCK * 4, BLOCK))


def validate_key(text):
    key = normalize_key(text)
    if not key:
        return False
    parts = key.split("-")
    if parts[0] != PREFIX:
        return False
    for part in parts[1:]:
        if any(ch not in ALPHABET for ch in part):
            return False
    return parts[3] == _checksum(parts[1], parts[2])
