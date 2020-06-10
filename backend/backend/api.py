from django.shortcuts import render,redirect
from django.views.generic import TemplateView
from django.http import HttpResponseRedirect
from .models import Product
from .forms import ProductForm

### CRUD FOR PRODUCT ###

def create_product(request):
    # handle the post to this url ONLY
    print("HERE")
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            real_price = form.cleaned_data['real_price']
            direct_labor = form.cleaned_data['direct_labor']
            direct_wages = form.cleaned_data['direct_wages']
            indirect_wages = form.cleaned_data['indirect_wages']
            indirect_labor = form.cleaned_data['indirect_labor']
            # print(name, real_price, direct_labor, direct_wages, indirect_wages, indirect_labor)
            product = Product(
                name=name,
                real_price=real_price,
                direct_labor=direct_labor,
                direct_wages=direct_wages,
                indirect_wages=indirect_wages,
                indirect_labor=indirect_labor
            )

            product.save()
        else:
            print(form._errors)
    
        return HttpResponseRedirect("/")

    # redirect to 404 if method isn't post
    else:
        return HttpResponseRedirect("/fourohfour")

def delete_product(request):
    # TODO: change to DELETE request??
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
                name = form.cleaned_data['name']
                print(name)
        else:
            print(form._errors)
            # TODO: maybe add routing to uh oh error page??
    
        return HttpResponseRedirect("/")
    else:
        return HttpResponseRedirect("/fourohfour")