from django.shortcuts import render,redirect
from django.views.generic import TemplateView
from django.http import HttpResponseRedirect
from .models import Product
from .models import Dependency
from .forms import ProductForm
<<<<<<< HEAD
import product_graph_bindings
=======
from .models import Dependency
from .forms import DependencyForm
from .forms import EditDependencyForm
>>>>>>> 2064b81f2035cdb543d71bf91a8b40f75107dc2b

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
<<<<<<< HEAD
            # NOTE: Updating the indirect values here!
            update_product_indirect_values()
        else:
            print(form._errors)

=======
            print("Item ID: ", product.id)
        else:
            print(form._errors)
>>>>>>> 2064b81f2035cdb543d71bf91a8b40f75107dc2b
        return HttpResponseRedirect("/")
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
<<<<<<< HEAD
            # NOTE: Updating the indirect values here!
            update_product_indirect_values()

=======
>>>>>>> 2064b81f2035cdb543d71bf91a8b40f75107dc2b
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
        form = ProductForm(request.POST)
        if form.is_valid():
            try:
                # find by name (primary key)
                # if not found, goes to except block
                # delete on find
                Product.objects.get(name=name).delete()
            except:    
                # TODO: is this the best action to take?
                return HttpResponseRedirect("/fourohfour")

        else:
            print(form._errors)
            # TODO: maybe add routing to uh oh error page??
    
        return HttpResponseRedirect("/")
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

            

            # redirect using NEW dependency, since it may have been updated
            return HttpResponseRedirect("/product/{}".format(prod_name))

        else:
            print("Error resulting from form", form._errors)

            # redirect to the dependency page using ORIGINAL name, since update did not work if here
            return HttpResponseRedirect("/product/{}".format(prod_name))

    else:
        return HttpResponseRedirect("/fourohfour")


def delete_dependency(request, dep_name):
<<<<<<< HEAD
    pass


### Calculating indirect costs ###

def update_product_indirect_values():
    # TODO: might want to make a separate function that handles a request, if we stop doing this
    # calculation automatically when data is added
    #if request.method != 'PUT':
    #    return HttpResponseRedirect("/fourohofur")

    # NOTE: this code has very bad perf and does many queries when maybe it can do group_by and stuff?
    labor_graph = {}
    for p in Product.objects.all():
        deps = []
        for d in Dependency.objects.filter(dependent=p.id):
            deps.append((d.dependency_id, d.quantity))
        labor_graph[p.id] = product_graph_bindings.SimpleProduct(p.direct_labor, deps)

    (indirect_labor_values, time) = product_graph_bindings.calc_indirect_vals_for_n_iterations(labor_graph, 25)
    for (id_val, indirect_labor_val) in indirect_labor_values:
        prod = Product.objects.filter(id=id_val).update(indirect_labor=indirect_labor_val)
=======
    # TODO: change to DELETE request??
    if request.method == 'POST':
        form = DependencyForm(request.POST)
        if form.is_valid():
            try:
                # find by name (primary key)
                # if not found, goes to except block
                # delete on find
                Dependency.objects.get(name=dep_name).delete()
            except:
                # TODO: is this the best action to take?
                return HttpResponseRedirect("/fourohfour")

        else:
            print(form._errors)
            # TODO: maybe add routing to uh oh error page??

        return HttpResponseRedirect("/")
    else:
        return HttpResponseRedirect("/fourohfour")
>>>>>>> 2064b81f2035cdb543d71bf91a8b40f75107dc2b
