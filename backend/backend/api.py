from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.http import HttpResponseRedirect
from django.contrib.auth import logout as auth_logout
from .models import *
from .forms import *
from .decorators import *
import product_graph_bindings


def commit_history():
    """
    Commits the current graph state to history, for the purpose of analytics.
    """
    histpoint = HistoryPoint()
    histpoint.save()
    for p in Product.objects.all():
        p_history = ProductHistory(
            history_point=histpoint,
            product_id=p.id,
            name=p.name,
            measurement=p.measurement,
            real_price=p.real_price,
            direct_labor=p.direct_labor,
            direct_wages=p.direct_wages,
            indirect_wages=p.indirect_wages,
            indirect_labor=p.indirect_labor
        )
        p_history.save()
    for d in Dependency.objects.all():
        d_history = DependencyHistory(
            history_point=histpoint,
            dependent_id=d.dependent_id,
            dependency_id=d.dependency_id,
            quantity=d.quantity
        )
        d_history.save()


def commit_history_request(request, name=None):
    if request.method == "POST":
        commit_history()
    if name is None:
        return redirect("/products/")
    else:
        return redirect("/product/" + name)


def logout(request):
    """
    Logs a user out
    :param request: The request sent to server
    :type request: HttpRequest
    :return: a redirect to the home page on sucess, 404 if failure or request method is
        not POST
    :rtype: HttpResponseRedirect
    """
    if request.method == "POST":
        auth_logout(request)
        return redirect("/")

    return redirect("/fourohfour")


### CRUD FOR PRODUCT ###
@auth_required
def create_product(request):
    """
    Creates a product in the database. This function handles POST requests sent to the URL 'api/create/product'
    :param request: The request sent to server
    :type request: HttpRequest
    :return: a redirect to the homepage '/' on successful save to DB, to '/fourohfour' on failure or on request
        types that are not POST
    :rtype: HttpResponseRedirect
    """
    # handle the post to this url ONLY
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            product = Product(
                name=form.cleaned_data['name'],
                measurement=form.cleaned_data['measurement'],
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
@auth_required
def edit_product(request, name):
    """
    Updates a product in the database. This function handles POST requests sent to the URL 'api/edit/product/:id'
    :param request: The request sent to server
    :type request: HttpRequest
    :param name: the name of the product selected to update
    :type name: str (This will change to int to reflect the future change in the Product model)
    :return: a redirect to the selected product info page using new id '/product/:id' on successful find and update to DB,
        to '/product/:id' using original id on failure and to '/fourohfour' on request types that are not POST
    :rtype: HttpResponseRedirect
    """
    # url should only accept post requests
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            Product.objects.filter(name=name).update(
                name=form.cleaned_data['name'],
                measurement=form.cleaned_data['measurement'],
                real_price=form.cleaned_data['real_price'],
                direct_labor=form.cleaned_data['direct_labor'],
                direct_wages=form.cleaned_data['direct_wages'],
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


@auth_required
def delete_product(request, name):
    """
    Deletes a product in the database. This function handles POST requests sent to the URL 'api/delete/product/:id'
    :param request: The request sent to server
    :type request: HttpRequest
    :param name: the name of the product selected to delete
    :type name: str (This will change to int to reflect the future change in the Product model)
    :return: a redirect to the homepage '/' on successful find and delete to DB, to '/fourohfour' on failure or on request
        types that are not POST
    :rtype: HttpResponseRedirect
    """
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
@auth_required
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
                dependent=dependent,
                dependency=dependency,
                quantity=form.cleaned_data['quantity']

            )
            newDependency.save()
            update_product_indirect_values()
        else:
            print(form._errors)

        return HttpResponseRedirect("/product/{}".format(prod_name))

    # redirect to 404 if method isn't post
    else:
        return HttpResponseRedirect("/fourohfour")


@auth_required
def edit_dependency(request, prod_name):
    # url should only accept post requests
    if request.method == 'POST':
        form = EditDependencyForm(request.POST)
        if form.is_valid():
            try:
                dep = Dependency.objects.filter(id=form.cleaned_data['id'])
                dep.update(
                    dependent=Product.objects.get(name=prod_name),
                    # Assuming that the dependencies are dependent on the product
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


@auth_required
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
    """
    Performs the calculation of indirect values by calling on the Rust library.
    """
    # TODO: might want to make a separate function that handles a request, if we stop doing this
    # calculation automatically when data is added
    #if request.method != 'PUT':
    #    return HttpResponseRedirect("/fourohofur")

    # NOTE: this code has very bad perf and does many queries when maybe it can do group_by and stuff?
    # need to combine some loops at very least

    labor_graph = {}
    cost_graph = {}
    for p in Product.objects.all():
        deps = []
        for d in Dependency.objects.filter(dependent=p.id):
            deps.append((d.dependency_id, d.quantity))
        # Calculating labor time
        labor_graph[p.id] = product_graph_bindings.SimpleProduct(p.direct_labor, deps)

        # Calculating cost-price
        cost_graph[p.id] = product_graph_bindings.SimpleProduct(p.direct_wages, deps)

    (indirect_labor_values, errors) = product_graph_bindings.calc_indirect_vals_for_n_iterations(labor_graph, 25)

    # Check for errors in graph
    if len(errors) != 0:
        # clear old errors
        DependencyCycleError.objects.all().delete()
        # NOTE: batch inserts could be good here but they have some weird caveats
        for id in errors:
            newError = DependencyCycleError(product_id = id)
            newError.save()
        return
    else:
        # Clear any preexisting error data since the graph is now valid
        DependencyCycleError.objects.all().delete()

    (indirect_cost_values, errors) = product_graph_bindings.calc_indirect_vals_for_n_iterations(cost_graph, 25)

    # update products with calculated values
    for (id_val, indirect_labor_val) in indirect_labor_values:
        Product.objects.filter(id=id_val).update(indirect_labor=indirect_labor_val)



    # update products with calculated values
    for (id_val, indirect_cost_val) in indirect_cost_values:
        Product.objects.filter(id=id_val).update(indirect_wages=indirect_cost_val)
