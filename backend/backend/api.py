from django.shortcuts import render,redirect
from django.views.generic import TemplateView
from django.http import HttpResponseRedirect
from .models import Product
from .models import Dependency
from .forms import ProductForm
import product_graph_bindings

### CRUD FOR PRODUCT ###
def update_product_indirect_values():
    #if request.method != 'PUT':
    #    return HttpResponseRedirect("/fourohofur")

    # NOTE: this code has very bad perf and does many queries when maybe it can do group_by and stuff?
    labor_graph = {}
    for p in Product.objects.all():
        deps = []
        for d in Dependency.objects.filter(dependent=p.id):
            deps.append((d.dependency, d.quantity))
        labor_graph[p.id] = product_graph_bindings.SimpleProduct(p.direct_labor, deps)

    #for product_id_key in labor_graph:
        #for d in Dependency.objects.filter(dependent=product_id_key):
            #labor_graph[product_id_key].dependencies.append((d.dependency, d.quantity))

    (indirect_labor_values, time) = product_graph_bindings.calc_indirect_vals_for_n_iterations(labor_graph, 25)
    for (id_val, indirect_labor_val) in indirect_labor_values:
        prod = Product.objects.filter(id=id_val).update(indirect_labor=indirect_labor_val)

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
                # indirect_wages = form.cleaned_data['indirect_wages'],
                # indirect_labor = form.cleaned_data['indirect_labor']
            )
            # NOTE: Updating the indirect values here!
            update_product_indirect_values()

            # redirect using NEW name, since it may have been updated
            return HttpResponseRedirect("/product/{}".format(form.cleaned_data['name']))

        else:
            print(form._errors)
            
            # redirect to the product page using ORIGINAL name, since update did not work if here
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

def create_dependency(request):
    pass


def edit_dependency(request, prod_name):
    pass


def delete_dependency(request, dep_name):
    pass
