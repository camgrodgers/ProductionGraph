#![allow(dead_code)]

mod product_graph;
mod product_graph_rayon;
use product_graph_rayon::*;
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
        let data = ProductGraph::generate_product_graph(num_prods);
        let start = Instant::now();
        let _results = data.calc_for_n_iterations(num_iters);
        let duration = start.elapsed();
        times.push((i, duration));
    }

    for (multiple, duration) in times {
        println!(
            "Time elapsed in threaded for {} iterations on {} products is: {:?}",
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
        let mut data = product_graph::ProductGraph::generate_product_graph(num_prods);
        let start = Instant::now();
        let _results = data.calc_for_n_iterations(num_iters);
        let duration = start.elapsed();
        times.push((i, duration));
    }

    for (multiple, duration) in times {
        println!(
            "Time elapsed for {} iterations on {} products is: {:?}",
            num_iters,
            step * multiple,
            duration
        );
    }
}
