from __future__ import annotations

from flask import Flask, render_template, request
from travel_optimizer.algorithms import TravelGraph, quick_sort_routes
from travel_optimizer.data import SAMPLE_EDGES
from travel_optimizer.models import Edge, RouteResult

app = Flask(__name__)
graph = TravelGraph(SAMPLE_EDGES)


def serialize_route(route: RouteResult) -> dict[str, object]:
    return {
        "path": route.path,
        "path_text": " -> ".join(route.path),
        "distance": round(route.total_distance, 1),
        "time": round(route.total_time, 1),
        "cost": round(route.total_cost, 1),
        "stops": route.hops,
        "score_key": route.score_key,
    }


def serialize_edges(edges: list[Edge]) -> list[dict[str, object]]:
    return [
        {
            "source": edge.source,
            "destination": edge.destination,
            "distance": edge.distance,
            "time": edge.time,
            "cost": edge.cost,
        }
        for edge in edges
    ]


def build_chart_points(routes: list[RouteResult]) -> list[dict[str, object]]:
    return [
        {
            "label": " -> ".join(route.path),
            "nodes": len(route.path),
            "time": round(route.total_time, 1),
            "cost": round(route.total_cost, 1),
        }
        for route in routes
    ]


@app.route("/", methods=["GET", "POST"])
def index():
    context: dict[str, object] = {
        "cities": graph.nodes,
        "selected_source": "",
        "selected_destination": "",
        "budget": "",
        "max_stops": "5",
        "results": None,
        "error": None,
    }

    if request.method == "POST":
        source = request.form.get("source", "").strip().title()
        destination = request.form.get("destination", "").strip().title()
        budget_text = request.form.get("budget", "").strip()
        max_stops_text = request.form.get("max_stops", "5").strip()

        context.update({
            "selected_source": source,
            "selected_destination": destination,
            "budget": budget_text,
            "max_stops": max_stops_text,
        })

        try:
            if not source or not destination:
                raise ValueError("Please select both source and destination cities.")

            max_stops = int(max_stops_text or 5)
            if max_stops < 1:
                raise ValueError("Maximum stops must be at least 1.")

            shortest_route = graph.dijkstra(source, destination, weight="distance")
            cheapest_route = graph.dijkstra(source, destination, weight="cost")
            all_routes = graph.enumerate_routes(
                source, destination, max_stops=max_stops
            )

            if not all_routes:
                all_routes = [shortest_route]

            sorted_by_cost = quick_sort_routes(all_routes, key="cost")
            sorted_by_time = quick_sort_routes(all_routes, key="time")

            budget_route = None
            if budget_text:
                try:
                    budget = float(budget_text)
                    if budget < 0:
                        raise ValueError("Budget cannot be negative.")
                    budget_route = graph.best_route_within_budget(
                        source, destination, budget=budget, optimize="time"
                    )
                except ValueError as error:
                    raise ValueError(f"Invalid budget: {error}") from error

            mst_edges, total_network_cost = graph.kruskal_minimum_network(
                weight="cost"
            )

            context["results"] = {
                "shortest_route": serialize_route(shortest_route),
                "cheapest_route": serialize_route(cheapest_route),
                "routes_by_cost": [
                    serialize_route(route) for route in sorted_by_cost[:5]
                ],
                "routes_by_time": [
                    serialize_route(route) for route in sorted_by_time[:5]
                ],
                "budget_route": serialize_route(budget_route) if budget_route else None,
                "budget_checked": bool(budget_text),
                "network_edges": serialize_edges(mst_edges),
                "network_total_cost": round(total_network_cost, 1),
                "chart_points": build_chart_points(sorted_by_time[:5]),
                "route_count": len(all_routes),
            }

        except (ValueError, TypeError) as error:
            context["error"] = str(error)

    return render_template("index.html", **context)


if __name__ == "__main__":
    app.run(debug=True)
