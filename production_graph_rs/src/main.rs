#![allow(dead_code)]

mod product_graph;
mod product_graph_rayon;
use product_graph_rayon::*;
use std::time::Instant;

fn main() {
    //    let mut data = ProductGraph::with_capacity(4);
    //    data.insert(0,Product{direct_cost: 5.0, indirect_cost: 0.0, dependencies: vec![DependencyInfo{ id: 1, quantity:  1.01}]});
    //    data.insert(1,Product{direct_cost: 10.0, indirect_cost: 0.0, dependencies: vec![DependencyInfo{ id: 0, quantity:  1.9}]});
    //    data.insert(2,Product{direct_cost: 10.0, indirect_cost: 0.0, dependencies: vec![DependencyInfo{ id: 2, quantity:  0.1}]});
    //    data.insert(3,Product{direct_cost: 10.0, indirect_cost: 0.0, dependencies: vec![DependencyInfo{ id: 3, quantity:  0.1}]});
    //match data.check_graph() {
    //match ProductGraph::detect_impossible_cycles(&data) {
    //    Ok(()) => {},
    //    Err(err) => {
    //        println!("err");
    //    }
    //}
    benchmark();


    //for (id, c) in data.iter().enumerate() {
    //    println!("id: {}, direct_cost: {}, dep_count: {}, indirect_cost: {}", id, c.direct_cost, c.dependencies.len(), c.indirect_cost);
    //}
}


fn benchmark() {
    let num_iters = 25;
    let mut times = Vec::new();
    for i in 0..15 {
        let num_prods = 1_000_000 * i;
        let data = ProductGraph::generate_product_graph(num_prods);
        let start = Instant::now();
        let _results = data.calc_for_n_iterations(num_iters);
        let duration = start.elapsed();
        times.push((i, duration));
    }

    for (multiple, duration) in times {
        println!("Time elapsed for {} iterations on {} * 1mil products is: {:?}",
                 num_iters, multiple, duration
                 );
    }
}
