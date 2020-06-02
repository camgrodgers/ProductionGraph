from django.shortcuts import render


dummy_data = [
    {
        'name': 'Lemonade',
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