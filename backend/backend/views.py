from django.shortcuts import render


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


selected_product = dummy_data[0]

# Create your views here.
def home(request):
    context = {
        'products': dummy_data
    }
    return render(request, 'home/index.html', context)

def product_view(request):
    context = {
        'product': selected_product
    }
    return render(request, 'home/product_info.html', context)

def product_analytics(request):
    context = {
        'product': selected_product
    }
    return render(request, 'home/product_analytics.html', context)