from django.db import models
import uuid

# TODO: Normalize? 
class Product(models.Model):
    name = models.CharField(max_length = 100, unique = True) # NOTE: this max length is arbitrary placeholder
    measurement = models.CharField(max_length = 40)
    real_price = models.FloatField()
    direct_labor = models.FloatField() # Consider placing a lower bound of 0.0?
    direct_wages = models.FloatField()
    indirect_wages = models.FloatField(default=0)
    indirect_labor = models.FloatField(default=0)

    @property
    def cost_price(self):
        return self.direct_wages + self.indirect_wages

    @property
    def value(self):
        return self.direct_labor + self.indirect_labor

class Dependency(models.Model):
    dependent = models.ForeignKey(
            Product,
            on_delete=models.CASCADE,
            related_name = 'dependents'
            )
    dependency = models.ForeignKey(
            Product,
            on_delete=models.CASCADE,
            related_name = 'dependencies'
            )
    quantity = models.FloatField()

class DependencyCycleError(models.Model):
    product = models.ForeignKey(
            Product,
            on_delete=models.CASCADE,
            )

class Economy(models.Model):
    real_average_profit_rate = models.FloatField()
    estimated_average_profit_rate = models.FloatField()

class HistoryPoint(models.Model):
    date_time = models.DateTimeField(auto_now_add=True)
    # TODO: Other fields worth recording here? Profit rate? other Model for storing some calculated values?

class ProductHistory(models.Model):
    history_point = models.ForeignKey(
            HistoryPoint,
            on_delete = models.CASCADE
            )
    product_id = models.IntegerField() # NOTE: This is not a foreign key field because reasons
    name = models.CharField(max_length = 100) # NOTE: this max length is arbitrary placeholder
    measurement = models.CharField(max_length = 40)
    real_price = models.FloatField()
    direct_labor = models.FloatField() # Consider placing a lower bound of 0.0?
    direct_wages = models.FloatField()
    indirect_wages = models.FloatField(default=0)
    indirect_labor = models.FloatField(default=0)

# NOTE: actually displaying the history for these is not a priority
class DependencyHistory(models.Model):
    history_point = models.ForeignKey(
            HistoryPoint,
            on_delete = models.CASCADE
            )
    dependent_id = models.IntegerField()
    dependency_id = models.IntegerField()
    quantity = models.FloatField()
