#![allow(dead_code)]

mod product_graph;
mod product_graph_rayon;
use product_graph_rayon::*;
use std::time::Instant;

fn main() {
    let mut data = ProductGraph::with_capacity(4);
    data.push(Product::new(5.0));
    data.push(Product::new(10.0));
    data.push(Product::new(10.0));
    data.push(Product::new(10.0));
    data.set_dependency(0, 1, 1.01).unwrap();
    data.set_dependency(1, 0, 1.9).unwrap();
    data.set_dependency(2, 3, 0.1).unwrap();
    data.set_dependency(3, 2, 10.1).unwrap();
    let start = Instant::now();
    match data.check_graph() {
        //match product_graph::ProductGraph::detect_impossible_cycles(&data) {
        Ok(()) => {}
        Err(err) => {
            for e in err.prods_in_inf_cycles {
                println!("{:?}", e);
            }
        }
    }
    let duration = start.elapsed();
    println!("{:?}", duration);
    //benchmark_rayon();
    //benchmark_plain();

    //for (id, c) in data.iter().enumerate() {
    //    println!("id: {}, direct_cost: {}, dep_count: {}, indirect_cost: {}", id, c.direct_cost, c.dependencies.len(), c.indirect_cost);
    //}
}

fn benchmark_rayon() {
    let num_iters = 25;
    let mut times = Vec::new();
    for i in 1..=15 {
        let num_prods = 1_000_000 * i;
        let data = ProductGraph::generate_product_graph(num_prods);
        let start = Instant::now();
        let _results = data.calc_for_n_iterations(num_iters);
        let duration = start.elapsed();
        times.push((i, duration));
    }

    for (multiple, duration) in times {
        println!(
            "Time elapsed in threaded for {} iterations on {} * 1mil products is: {:?}",
            num_iters, multiple, duration
        );
    }
}
fn benchmark_plain() {
    let num_iters = 25;
    let mut times = Vec::new();
    for i in 1..=15 {
        let num_prods = 1_000_000 * i;
        let mut data = product_graph::ProductGraph::generate_product_graph(num_prods);
        let start = Instant::now();
        let _results = data.calc_for_n_iterations(num_iters);
        let duration = start.elapsed();
        times.push((i, duration));
    }

    for (multiple, duration) in times {
        println!(
            "Time elapsed for {} iterations on {} * 1mil products is: {:?}",
            num_iters, multiple, duration
        );
    }
}
