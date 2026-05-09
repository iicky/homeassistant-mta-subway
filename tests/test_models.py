"""Edge case tests for pydantic models."""

from __future__ import annotations

from custom_components.mta_subway.models import (
    Alert,
    AlertEntity,
    Route,
    TranslatedString,
)


def test_alert_is_active_when_no_period_specified() -> None:
    alert = Alert.model_validate(
        {
            "informed_entity": [{"route_id": "1"}],
            "transit_realtime.mercury_alert": {"alert_type": "Delays"},
        }
    )
    assert alert.is_active_at(0) is True
    assert alert.is_active_at(9_999_999_999) is True


def test_alert_with_open_ended_active_period() -> None:
    alert = Alert.model_validate(
        {
            "active_period": [{"start": 1000}],
            "informed_entity": [{"route_id": "1"}],
        }
    )
    assert alert.is_active_at(999) is False
    assert alert.is_active_at(1000) is True
    assert alert.is_active_at(2_000_000_000) is True


def test_alert_with_alert_type_none_falls_through_to_service_change() -> None:
    """Alerts without a mercury_alert extension should still parse."""
    alert = Alert.model_validate(
        {
            "informed_entity": [{"route_id": "1"}],
        }
    )
    assert alert.alert_type is None


def test_translated_string_returns_none_when_no_translations() -> None:
    ts = TranslatedString.model_validate({"translation": []})
    assert ts.text() is None


def test_translated_string_falls_back_to_first_when_lang_missing() -> None:
    ts = TranslatedString.model_validate(
        {"translation": [{"text": "Foo", "language": "es"}]}
    )
    assert ts.text("en") == "Foo"


def test_route_is_frozen() -> None:
    route = Route.model_validate(
        {
            "id": "1",
            "name": "1",
            "color": "#ee352e",
            "status": "Good Service",
            "scheduled": True,
        }
    )
    try:
        route.status = "Mutated"  # type: ignore[misc]
    except (TypeError, ValueError):
        return
    msg = "Route should be frozen"
    raise AssertionError(msg)


def test_alert_entity_round_trips() -> None:
    payload = {
        "id": "alert:1",
        "alert": {
            "informed_entity": [{"route_id": "1"}],
            "header_text": {"translation": [{"text": "Hi", "language": "en"}]},
        },
    }
    entity = AlertEntity.model_validate(payload)
    assert entity.id == "alert:1"
    assert entity.alert.affects_route("1")
    assert not entity.alert.affects_route("2")
