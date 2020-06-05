from django.shortcuts import render,redirect


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
    }
]


def retrieve_product(name):
    target_product = None

    for product in dummy_data:
        if product["name"] == name:
            target_product = product
            break
    
    return target_product


def fourohfour(request):
    return render(request, 'fourohfour/fourohfour.html')

def home(request):
    context = {
        'products': dummy_data
    }
    return render(request, 'home/index.html', context)

def product_view(request, name):
    target_product = retrieve_product(name)
    
    if target_product is None:
        return redirect('/fourohfour')
    else:
        context = {
            'product': target_product
        }
        return render(request, 'home/product_info.html', context)

def product_analytics(request, name):
    target_product = retrieve_product(name)

    if target_product is None:
        return redirect('/fourohfour')
    else:
        context = {
            'product': target_product
        }
        return render(request, 'home/product_analytics.html', context)