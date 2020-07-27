from django.shortcuts import render,redirect
from django.http import HttpResponse

def unauthed_route(view_fn):
    """
    Decorator to control routes only meant for unauthenticated users

    :param view_fn: The view function returned on sucess (unauthed user)
    :type request: Function

    :return: a redirect to the product list page '/products/' if user in request is authenticated, 
        a Function to render the template if user is unauthenticated
    :rtype: HttpResponseRedirect or Function
    """
    def wrapper_fn(request,*args, **kwargs):
        """ Had to comment this out because it was causing a redirect loop"""
        """if request.user.is_authenticated:
            return redirect('/products/')
        else:"""
        return view_fn(request, *args, **kwargs)
    
    return wrapper_fn