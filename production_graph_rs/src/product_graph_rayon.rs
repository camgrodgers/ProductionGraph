use rand::Rng;
use rayon::prelude::*;

// TODO: generics
#[derive(Clone)]
pub struct Product {
    direct_cost: f32,
    dependencies: Vec<Dependency>,
}

#[derive(Clone)]
pub struct Dependency {
    id: usize,
    quantity: f32,
}

#[derive(Clone)]
pub struct ProductGraph {
    graph: Vec<Product>,
}

impl ProductGraph {
    fn calc_iteration(&self, indir_costs_old: &Vec<f32>) -> Vec<f32> {
        let mut indir_costs_new = vec![0.0; self.graph.len()];
        
        let indir_costs_new: Vec<f32> = self.graph.par_iter()
            .map(|d| {
                let mut indirect_cost = 0.0;
                for dep in d.dependencies.iter() {
                    let dep_cost = self.graph[dep.id].direct_cost
                        + indir_costs_old[dep.id];
                    indirect_cost += dep.quantity * dep_cost;
                }
                indirect_cost
            })
            .collect();

            /*
        for i in 0..self.graph.len() {
            let mut indirect_cost = 0.0;
            for depinfo in &self.graph[i].dependencies {
                let dep_cost = &self.graph[depinfo.id].direct_cost
                    + indir_costs_old[depinfo.id];
                indirect_cost += depinfo.quantity * dep_cost;
            }
            //if track_increments {
            //    increments[i] = indirect_cost - self.graph[i].indirect_cost;
            //}
            indir_costs_new[i] = indirect_cost;
        }*/




        indir_costs_new
    }

    pub fn calc_for_n_iterations(&self, count: u16) -> Vec<f32> {
        let mut indir_costs = vec![0.0; self.graph.len()];
        for _ in 0..count {
            indir_costs = self.calc_iteration(&indir_costs);
        }
        indir_costs
    }


    pub fn with_capacity(size: usize) -> Self {
        ProductGraph {
            graph: Vec::with_capacity(size),
        }
    }
    
    pub fn from_raw_graph(graph: Vec<Product>) -> Self {
        ProductGraph {
            graph: graph
        }
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

