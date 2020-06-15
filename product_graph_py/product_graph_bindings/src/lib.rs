use pyo3::prelude::*;
use pyo3::wrap_pyfunction;
use std::collections::HashMap;

#[pyclass]
#[derive(Clone)]
struct ProductGraphMap {
    graph: HashMap<String, Product>
}

#[pyclass]
#[derive(Clone)]
struct Product { 
    direct_labor: f32,
    dependencies: Vec<(String, f32)>,
}

#[pymethods]
impl Product {
    #[new]
    fn new(direct_labor: f32, dependencies: Vec<(String, f32)>) -> Product {
        Product {
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
fn calc_indirect_vals_for_n_iterations(graph: ProductGraphMap, count: u16) -> Vec<(String, f32)> {
    vec![("asdf".into(), 1.0)]
}



#[pyfunction]
fn sum_vec(a: Vec<i32>) -> i32 {
    a.iter().sum()
}

#[pymodule]
fn arr_sum(py: Python, m: &PyModule) -> PyResult<()> {
    m.add_wrapped(wrap_pyfunction!(sum_vec))?;
    m.add_wrapped(wrap_pyfunction!(calc_indirect_vals_for_n_iterations))?;
    m.add_class::<Product>()?;
    m.add_class::<ProductGraphMap>()?;

    Ok(())
}
