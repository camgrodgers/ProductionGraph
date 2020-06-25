from django.shortcuts import render,redirect
from django.views.generic import TemplateView
from django.http import HttpResponseRedirect
from .models import Product
from .forms import ProductForm

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

# def handle_edit_product(form, name):



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
    if request.method != 'GET':
        return HttpResponseRedirect("/fourohfour")

    return render(request, 'fourohfour/fourohfour.html')


def home(request):
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

    context = {
        'products': Product.objects.all()
    }

    return render(request, 'home/index.html', context)


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
    
    if target_product is None or request.method != 'GET':
        return redirect('/fourohfour')
    else:
        context = {
            'product': target_product,
            'dependencies': []
        }
        return render(request, 'home/product_info.html', context)


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
        return render(request, 'home/product_analytics.html', context)