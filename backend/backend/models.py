from django.db import models
import uuid

# TODO: Normalize? 
class Product(models.Model):
    """This class is a model for data that relates directly to products in the economy."""
    name = models.CharField(max_length = 100, unique = True) # NOTE: this max length is arbitrary placeholder
    # The unit of measurement for a product
    measurement = models.CharField(max_length = 40)
    # The price of the product in the real world
    real_price = models.FloatField()
    # The labor hours directly expended in production of the product
    direct_labor = models.FloatField() # Consider placing a lower bound of 0.0?
    # The wages directly expended in production of the product
    direct_wages = models.FloatField()
    # The wages expended in production of the product's dependencies
    indirect_wages = models.FloatField(default=0)
    # The labor hours expended in production of the product's dependencies
    indirect_labor = models.FloatField(default=0)

    @property
    def cost_price(self):
        # wage price + wage price of deps + profits of deps. NOTE: very rough estimate of profits, hardcoded
        return self.direct_wages + self.indirect_wages + (self.indirect_wages * 0.1)

    @property
    def value(self):
        return self.direct_labor + self.indirect_labor

class Dependency(models.Model):
    """This class is a model for dependency relations between different products.
    The dependent depends on a certain quantity of the dependency to be produced."""
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
    """This class is a model used to list Products that depend on 1 or more of themselves,
    or on another product which does so."""
    product = models.ForeignKey(
            Product,
            on_delete=models.CASCADE,
            )

# This is currently unused
class Economy(models.Model):
    real_average_profit_rate = models.FloatField()
    estimated_average_profit_rate = models.FloatField()

class HistoryPoint(models.Model):
    """This class is a model that is used for records of past states of the Product graph."""
    date_time = models.DateTimeField(auto_now_add=True)
    # TODO: Other fields worth recording here? Profit rate? other Model for storing some calculated values?

class ProductHistory(models.Model):
    """This class is a model that stores historical Product data."""
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
    """This class is a model that stores historical Dependency data."""
    history_point = models.ForeignKey(
            HistoryPoint,
            on_delete = models.CASCADE
            )
    dependent_id = models.IntegerField()
    dependency_id = models.IntegerField()
    quantity = models.FloatField()
