from django.shortcuts import render,redirect
from django.views.generic import TemplateView
from django.http import HttpResponseRedirect
from .models import Product
from .forms import ProductForm

### CRUD FOR PRODUCT ###

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
                real_price=form.cleaned_data['real_price'],
                direct_labor=form.cleaned_data['direct_labor'],
                direct_wages=form.cleaned_data['direct_wages'],
            )

            product.save()
        else:
            print(form._errors)
    
        return HttpResponseRedirect("/")

    # redirect to 404 if method isn't post
    else:
        return HttpResponseRedirect("/fourohfour")

# TODO: add safety try/except blocks (see delete_product)
def edit_product(request, name):
    """
    Updates a product in the database. This function handles POST requests sent to the URL 'api/edit/product/:id'

    :param request: The request sent to server
    :type request: HttpRequest

    :param name: the name of the product selected to update
    :type name: str (This will change to int to reflect the future change in the Product model)

    :return: a redirect to the selected product info page using new id '/product/:id' on successful find and update to DB, 
        to '/product/:id' using original id on failure and to '/fourohfour' on request types that are not POST
    :rtype: HttpResponseRedirect
    """
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

            # redirect using NEW name, since it may have been updated
            return HttpResponseRedirect("/product/{}".format(form.cleaned_data['name']))

        else:
            print(form._errors)
            
            # redirect to the product page using ORIGINAL name, since update did not work if here
            return HttpResponseRedirect("/product/{}".format(name))

    else:
        return HttpResponseRedirect("/fourohfour")


def delete_product(request, name):
    """
    Deletes a product in the database. This function handles POST requests sent to the URL 'api/delete/product/:id'

    :param request: The request sent to server
    :type request: HttpRequest

    :param name: the name of the product selected to delete
    :type name: str (This will change to int to reflect the future change in the Product model)

    :return: a redirect to the homepage '/' on successful find and delete to DB, to '/fourohfour' on failure or on request 
        types that are not POST
    :rtype: HttpResponseRedirect
    """
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
    """
    """
    pass


def edit_dependency(request, prod_name):
    """
    """
    pass


def delete_dependency(request, dep_name):
    """
    """
    pass