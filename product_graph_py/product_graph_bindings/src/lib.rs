use product_graph_rs::*;
use pyo3::prelude::*;
use pyo3::wrap_pyfunction;
use std::collections::HashMap;

/*
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
    direct_labor: f32,
    dependencies: Vec<(String, f32)>,
}

#[pymethods]
impl SimpleProduct {
    #[new]
    fn new(direct_labor: f32, dependencies: Vec<(String, f32)>) -> SimpleProduct {
        SimpleProduct {
            direct_labor,
            dependencies,
        }
    }

    #[getter(direct_labor)]
    fn get_direct_labor(&self) -> f32 {
        self.direct_labor
    }
    #[setter(direct_labor)]
    fn set_direct_labor(&mut self, direct_labor: f32) {
        self.direct_labor = direct_labor;
    }
}

#[pyfunction]
fn calc_indirect_vals_for_n_iterations(
    graph: HashMap<String, SimpleProduct>,
    count: u16,
) -> Vec<(String, f32)> {
    // NOTE: ugly, bad for memory... maybe these maps should share data via reference or use bimap
    let indexes: HashMap<String, usize> = graph
        .keys()
        .enumerate()
        .map(|(i, k)| (k.clone(), i))
        .collect();
    let names: HashMap<usize, String> = graph
        .keys()
        .enumerate()
        .map(|(i, k)| (i, k.clone()))
        .collect();
    let mut new_graph = ProductGraph::with_capacity(graph.len());
    for (i, (_, p)) in graph.iter().enumerate() {
        new_graph.push(Product::new(p.direct_labor));
        for (s, quant) in p.dependencies.iter() {
            new_graph.set_dependency(i, indexes[s], *quant);
        }
    }

    match new_graph.check_graph() {
        Ok(()) => (),
        Err(_) => {
            return Vec::new();
        }
    }

    let indirect_costs = new_graph.calc_for_n_iterations(count);
    let indirect_costs: Vec<(String, f32)> = indirect_costs
        .iter()
        .enumerate()
        .map(|(i, quant)| (names[&i].clone(), *quant))
        .collect();
    indirect_costs
}

#[pyfunction]
fn sum_vec(a: Vec<i32>) -> i32 {
    a.iter().sum()
}

#[pymodule]
fn product_graph_bindings(py: Python, m: &PyModule) -> PyResult<()> {
    m.add_wrapped(wrap_pyfunction!(sum_vec))?;
    m.add_wrapped(wrap_pyfunction!(calc_indirect_vals_for_n_iterations))?;
    m.add_class::<SimpleProduct>()?;

    Ok(())
}
