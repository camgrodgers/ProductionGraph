from django.shortcuts import render,redirect
from django.views.generic import TemplateView
from django.http import HttpResponseRedirect
from .models import Product
from .models import Dependency
from .forms import ProductForm
import product_graph_bindings
from .models import Dependency
from .forms import DependencyForm
from .forms import EditDependencyForm
from .forms import DeleteDependencyForm

### CRUD FOR PRODUCT ###

def create_product(request):
    # handle the post to this url ONLY
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            product = Product(
                name=form.cleaned_data['name'],
                real_price=form.cleaned_data['real_price'],
                direct_labor=form.cleaned_data['direct_labor'],
                direct_wages=form.cleaned_data['direct_wages'],
            )

            product.save()
            # NOTE: Updating the indirect values here!
            update_product_indirect_values()
        else:
            print(form._errors)

        page = form.cleaned_data['page']

        if page is None or page == 1:
            return HttpResponseRedirect("/products")
        else:
            # do we want to route to the same page after creation?
            # should we route to the first / last page instead? If we 
            # sort our list of products, this would be more difficult. 
            # if the products are in order of creation, we could redirect to the
            # last page maybe?
            return HttpResponseRedirect("/products/?page={}".format(page))

        
    # redirect to 404 if method isn't post
    else:
        return HttpResponseRedirect("/fourohfour")



# TODO: add safety try/except blocks (see delete_product)
def edit_product(request, name):
    # url should only accept post requests
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            Product.objects.filter(name=name).update(
                name = form.cleaned_data['name'],
                real_price = form.cleaned_data['real_price'],
                direct_labor = form.cleaned_data['direct_labor'],
                direct_wages = form.cleaned_data['direct_wages'],
            )
            # NOTE: Updating the indirect values here!
            update_product_indirect_values()
            # redirect using NEW name, since it may have been updated
            return HttpResponseRedirect("/product/{}".format(form.cleaned_data['name']))

        else:
            print(form._errors)
            
            # redirect to the product page using ORIGINAL name, since update did not work
            return HttpResponseRedirect("/product/{}".format(name))

    else:
        return HttpResponseRedirect("/fourohfour")


def delete_product(request, name):
    # TODO: change to DELETE request??
    if request.method == 'POST':
        try:
            # find by name (primary key)
            # if not found, goes to except block
            # delete on find
            Product.objects.get(name=name).delete()
            update_product_indirect_values()
        except:    
            # TODO: is this the best action to take?
            # I think we should look into handling errors and notifying the user,
            # rather than routing to 404 anytime a DB operation fails
            return HttpResponseRedirect("/fourohfour")
    
        return HttpResponseRedirect("/products")
    else:
        return HttpResponseRedirect("/fourohfour")


### CRUD FOR DEPENDENCY ###

def create_dependency(request, prod_name):
    # handle the post to this url ONLY
    if request.method == 'POST':
        form = DependencyForm(request.POST)
        if form.is_valid():
        
           try:
               dependent = Product.objects.get(name=prod_name)
               dependency = Product.objects.get(name=form.cleaned_data['dependency'])

           except:
               return HttpResponseRedirect("/fourohfour")
           
           # Check if a dependency of this directionbetween these Products already exists
           if (Dependency.objects.filter(dependent=dependent).filter(dependency=dependency)):
              print("This dependency already exists!")
              return HttpResponseRedirect("/product/{}".format(prod_name))

           newDependency = Dependency(
               dependent = dependent,
               dependency = dependency,
               quantity = form.cleaned_data['quantity']

            )
           newDependency.save()
           update_product_indirect_values()
        else:
            print(form._errors)

        return HttpResponseRedirect("/product/{}".format(prod_name))

    # redirect to 404 if method isn't post
    else:
        return HttpResponseRedirect("/fourohfour")


def edit_dependency(request, prod_name):
    # url should only accept post requests
    if request.method == 'POST':
        form = EditDependencyForm(request.POST)
        if form.is_valid():
            try:
                dep = Dependency.objects.filter(id=form.cleaned_data['id'])
                dep.update(
                dependent=Product.objects.get(name=prod_name),  # Assuming that the dependencies are dependent on the product
                dependency=Product.objects.get(name=form.cleaned_data['dependency']),
                quantity=form.cleaned_data['quantity']
                )
            except:
                print("Problem setting dep")
                return HttpResponseRedirect("/product/{}".format(prod_name))

            

            update_product_indirect_values()
            # redirect using NEW dependency, since it may have been updated
            return HttpResponseRedirect("/product/{}".format(prod_name))

        else:
            print("Error resulting from form", form._errors)

            # redirect to the dependency page using ORIGINAL name, since update did not work if here
            return HttpResponseRedirect("/product/{}".format(prod_name))

    else:
        return HttpResponseRedirect("/fourohfour")

def delete_dependency(request):
    # TODO: change to DELETE request??
    if request.method == 'POST':
        redirect_to = ""
        form = DeleteDependencyForm(request.POST)
        if form.is_valid():
            try:
                # find by id (primary key)
                # if not found, goes to except block
                # delete on find
                dep_id = form.cleaned_data['id']
                redirect_to = form.cleaned_data['redirect_to']
                Dependency.objects.get(id=dep_id).delete()
            except:
                # TODO: is this the best action to take?
                return HttpResponseRedirect("/fourohfour")

        else:
            print(form._errors)
            # TODO: maybe add routing to uh oh error page??

        update_product_indirect_values()
        return HttpResponseRedirect("/product/{}".format(redirect_to))
    else:
        return HttpResponseRedirect("/fourohfour")


### Calculating indirect costs ###

def update_product_indirect_values():
    # TODO: might want to make a separate function that handles a request, if we stop doing this
    # calculation automatically when data is added
    #if request.method != 'PUT':
    #    return HttpResponseRedirect("/fourohofur")

    # NOTE: this code has very bad perf and does many queries when maybe it can do group_by and stuff?
    # Calculating labor time
    labor_graph = {}
    for p in Product.objects.all():
        deps = []
        for d in Dependency.objects.filter(dependent=p.id):
            deps.append((d.dependency_id, d.quantity))
        labor_graph[p.id] = product_graph_bindings.SimpleProduct(p.direct_labor, deps)

    (indirect_labor_values, errors) = product_graph_bindings.calc_indirect_vals_for_n_iterations(labor_graph, 25)

    if len(errors) != 0:
        for id in errors:
            newError = Error(product = id)
            newError.save()
            # TODO: early return? maybe want to show the messed up values?
    else:
        # Clear any preexisting error data since the graph is now valid
        Error.objects.all().delete()


    for (id_val, indirect_labor_val) in indirect_labor_values:
        prod = Product.objects.filter(id=id_val).update(indirect_labor=indirect_labor_val)
    # Calculating cost-price
    cost_graph = {}
    for p in Product.objects.all():
        deps = []
        for d in Dependency.objects.filter(dependent=p.id):
            deps.append((d.dependency_id, d.quantity))
        cost_graph[p.id] = product_graph_bindings.SimpleProduct(p.direct_wages, deps)

    (indirect_cost_values, errors) = product_graph_bindings.calc_indirect_vals_for_n_iterations(cost_graph, 25)
    for (id_val, indirect_cost_val) in indirect_cost_values:
        prod = Product.objects.filter(id=id_val).update(indirect_wages=indirect_cost_val)
