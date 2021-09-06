from total_tests import total_coloring_test
import networkx
import matplotlib.pyplot as plt
import random


# Runs experiments on randomly created graphs for various sizes
def graph_size_experiments(modes: [], sizes: []):
    res = {mode: [] for mode in modes}
    density = 0.6
    for size in sizes:
        seed = random.randint(1, 10000)
        graph = networkx.erdos_renyi_graph(size, density, seed)
        for mode in modes:
            success, elapsed = total_coloring_test("Random graph on {} vertices".format(size), mode,
                                                   graph, None, False)
            if not success:
                return None
            res[mode].append(elapsed)
    return res


# Runs experiments on randomly created graphs for various densities
def graph_density_experiments(modes: [], densities: []):
    res = {mode: [] for mode in modes}
    graph_size = 25
    for dens in densities:
        seed = random.randint(1, 10000)
        graph = networkx.erdos_renyi_graph(graph_size, dens, seed)
        for mode in modes:
            success, elapsed = total_coloring_test("Random graph of size {} with {} density".format(graph_size, dens), mode,
                                                   graph, None, False)
            if not success:
                return None
            res[mode].append(elapsed)
    return res


# Runs experiments on randomly created graphs and takes an average
def graph_average(modes: []):
    res = {mode: [] for mode in modes}
    graph_size = 8
    dens = 0.75

    runs = 10
    for _ in range(runs):
        seed = random.randint(1, 10000)
        graph = networkx.erdos_renyi_graph(graph_size, dens, seed)
        for mode in modes:
            success, elapsed = total_coloring_test("Random graph of size {} with {} density".format(graph_size, dens), mode,
                                                   graph, None, False)
            if not success:
                return None
            res[mode].append(elapsed)

    for mode in modes:
        print('Graphs size {}, density {}, mode {}: Average time {}s'.format(
            graph_size, dens, mode, sum(res[mode]) / len(res[mode])))


# Runs experiments on star graphs
def star_graph_experiments(modes: [], sizes: []):
    res = {mode: [] for mode in modes}
    for size in sizes:
        for mode in modes:
            success, elapsed = total_coloring_test("Star graph on {} vertices".format(size), mode,
                                                   networkx.star_graph(size), size + 1, False)
            if not success:
                return None
            res[mode].append(elapsed)
    return res


# Runs experiments on complete graphs
def complete_graph_experiments(modes: [], sizes: [], expected: []):
    res = {mode: [] for mode in modes}
    for i in range(len(sizes)):
        for mode in modes:
            success, elapsed = total_coloring_test("Complete graph on {} vertices".format(sizes[i]), mode,
                                                   networkx.complete_graph(sizes[i]), expected[i], False)
            if not success:
                return None
            res[mode].append(elapsed)
    return res


# Runs experiments on bipartite graphs
def bipartite_graph_experiments(modes: [], sizes: [], expected: []):
    res = {mode: [] for mode in modes}
    for i in range(len(sizes)):
        for mode in modes:
            success, elapsed = total_coloring_test("Complete bipartite graph on {} vertices".format(sizes[i]), mode,
                                                   networkx.complete_multipartite_graph(sizes[i], sizes[i]), expected[i], False)
            if not success:
                return None
            res[mode].append(elapsed)
    return res


def handle_failure():
    print("Experiments failed")
    exit(1)


# Runs experiments which compare the time of CSP and SAT
def run_experiments():
    modes = ["CSP", "SAT", "CSP_iterative", "SAT_iterative"]

    experiment_results = []

    # Specific graph structures
    star_graph_sizes = [size for size in range(10, 100, 10)]
    results = star_graph_experiments(modes, star_graph_sizes)
    if results is None:
        handle_failure()
    experiment_results.append((star_graph_sizes, results, "star graphs"))

    complete_graph_sizes = [size for size in range(1, 8, 1)]
    total_expected = [1, 3, 3, 5, 5, 7, 7]
    results = complete_graph_experiments(modes, complete_graph_sizes, total_expected)
    if results is None:
        handle_failure()
    experiment_results.append((complete_graph_sizes, results, "complete graphs"))

    complete_bipartite_graph_sizes = [size for size in range(2, 5, 1)]
    complete_bipartite_expected = [4, 5, 6]
    results = bipartite_graph_experiments(modes, complete_bipartite_graph_sizes, complete_bipartite_expected)
    if results is None:
        handle_failure()
    experiment_results.append((complete_bipartite_graph_sizes, results, "complete bipartite graphs"))

    # Randomly generated graphs, experiments based on size in nodes
    random_graph_sizes = [size for size in range(5, 50, 5)]
    results = graph_size_experiments(modes, random_graph_sizes)
    if results is None:
        handle_failure()
    experiment_results.append((random_graph_sizes, results, "random graphs based on size"))

    # Randomly generated graphs, experiments based on density
    densities = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
    densities_results = graph_density_experiments(modes, densities)
    if densities_results is None:
        handle_failure()

    # Plotting
    for experiment_res in experiment_results:
        input_sizes, output, experiment_name = experiment_res
        for mode in results:
            plt.plot(input_sizes, output[mode], label='{}'.format(mode))

        plt.title(
            'Comparison of ' + ','.join(modes) + ' for {}'.format(experiment_name))
        plt.xlabel('Size of the graph in nodes')
        plt.ylabel('Time in seconds')
        plt.legend()
        plt.show()

    for mode in densities_results:
        plt.plot(densities, densities_results[mode], label='{}'.format(mode))
    plt.title(
        'Comparison of ' + ','.join(modes) + ' for random graphs based on density')
    plt.xlabel('Probability of edge creation')
    plt.ylabel('Time in seconds')
    plt.legend()
    plt.show()

    graph_average(modes)
