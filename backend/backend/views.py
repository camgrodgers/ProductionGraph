from django.shortcuts import render,redirect
from django.views.generic import TemplateView
from django.http import HttpResponseRedirect
from .models import Product
from .models import Dependency
from .forms import ProductForm
from .filters import ProductFilter

# HELPERS
# I think eventually we should change this
# If a user creates a product called "This is my product,"
# then the URL would be "/product/This is my product" which
# is very gross. Perhaps add a __str__ function to the Model
# that returns all lowercase string of first word in name?
def retrieve_product(product_name):
    try:
        return Product.objects.get(name=product_name)
    except:    
        return None

def retrieveDependencies (product):
    try:
        return Dependency.objects.filter(dependent=product)
    except:
        return []

# def handle_edit_product(form, name):



### VIEWS ###

def fourohfour(request):
    return render(request, 'fourohfour/fourohfour.html')


def home(request):
    if request.method != 'GET':
        return HttpResponseRedirect("/fourohfour")


    products = Product.objects.all()
    myFilter = ProductFilter(request.GET, queryset=products) #Instantiates filter using definiton from filters.py
    products = myFilter.qs                                   #Creates a query set by filtering the data

    context = {
        'products': products,
        'myFilter': myFilter
    }

    return render(request, 'home/index.html', context)


#TODO: 
# 1). Add modals for creating / deleting dependencies
# 2). Add Button + Confirmation modal (i.e. "Are you sure?") for delete product

def product_view(request, name):
    target_product = retrieve_product(name)
    product_dependencies = retrieveDependencies(target_product)
    selected_dep = None
    
    if target_product is None or request.method != 'GET':
        return redirect('/fourohfour')
    else:
        context = {
            'product': target_product,
            'dependencies': product_dependencies,
            'selected_dep': selected_dep
        }
        return render(request, 'home/product_info.html', context)


def product_analytics(request, name):
    target_product = retrieve_product(name)

    if target_product is None or request.method != "GET":
        return redirect('/fourohfour')
    else:
        context = {
            'product': target_product,
            'dependencies': []
        }
        return render(request, 'home/product_analytics.html', context)


def create_product(request):
    return render(request, 'home/test.html', {'req': request})
