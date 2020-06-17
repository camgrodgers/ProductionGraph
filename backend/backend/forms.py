from django import forms

class ProductForm(forms.Form):
    name = forms.CharField(max_length = 100) # NOTE: this max length is arbitrary placeholder
    real_price = forms.FloatField()
    direct_labor = forms.FloatField() # Consider placing a lower bound of 0.0?
    direct_wages = forms.FloatField()

class DependencyForm(forms.Form):
    pass