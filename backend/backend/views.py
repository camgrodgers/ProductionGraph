from django.shortcuts import render,redirect
from django.views.generic import TemplateView
from django.http import HttpResponseRedirect
from .models import Product
from .forms import CreateProductForm


# products = Product.objects.all()
# proucts = Product.object.get(owner = logged in user)
dummy_data = [
    {
        'name': 'Lemonade',
        'current_real_price': 0,
        'direct_labor_time': 0,
        'direct_wages': 5,
        'est_cost_price': 100,
        'est_time_labor': 0,
        'dependencies': [
            ('water', 0),
            ('ice', 0),
            ('lemon', 0),
            ('sugar', 0),
        ]
    },
    {
        'name': 'Mixtape',
        'current_real_price': 0,
        'direct_labor_time': 0,
        'direct_wages': 2,
        'est_cost_price': 10,
        'est_time_labor': 0,
        'dependencies': [
            ('fire', 100000),
            ('creativity', 10000),
            ('pure skill', 1000)
        ]
    },
        {
        'name': 'Pakudex',
        'current_real_price': 0,
        'direct_labor_time': 0,
        'direct_wages': 2,
        'est_cost_price': 10,
        'est_time_labor': 0,
        'dependencies': [
            ('developers', 5),
        ]
    }
]

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


# VIEWS

def fourohfour(request):
    return render(request, 'fourohfour/fourohfour.html')

def home(request):
    if request.method == 'POST':
        form = CreateProductForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            real_price = form.cleaned_data['real_price']
            direct_labor = form.cleaned_data['direct_labor']
            direct_wages = form.cleaned_data['direct_wages']
            indirect_wages = form.cleaned_data['indirect_wages']
            indirect_labor = form.cleaned_data['indirect_labor']

            new_product = Product(
                name=name,
                real_price=real_price,
                direct_labor=direct_labor,
                direct_wages=direct_wages,
                indirect_wages=indirect_wages,
                indirect_labor=indirect_labor
            )

            new_product.save()

            
            return HttpResponseRedirect("")
    else:
        form = CreateProductForm()

    context = {
        'products': Product.objects.all(),
        'form': form
    }
    return render(request, 'home/index.html', context)

def product_view(request, name):
    target_product = retrieve_product(name)
    
    if target_product is None:
        return redirect('/fourohfour')
    else:
        context = {
            'product': target_product,
            'dependencies': []
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