"""Pydantic models for the subwaynow.app /routes?detailed=1 response."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class DirectionalStatus(BaseModel):
    """Per-direction string values keyed by north / south."""

    model_config = ConfigDict(extra="ignore")

    north: str | None = None
    south: str | None = None


class ServiceChangeSummary(BaseModel):
    """Service-change summary lists keyed by direction or `both`."""

    model_config = ConfigDict(extra="ignore")

    both: list[str] = Field(default_factory=list)
    north: list[str] = Field(default_factory=list)
    south: list[str] = Field(default_factory=list)


class Route(BaseModel):
    """Service status for a single subway line."""

    model_config = ConfigDict(extra="ignore")

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

    model_config = ConfigDict(extra="ignore")

    routes: dict[str, Route]
