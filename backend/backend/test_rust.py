from django.test import TestCase
from .models import Product
from .models import Dependency
from .api import *


class CalcDirectTestCase(TestCase):
    def setUp(self):
        p1 = Product(name="Prod1", real_price=10.0, direct_labor=10.0, direct_wages=10.0)
        p2 = Product(name="Prod2", real_price=10.0, direct_labor=10.0, direct_wages=10.0)
        p1.save()
        p2.save()
        d = Dependency(dependent_id=p1.id, dependency_id=p2.id, quantity =10.0)
        d.save()

    def test_calculates_correct_values_without_indirection(self):
        update_product_indirect_values()
        self.assertEqual(Product.objects.get(id=1).indirect_labor, 100.0)
        self.assertEqual(Product.objects.get(id=2).indirect_labor, 0.0)

class CalcIndirTestCase(TestCase):
    def setUp(self):
        # TODO: Clean this stuff up
        p1 = Product(name="Prod1", real_price=10.0, direct_labor=10.0, direct_wages=10.0)
        p2 = Product(name="Prod2", real_price=10.0, direct_labor=10.0, direct_wages=10.0)
        p3 = Product(name="Prod3", real_price=10.0, direct_labor=10.0, direct_wages=10.0)
        p4 = Product(name="Prod4", real_price=10.0, direct_labor=10.0, direct_wages=10.0)
        p1.save()
        p2.save()
        p3.save()
        p4.save()
        d1 = Dependency(dependent_id=p2.id, dependency_id=p1.id, quantity =1.0)
        d2 = Dependency(dependent_id=p3.id, dependency_id=p1.id, quantity =1.0)
        d3 = Dependency(dependent_id=p3.id, dependency_id=p2.id, quantity =1.0)
        d4 = Dependency(dependent_id=p4.id, dependency_id=p3.id, quantity =1.0)
        d1.save()
        d2.save()
        d3.save()
        d4.save()

    def test_calculates_correct_values_with_indirection(self):
        update_product_indirect_values()
        self.assertEqual(Product.objects.get(id=1).indirect_labor, 0.0)
        self.assertEqual(Product.objects.get(id=2).indirect_labor, 10.0)
        self.assertEqual(Product.objects.get(id=3).indirect_labor, 30.0)
        self.assertEqual(Product.objects.get(id=4).indirect_labor, 40.0)

class CalcIndirCostTestCase(TestCase):
    def setUp(self):
        # TODO: Clean this stuff up
        p1 = Product(name="Prod1", real_price=10.0, direct_labor=10.0, direct_wages=10.0)
        p2 = Product(name="Prod2", real_price=10.0, direct_labor=10.0, direct_wages=10.0)
        p3 = Product(name="Prod3", real_price=10.0, direct_labor=10.0, direct_wages=10.0)
        p4 = Product(name="Prod4", real_price=10.0, direct_labor=10.0, direct_wages=10.0)
        p1.save()
        p2.save()
        p3.save()
        p4.save()
        d1 = Dependency(dependent_id=p2.id, dependency_id=p1.id, quantity =1.0)
        d2 = Dependency(dependent_id=p3.id, dependency_id=p1.id, quantity =1.0)
        d3 = Dependency(dependent_id=p3.id, dependency_id=p2.id, quantity =1.0)
        d4 = Dependency(dependent_id=p4.id, dependency_id=p3.id, quantity =1.0)
        d1.save()
        d2.save()
        d3.save()
        d4.save()

    def test_calculates_correct_values_with_indirection(self):
        update_product_indirect_values()
        self.assertEqual(Product.objects.get(id=1).indirect_wages, 0.0)
        self.assertEqual(Product.objects.get(id=2).indirect_wages, 10.0)
        self.assertEqual(Product.objects.get(id=3).indirect_wages, 30.0)
        self.assertEqual(Product.objects.get(id=4).indirect_wages, 40.0)
