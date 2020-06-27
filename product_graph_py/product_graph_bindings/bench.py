import product_graph_bindings
import random
import time

# Might write a python version of the calculation code here
def calc_indirect_vals_for_n_iterations(data, num_iters):
    pass

def bench_rust(step, begin, end):
    num_iters = 25
    times = []
    for i in range(begin, end):
        num_prods = step * i
        data = generate_graph(num_prods)
        start = time.time()
        (results, dur) = product_graph_bindings.calc_indirect_vals_for_n_iterations(data, num_iters)
        print(dur)
        end = time.time()
        times.append((i, end - start))

    for (multiple, duration) in times:
        print(f"Time elapsed for {multiple * step} products is: {duration}")


def generate_graph(num_prods):
    graph = {}
    for i in range(0, int(num_prods / 2)):
        deps = []
        for j in range(0, 8):
            deps.append(( random.randint(int(num_prods /2) , num_prods -1), 0.000000000001))
        graph[i] = product_graph_bindings.SimpleProduct(10.0, deps)

    for i in range(int(num_prods / 2), num_prods):
        deps = []
        for j in range(0, 8):
            deps.append((random.randint(0, int(num_prods /2)), 0.001))
        graph[i] = product_graph_bindings.SimpleProduct(10.0, deps)

    return graph

def generate_graph1(num_prods):
    graph = {}
    for i in range(0, num_prods):
        graph[i] = product_graph_bindings.SimpleProduct(10.0, [])

    return graph


bench_rust(5000000, 1, 2)
