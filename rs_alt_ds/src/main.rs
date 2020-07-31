mod product_graph_hashmap;
mod product;
mod dependency;

use product_graph_hashmap::HashedProductGraph;
use std::time::Instant;

fn main() {
    benchmark_rayon(100_000, 1, 10);
    benchmark_plain(100_000, 1, 10);
}

fn benchmark_rayon(step: usize, begin: usize, end: usize) {
    let num_iters = 25;
    let mut times = Vec::new();
    for i in begin..=end {
        let num_prods = step * i;
        let start = Instant::now();
        let data = HashedProductGraph::generate_product_graph(num_prods);
        println!(
            "Generating product graph on {} prods took {:?}",
            num_prods,
            start.elapsed()
        );
        let start = Instant::now();
        let _results = data.calc_for_n_iterations(num_iters);
        let duration = start.elapsed();
        times.push((i, duration));
    }

    for (multiple, duration) in times {
        println!(
            "Time elapsed in multi-threaded for {} iterations on {} products is: {:?}",
            num_iters,
            step * multiple,
            duration
        );
    }
}

fn benchmark_plain(step: usize, begin: usize, end: usize) {
    let num_iters = 25;
    let mut times = Vec::new();
    for i in begin..=end {
        let num_prods = step * i;
        let mut data = HashedProductGraph::generate_product_graph(num_prods);
        let start = Instant::now();
        let _results = data.calc_for_n_iterations(num_iters);
        let duration = start.elapsed();
        times.push((i, duration));
    }

    for (multiple, duration) in times {
        println!(
            "Time elapsed in single-threaded for {} iterations on {} products is: {:?}",
            num_iters,
            step * multiple,
            duration
        );
    }
}