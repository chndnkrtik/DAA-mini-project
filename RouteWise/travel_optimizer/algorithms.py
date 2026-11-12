from __future__ import annotations

import heapq
from dataclasses import dataclass

from .models import Edge, RouteLeg, RouteResult


@dataclass
class DisjointSet:
    parent: dict[str, str]
    rank: dict[str, int]

    @classmethod
    def create(cls, items: list[str]) -> "DisjointSet":
        return cls(
            parent={item: item for item in items},
            rank={item: 0 for item in items},
        )

    def find(self, item: str) -> str:
        if self.parent[item] != item:
            self.parent[item] = self.find(self.parent[item])
        return self.parent[item]

    def union(self, left: str, right: str) -> bool:
        left_root = self.find(left)
        right_root = self.find(right)
        if left_root == right_root:
            return False

        if self.rank[left_root] < self.rank[right_root]:
            left_root, right_root = right_root, left_root

        self.parent[right_root] = left_root
        if self.rank[left_root] == self.rank[right_root]:
            self.rank[left_root] += 1
        return True


class TravelGraph:
    def __init__(self, edges: list[Edge]):
        self.edges = list(edges)
        self.adjacency: dict[str, list[Edge]] = {}
        for edge in self.edges:
            self.adjacency.setdefault(edge.source, []).append(edge)
            self.adjacency.setdefault(edge.destination, [])
        self.nodes = sorted(self.adjacency)

    def _validate_weight(self, weight: str) -> None:
        if weight not in {"distance", "time", "cost"}:
            raise ValueError("Weight must be distance, time, or cost.")

    def _build_route(
        self,
        previous: dict[str, Edge | None],
        source: str,
        destination: str,
        score_key: str,
    ) -> RouteResult:
        path_edges: list[Edge] = []
        current = destination

        while current != source:
            edge = previous[current]
            if edge is None:
                raise ValueError(f"No route found from {source} to {destination}.")
            path_edges.append(edge)
            current = edge.source

        path_edges.reverse()
        path = [source]
        legs: list[RouteLeg] = []

        for edge in path_edges:
            path.append(edge.destination)
            legs.append(RouteLeg(
                source=edge.source,
                destination=edge.destination,
                distance=edge.distance,
                time=edge.time,
                cost=edge.cost,
            ))

        return RouteResult(
            path=path,
            legs=legs,
            total_distance=sum(leg.distance for leg in legs),
            total_time=sum(leg.time for leg in legs),
            total_cost=sum(leg.cost for leg in legs),
            score_key=score_key,
        )

    def dijkstra(self, source: str, destination: str, weight: str = "distance") -> RouteResult:
        self._validate_weight(weight)
        if source not in self.adjacency or destination not in self.adjacency:
            raise ValueError("Source or destination city is not available in the network.")

        if source == destination:
            return RouteResult(source and [source], [], 0.0, 0.0, 0.0, weight)

        distances = {node: float("inf") for node in self.nodes}
        previous: dict[str, Edge | None] = {node: None for node in self.nodes}
        distances[source] = 0.0
        queue: list[tuple[float, str]] = [(0.0, source)]

        while queue:
            current_distance, current_node = heapq.heappop(queue)
            if current_distance > distances[current_node]:
                continue
            if current_node == destination:
                break

            for edge in self.adjacency[current_node]:
                edge_weight = getattr(edge, weight)
                candidate = current_distance + edge_weight
                if candidate < distances[edge.destination]:
                    distances[edge.destination] = candidate
                    previous[edge.destination] = edge
                    heapq.heappush(queue, (candidate, edge.destination))

        if distances[destination] == float("inf"):
            raise ValueError(f"No route found from {source} to {destination}.")

        return self._build_route(previous, source, destination, score_key=weight)

    def kruskal_minimum_network(self, weight: str = "cost") -> tuple[list[Edge], float]:
        self._validate_weight(weight)
        # Treat each route as undirected for minimum-spanning-tree construction.
        unique_edges: dict[tuple[str, str], Edge] = {}
        for edge in self.edges:
            key = tuple(sorted((edge.source, edge.destination)))
            current = unique_edges.get(key)
            if current is None or getattr(edge, weight) < getattr(current, weight):
                unique_edges[key] = edge

        sorted_edges = merge_sort_edges(list(unique_edges.values()), key=weight)
        disjoint_set = DisjointSet.create(self.nodes)
        mst: list[Edge] = []
        total_weight = 0.0

        for edge in sorted_edges:
            if disjoint_set.union(edge.source, edge.destination):
                mst.append(edge)
                total_weight += getattr(edge, weight)
                if len(mst) == len(self.nodes) - 1:
                    break

        return mst, total_weight

    def enumerate_routes(
        self, source: str, destination: str, max_stops: int = 5
    ) -> list[RouteResult]:
        if source not in self.adjacency or destination not in self.adjacency:
            raise ValueError("Source or destination city is not available in the network.")
        if max_stops < 1:
            raise ValueError("Maximum stops must be at least 1.")

        results: list[RouteResult] = []
        path = [source]
        used = {source}

        def dfs(city: str) -> None:
            if len(path) - 1 > max_stops:
                return
            if city == destination:
                legs: list[RouteLeg] = []
                for start, end in zip(path, path[1:]):
                    edge = next(
                        e for e in self.adjacency[start] if e.destination == end
                    )
                    legs.append(RouteLeg(
                        edge.source, edge.destination,
                        edge.distance, edge.time, edge.cost
                    ))
                results.append(RouteResult(
                    path=list(path),
                    legs=legs,
                    total_distance=sum(x.distance for x in legs),
                    total_time=sum(x.time for x in legs),
                    total_cost=sum(x.cost for x in legs),
                    score_key="cost",
                ))
                return

            for edge in self.adjacency[city]:
                if edge.destination not in used:
                    used.add(edge.destination)
                    path.append(edge.destination)
                    dfs(edge.destination)
                    path.pop()
                    used.remove(edge.destination)

        dfs(source)
        return results

    def best_route_within_budget(
        self,
        source: str,
        destination: str,
        budget: float,
        optimize: str = "time",
    ) -> RouteResult | None:
        self._validate_weight(optimize)
        if budget < 0:
            raise ValueError("Budget cannot be negative.")
        routes = self.enumerate_routes(source, destination, max_stops=max(1, len(self.nodes) - 1))
        eligible = [route for route in routes if route.total_cost <= budget]
        if not eligible:
            return None
        return min(eligible, key=lambda route: getattr(route, f"total_{optimize}"))


def merge_sort_edges(edges: list[Edge], key: str = "cost") -> list[Edge]:
    if len(edges) <= 1:
        return edges[:]
    middle = len(edges) // 2
    left = merge_sort_edges(edges[:middle], key)
    right = merge_sort_edges(edges[middle:], key)
    merged: list[Edge] = []
    left_index = right_index = 0

    while left_index < len(left) and right_index < len(right):
        if getattr(left[left_index], key) <= getattr(right[right_index], key):
            merged.append(left[left_index])
            left_index += 1
        else:
            merged.append(right[right_index])
            right_index += 1

    merged.extend(left[left_index:])
    merged.extend(right[right_index:])
    return merged


def quick_sort_routes(routes: list[RouteResult], key: str = "cost") -> list[RouteResult]:
    if key not in {"cost", "time", "distance"}:
        raise ValueError("Sort key must be cost, time, or distance.")
    if len(routes) <= 1:
        return routes[:]

    pivot = getattr(routes[len(routes) // 2], f"total_{key}")
    lower = [r for r in routes if getattr(r, f"total_{key}") < pivot]
    equal = [r for r in routes if getattr(r, f"total_{key}") == pivot]
    higher = [r for r in routes if getattr(r, f"total_{key}") > pivot]
    return (
        quick_sort_routes(lower, key)
        + equal
        + quick_sort_routes(higher, key)
    )
