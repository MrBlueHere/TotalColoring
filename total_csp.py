from constraint import *
import random


# Assignes the colors to graph based on the solution
# if the value wasn't defined by the solver, random value is chosen
def fill_colors(graph, solution, node_nums, edge_nums, defined, colors_count):
    for u in graph.nodes():
        if u in defined:
            graph.nodes[u]["color"] = solution[node_nums[u]]
        else:
            graph.nodes[u]["color"] = random.randint(0, colors_count - 1)
    for u, v in graph.edges():
        num = edge_nums[u, v]
        if num in defined:
            graph.edges[u, v]["color"] = solution[num]
        else:
            graph.edges[u, v]["color"] = random.randint(0, colors_count - 1)


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


# Finds total chromatic index and assigns color to each node and edge
# in iterative manner, by providing not fully specified problem to the solver
def total_coloring_iterative(graph):
    # Size of the chunks in which the problem will be iteratively defined
    chunk_size = max(1, len(graph.nodes()) // 2)

    # Integers for vertices for easier manipulation and hashing
    node_nums = {}
    nodes = []

    node_n = 0
    max_deg = 0
    for node in graph.nodes:
        node_nums[node] = node_n
        nodes.append(node)
        max_deg = max(max_deg, graph.degree[node])
        node_n += 1

    # Integers for edges for easier manipulation and hashing
    edge_num = len(graph.nodes())
    edge_nums = {}
    for e in graph.edges():
        e0, e1 = e
        # Edges aren't directed
        edge_nums[e0, e1] = edge_num
        edge_nums[e1, e0] = edge_num
        edge_num += 1

    colors = max_deg
    solution_found = False

    # Search for solution with the given amount of colors (lower bound is max_degree + 1)
    while not solution_found:
        colors += 1
        color_domain = [c for c in range(colors)]
        problem = Problem()

        # Set up variables for nodes and edges
        problem.addVariables(node_nums.values(), color_domain)
        problem.addVariables(set(edge_nums.values()), color_domain)

        # Iteratively find solutions
        starting_at = 0
        defined = set()
        while starting_at < len(graph.nodes):
            # Define the problem chunk
            for i in range(starting_at, min(starting_at + chunk_size, len(graph.nodes()))):
                node = nodes[i]
                defined.add(node_nums[node])
                # Constraint for node and all its edges
                # + Constraint for neighboring edges
                incident = [edge_nums[e] for e in graph.edges(node)]
                for e in incident:
                    defined.add(e)
                problem.addConstraint(AllDifferentConstraint(), incident + [node_nums[node]])

                for u in graph[node]:
                    # Constraint for neighboring vertices and their edge
                    problem.addConstraint(AllDifferentConstraint(),
                                          [node_nums[node], node_nums[u], edge_nums[(node, u)]])

            # Try to get solution
            solution = problem.getSolution()
            solution_found = solution is not None
            if solution_found:
                fill_colors(graph, solution, node_nums, edge_nums, defined, colors)
                # The solution for partially defined problem was correct
                if validate_solution(graph):
                    break

            starting_at += chunk_size
            
    return colors


# Finds total chromatic index and assigns color to each node and edge
def total_coloring(graph):
    # Integers for vertices for easier manipulation and hashing
    node_nums = {}
    node_num = 0
    max_deg = 0
    for node in graph.nodes:
        node_nums[node] = node_num
        max_deg = max(max_deg, graph.degree[node])
        node_num += 1

    # Integers for edges for easier manipulation and hashing
    edge_num = len(graph.nodes())
    edge_nums = {}
    for e in graph.edges():
        e0, e1 = e
        # Edges aren't directed
        edge_nums[e0, e1] = edge_num
        edge_nums[e1, e0] = edge_num
        edge_num += 1

    colors = max_deg
    solution_found = False
    solution = []

    # Search for solution with the given amount of colors (lower bound is max_degree + 1)
    while not solution_found:
        colors += 1
        color_domain = [c for c in range(colors)]
        problem = Problem()

        # Set up variables for nodes and edges
        problem.addVariables(node_nums.values(), color_domain)
        problem.addVariables(set(edge_nums.values()), color_domain)

        for node_num in node_nums:
            # Constraint for node and all its edges
            # + Constraint for neighboring edges
            incident = [edge_nums[e] for e in graph.edges(node_num)]
            problem.addConstraint(AllDifferentConstraint(), incident + [node_nums[node_num]])

            for u in graph[node_num]:
                # Constraint for neighboring vertices and their edge
                problem.addConstraint(AllDifferentConstraint(), [node_nums[node_num], node_nums[u], edge_nums[(node_num, u)]])

        solution = problem.getSolution()
        solution_found = solution is not None

    # Assign values
    for u in graph.nodes():
        graph.nodes[u]["color"] = solution[node_nums[u]]
    for u, v in graph.edges():
        num = edge_nums[u, v]
        graph.edges[u, v]["color"] = solution[num]
    return colors
