use pyo3::prelude::*;
use pyo3::wrap_pyfunction;

#[pyfunction]
fn sum_vec(a: Vec<i32>) -> i32 {
    a.iter().sum()
}

#[pymodule]
fn arr_sum(py: Python, m: &PyModule) -> PyResult<()> {
    m.add_wrapped(wrap_pyfunction!(sum_vec))?;

    Ok(())
}
