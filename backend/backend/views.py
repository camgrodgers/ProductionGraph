from django.shortcuts import render,redirect
from django.views.generic import TemplateView
from django.http import HttpResponseRedirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Product
from .models import Dependency
from .models import DependencyCycleError
from .forms import ProductForm
from .filters import ProductFilter

# HELPERS
# I think eventually we should change this
# If a user creates a product called "This is my product,"
# then the URL would be "/product/This is my product" which
# is very gross. Perhaps add a __str__ function to the Model
# that returns all lowercase string of first word in name?
def retrieve_product(product_name):
    """
    Queries DB for a product by name (This will be updated to query by ID)

    :param product_name: The name of target product (This will be updated to query by ID)
    :type request: str

    :return: a Product object on success, None on failure
    :rtype: Product or None
    """
    try:
        return Product.objects.get(name=product_name)
    except:    
        return None

def retrieveDependencies (product):
    try:
        return Dependency.objects.filter(dependent=product)
    except:
        return []

# TODO: could replace this with .exists()?
def retrieveProductError(_product):
    try:
        return DependencyCycleError.objects.get(product_id=_product.id)
    except:
        return None

# def handle_edit_product(form, name):

def generate_paginator(current_page_index, last_page):
    page_range = []

    if current_page_index - 3 >= 0 and last_page - 3 > current_page_index:
        page_range.append(1)
        page_range.append(('...', current_page_index - 1))
        for i in range(current_page_index - 1, current_page_index + 2):
            page_range.append(i+1)
        page_range.append(('...', current_page_index + 3))

        for i in range(last_page - 2, last_page):
            page_range.append(i+1)
    
    # elif current_page_index - 3 < 0:
    else:
        for i in range(0,3):
            page_range.append(i+1)
        page_range.append(('...',4))

        for i in range(last_page - 3, last_page):
            page_range.append(i+1)

    return page_range



### VIEWS ###

def fourohfour(request):
    """
    GET request handler for the URL '/fourohfour'

    :param request: The request sent to server
    :type request: HttpRequest

    :return: HttpResponse containing the page HTML, an HttpResponseRedirect to the 404 page '/fourohfour' if 
        request type isn't a GET
    :rtype: HttpResponse or HttpResponseRedirect
    """
    return render(request, 'fourohfour/fourohfour.html')

# root url is now empty, so redirect to products list view
def home(request):
    """
    GET request handler for the URL '/'

    :param request: The request sent to server
    :type request: HttpRequest
    
    :return: HttpResponse containing the page HTML
    :rtype: HttpResponse
    """
    return render(request, 'home/index.html')

def login(request):
    return render(request, 'home/login.html')

def register(request):
    return render(request, 'home/register.html')

def errors_page(request):
    if request.method != 'GET':
        return HttpResponseRedirect("/fourohfour")
    
    error_list = []
    for p in DependencyCycleError.objects.all():
        error_list.append(p.product.id)
    product_list = Product.objects.filter(id__in=error_list)

    context = {
            'products': product_list,
            }

    return render(request, 'product_pages/errorlisting.html', context)

def products_page(request):
    """
    GET request handler for the URL '/'

    :param request: The request sent to server
    :type request: HttpRequest
    
    :return: HttpResponse containing the page HTML and a context of a list of Product objects, and an
         HttpResponseRedirect to the 404 page '/fourohfour' if request type isn't a GET
    :rtype: HttpResponse or HttpResponseRedirect
    """
    if request.method != 'GET':
        return HttpResponseRedirect("/fourohfour")
    
    page = request.GET.get('page', 1)
    
    has_filter = request.GET.get('note')

    # this is not necessary, this is just to keep consistency
    # that /products alone defaults to page 1
    if page is not None and page == '1':
        return HttpResponseRedirect("/products")
    
    if has_filter == '':
        return HttpResponseRedirect("/products/")

    product_list = Product.objects.all()

    
    myFilter = ProductFilter(request.GET, queryset=product_list) # Instantiates filter using definiton from filters.py
    product_list = myFilter.qs                                   # Creates a query set by filtering the data

    paginator = Paginator(product_list, 10)
    errors_exist = DependencyCycleError.objects.exists()

    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
        page = 1
    except EmptyPage:
        products = paginator.page(paginator.num_pages)
        page = paginator.num_pages

    page_range = generate_paginator(products.number - 1, len(paginator.page_range))

    context = {
        'products': products,
        'myFilter': myFilter,
        'has_filter': has_filter,
        'current_page': page,
        'errors': errors_exist,
        'page_range': page_range
    }

    return render(request, 'product_pages/index.html', context)



#TODO: 
# 1). Add modals for creating / deleting dependencies
# 2). Add Button + Confirmation modal (i.e. "Are you sure?") for delete product

def product_view(request, name):
    """
    GET request handler for the URL '/product/:id'

    :param request: The request sent to server
    :type request: HttpRequest

    :param name: the name of the product selected
    :type name: str (This will change to int to reflect the future change in the Product model)

    :return: HttpResponse containing the page HTML and a context of the selected Product object, and an
         HttpResponseRedirect to the 404 page '/fourohfour' if request type isn't a GET
    :rtype: HttpResponse or HttpResponseRedirect
    """
    target_product = retrieve_product(name)
    product_dependencies = retrieveDependencies(target_product)
    selected_dep = None
    graph_error = retrieveProductError(target_product)
    
    if target_product is None or request.method != 'GET':
        return redirect('/fourohfour')
    else:
        context = {
            'product': target_product,
            'dependencies': product_dependencies,
            'selected_dep': selected_dep,
            'graph_error': graph_error
        }
        return render(request, 'product_pages/product_info.html', context)


def product_analytics(request, name):
    """
    GET request handler for the URL '/product/:id/analytics/'

    :param request: The request sent to server
    :type request: HttpRequest

    :param name: the name of the product selected
    :type name: str (This will change to int to reflect the future change in the Product model)

    :return: HttpResponse containing the page HTML and a context of the selected Product object, and an
         HttpResponseRedirect to the 404 page '/fourohfour' if request type isn't a GET
    :rtype: HttpResponse or HttpResponseRedirect
    """
    target_product = retrieve_product(name)

    if target_product is None or request.method != "GET":
        return redirect('/fourohfour')
    else:
        context = {
            'product': target_product,
            'dependencies': []
        }
        return render(request, 'product_pages/product_analytics.html', context)
