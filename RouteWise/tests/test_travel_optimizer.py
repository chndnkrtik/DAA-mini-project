from travel_optimizer.algorithms import TravelGraph, quick_sort_routes
from travel_optimizer.data import SAMPLE_EDGES


def build_graph() -> TravelGraph:
    return TravelGraph(SAMPLE_EDGES)


def test_shortest_and_cheapest_routes_are_generated() -> None:
    graph = build_graph()
    shortest = graph.dijkstra("Delhi", "Mumbai", weight="distance")
    cheapest = graph.dijkstra("Delhi", "Mumbai", weight="cost")

    assert shortest.path[0] == "Delhi"
    assert shortest.path[-1] == "Mumbai"
    assert cheapest.path[0] == "Delhi"
    assert cheapest.path[-1] == "Mumbai"


def test_budget_route_respects_limit() -> None:
    graph = build_graph()
    route = graph.best_route_within_budget(
        "Delhi", "Mumbai", budget=7000, optimize="time"
    )
    assert route is not None
    assert route.total_cost <= 7000


def test_kruskal_returns_network() -> None:
    graph = build_graph()
    mst_edges, total_cost = graph.kruskal_minimum_network(weight="cost")
    assert len(mst_edges) == len(graph.nodes) - 1
    assert total_cost > 0


def test_quick_sort_orders_routes_by_cost() -> None:
    graph = build_graph()
    routes = graph.enumerate_routes("Delhi", "Mumbai", max_stops=5)
    sorted_routes = quick_sort_routes(routes, key="cost")
    costs = [route.total_cost for route in sorted_routes]
    assert costs == sorted(costs)
