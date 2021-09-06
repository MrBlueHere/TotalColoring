# Credits: https://gist.github.com/adewes/5884820

import random

# Functions for generating colors for the plotted graph


# Gets distinct colors for nodes and edges
def get_graph_colors(graph) -> ([], []):
    node_coloring = []
    colors = {}
    for n in graph.nodes():
        color = graph.nodes[n]["color"]
        if color not in colors:
            new_col = generate_new_color(node_coloring, 1)
            colors[color] = new_col
        node_coloring.append(colors[color])

    edge_coloring = []
    for n in graph.edges():
        color = graph.edges[n]["color"]
        if color not in colors:
            new_col = generate_new_color(edge_coloring, 1)
            colors[color] = new_col
        edge_coloring.append(colors[color])

    return node_coloring, edge_coloring


def get_random_color(pastel_factor=0.5):
    return [(x+pastel_factor)/(1.0+pastel_factor) for x in [random.uniform(0, 1.0) for i in [1, 2, 3]]]


def color_distance(c1, c2):
    return sum([abs(x[0]-x[1]) for x in zip(c1, c2)])


def generate_new_color(existing_colors, pastel_factor):
    max_distance = None
    best_color = None
    for i in range(0, 100):
        color = get_random_color(pastel_factor=pastel_factor)
        if not existing_colors:
            return color
        best_distance = min([color_distance(color, c) for c in existing_colors])
        if not max_distance or best_distance > max_distance:
            max_distance = best_distance
            best_color = color
    return best_color
