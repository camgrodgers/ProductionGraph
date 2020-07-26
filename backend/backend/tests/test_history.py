from django.test import TestCase
from ..models import *
from ..api import *

class HistoryTestCase(TestCase):
    def setUp(self):
        p1 = Product(name="Prod1", measurement="unit", real_price=10.0, direct_labor=10.0, direct_wages=10.0)
        p2 = Product(name="Prod2", measurement="unit", real_price=10.0, direct_labor=10.0, direct_wages=10.0)
        p3 = Product(name="Prod3", measurement="unit", real_price=10.0, direct_labor=10.0, direct_wages=10.0)
        p4 = Product(name="Prod4", measurement="unit", real_price=10.0, direct_labor=10.0, direct_wages=10.0)
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

    def test_history_logs_one_commit(self):
        update_product_indirect_values()
        commit_history()
        self.assertEqual(ProductHistory.objects.get(product_id=1, history_point_id=1).indirect_labor, 0.0)
        self.assertEqual(ProductHistory.objects.get(product_id=2, history_point_id=1).indirect_labor, 10.0)
        self.assertEqual(ProductHistory.objects.get(product_id=3, history_point_id=1).indirect_labor, 30.0)
        self.assertEqual(ProductHistory.objects.get(product_id=4, history_point_id=1).indirect_labor, 40.0)

    def test_history_logs_two_commits(self):
        update_product_indirect_values()
        commit_history()
        Product.objects.filter(id=3).update(direct_labor=20.0)
        update_product_indirect_values()
        commit_history()
        self.assertEqual(ProductHistory.objects.get(product_id=4, history_point_id=1).indirect_labor, 40.0)
        self.assertEqual(ProductHistory.objects.get(product_id=4, history_point_id=2).indirect_labor, 50.0)

