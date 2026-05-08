"""Shared fixtures for MTA Subway tests."""

from __future__ import annotations

import pytest

pytest_plugins = ["pytest_homeassistant_custom_component"]


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations: object) -> None:
    """Enable loading the mta_subway custom integration in all tests."""
