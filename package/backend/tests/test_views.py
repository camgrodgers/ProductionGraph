from django.test import TestCase
from .. import views
from ..models import Product
from django.test import Client

class TestViews(TestCase):
    def test_retrieve_product(self):
        prod = Product(name="Hot Dog")
        self.assertNotEqual(prod, views.retrieve_product("Bad Dog"))
