from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.http import HttpResponseRedirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import *
from .forms import *
from .filters import *
from .decorators import *
import numpy


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


def retrieveDependencies(product):
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
    """
    Determines the paginator range values

    :param current_page_index: The currently viewed page (indexed, so page - 1)
    :type current_page_index: unsigned integer

    :param last_page: last page in the paginator (indexed, so len - 1)
    :type last_page: unsigned integer

    :return: an array of integers, separated with a tuple ('...', integer) to indicate a break in the list 
        and the page to jump to on a click of '...'
    :rtype: Array
    """
    page_range = []

    if current_page_index - 3 >= 0 and last_page - 3 > current_page_index:
        page_range.append(1)
        page_range.append(('...', current_page_index - 1))
        for i in range(current_page_index - 1, current_page_index + 2):
            page_range.append(i + 1)
        page_range.append(('...', current_page_index + 3))

        for i in range(last_page - 2, last_page):
            page_range.append(i + 1)

    # elif current_page_index - 3 < 0:
    else:
        for i in range(0, 3):
            page_range.append(i + 1)
        page_range.append(('...', 4))

        for i in range(last_page - 3, last_page):
            page_range.append(i + 1)

    return page_range


### VIEWS ###
@unauthed_route
def login(request):
    """
    Logs a user in

    :param request: The request sent to server
    :type request: HttpRequest

    :return: a redirect to the product list page on sucess, remains on this page on failure
    :rtype: HttpResponseRedirect
    """
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user)
            return redirect('/products/')
        else:
            messages.info(request, "Username or password is incorrect")

    return render(request, 'home/login.html')


@unauthed_route
def register(request):
    """
    Registers a new user

    :param request: The request sent to server
    :type request: HttpRequest

    :return: a redirect to the login page on sucess, remains on this page on failure
    :rtype: HttpResponseRedirect
    """
    if request.method == "POST":
        register_form = CreateUserForm(request.POST)

        if register_form.is_valid():
            register_form.save()
            messages.success(request, 'Account was created successfully')
            return redirect("/login")
        else:
            print(register_form.errors)
            for message in list(register_form.errors.values()):
                messages.info(request, message)

    return render(request, 'home/register.html')


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


def home(request):
    """
    GET request handler for the URL '/'

    :param request: The request sent to server
    :type request: HttpRequest
    
    :return: HttpResponse containing the page HTML
    :rtype: HttpResponse
    """
    return render(request, 'home/index.html')


# @login_required(login_url='/login/')
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
    # print(errors_exist)

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


# TODO:
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
    graph_error = retrieveProductError(target_product)

    product_list = Product.objects.all()
    

    if target_product is None or request.method != 'GET':
        return redirect('/fourohfour')
    else:
        context = {
            'product': target_product,
            'dependencies': product_dependencies,
            'products': product_list,
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
        labels = []
        real_price = []
        estimated_labor_time = []
        estimated_cost = []

        all_history = ProductHistory.objects.all()
        j = 1
        for i in range(0, len(all_history)):
            if name == all_history[i].name:
                labels.append(f"{all_history[i].history_point.date_time:%Y/%m/%d %H:%M}")
                real_price.append(all_history[i].real_price)
                estimated_labor_time.append(all_history[i].direct_labor + all_history[i].indirect_labor)
                estimated_cost.append(all_history[i].indirect_wages + all_history[i].direct_wages)
        cor_labor_price = numpy.corrcoef(numpy.array(real_price), numpy.array(estimated_labor_time))
        cor_labor_price = cor_labor_price[0,1]
        cor_cost_price = numpy.corrcoef(estimated_cost, real_price)
        cor_cost_price = cor_cost_price[0,1]

        chartjs_config = {
            'type': 'line',
            'data': {
                'labels': labels,
                'datasets': [
                    {
                        'label': "Real Price",
                        'borderColor': "rgba(0,33,165,1)",
                        'yAxisID': 'l',
                        'data': real_price
                    },
                    {
                        'label': "Estimated Cost",
                        'borderColor': "rgba(250,70,22,1)",
                        'yAxisID': "l",
                        'data': estimated_cost
                    },
                    {
                        'label': "Estimated Labor Time",
                        'borderColor': 'rgba(25, 25, 25, 1)',
                        'pointHoverBorderColor': 'rgba(25, 25, 25, 1)',
                        'yAxisID': "r",
                        'data': estimated_labor_time
                    }
                ]},
            'options': {
                'responsive': 'true',
                'legend': {
                    'position': 'top',
                    'display': 'true'
                    },
                'scales': {
                    'yAxes': [{
                        'id': "l",
                        'type': "linear",
                        'position': "left",
                        'scaleLabel': {
                            'display': 'true',
                            'labelString': 'Dollars ($)'}
                    }, {
                        'id': "r",
                        'type': "linear",
                        'position': "right",
                        'scaleLabel': {
                            'display': 'true',
                            'labelString': 'Hours'}
                    }]
                }
            }

        }

        context = {
            'product': target_product,
            'dependencies': [],
            'labels': labels,
            'chartjs_config': chartjs_config,
            'cor_labor_price': cor_labor_price,
            'cor_cost_price': cor_cost_price

        }
        return render(request, 'product_pages/product_analytics.html', context)


def products_analytics(request):
    """
    GET request handler for the URL '/products/analytics/'

    :param request: The request sent to server
    :type request: HttpRequest

    :return: HttpResponse containing the page HTML and a context of the Product objects, and an
         HttpResponseRedirect to the 404 page '/fourohfour' if request type isn't a GET
    :rtype: HttpResponse or HttpResponseRedirect
    """
    if request.method != "GET":
        return redirect('/fourohfour')

    labels = []
    real_price = []
    estimated_labor_time = []
    estimated_cost = []

    all_prods = Product.objects.all().order_by('real_price')
    j = 1
    for prod in all_prods:
        labels.append(f"{prod.name}")
        real_price.append(prod.real_price)
        estimated_labor_time.append(prod.value)
        estimated_cost.append(prod.cost_price)
    cor_labor_price = numpy.corrcoef(numpy.array(real_price), numpy.array(estimated_labor_time))
    cor_labor_price = cor_labor_price[0,1]
    cor_cost_price = numpy.corrcoef(estimated_cost, real_price)
    cor_cost_price = cor_cost_price[0,1]

    chartjs_config = {
        'type': 'line',
        'data': {
            'labels': labels,
            'datasets': [
                {
                    'label': "Real Price",
                    'borderColor': "rgba(0,33,165,1)",
                    'yAxisID': 'l',
                    'data': real_price
                },
                {
                    'label': "Estimated Cost",
                    'borderColor': "rgba(250,70,22,1)",
                    'yAxisID': "l",
                    'data': estimated_cost
                },
                {
                    'label': "Estimated Labor Time",
                    'borderColor': 'rgba(25, 25, 25, 1)',
                    'pointHoverBorderColor': 'rgba(25, 25, 25, 1)',
                    'yAxisID': "r",
                    'data': estimated_labor_time
                }
            ]},
        'options': {
            'responsive': 'true',
            'legend': {
                'position': 'top',
                'display': 'true'
                },
            'scales': {
                'yAxes': [{
                    'id': "l",
                    'type': "linear",
                    'position': "left",
                    'scaleLabel': {
                        'display': 'true',
                        'labelString': 'Dollars ($)'}
                }, {
                    'id': "r",
                    'type': "linear",
                    'position': "right",
                    'scaleLabel': {
                        'display': 'true',
                        'labelString': 'Hours'}
                }]
            }
        }

    }

    context = {
        'dependencies': [],
        'labels': labels,
        'chartjs_config': chartjs_config,
        'cor_labor_price': cor_labor_price,
        'cor_cost_price': cor_cost_price

    }
    return render(request, 'product_pages/product_analytics.html', context)

