use product_graph_rs::*;
use pyo3::prelude::*;
use pyo3::wrap_pyfunction;
use std::collections::HashMap;
//use std::time::Instant;

/*
 * TODO: probably implement these
#[pyclass]
#[derive(Clone)]
struct ProductGraphMap {
    graph: HashMap<String, Product>
}

#[pymethods]
impl ProductGraphMap {
    #[new]
    fn new(
}*/

#[pyclass]
#[derive(Clone)]
struct SimpleProduct {
    direct_cost: f32,
    dependencies: Vec<(u64, f32)>,
}

#[pymethods]
impl SimpleProduct {
    #[new]
    fn new(direct_cost: f32, dependencies: Vec<(u64, f32)>) -> SimpleProduct {
        SimpleProduct {
            direct_cost,
            dependencies,
        }
    }

    #[getter(direct_cost)]
    fn get_direct_cost(&self) -> f32 {
        self.direct_cost
    }
    #[setter(direct_cost)]
    fn set_direct_cost(&mut self, direct_cost: f32) {
        self.direct_cost = direct_cost;
    }
}

// TODO: consider returning option type?
#[pyfunction]
fn calc_indirect_vals_for_n_iterations(
    graph: HashMap<u64, SimpleProduct>,
    count: u16,
) -> (Vec<(u64, f32)>, Vec<u64>) {
    // First, converting from a hashmap to the array-backed graph
    // NOTE: ugly, bad for memory... have to hold the IDs in a hashmap for converting back and
    // forth
    let mut ids_to_indexes = HashMap::with_capacity(graph.len());
    let mut indexes_to_ids = HashMap::with_capacity(graph.len());
    let mut new_graph = ProductGraph::with_capacity(graph.len());
    for (i, (k, prod)) in graph.iter().enumerate() {
        ids_to_indexes.insert(k, i);
        indexes_to_ids.insert(i, k);
        new_graph.push(Product::new(prod.direct_cost));
    }
    for (i, prod) in graph.values().enumerate() {
        new_graph.set_dependencies_capacity(i, prod.dependencies.len());
        for (id, quant) in prod.dependencies.iter() {
            new_graph.set_dependency(i, ids_to_indexes[id], *quant);
        }
    }

    match new_graph.check_graph() {
        Ok(()) => (),
        Err(e) => {
            let errors = e.prods_in_inf_cycles.iter().map(|i| *indexes_to_ids[i]).collect();
            return (Vec::new(), errors);
        }
    }

    //let start = Instant::now();
    let indirect_costs = new_graph.calc_for_n_iterations(count);
    let indirect_costs: Vec<(u64, f32)> = indirect_costs
        .iter()
        .enumerate()
        .map(|(i, quant)| (*indexes_to_ids[&i], *quant))
        .collect();
    (indirect_costs, Vec::new())
}

#[pymodule]
fn product_graph_bindings(py: Python, m: &PyModule) -> PyResult<()> {
    m.add_wrapped(wrap_pyfunction!(calc_indirect_vals_for_n_iterations))?;
    m.add_class::<SimpleProduct>()?;

    Ok(())
}
