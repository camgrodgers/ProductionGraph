from django.db import models
from ..models import Product
from django.test import TestCase
class TestProduct(TestCase):
    def test_product_name(self):
        prod = Product(name="Hot Dog")
        self.assertEqual("Hot Dog", prod.name)
        prod = Product(name="This name is over 100 characters and should not work according to the model specs. We will obviously find out and see if that is the case.")
        self.assertEqual("This name is over 100 characters and should not work according to the model specs. We will obviously find out and see if that is the case.",prod.name)
    def test_product_measurement(self):
        prod = Product(measurement="Pound")
        self.assertEqual("Pound", prod.measurement)
        prod = Product(measurement="This measurement is over 40 characters and should not work.")
