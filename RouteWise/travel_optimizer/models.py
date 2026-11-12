from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Edge:
    source: str
    destination: str
    distance: float
    time: float
    cost: float


@dataclass(frozen=True)
class RouteLeg:
    source: str
    destination: str
    distance: float
    time: float
    cost: float


@dataclass
class RouteResult:
    path: list[str]
    legs: list[RouteLeg]
    total_distance: float
    total_time: float
    total_cost: float
    score_key: str = "distance"

    @property
    def hops(self) -> int:
        return max(0, len(self.path) - 1)
