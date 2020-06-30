# ProductionGraph
ProductionGraph is a set of programs for estimating costs and labor hours of commodities. 


### ProductionGraph components:

#### production_graph_rs
The 'production_graph_rs' folder contains a high-performance Rust library that performs the estimation. It represents production of commodities as a dependency graph. Each commodity has a "direct cost," which could be labor or wages used directly in its production, and a list of dependencies and their associated quantities, which represent other commodities in the graph that the commodity depends on. The library is documented here:

https://docs.rs/product_graph_rs/0.1.0/product_graph_rs/product_graph_rayon/index.html

And is available on crates.io:

https://crates.io/crates/product_graph_rs

In order to build and test the library individually, enter its directory and use the following commands:
```bash
// Build library
cargo build
// Test library
cargo test
// Benchmark library (Warning, heavy memory consumption. Not recommended on a machine without several free GB of RAM.)
cargo run --release
```

#### product_graph_py
The 'product_graph_py' directory contains code for thin Python bindings that make it possible for python programs, such as the backend, to use the rust library. The bindings are on PyPI:

https://pypi.org/project/product_graph_bindings/


### Development info

Development Startup Procedure:

```bash
// initial start up

$ pip3 install --user --requirement requirements.txt
$ python3 manage.py tailwind install


// general start up

$ python3 manage.py tailwind start
$ python3 manage.py runserver

// building tailwind for production

$ python manage.py tailwind build
```

`tailwind start` command watches for changes to recompile css during development, so should be run concurrently with runserver command.

Testing Procedure:

```bash
// Run all tests
$ python3 manage.py test backend.tests

// Run specific test
$ python3 manage.py test backend.tests.test_urls
```
