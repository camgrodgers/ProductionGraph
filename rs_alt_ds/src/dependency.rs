/// id: id from database
/// quantity: required amt for product
#[derive(Clone, Debug)]
pub struct Dependency {
    pub id: u64,
    pub quantity: f32,
}