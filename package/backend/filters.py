import django_filters 
from .models import *
from django_filters import CharFilter

class ProductFilter(django_filters.FilterSet):
    note = CharFilter(field_name='name', lookup_expr="icontains")

    class Meta:
        model = Product
        fields = ('__all__')
        exclude = ['real_price', 'direct_labor', 'direct_wages', 'indirect_wages', 'indirect_labor', 'measurement']