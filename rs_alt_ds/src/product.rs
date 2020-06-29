use std::f32;
use crate::dependency::Dependency;
#[derive(Clone, Debug)]
pub struct Product {
    pub id: u64,
    pub direct_cost: f32,
    pub dependencies: Vec<Dependency>,
}

// TODO: improve ergonomics for adding data
impl Product {
    /// Create a new Product with a given direct cost.
    pub fn new(id: u64, direct_cost: f32) -> Product {
        Product {
            id,
            direct_cost,
            dependencies: Vec::new(),
            // research how much performace would actually be gained by switching 
            // to a hashmap for deps as well, the potential performance bump would
            // be from Product::set_dependency, where instead of iteration you could 
            // have a statement such as deps.entry(&id).or_insert(dep)
        }
    }

    /// Product::update_cost will update the direct_cost of the product given passed in
    /// parameter 'direct_cost'
    // Note: not really sure this function is necessary
    pub fn update_cost(&mut self, direct_cost: f32) {
        self.direct_cost = direct_cost
    }

    /// Product::set_dependency will set the quantity of a dependency
    /// if it already exists (based on id), or will push a new dependency given 
    /// it doesn't already exist in the product's dependencies vector.
    pub fn set_dependency(&mut self, dep_id: u64, dep_quantity: f32) {
        let deps = &mut self.dependencies;
        match deps.iter().position(|d| d.id == dep_id) {
            Some(i) => deps[i].quantity = dep_quantity,
            None => {
                deps.push(Dependency {
                    id: dep_id,
                    quantity: dep_quantity
                });
                deps.shrink_to_fit();
            }
        }
    }
}