"""
Tests for the JWT_SECRET_KEY placeholder/length guard in app.core.config.

Covers the two gaps found in review: the guard previously only matched
one exact placeholder string (missing the different one documented in
.env.example), and had no minimum-length fallback for secrets that are
real-looking but still trivially weak.
"""

import pytest

from app.core.config import Settings, KNOWN_PLACEHOLDER_JWT_SECRETS


def _settings(**overrides):
    return Settings(_env_file=None, **overrides)


def test_debug_mode_allows_placeholder():
    # Explicit JWT_SECRET_KEY, not relying on the class default - conftest
    # sets a real one via the environment so local `pytest` runs don't
    # need it configured, which would otherwise shadow the default here.
    s = _settings(DEBUG=True, JWT_SECRET_KEY=next(iter(KNOWN_PLACEHOLDER_JWT_SECRETS)))
    assert s.JWT_SECRET_KEY in KNOWN_PLACEHOLDER_JWT_SECRETS


def test_real_secret_outside_debug_is_accepted():
    s = _settings(DEBUG=False, JWT_SECRET_KEY="a-real-random-secret-at-least-32-chars-long")
    assert s.DEBUG is False


@pytest.mark.parametrize("placeholder", sorted(KNOWN_PLACEHOLDER_JWT_SECRETS))
def test_every_known_placeholder_rejected_outside_debug(placeholder):
    with pytest.raises(RuntimeError):
        _settings(DEBUG=False, JWT_SECRET_KEY=placeholder)


def test_short_secret_rejected_outside_debug():
    with pytest.raises(RuntimeError):
        _settings(DEBUG=False, JWT_SECRET_KEY="too-short")
