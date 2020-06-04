from django.db import models

# TODO: Normalize? 
class Product(models.Model):
    name = models.CharField(max_length = 100, primary_key = True, unique = True) # NOTE: this max length is arbitrary placeholder
    real_price = models.FloatField()
    direct_labor = models.FloatField() # Consider placing a lower bound of 0.0?
    direct_wages = models.FloatField()
    cost_price = models.FloatField()
    indirect_labor = models.FloatField()

class Dependency(models.Model):
    dependent = models.ForeignKey(
            'Product',
            on_delete=models.CASCADE,
            related_name = 'dependents'
            )
    dependency = models.ForeignKey(
            'Product',
            on_delete=models.CASCADE,
            related_name = 'dependencies'
            )
    quantity = models.FloatField()




