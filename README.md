<p align="center">
  <img src="https://github.com/camgrodgers/ProductionGraph/raw/camgrodgers-edit-readme/logo.png" />
</p>

# ProductionGraph

ProductionGraph is a web service for estimating total costs and labor hours of commodities, and testing the results against real data.
Github link:
https://github.com/camgrodgers/ProductionGraph

### ProductionGraph components:

#### package

The 'package' directory contains the Django project from the 'backend' folder, structured for purposes of installation via pip. It can be installed either by entering the directory and executing:

```
pip install .
```

Or via PyPI (https://pypi.org/project/productiongraph/):

```
pip install productiongraph==0.2.0
```

Once the server is installed via pip, a number of commands will be available for initializing and running the server:

```
// Set up the database and run the server in one command
prodgraph_migrate_and_run
// Set up the database
prodgraph_init
// Run the server
prodgraph_run
// Run tests
prodgraph_tests
```

#### backend

The 'backend' directory contains a Django project that allows users to enter products and their associated direct costs and dependencies. As the user enters data, the server automatically calculates and displays indirect wages, indirect labor times, total estimated costs, and total estimated labor times.

#### production_graph_rs

The 'production_graph_rs' folder contains a high-performance Rust library that performs the estimation. It represents production of commodities as a dependency graph. The library is documented here:

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

Note: this is not presently part of the same build process as the server, as changes in the library should not be automatically applied to the server's codebase and build process.

#### rs_alt_ds

The 'rs_alt_ds' directory contains a port of the rust library from 'production_graph_rs' to using a hashmap. This was created for benchmarking purposes. It was found that the hashmap version had significantly higher overhead than an array-backed version.

#### product_graph_py

The 'product_graph_py' directory contains code for thin Python bindings that make it possible for python programs, such as the backend, to use the rust library. The bindings are on PyPI:

https://pypi.org/project/product_graph_bindings/

Note: building this is not presently part of the same build process as the server, as changes in the library should not be automatically applied to the server's codebase and build process.

### Web interface usage

#### Basics
In order to begin entering data, you must create an account and log in. Once logged in, you can create, view, edit, and delete Products and their Dependencies.

#### Error checking
If you create any Products that depend on themselves in a quantity of 1.0 or more, directly or indirectly, the program will display an error warning and direct you to fix the error. This can be used to detect bad data entry, or to detect crisis situations in an economy. 

#### Commit history
You can record the current state of the graph as a point in history, to keep track of the history of changes to prices and labor times. Multiple states can be logged in the history. 

#### Analytics
Once you have entered three or more Products with three or more history points, you can click the analytics button on any individual product page to view the history of its prices as a chart. 
This chart will also display the correlation rates between labor time and the real price, and estimated price and the real price.
Another chart will be viewable from the Product listing page, which plots the same variables for the entire current set of Product data rather than a historical dataset for one single Product.
If the correlations are high, then the dataset is in line with Smith's value theory. A real-world dataset could be entered and used in this manner to empirically test the theory of value.

### Development info

Development Startup Procedure:

```bash
// initial start up

$ pip3 install --user --requirement requirements.txt
$ python3 manage.py tailwind install


// general start up

$ python3 manage.py tailwind start
$ python3 manage.py runserver

// or all at once
$ python3 manage.py tailwind start & python3 manage.py runserver

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

## Our Team 

| **Project Manager** | **Dev Team** | **Dev Team** | **Dev Team** | **Dev Team** | 
| :---: |:---:| :---:| :---:| :---:| 
| [![Cameron Rodgers]( https://avatars0.githubusercontent.com/u/46136660?s=400&u=7d086b2b4187b862e854c751cc02d4f00358eaf5&v=4)]( https://github.com/camgrodgers) | [![Aaron Leopold]( https://avatars3.githubusercontent.com/u/36278431?s=400&u=e081a3c4c5721096cfff9a7f8399eeeee0026338&v=4)]( https://github.com/aaronleopold) | [![Benjamin Rheault]( https://avatars0.githubusercontent.com/u/44026930?s=400&v=4)]( https://github.com/bhreault) | [![Matthew Petela]( https://avatars2.githubusercontent.com/u/25089614?s=400&v=4)]( http://github.com/matthewpetela) | [![Osiris Villacampa]( https://avatars0.githubusercontent.com/u/44124858?s=400&v=4&s=200)]( http://github.com/ovillacampa) 
| ` github.com/camgrodgers` | ` github.com/aaronleopold` | ` github.com/bhreault` | ` github.com/matthewpetela` | ` github.com/ovillacampa` | 
