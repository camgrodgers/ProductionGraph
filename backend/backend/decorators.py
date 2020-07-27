from django.shortcuts import render,redirect
from django.http import HttpResponse

def unauthed_route(view_fn):
    """
    Decorator to control routes only meant for unauthenticated users (e.g. registered users 
    don't need access to the login or register page)

    :param view_fn: The view function returned on sucess (unauthed user)
    :type request: Function

    :return: a redirect to the product list page '/products/' if user in request is authenticated, 
        a Function to render the requested template if user is unauthenticated
    :rtype: HttpResponseRedirect or Function
    """
    def wrapper_fn(request,*args, **kwargs):
        if request.user.is_authenticated:
            return redirect('/products/')
        else:
            return view_fn(request, *args, **kwargs)
    
    return wrapper_fn

def auth_required(api_fn):
    """
    Decorator to control routes only meant for authenticated users (e.g. creating products 
    / editing products requires a logged in user)

    :param view_fn: The API function returned on sucess (authed user)
    :type request: Function

    :return: a redirect to the product list page '/login/' if user in request is unauthenticated, 
        a Function to render the requested template if user is authenticated
    :rtype: HttpResponseRedirect or Function
    """
    def wrapper_fn(request, *args, **kwargs):
        if request.user.is_authenticated:
            return api_fn(request, *args, **kwargs)

        else:
            return redirect('/login/')
    
    return wrapper_fn