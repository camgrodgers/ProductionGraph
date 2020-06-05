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
    try:
        return Product.objects.get(name=product_name)
    except:    
        return None

def handle_create_product(form):
    name = form.cleaned_data['name']
    real_price = form.cleaned_data['real_price']
    direct_labor = form.cleaned_data['direct_labor']
    direct_wages = form.cleaned_data['direct_wages']
    indirect_wages = form.cleaned_data['indirect_wages']
    indirect_labor = form.cleaned_data['indirect_labor']
    product = Product(
        name=name,
        real_price=real_price,
        direct_labor=direct_labor,
        direct_wages=direct_wages,
        indirect_wages=indirect_wages,
        indirect_labor=indirect_labor
    )

    product.save()

# def handle_edit_product(form, name):



# VIEWS
def fourohfour(request):
    return render(request, 'fourohfour/fourohfour.html')

# I do not like the structure I have here, but since
# there is only one POST operation it will be okay
# FIXME: maybe? 
def home(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            handle_create_product(form)
            return HttpResponseRedirect("")
    else:
        form = ProductForm()

    context = {
        'products': Product.objects.all(),
        'form': form
    }
    return render(request, 'home/index.html', context)


#TODO: 
# 1). Add modals for creating / deleting dependencies
# 2). Add Button + Confirmation modal (i.e. "Are you sure?") for delete product


# I do not like the structure I have here, and it will
# break once I add the POST for adding / editing dependency values
# FIXME: definitely
# IDEAS:
# 1). Post each operation to a different URL (typical rest style)
def product_view(request, name):
    target_product = retrieve_product(name)
    
    if target_product is None:
        return redirect('/fourohfour')
    else:
        if request.method == 'POST':
            form = ProductForm(request.POST)
            if form.is_valid():
                Product.objects.filter(name=name).update(
                    name = form.cleaned_data['name'],
                    real_price = form.cleaned_data['real_price'],
                    direct_labor = form.cleaned_data['direct_labor'],
                    direct_wages = form.cleaned_data['direct_wages'],
                    indirect_wages = form.cleaned_data['indirect_wages'],
                    indirect_labor = form.cleaned_data['indirect_labor']
                )
                return HttpResponseRedirect("/product/{}".format(form.cleaned_data['name']))
            else:
                print(form._errors)

        else:
            form = ProductForm()
        context = {
            'product': target_product,
            'dependencies': [],
            'form': form
        }
        return render(request, 'home/product_info.html', context)


def product_analytics(request, name):
    target_product = retrieve_product(name)

    if target_product is None:
        return redirect('/fourohfour')
    else:
        context = {
            'product': target_product,
            'dependencies': []
        }
        return render(request, 'home/product_analytics.html', context)


def create_product(request):
    return render(request, 'home/test.html', {'req': request})