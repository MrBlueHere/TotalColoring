#!/usr/bin/env python3

import networkx
import total_sat as sat_solver
import total_csp as csp_solver
import matplotlib.pyplot as plt
import coloring
import time


# Validates the graph
def verify_total_coloring(graph, expected_colors, colors) -> str:
    for u in graph.nodes():
        if "color" not in graph.nodes[u]:
            return f"Vertex {u} has no assigned color."
    for u, v in graph.edges():
        if "color" not in graph.edges[u, v]:
            return f"Edge {u,v} has no assigned color."

    for u, v in graph.edges():
        if graph.nodes[u]["color"] == graph.nodes[v]["color"]:
            c = graph.nodes[v]["color"]
            return f"Vertices {u} and {v} have the same color {c}."
        if graph.nodes[u]["color"] == graph.edges[u, v]["color"]:
            c = graph.nodes[u]["color"]
            return f"Vertex {u} and edge {u,v} have the same color {c}."
        if graph.nodes[v]["color"] == graph.edges[u, v]["color"]:
            c = graph.nodes[v]["color"]
            return f"Vertex {v} and edge {u,v} have the same color {c}."

    for u in graph.nodes():
        for v in graph[u]:
            for w in graph[u]:
                if v != w and graph.edges[u, v]["color"] == graph.edges[u, w]["color"]:
                    c = graph.edges[u, v]["color"]
                    return f"Edges {u,v} and {u,w} have the same color {c}."

    if colors != expected_colors and expected_colors is not None:
        return f"The number of colors {colors} differs from the expected {expected_colors}."


# Gets appropriate plot layout for the given graph
def get_layout(graph, name: str):
    if "cycle" in name.lower():
        return networkx.circular_layout(graph)
    elif "star" in name.lower():
        return networkx.circular_layout(graph)
    elif "hypercube" in name.lower():
        return networkx.spring_layout(graph)
    return networkx.circular_layout(graph)


# Runs the tests and plots the results
def total_coloring_test(name: str, mode: str, graph, expected_colors, draw: bool) -> (bool, time):
    print("Test: {}".format(name))

    if mode == "SAT":
        start = time.time()
        colors = sat_solver.total_coloring(graph)
        end = time.time()
    elif mode == "CSP":
        start = time.time()
        colors = csp_solver.total_coloring(graph)
        end = time.time()
    elif mode == "CSP_iterative":
        start = time.time()
        colors = csp_solver.total_coloring_iterative(graph)
        end = time.time()
    elif mode == "SAT_iterative":
        start = time.time()
        colors = sat_solver.total_coloring_iterative(graph)
        end = time.time()
    else:
        return False, None

    result = verify_total_coloring(graph, expected_colors, colors)

    if result:
        print("Failed: {}".format(result))
        return False, None
    else:
        print("Colored with {} colors".format(colors))
        if draw:
            node_coloring, edge_coloring = coloring.get_graph_colors(graph)
            networkx.draw(graph, node_color=node_coloring, edge_color=edge_coloring, width=1.5, pos=get_layout(graph, name))
            plt.show()
        return True, (end - start)


# Driver code for tests
def run_tests(mode: str, draw: bool) -> bool:
    success, time_elapsed = total_coloring_test("Complete graph on 3 vertices", mode, networkx.complete_graph(3), 3, draw)
    if not success:
        return False

    success, time_elapsed = total_coloring_test("Complete graph on 5 vertices", mode, networkx.complete_graph(5), 5, draw)
    if not success:
        return False

    success, time_elapsed = total_coloring_test("Cycle of length 5", mode, networkx.cycle_graph(5), 4, draw)
    if not success:
        return False

    success, time_elapsed = total_coloring_test("Star graph on 5 vertices", mode, networkx.star_graph(4), 5, draw)
    if not success:
        return False

    success, time_elapsed = total_coloring_test("Cycle of length 14", mode, networkx.cycle_graph(14), 4, draw)
    if not success:
        return False

    success, time_elapsed = total_coloring_test("Star graph on 50 vertices", mode, networkx.star_graph(50), 51, draw)
    if not success:
        return False

    success, time_elapsed = total_coloring_test("Complete bipartite graph on 4+4 vertices", mode, networkx.complete_multipartite_graph(4, 4), 6, draw)
    if not success:
        return False

    return True
