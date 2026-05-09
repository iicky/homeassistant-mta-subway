"""Pydantic models for the subwaynow.app and MTA alerts feeds."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class DirectionalStatus(BaseModel):
    """Per-direction string values keyed by north / south."""

    model_config = ConfigDict(extra="ignore", frozen=True)

    north: str | None = None
    south: str | None = None


class ServiceChangeSummary(BaseModel):
    """Service-change summary lists keyed by direction or `both`."""

    model_config = ConfigDict(extra="ignore", frozen=True)

    both: list[str] = Field(default_factory=list)
    north: list[str] = Field(default_factory=list)
    south: list[str] = Field(default_factory=list)


class Route(BaseModel):
    """Service status for a single subway line."""

    model_config = ConfigDict(extra="ignore", frozen=True)

    id: str
    name: str
    color: str
    status: str
    scheduled: bool
    direction_statuses: DirectionalStatus | None = None
    delay_summaries: DirectionalStatus | None = None
    service_irregularity_summaries: DirectionalStatus | None = None
    service_change_summaries: ServiceChangeSummary | None = None


class SubwayResponse(BaseModel):
    """Top-level response from subwaynow.app /routes?detailed=1."""

    model_config = ConfigDict(extra="ignore", frozen=True)

    routes: dict[str, Route]


class TimeRange(BaseModel):
    """An alert's active time window in UNIX seconds."""

    model_config = ConfigDict(extra="ignore", frozen=True)

    start: int | None = None
    end: int | None = None


class InformedEntity(BaseModel):
    """A route, stop, or trip an alert applies to."""

    model_config = ConfigDict(extra="ignore", frozen=True)

    agency_id: str | None = None
    route_id: str | None = None
    stop_id: str | None = None
    trip_id: str | None = None


class TranslatedText(BaseModel):
    """One language variant of a translatable string."""

    model_config = ConfigDict(extra="ignore", frozen=True)

    text: str
    language: str | None = None


class TranslatedString(BaseModel):
    """A GTFS-RT TranslatedString with helpers for picking a language."""

    model_config = ConfigDict(extra="ignore", frozen=True)

    translation: list[TranslatedText] = []

    def text(self, language: str = "en") -> str | None:
        for translation in self.translation:
            if translation.language == language:
                return translation.text
        return self.translation[0].text if self.translation else None


class MercuryAlertExtension(BaseModel):
    """MTA's `transit_realtime.mercury_alert` extension on each alert."""

    model_config = ConfigDict(extra="ignore", frozen=True)

    created_at: int | None = None
    updated_at: int | None = None
    alert_type: str | None = None


class Alert(BaseModel):
    """A single GTFS-RT service alert."""

    model_config = ConfigDict(extra="ignore", populate_by_name=True, frozen=True)

    active_period: list[TimeRange] = []
    informed_entity: list[InformedEntity] = []
    header_text: TranslatedString | None = None
    description_text: TranslatedString | None = None
    mercury: MercuryAlertExtension | None = Field(
        default=None, alias="transit_realtime.mercury_alert"
    )

    @property
    def alert_type(self) -> str | None:
        return self.mercury.alert_type if self.mercury else None

    def affects_route(self, route_id: str) -> bool:
        return any(entity.route_id == route_id for entity in self.informed_entity)

    def is_active_at(self, timestamp: int) -> bool:
        if not self.active_period:
            return True
        for period in self.active_period:
            start = period.start if period.start is not None else 0
            end = period.end if period.end is not None else 9_999_999_999
            if start <= timestamp <= end:
                return True
        return False


class AlertEntity(BaseModel):
    """A wrapped alert with its feed-level id."""

    model_config = ConfigDict(extra="ignore", frozen=True)

    id: str
    alert: Alert


class AlertsFeed(BaseModel):
    """Top-level GTFS-RT alerts feed (JSON variant)."""

    model_config = ConfigDict(extra="ignore", frozen=True)

    entity: list[AlertEntity] = []
