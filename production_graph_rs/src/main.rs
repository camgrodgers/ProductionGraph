mod production_graph;
use production_graph::product_graph::*;
use std::time::{Duration, Instant};

fn main() {

    let mut data = ProductGraph::generate_product_graph(1_000_000);
//    let mut data = ProductGraph::with_capacity(4);
//    data.insert(0,Product{direct_cost: 5.0, indirect_cost: 0.0, dependencies: vec![DependencyInfo{ id: 1, quantity:  1.01}]});
//    data.insert(1,Product{direct_cost: 10.0, indirect_cost: 0.0, dependencies: vec![DependencyInfo{ id: 0, quantity:  1.9}]});
//    data.insert(2,Product{direct_cost: 10.0, indirect_cost: 0.0, dependencies: vec![DependencyInfo{ id: 2, quantity:  0.1}]});
//    data.insert(3,Product{direct_cost: 10.0, indirect_cost: 0.0, dependencies: vec![DependencyInfo{ id: 3, quantity:  0.1}]});
//    match ProductGraph::detect_impossible_cycles(&data) {
//        Ok(()) => {},
//        Err(err) => {
//            for i in err.prods_in_cycles { println!("{}", i); }
//        }
//    }

    let start = Instant::now();
    ProductGraph::calc_for_n_iterations(&mut data, 50);
    let duration = start.elapsed();

    println!("Time elapsed in calc_for_n_iterations for 50 iterations is: {:?}", duration);

    //for (id, c) in data.iter().enumerate() {
    //    println!("id: {}, direct_cost: {}, dep_count: {}, indirect_cost: {}", id, c.direct_cost, c.dependencies.len(), c.indirect_cost);
    //}
}
