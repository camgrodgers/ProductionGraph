use rand::Rng;
use rayon::prelude::*;

/// The Product struct represents the non-computable data for a product in real life.
/// For example, a cup of lemonade could have a direct cost of $0.1 in wages, or 0.1 in labor hours,
/// and could depend on 0.8 cups of water, 0.1 cup lemon juice, and 0.1 cup of sugar.
/// However, the total cost of the lemonade is unknown at this point, as the indirect costs of all
/// the products in the graph depend on each other, cyclically and acyclically.
/// The Product struct is intended to be used as part of the ProductGraph to calculate the unknown
/// indirect costs.
// TODO: generics?
pub struct Product {
    pub direct_cost: f32,
    pub dependencies: Vec<Dependency>,
}

// TODO: improve ergonomics for adding data
impl Product {
    /// Create a new Product with a given direct cost.
    // TODO: should this check the cost too?
    pub fn new(direct_cost: f32) -> Self {
        Product {
            direct_cost: direct_cost,
            dependencies: Vec::new(),
        }
    }

    /// Replace the current list of dependencies for the Product with a new list.
    pub fn set_dependencies(&mut self, deps: Vec<Dependency>) {
        self.dependencies = deps;
    }
}

/// The Dependency struct contains an index for a dependency in the array-backed graph, and the
/// quantity that is depended on.
pub struct Dependency {
    id: usize,
    quantity: f32,
}

/// The ProductGraph is a Vector-backed graph of Products. The Products are the graph nodes, and
/// the dependencies are weighted, directed edges. The "key" or "id" of each Product is its index
/// in the Vector. This graph is specialized for the purpose of rapidly estimating indirect costs.
pub struct ProductGraph {
    graph: Vec<Product>,
}

pub struct GraphError {
    pub prods_in_inf_cycles: Option<Vec<usize>>,
    pub out_of_bounds_dependency: Option<Vec<usize>>,
    pub negative_quantity: Option<Vec<usize>>,
}

impl ProductGraph {
    /// One iteration of the iterative estimation algorithm for indirect costs. Takes in the graph,
    /// and returns the estimated indirect costs, associated with each product in the graph by index.
    fn calc_iteration(&self, indir_costs_old: &Vec<f32>) -> Vec<f32> {
        // NOTE: allocates new memory each iteration. This is the tradeoff for getting free
        // multithreading from Rayon and appeasing the borrow checker. Because it is only a Vec
        // of f32, it is not a large memory allocation relative to the graph, but it is
        // expensive compared to in-place mutation or a rotating pair of buffers.
        self.graph
            .par_iter()
            .map(|prod| {
                // Using non-parallel iterators here because dependencies per product grow
                // logarithmically in relation to the total number of products in an economy
                // and thus there will not be a large enough number of dependencies to justify
                // multithreading.
                prod.dependencies.iter().fold(0.0, |acc, dep| {
                    let dep_cost = self.graph[dep.id].direct_cost + indir_costs_old[dep.id];
                    acc + dep.quantity * dep_cost
                })
            })
            .collect()
    }

    /// Multiple iterations of the iterative estimation for indirect costs. Performs count number of
    /// iterations. With each iteration, the estimates become more precise. ~15 iterations gives a
    /// good estimate, ~25 is better, and ~50 is extremely precise. More iterations are needed to
    /// get accurate results if any Product depends directly or indirectly on values that approach
    /// 1.0. For instance, if corn depends on 0.01 of itself, 15 iterations should give a good
    /// result. However, if it depends on 0.9 of itself, it could take 50 iterations to be sure.
    pub fn calc_for_n_iterations(&self, count: u16) -> Vec<f32> {
        let mut indir_costs = vec![0.0; self.graph.len()];
        for _ in 0..count {
            indir_costs = self.calc_iteration(&indir_costs);
        }
        indir_costs
    }

    /// Check the graph for errors in the dataset. If a Product depends directly or indirectly on
    /// 1.0 or more of itself, this represents either bad data or a broken economy, as it will cause
    /// the price of that Product and those that depend on it to go to infinity.
    pub fn check_graph(&self) -> Result<(), GraphError> {
        let result1 = self.calc_iteration(&vec![0.0; self.graph.len()]);
        let result2 = self.calc_iteration(&result1);
        let result3 = self.calc_iteration(&result2);
        let increments1 = Self::diff_results(&result1, &result2);
        let increments2 = Self::diff_results(&result2, &result3);

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
                prods_in_inf_cycles: Some(prods_in_infinite_cycles),
                out_of_bounds_dependency: None,
                negative_quantity: None,
            })
        }
    }

    // Helper function for check_graph()
    fn diff_results(results1: &Vec<f32>, results2: &Vec<f32>) -> Vec<f32> {
        results1
            .par_iter()
            .zip_eq(results2.par_iter())
            .map(|(result1, result2)| result2 - result1)
            .collect()
    }

    pub fn with_capacity(size: usize) -> Self {
        ProductGraph {
            graph: Vec::with_capacity(size),
        }
    }

    pub fn from_raw_graph(graph: Vec<Product>) -> Self {
        ProductGraph { graph: graph }
    }

    pub fn push(&mut self, prod: Product) {
        self.graph.push(prod);
    }

    pub fn set_dependency(
        &mut self,
        dependant: usize,
        dependency: usize,
        quantity: f32,
    ) -> Result<(), ()> {
        if dependant >= self.graph.len()
            || (dependency == dependant && quantity >= 1.0)
            || dependency >= self.graph.len()
            || quantity < 0.0
            || quantity == f32::INFINITY
        {
            return Err(());
        }

        let dep = Dependency {
            id: dependency,
            quantity: quantity,
        };

        self.graph[dependant].dependencies.push(dep);
        self.graph[dependant].dependencies.shrink_to_fit();
        Ok(())
    }

    /// Generate a random product graph for testing and benchmarking purposes.
    pub fn generate_product_graph(count: usize) -> ProductGraph {
        let mut rng = rand::thread_rng();

        let mut prods = ProductGraph::with_capacity(count);
        for _ in 0..(count / 2) {
            let c = Product {
                direct_cost: rng.gen_range(0.01, 10.0),
                dependencies: Vec::new(),
            };
            prods.graph.push(c);
        }
        for _ in (count / 2)..count {
            let mut deps = Vec::with_capacity(7);
            for _ in 0..7 {
                deps.push(Dependency {
                    id: rng.gen_range(0, count / 2),
                    quantity: rng.gen_range(0.01, 10.0),
                });
            }
            let c = Product {
                direct_cost: rng.gen_range(0.01, 10.0),
                dependencies: deps,
            };
            prods.graph.push(c);
        }

        prods
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn detects_direct_infinite_cycle() {
        //let prod = Product::new(10.0)
        //    .add_dependencies(vec![Dependency{ id: 0, quantity: 1.0}]);
        let prod = Product {
            direct_cost: 10.0,
            dependencies: vec![Dependency {
                id: 0,
                quantity: 1.0,
            }],
        };
        let prods = ProductGraph { graph: vec![prod] };
        let result = prods.check_graph();
        match result {
            Ok(()) => panic!(),
            Err(e) => assert_eq!(0, e.prods_in_inf_cycles.unwrap()[0]),
        }
    }

    #[test]
    fn calculates_correct_values_without_indirection() {
        let mut prods = ProductGraph::with_capacity(2);
        for _ in 0..2 {
            let prod = Product::new(10.0);
            prods.push(prod);
        }
        prods.set_dependency(0, 1, 10.0).unwrap();
        let indirect_costs = prods.calc_for_n_iterations(50);
        assert_eq!(indirect_costs[0], 100.0);
        assert_eq!(indirect_costs[1], 0.0);
    }

    #[test]
    fn detects_indirect_infinite_cycle() {
        let mut prods = ProductGraph::with_capacity(3);
        for _ in 0..3 {
            let prod = Product::new(10.0);
            prods.push(prod);
        }
        prods.set_dependency(0, 1, 0.5).unwrap();
        prods.set_dependency(0, 2, 0.5).unwrap();
        prods.set_dependency(2, 0, 1.0).unwrap();
        prods.set_dependency(1, 0, 1.0).unwrap();

        let result = prods.check_graph();
        match result {
            Ok(()) => panic!(),
            Err(e) => {
                let v = vec![0, 1, 2];
                assert_eq!(v, e.prods_in_inf_cycles.unwrap());
            }
        }
    }

    #[test]
    fn calculates_correct_values_with_indirection() {
        let mut prods = ProductGraph::with_capacity(2);
        for _ in 0..4 {
            let prod = Product::new(10.0);
            prods.push(prod);
        }
        prods.set_dependency(1, 0, 1.0).unwrap();
        prods.set_dependency(2, 0, 1.0).unwrap();
        prods.set_dependency(2, 1, 1.0).unwrap();
        prods.set_dependency(3, 2, 1.0).unwrap();

        let indirect_costs = prods.calc_for_n_iterations(50);
        assert_eq!(0.0, indirect_costs[0]);
        assert_eq!(10.0, indirect_costs[1]);
        assert_eq!(30.0, indirect_costs[2]);
        assert_eq!(40.0, indirect_costs[3]);
    }
}
