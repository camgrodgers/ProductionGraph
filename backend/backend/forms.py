from django import forms

class ProductForm(forms.Form):
    name = forms.CharField(max_length = 100) # NOTE: this max length is arbitrary placeholder
    real_price = forms.FloatField()
    direct_labor = forms.FloatField() # Consider placing a lower bound of 0.0?
    direct_wages = forms.FloatField()
    page = forms.IntegerField(required = False)

class DependencyForm(forms.Form):
    # The Dependent is not needed in the form, since it can be gotten from product.name in the html file
    dependency = forms.CharField()
    quantity = forms.FloatField()

class EditDependencyForm(forms.Form):
    # The Dependent is not needed in the form, since it can be gotten from product.name in the html file
    id = forms.FloatField()
    dependency = forms.CharField()
    quantity = forms.FloatField()

class DeleteDependencyForm(forms.Form):
    id = forms.FloatField()
    redirect_to = forms.CharField(max_length = 100)