"""Diagnostics support for the MTA Subway integration."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from . import MTASubwayConfigEntry


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant,
    entry: MTASubwayConfigEntry,
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    data = entry.runtime_data
    routes = data.routes.data or {}
    alerts = data.alerts.data or []

    return {
        "config_entry": {
            "data": dict(entry.data),
            "options": dict(entry.options),
        },
        "routes": {
            "last_update_success": data.routes.last_update_success,
            "last_exception": str(data.routes.last_exception)
            if data.routes.last_exception
            else None,
            "count": len(routes),
            "lines": sorted(routes.keys()),
            "sample": (routes[next(iter(routes))].model_dump() if routes else None),
        },
        "alerts": {
            "last_update_success": data.alerts.last_update_success,
            "last_exception": str(data.alerts.last_exception)
            if data.alerts.last_exception
            else None,
            "count": len(alerts),
            "alert_types": sorted(
                {a.alert.alert_type for a in alerts if a.alert.alert_type}
            ),
            "by_route": {
                route_id: sum(
                    1
                    for a in alerts
                    if any(ie.route_id == route_id for ie in a.alert.informed_entity)
                )
                for route_id in sorted(routes.keys())
            },
        },
    }
