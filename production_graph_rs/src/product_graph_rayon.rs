use rand::Rng;
use rayon::prelude::*;

// TODO: generics?
pub struct Product {
    pub direct_cost: f32,
    pub dependencies: Vec<Dependency>,
}

// TODO: improve ergonomics for adding data
impl Product {
    pub fn new(direct_cost: f32) -> Self {
        Product {
            direct_cost: direct_cost,
            dependencies: Vec::new(),
        }
    }

    pub fn set_dependencies(&mut self, deps: Vec<Dependency>) {
        self.dependencies = deps;
    }
}

pub struct Dependency {
    id: usize,
    quantity: f32,
}

pub struct ProductGraph {
    graph: Vec<Product>,
}

pub struct GraphError {
    pub prods_in_inf_cycles: Option<Vec<usize>>,
    pub out_of_bounds_dependency: Option<Vec<usize>>,
    pub negative_quantity: Option<Vec<usize>>,
}

impl ProductGraph {
    fn calc_iteration(&self, indir_costs_old: &Vec<f32>) -> Vec<f32> {
        let indir_costs_new: Vec<f32> = self
            .graph
            .par_iter()
            .map(|prod| {
                prod.dependencies.iter().fold(0.0, |acc, dep| {
                    let dep_cost = self.graph[dep.id].direct_cost + indir_costs_old[dep.id];
                    acc + dep.quantity * dep_cost
                })
            })
            .collect();
        indir_costs_new
    }

    pub fn calc_for_n_iterations(&self, count: u16) -> Vec<f32> {
        let mut indir_costs = vec![0.0; self.graph.len()];
        for _ in 0..count {
            indir_costs = self.calc_iteration(&indir_costs);
        }
        indir_costs
    }

    pub fn check_graph(&self) -> Result<(), GraphError> {
        let result1 = self.calc_iteration(&vec![0.0; self.graph.len()]);
        let result2 = self.calc_iteration(&result1);
        let result3 = self.calc_iteration(&result2);
        let increments1 = Self::diff_results(&result1, &result2);
        let increments2 = Self::diff_results(&result2, &result3);

        let prods_in_infinite_cycles: Vec<usize> = increments1
            .par_iter()
            .zip(increments2.par_iter())
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

    fn diff_results(results1: &Vec<f32>, results2: &Vec<f32>) -> Vec<f32> {
        results1
            .par_iter()
            .zip(results2.par_iter())
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

    fn set_dependency(
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

    // NOTE: This test is no longer relevant to public API
    #[test]
    fn detects_direct_infinite_cycle() {
        //let prod = Product::new(10.0)
        //    .add_dependencies(vec![Dependency{ id: 0, quantity: 1.0}]);
        let prod = Product {
            direct_cost: 10.0,
            dependencies: vec![Dependency{ id: 0, quantity: 1.0}]
        };
        let prods = ProductGraph {
            graph: vec![prod]
        };
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
            let mut prod = Product::new(10.0);
            prods.push(prod);
        }
        prods.set_dependency(0, 1, 10.0).unwrap();
        let indirect_costs = ProductGraph::calc_for_n_iterations(&mut prods, 50);
        assert_eq!(indirect_costs[0], 100.0);
        assert_eq!(indirect_costs[1], 0.0);
    }
    /*
    #[test]
    fn detects_indirect_infinite_cycle() {
        let mut prods = ProductGraph::with_capacity(3);
        for _ in 0..3 {
            let mut prod = Product::new();
            prod.set_direct_cost(10.0).unwrap();
            prods.push(prod);
        }
        prods.set_dependency(0, 1, 0.5).unwrap();
        prods.set_dependency(0, 2, 0.5).unwrap();
        prods.set_dependency(2, 0, 1.0).unwrap();
        prods.set_dependency(1, 0, 1.0).unwrap();

        let result = ProductGraph::detect_impossible_cycles(&prods);
        match result {
            Ok(()) => panic!(),
            Err(e) => {
                let v = vec![0, 1, 2];
                assert_eq!(v, e.prods_in_cycles);
            }
        }
    }


    #[test]
    fn calculates_correct_values_with_indirection() {
        let mut prods = ProductGraph::with_capacity(2);
        for _ in 0..4 {
            let mut prod = Product::new();
            prod.set_direct_cost(10.0).unwrap();
            prods.push(prod);
        }
        prods.set_dependency(1, 0, 1.0).unwrap();
        prods.set_dependency(2, 0, 1.0).unwrap();
        prods.set_dependency(2, 1, 1.0).unwrap();
        prods.set_dependency(3, 2, 1.0).unwrap();

        ProductGraph::calc_for_n_iterations(&mut prods, 50);
        //TODO: Need a getter for graph indexes
        assert_eq!(0.0, prods.graph[0].indirect_cost);
        assert_eq!(10.0, prods.graph[1].indirect_cost);
        assert_eq!(30.0, prods.graph[2].indirect_cost);
        assert_eq!(40.0, prods.graph[3].indirect_cost);
    }
    */
}
