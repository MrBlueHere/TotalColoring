#!/usr/bin/env python3

from pysat.solvers import Glucose3
import networkx
from bisect import bisect_left


# Assignes the colors to graph based on the solution
# if the value wasn't defined by the solver, random value is chosen
def fill_colors(graph, solution, color_values, variables, edge_nums):
    solution = [x for x in solution if x > 0]
    for u in graph.nodes():
        node_col = -1
        for c in color_values:
            var_num = variables[u, c]
            if binary_search(solution, var_num) is not None:
                node_col = c
                break
        graph.nodes[u]["color"] = node_col - 1
    for u, v in graph.edges():
        edge_col = -1
        for c in color_values:
            var_num = variables[edge_nums[u, v], c]
            if binary_search(solution, var_num) is not None:
                edge_col = c
                break
        graph.edges[u, v]["color"] = edge_col - 1


# Validates the solution returned from iterative process
def validate_solution(graph):
    for u, v in graph.edges():
        # Neighboring vertices with same color
        if graph.nodes[u]["color"] == graph.nodes[v]["color"]:
            return False
        # Vertex and its edge have the same color
        if graph.nodes[u]["color"] == graph.edges[u, v]["color"] or graph.nodes[v]["color"] == graph.edges[u, v]["color"]:
            return False

    for u in graph.nodes():
        incident_colors = [graph.edges[e]["color"] for e in graph.edges(u)]
        unique = set()
        for col in incident_colors:
            # Neighboring edges with the same color
            if col in unique:
                return False
            unique.add(col)
    return True


def binary_search(a, x):
    i = bisect_left(a, x)
    if i != len(a) and a[i] == x:
        return i
    else:
        return None


# Finds total chromatic index and assigns color to each node and edge
# in iterative manner, by providing not fully specified problem to the solver
def total_coloring_iterative(graph):
    # Size of the chunks in which the problem will be iteratively defined
    chunk_size = max(1, len(graph.nodes()) // 3)

    nodes = []

    # Initiate
    max_deg = 0
    for node in graph.nodes:
        max_deg = max(max_deg, graph.degree[node])
        nodes.append(node)
    colors_count = max_deg

    edge_nums = {}
    edge_num = len(graph.nodes)
    edge_nums_values = []
    for e in graph.edges:
        edge_nums[e[0], e[1]] = edge_num
        edge_nums[e[1], e[0]] = edge_num
        edge_nums_values.append(edge_num)
        edge_num += 1

    solution_found = False
    solution = []

    color_values = []
    variables = {}

    # Search for solution with the given amount of colors (lower bound is max_degree + 1)
    while not solution_found:
        colors_count += 1
        color_values = [c + 1 for c in range(colors_count)]

        # Define problem
        g = Glucose3()

        # Define variables
        cnt = 0
        variables = {}
        for v in graph.nodes:
            for c in color_values:
                variables[(v, c)] = cnt * colors_count + c
            cnt += 1
        for e in edge_nums_values:
            for c in color_values:
                variables[(e, c)] = cnt * colors_count + c
            cnt += 1

        # Common clauses so that we get at least some colors assigned
        for v in graph.nodes:
            # Constraint - At least 1 color for each node
            g.add_clause([variables[v, c] for c in color_values])

            # Constraint - At most 1 color for each node
            for i in range(len(color_values) - 1):
                for j in range(i + 1, len(color_values)):
                    g.add_clause([-variables[v, color_values[i]], -variables[v, color_values[j]]])

        for e0, e1 in graph.edges:
            e = edge_nums[e0, e1]
            # Constraint - At least 1 color for each edge
            g.add_clause([variables[e, c] for c in color_values])

            # Constraint - At least 1 color for each edge
            for i in range(len(color_values) - 1):
                for j in range(i + 1, len(color_values)):
                    g.add_clause([-variables[e, color_values[i]], -variables[e, color_values[j]]])

            # Constraint - Different color for each (edge, v, u)
            for c in color_values:
                g.add_clause([-variables[e0, c], -variables[e1, c]])
                g.add_clause([-variables[e0, c], -variables[e, c]])
                g.add_clause([-variables[e1, c], -variables[e, c]])

        # Iteratively find solutions
        starting_at = 0
        while starting_at < len(graph.nodes):
            # Define the problem chunk
            for node_i in range(starting_at, min(starting_at + chunk_size, len(graph.nodes()))):
                v = nodes[node_i]
                # Constraint - Different color for each pair of edges sharing a node
                incident = [e for e in graph.edges(v)]
                for c in color_values:
                    if len(incident) > 1:
                        for i in range(len(incident) - 1):
                            for j in range(i + 1, len(incident)):
                                g.add_clause([-variables[edge_nums[incident[i]], c], -variables[edge_nums[incident[j]], c]])

            # Try to get solution
            if g.solve():
                solution = g.get_model()
                fill_colors(graph, solution, color_values, variables, edge_nums)
                if validate_solution(graph):
                    solution_found = True
                    break

            starting_at += chunk_size

    fill_colors(graph, solution, color_values, variables, edge_nums)
    return colors_count


# Finds total chromatic index and assigns color to each node and edge
def total_coloring(graph: networkx.Graph):
    # Initiate
    max_deg = 0
    for node in graph.nodes:
        max_deg = max(max_deg, graph.degree[node])
    colors_count = max_deg

    edge_nums = {}
    edge_num = len(graph.nodes)
    edge_nums_values = []
    for e in graph.edges:
        edge_nums[e[0], e[1]] = edge_num
        edge_nums[e[1], e[0]] = edge_num
        edge_nums_values.append(edge_num)
        edge_num += 1

    solution_found = False
    solution = []

    color_values = []
    variables = {}

    # Search for solution with the given amount of colors (lower bound is max_degree + 1)
    while not solution_found:
        colors_count += 1
        color_values = [c + 1 for c in range(colors_count)]

        # Define problem
        g = Glucose3()

        # Define variables
        cnt = 0
        variables = {}
        for v in graph.nodes:
            for c in color_values:
                variables[(v, c)] = cnt * colors_count + c
            cnt += 1
        for e in edge_nums_values:
            for c in color_values:
                variables[(e, c)] = cnt * colors_count + c
            cnt += 1

        for v in graph.nodes:
            # Constraint - At least 1 color for each node
            g.add_clause([variables[v, c] for c in color_values])

            # Constraint - At most 1 color for each node
            for i in range(len(color_values) - 1):
                for j in range(i + 1, len(color_values)):
                    g.add_clause([-variables[v, color_values[i]], -variables[v, color_values[j]]])

            # Constraint - Different color for each pair of edges sharing a node
            incident = [e for e in graph.edges(v)]
            for c in color_values:
                if len(incident) > 1:
                    for i in range(len(incident) - 1):
                        for j in range(i + 1, len(incident)):
                            g.add_clause([-variables[edge_nums[incident[i]], c], -variables[edge_nums[incident[j]], c]])

        for e0, e1 in graph.edges:
            e = edge_nums[e0, e1]
            # Constraint - At least 1 color for each edge
            g.add_clause([variables[e, c] for c in color_values])

            # Constraint - At least 1 color for each edge
            for i in range(len(color_values) - 1):
                for j in range(i + 1, len(color_values)):
                    g.add_clause([-variables[e, color_values[i]], -variables[e, color_values[j]]])

            # Constraint - Different color for each (edge, v, u)
            for c in color_values:
                g.add_clause([-variables[e0, c], -variables[e1, c]])
                g.add_clause([-variables[e0, c], -variables[e, c]])
                g.add_clause([-variables[e1, c], -variables[e, c]])

        # Get solution
        if g.solve():
            solution_found = True
            solution = g.get_model()

    solution = [x for x in solution if x > 0]
    for u in graph.nodes():
        node_col = -1
        for c in color_values:
            var_num = variables[u, c]
            if binary_search(solution, var_num) is not None:
                node_col = c
                break
        graph.nodes[u]["color"] = node_col - 1
    for u, v in graph.edges():
        edge_col = -1
        for c in color_values:
            var_num = variables[edge_nums[u, v], c]
            if binary_search(solution, var_num) is not None:
                edge_col = c
                break
        graph.edges[u, v]["color"] = edge_col - 1
    return colors_count
