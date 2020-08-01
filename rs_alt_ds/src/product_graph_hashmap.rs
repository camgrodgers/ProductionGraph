use std::f32;
use rayon::prelude::*;
use std::mem;
use hashbrown::HashMap;
use rayon::iter::IntoParallelRefIterator;
use rayon::iter::ParallelIterator;
// use rayon::iter::FromParallelIterator;
use rayon::iter::IndexedParallelIterator;
use rand::Rng;

use crate::product::Product;

// TODO: impl Error
#[derive(Debug, Clone)]
pub struct GraphError {
    pub out_of_bounds_dependency: Vec<u64>,
    pub negative: Vec<u64>,
    pub prods_in_inf_cycles: Vec<u64>,
}

#[derive(Clone)]
pub struct HashedProductGraph {
    // what should the key be??
    graph: HashMap<u64, Product>,
}

impl HashedProductGraph {
    pub fn new() -> Self {
        HashedProductGraph {
            graph: HashMap::new()
        }
    }

    pub fn with_capacity(size: usize) -> HashedProductGraph {
        HashedProductGraph {
            graph: HashMap::with_capacity(size)
        }
    }

    /// Create a HashedProductGraph from a plain Vec of Products.
    pub fn from_vec(vec: Vec<Product>) -> HashedProductGraph {

        let mut hashed_map = HashedProductGraph {
            graph: HashMap::new()
        };

        for prod in vec {
            hashed_map.insert(prod);
        }

        hashed_map
    }

    /// Insert a Product into the internal HashMap
    pub fn insert(&mut self, prod: Product) {
        self.graph.insert(prod.id, prod);
    }

    /// dependent: id of product: u64
    /// dependency: id of dependency
    /// quantity: the quantity needed for prod
    pub fn set_dependency(
        &mut self,
        dependant: u64,
        dependency: u64,
        quantity: f32,
    ) /*-> Result<(), ()> */{
        // if self.graph.len() == 0 
        //     // check if dep_id is same as prod_id and if quantity is at or above 1,
        //     // basically ensuring they don't depend on 1.0 or more of themselves.
        //     || (dependency == dependant as usize && quantity >= 1.0) 
        //     || !self.graph.contains_key(&dependant)
        //     || quantity < 0.0
        //     || quantity == f32::INFINITY
        // {
        //     return Err(());
        // }

        match self.graph.get_mut(&dependant) {
            Some(prod) => prod.set_dependency(dependency, quantity),
            // None => return Err(())
            None => return
        }

        // Ok(())
    }

    pub fn len(&self) -> usize {
        self.graph.len()
    }

    // FIXME: collect into vec is not compatible with hashbrown hashmap, my other solution is to 
    // dereference the target passed in vec and assign it to collect. Documentation states that 
    // collect may be slower. 
    // TODO: ask cameron for clarification on this function
    fn calc_iteration(&self, indir_costs_old: & HashMap<u64, f32>) -> HashMap<u64, f32> {
        // is dereferencing like this in rust bad practice??
        self.graph
            .par_iter()
            .map(|(id, prod)| {
                let indir_val = prod.dependencies.iter().fold(0.0, |acc, dep| {
                    // FIXME: this method of accessing the old costs will not work I think, as the dep.id is 
                    // no longer index in the array
                    let dep_cost = self.graph[&dep.id].direct_cost + indir_costs_old[&dep.id];
                    acc + (dep.quantity * dep_cost)
                });
                (*id, indir_val)
            }).collect()
            //.collect_into_vec(indir_costs_new) //=> BROKEN
            // method not found in `rayon::iter::map::Map<hashbrown::external_trait_impls::rayon::map::ParIter<'_, u64, product::Product, ahash::random_state::RandomState>, 
            // [closure@src/product_graph_hashmap.rs:96:18: 103:14 indir_costs_old:_]>`

    }

    fn calc_iteration_new(&mut self, indir_costs: &mut HashMap<u64, f32>) {
        // let mut indir_costs_new = indir_costs.clone();

        self.graph
        .par_iter()
        .for_each(|(_, prod)| {
            // indir_costs_new.insert(prod.id, 1.0);
            let new_cost = prod.dependencies.iter().fold(0.0, |acc, dep| {
                let dep_cost = match self.graph.get(&dep.id) {
                    Some(_prod) => _prod.direct_cost,
                    _ => 0.0
                };

                acc + (dep.quantity * dep_cost)
            });
        });
    }

    pub fn calc_for_n_iterations_new(&self, n: u16) -> HashMap<u64, f32> {
        let indir_costs = &mut HashMap::<u64, f32>::new();
        
        indir_costs.clone()
    }

    /// Multiple iterations of the iterative estimation for indirect costs. Performs count number of
    /// iterations and then returns the final estimates. With each iteration, the estimates become
    /// more precise. ~15 iterations gives a good estimate, ~25 is better, and ~50 is extremely precise.
    /// More iterations are needed to get accurate results if any Product depends directly or indirectly
    /// on quantities of itself that approach 1.0. For instance, if corn depends on 0.01 of itself, 15 iterations
    /// should give a good result. However, if it depends on 0.9 of itself, it could take 50 iterations
    /// to be sure.
    // TODO: ask cameron for clarification on this function
    pub fn calc_for_n_iterations(&self, n: u16) -> HashMap<u64, f32> {
        let indir_costs = &mut (0..self.graph.len()).map(|i| (i as u64, 0.0)).collect();
        let indir_costs_copy = &mut (0..self.graph.len()).map(|i| (i as u64, 0.0)).collect();
        for _ in 0..n {
            *indir_costs_copy = self.calc_iteration(indir_costs);
            // At the end of each iteration, the copy var has the most-updated data in it.
            // Therefore, in the next iteration, it should be the old data, and the new data should
            // overwrite the old old data.
            mem::swap(indir_costs, indir_costs_copy);
        }
        indir_costs.clone()
    }

    /// Check the graph for errors in the dataset. If a Product depends directly or indirectly on
    /// 1.0 or more of itself, this represents either bad data or a broken economy, as it will cause
    /// the price of that Product and those that depend on it to go to infinity.
    /// Also checks for dependencies that reference vector elements out of bounds, and for values
    /// that are infinity or negative.
    pub fn check_graph(&self) -> Result<(), GraphError> {
        let mut out_of_bounds: Vec<u64> = Vec::new();
        let mut negative_value: Vec<u64> = Vec::new();
        let mut infinite: Vec<u64> = Vec::new();

        for (i, entry) in self.graph.iter() {
            let p = entry;

            if p.direct_cost < 0.0 {
                negative_value.push(*i);
            }
            if p.direct_cost == f32::INFINITY {
                infinite.push(*i);
            }

            for d in p.dependencies.iter() {
                if d.id >= self.graph.len() as u64 {
                    out_of_bounds.push(*i);
                }
                if d.quantity < 0.0 {
                    negative_value.push(*i);
                }
                if d.quantity == f32::INFINITY || (d.id == *i && d.quantity >= 1.0) {
                    infinite.push(*i);
                }
            }
        }

        if out_of_bounds.len() != 0 || negative_value.len() != 0 || infinite.len() != 0 {
            return Err(GraphError {
                out_of_bounds_dependency: out_of_bounds,
                negative: negative_value,
                prods_in_inf_cycles: infinite,
            });
        }

        // Checking for infinite cycles
        // FIXME: test failing for this implementation
        let indir_costs = &mut (0..self.graph.len()).map(|i| (i as u64, 0.0)).collect();
        let indir_costs_copy = &mut (0..self.graph.len()).map(|i| (i as u64, 0.0)).collect();
        let mut increments_gather = || {
            *indir_costs_copy = self.calc_iteration(indir_costs);
            let increments = indir_costs
                .iter()
                .zip(indir_costs_copy.iter())
                .map(|((r1id, r1val), (r2id, r2val))| (*r1id, r2val - r1val))
                .collect::<HashMap<u64, f32>>();
            mem::swap(indir_costs, indir_costs_copy);
            increments
        };
        increments_gather(); // Throw away first result as it involves the 0.0 initialized vec
        let increments1 = increments_gather();
        let increments2 = increments_gather();

        let prods_in_infinite_cycles: Vec<u64> = increments1
            .iter()
            .zip(increments2.iter())
            .filter_map(|((increment1id, inc1val), (increment2id, inc2val))| {
                if inc1val <= inc2val && *inc2val != 0.0 {
                    Some(*increment1id)
                } else {
                    None
                }
            })
            .collect();

        if prods_in_infinite_cycles.len() == 0 {
            Ok(())
        } else {
            Err(GraphError {
                prods_in_inf_cycles: prods_in_infinite_cycles,
                out_of_bounds_dependency: Vec::new(),
                negative: Vec::new(),
            })
        }
    }


    /// Generate a random product graph for testing and benchmarking purposes.
    pub fn generate_product_graph(count: usize) -> HashedProductGraph {
        let mut rng = rand::thread_rng();
        let mut prods = HashedProductGraph::from_vec((0..count).map(|i| {
            Product::new(i as u64, 10.0)
        }).collect());

        for i in 0..(count / 2) {
            //prods.set_dependencies_capacity(i, 8);
            for _ in 0..8 {
                prods.set_dependency(i as u64 ,rng.gen_range(count / 2, count) as u64, 0.00000000001);
            }
        }
        for i in (count / 2)..count {
            //prods.set_dependencies_capacity(i, 8);
            for _ in 0..8 {
                prods.set_dependency(i as u64, rng.gen_range(0, count / 2) as u64, rng.gen_range(0.01, 5.0));
            }
        }

        prods
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn detects_direct_infinite_cycle() {
        let mut prods = HashedProductGraph::from_vec(vec![Product::new(0, 10.0)]);
        prods.set_dependency(0, 0, 1.0);
        let result = prods.check_graph();
        match result {
            Ok(()) => panic!(),
            Err(e) => assert_eq!(0, e.prods_in_inf_cycles[0]),
        }
    }

    #[test]
    fn detects_indirect_infinite_cycle() {
        let mut prods = HashedProductGraph::with_capacity(3);
        for i in 0..3 {
            prods.insert(Product::new(i, 10.0));
        }

        prods.set_dependency(0, 1, 0.5);
        prods.set_dependency(0, 2, 0.5);
        prods.set_dependency(2, 0, 1.0);
        prods.set_dependency(1, 0, 1.0);

        let result = prods.check_graph();
        match result {
            Ok(()) => panic!(),
            Err(e) => {
                for id in vec![0, 1, 2] {
                    assert!(e.prods_in_inf_cycles.contains(&id))
                }
            }
        }
    }
}
