from django.db import models
import uuid

# TODO: Normalize? 
class Product(models.Model):
    name = models.CharField(max_length = 100, unique = True) # NOTE: this max length is arbitrary placeholder
    real_price = models.FloatField()
    direct_labor = models.FloatField() # Consider placing a lower bound of 0.0?
    direct_wages = models.FloatField()
    indirect_wages = models.FloatField(default=0)
    indirect_labor = models.FloatField(default=0)
    # id = models.UUIDField( 
    #      primary_key = True, 
    #      default = uuid.uuid4, 
    #      editable = False)

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


class Economy(models.Model):
    real_average_profit_rate = models.FloatField()
    estimated_average_profit_rate = models.FloatField()



