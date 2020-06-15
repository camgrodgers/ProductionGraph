use rand::Rng;
use std::error;
use std::f32;
use std::fmt;

#[derive(Clone)]
pub struct ProductGraph {
    graph: Vec<Product>,
}

impl ProductGraph {
    pub fn with_capacity(size: usize) -> Self {
        ProductGraph {
            graph: Vec::with_capacity(size),
        }
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

        let dep = DependencyInfo {
            id: dependency,
            quantity,
        };

        self.graph[dependant].dependencies.push(dep);
        self.graph[dependant].dependencies.shrink_to_fit();
        Ok(())
    }

    fn calc_iteration(&mut self, track_increments: bool) -> Vec<f32> {
        let mut increments = if track_increments {
            vec![0.0; self.graph.len()]
        } else {
            Vec::new()
        };

        for i in 0..self.graph.len() {
            let mut indirect_cost = 0.0;
            for depinfo in &self.graph[i].dependencies {
                let dep = &self.graph[depinfo.id];
                indirect_cost += depinfo.quantity * (dep.direct_cost + dep.indirect_cost);
            }
            if track_increments {
                increments[i] = indirect_cost - self.graph[i].indirect_cost;
            }
            self.graph[i].indirect_cost = indirect_cost;
        }
        increments
    }

    pub fn calc_for_n_iterations(&mut self, count: u16) {
        for p in self.graph.iter_mut() {
            p.indirect_cost = 0.0;
        }

        for _ in 0..count {
            self.calc_iteration(false);
        }
    }

    // NOTE: No product can depend on 1.0 or more of itself.
    // Note: this function gets a "broader sweep" when it is run after more increments or when
    // dependencies on prods in impossible cycles are a higher quantity
    pub fn detect_impossible_cycles(prods: &ProductGraph) -> Result<(), InfiniteValueError> {
        let mut prods = prods.clone();

        // increments in first iteration may be smaller than the next due to doubly indirect costs
        prods.calc_iteration(false);
        let increments1 = prods.calc_iteration(true);
        let increments2 = prods.calc_iteration(true);

        let mut prods_in_cycles = Vec::new();
        for i in 0..increments1.len() {
            if increments1[i] <= increments2[i] && increments2[i] != 0.0 {
                prods_in_cycles.push(i);
            }
        }

        if prods_in_cycles.len() == 0 {
            Ok(())
        } else {
            Err(InfiniteValueError {
                prods_in_cycles,
            })
        }
    }

    // Issue: it's tough to generate a graph that's possible in reality and/or the calculation method
    // For testing purposes, generating a graph that can't have cyclical dependencies
    pub fn generate_product_graph(count: usize) -> ProductGraph {
        let mut rng = rand::thread_rng();
        let mut prods = ProductGraph {
            graph: vec![
                Product {
                    direct_cost: 10.0,
                    indirect_cost: 0.0,
                    dependencies: Vec::new()
                };
                count
            ],
        };
        for i in 0..(count / 2) {
            for _ in 0..8 {
                prods
                    .set_dependency(i, rng.gen_range(count / 2, count), 0.00000000001)
                    .unwrap();
            }
        }
        for i in (count / 2)..count {
            for _ in 0..8 {
                prods
                    .set_dependency(i, rng.gen_range(0, count / 2), rng.gen_range(0.01, 5.0))
                    .unwrap();
            }
        }

        prods
    }
}

#[derive(Debug, Clone)]
pub struct InfiniteValueError {
    pub prods_in_cycles: Vec<usize>,
}

impl error::Error for InfiniteValueError {
    fn source(&self) -> Option<&(dyn error::Error + 'static)> {
        None
    }
}
impl fmt::Display for InfiniteValueError {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        write!(f, "ProductGraph contained dependency cycle where product depends on 1.0 or more of itself.")
    }
}

#[derive(Clone)]
pub struct Product {
    direct_cost: f32,
    // NOTE: indirect_cost must always be reset to zero after other values are changed
    indirect_cost: f32,
    dependencies: Vec<DependencyInfo>,
}

#[derive(Clone)]
pub struct DependencyInfo {
    id: usize,
    quantity: f32,
}

impl Product {
    pub fn new() -> Self {
        Product {
            direct_cost: 0.0,
            indirect_cost: 0.0,
            dependencies: Vec::new(),
        }
    }

    pub fn set_direct_cost(&mut self, new_val: f32) -> Result<(), ()> {
        match Product::check_value(new_val) {
            Ok(()) => {
                self.direct_cost = new_val;
                Ok(())
            }
            Err(()) => Err(()),
        }
    }

    pub fn direct_cost(&self) -> f32 {
        self.direct_cost
    }

    pub fn set_indirect_cost(&mut self, new_val: f32) -> Result<(), ()> {
        match Product::check_value(new_val) {
            Ok(()) => {
                self.indirect_cost = new_val;
                Ok(())
            }
            Err(()) => Err(()),
        }
    }

    pub fn indirect_cost(&self) -> f32 {
        self.indirect_cost
    }

    fn check_value(val: f32) -> Result<(), ()> {
        if val < 0.0 || val == f32::INFINITY {
            Err(())
        } else {
            Ok(())
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    //use test::Bencher;

    #[test]
    fn detects_direct_infinite_cycle() {
        let mut prods = ProductGraph::with_capacity(1);
        let mut prod = Product::new();
        prod.set_direct_cost(10.0).unwrap();
        prod.dependencies.push(DependencyInfo {
            id: 0,
            quantity: 1.0,
        });
        prods.push(prod);
        // NOTE: This line is now unneeded because set_dependency prevents direct infinite loops
        //prods.set_dependency(0, 0, 1.0).unwrap();
        let result = ProductGraph::detect_impossible_cycles(&prods);
        match result {
            Ok(()) => panic!(),
            Err(e) => assert_eq!(0, e.prods_in_cycles[0]),
        }
    }

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
    fn calculates_correct_values_without_indirection() {
        let mut prods = ProductGraph::with_capacity(2);
        for _ in 0..2 {
            let mut prod = Product::new();
            prod.set_direct_cost(10.0).unwrap();
            prods.push(prod);
        }
        prods.set_dependency(0, 1, 10.0).unwrap();
        ProductGraph::calc_for_n_iterations(&mut prods, 50);
        assert_eq!(prods.graph[0].indirect_cost, 100.0);
        assert_eq!(prods.graph[1].indirect_cost, 0.0);
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
}
