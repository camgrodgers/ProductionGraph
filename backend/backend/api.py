from django.shortcuts import render,redirect
from django.views.generic import TemplateView
from django.http import HttpResponseRedirect
from .models import Product
from .forms import ProductForm

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
            )
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
    return HttpResponseRedirect("/fourohfour")


def edit_dependency(request, prod_name):
    pass


def delete_dependency(request, dep_name):
    pass