use rand::Rng;
use rayon::prelude::*;
use std::mem;

/// The Product struct represents the non-computable data for a product in real life.
/// For example, a cup of lemonade could have a direct cost of $0.1 in wages, or 0.01 in labor hours,
/// and could depend on 0.8 cups of water, 0.1 cup lemon juice, and 0.1 cup of sugar.
/// However, the total cost of the lemonade is unknown at this point, as the indirect costs of all
/// the products in the graph depend on each other, cyclically and acyclically.
/// The Product struct is intended to be used as part of the ProductGraph to calculate the unknown
/// indirect costs.
// TODO: generics?
#[derive(Clone, Debug)]
pub struct Product {
    pub direct_cost: f32,
    pub dependencies: Vec<Dependency>,
}

// TODO: improve ergonomics for adding data
impl Product {
    /// Create a new Product with a given direct cost.
    pub fn new(direct_cost: f32) -> Product {
        Product {
            direct_cost,
            dependencies: Vec::new(),
        }
    }
}

/// The Dependency struct contains an index for a dependency in the array-backed graph, and the
/// quantity that is depended on.
#[derive(Clone, Debug)]
pub struct Dependency {
    pub id: usize,
    pub quantity: f32,
}

/// The ProductGraph is a Vector-backed graph of Products. The Products are the graph nodes, and
/// the dependencies are weighted, directed edges. The "key" or "id" of each Product is its index
/// in the Vector. This graph is specialized for the purpose of rapidly estimating indirect costs.
#[derive(Debug)]
pub struct ProductGraph {
    pub graph: Vec<Product>,
}

// TODO: impl Error
#[derive(Debug, Clone)]
pub struct GraphError {
    pub out_of_bounds_dependency: Vec<usize>,
    pub negative: Vec<usize>,
    pub prods_in_inf_cycles: Vec<usize>,
}

impl ProductGraph {
    // One iteration of the iterative estimation algorithm for indirect costs. Takes in the graph
    // and two buffers. Reads from one buffer and writes to the other. The buffers contain
    // the estimated indirect costs, associated with each product in the graph by index.
    fn calc_iteration(&self, indir_costs_old: &Vec<f32>, indir_costs_new: &mut Vec<f32>) {
        // NOTE: reuses a rotating pair of buffers to reduce allocations. This is one acceptable way
        // to reuse buffers with Rayon. The pair of buffers is actually the most memory-efficient
        // method of doing this with thread safety AFAICT. A Mutex or RWLock on the whole buffer would eliminate
        // advantages of multi-threading, and a RWLock per element would actually take more space
        // than the duplicate elements here (RWLock struct has three fields, which also have their
        // own fields, etc).
        self.graph
            .par_iter()
            .map(|prod| {
                // Using non-parallel iterators here because dependencies per product grow
                // logarithmically in relation to the total number of products in an economy
                // and thus there will not be a large enough number of dependencies to justify
                // multithreading overhead.
                prod.dependencies.iter().fold(0.0, |acc, dep| {
                    let dep_cost = self.graph[dep.id].direct_cost + indir_costs_old[dep.id];
                    acc + (dep.quantity * dep_cost)
                })
            })
            .collect_into_vec(indir_costs_new);
    }

    /// Multiple iterations of the iterative estimation for indirect costs. Performs count number of
    /// iterations and then returns the final estimates. With each iteration, the estimates become
    /// more precise. ~15 iterations gives a good estimate, ~25 is better, and ~50 is extremely precise.
    /// More iterations are needed to get accurate results if any Product depends directly or indirectly
    /// on quantities of itself that approach 1.0. For instance, if corn depends on 0.01 of itself, 15 iterations
    /// should give a good result. However, if it depends on 0.9 of itself, it could take 50 iterations
    /// to be sure.
    pub fn calc_for_n_iterations(&self, n: u16) -> Vec<f32> {
        let indir_costs = &mut vec![0.0; self.graph.len()];
        let indir_costs_copy = &mut vec![0.0; self.graph.len()];
        for _ in 0..n {
            self.calc_iteration(indir_costs, indir_costs_copy);
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
        // Checking for obvious issues
        // TODO: this code could be made a bit less procedural?
        let mut out_of_bounds = Vec::new();
        let mut negative_value = Vec::new();
        let mut infinite = Vec::new();
        for (i, p) in self.graph.iter().enumerate() {
            if p.direct_cost < 0.0 {
                negative_value.push(i);
            }
            if p.direct_cost == f32::INFINITY {
                infinite.push(i);
            }
            for d in p.dependencies.iter() {
                if d.id >= self.graph.len() {
                    out_of_bounds.push(i);
                }
                if d.quantity < 0.0 {
                    negative_value.push(i);
                }
                if d.quantity == f32::INFINITY || (d.id == i && d.quantity >= 1.0) {
                    infinite.push(i);
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
        let indir_costs = &mut vec![0.0; self.graph.len()];
        let indir_costs_copy = &mut vec![0.0; self.graph.len()];
        let mut increments_gather = || {
            self.calc_iteration(indir_costs, indir_costs_copy);
            let increments = indir_costs
                .par_iter()
                .zip_eq(indir_costs_copy.par_iter())
                .map(|(r1, r2)| r2 - r1)
                .collect::<Vec<f32>>();
            mem::swap(indir_costs, indir_costs_copy);
            increments
        };
        increments_gather(); // Throw away first result as it involves the 0.0 initialized vec
        let increments1 = increments_gather();
        let increments2 = increments_gather();

        let prods_in_infinite_cycles: Vec<usize> = increments1
            .par_iter()
            .zip_eq(increments2.par_iter())
            .enumerate()
            .filter_map(|(i, (increment1, increment2))| {
                if increment1 <= increment2 && *increment2 != 0.0 {
                    Some(i)
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

    /// Create a graph with a specified initial capacity. The capacity is not the size of the
    /// graph, but the amount of memory that is pre-allocated.
    pub fn with_capacity(size: usize) -> ProductGraph {
        ProductGraph {
            graph: Vec::with_capacity(size),
        }
    }

    /// Create a ProductGraph from a plain Vec of Products.
    pub fn from_raw_graph(graph: Vec<Product>) -> ProductGraph {
        ProductGraph { graph }
    }

    /// Add a Product to the ProductGraph. Because Products are IDed by Vector index, be careful to
    /// insert them in the correct order.
    pub fn push(&mut self, prod: Product) {
        self.graph.push(prod);
    }

    /// Create a dependency for a Product in the graph.
    pub fn set_dependency(&mut self, dependant: usize, dependency: usize, quantity: f32) {
        let deps = &mut self.graph[dependant].dependencies;
        // TODO: test if .find() works
        match deps.iter().position(|d| d.id == dependency) {
            Some(i) => deps[i].quantity = quantity,
            None => {
                deps.push(Dependency {                    id: dependency,
                    quantity,
                });
                deps.shrink_to_fit();
            }
        }
    }

    // TODO: batch dependency setting, removers, getters etc...


    /// Generate a random product graph for testing and benchmarking purposes.
    pub fn generate_product_graph(count: usize) -> ProductGraph {
        let mut rng = rand::thread_rng();
        let mut prods = ProductGraph::from_raw_graph(vec![Product::new(10.0); count]);
        for i in 0..(count / 2) {
            for _ in 0..8 {
                prods.set_dependency(i, rng.gen_range(count / 2, count), 0.00000000001);
            }
        }
        for i in (count / 2)..count {
            for _ in 0..8 {
                prods.set_dependency(i, rng.gen_range(0, count / 2), rng.gen_range(0.01, 5.0));
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
        let mut prods = ProductGraph::from_raw_graph(vec![Product::new(10.0)]);
        prods.set_dependency(0, 0, 1.0);
        let result = prods.check_graph();
        match result {
            Ok(()) => panic!(),
            Err(e) => assert_eq!(0, e.prods_in_inf_cycles[0]),
        }
    }

    #[test]
    fn detects_indirect_infinite_cycle() {
        let mut prods = ProductGraph::with_capacity(3);
        for _ in 0..3 {
            prods.push(Product::new(10.0));
        }
        prods.set_dependency(0, 1, 0.5);
        prods.set_dependency(0, 2, 0.5);
        prods.set_dependency(2, 0, 1.0);
        prods.set_dependency(1, 0, 1.0);

        let result = prods.check_graph();
        match result {
            Ok(()) => panic!(),
            Err(e) => {
                assert_eq!(vec![0, 1, 2], e.prods_in_inf_cycles);
            }
        }
    }

    #[test]
    fn calculates_correct_values_without_indirection() {
        let mut prods = ProductGraph::with_capacity(2);
        for _ in 0..2 {
            prods.push(Product::new(10.0));
        }
        prods.set_dependency(0, 1, 10.0);
        prods.check_graph().unwrap();

        let indirect_costs = prods.calc_for_n_iterations(50);
        assert_eq!(indirect_costs[0], 100.0);
        assert_eq!(indirect_costs[1], 0.0);
    }

    #[test]
    fn calculates_correct_values_with_indirection() {
        let mut prods = ProductGraph::with_capacity(2);
        for _ in 0..4 {
            prods.push(Product::new(10.0));
        }
        prods.set_dependency(1, 0, 1.0);
        prods.set_dependency(2, 0, 1.0);
        prods.set_dependency(2, 1, 1.0);
        prods.set_dependency(3, 2, 1.0);
        prods.check_graph().unwrap();

        let indirect_costs = prods.calc_for_n_iterations(50);
        assert_eq!(vec![0.0, 10.0, 30.0, 40.0], indirect_costs);
    }

    #[test]
    fn generates_random_graph_without_errors() {
        let prods = ProductGraph::generate_product_graph(100);
        prods.check_graph().unwrap();
    }
}
