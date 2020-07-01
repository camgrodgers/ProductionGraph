from django.test import Client
from django.test import TestCase

class TestGetURLs(TestCase):
    def setUp(self):
        self.client = Client()

    def test_home(self):
        #Get Response to Home
        res = self.client.get('/')
        self.assertEqual(res.status_code, 200)

    # def test_admin(self):
    #     #Get Response to Admin
    #     res = self.client.get('/admin')
    #     self.assertEqual(res.status_code, 301)

    #     #Get Response to correct Admin
    #     res = self.client.get('/admin/login/?next=/admin/')
    #     self.assertEqual(res.status_code, 200)

    def test_fourohfour(self):
        #Get Request to fourohfour
        response = self.client.get('/fourohfour')
        self.assertEqual(response.status_code, 301)

class TestPostURLS(TestCase):
    def setUp(self):
        self.client = Client()
        self.client.post("/api/create/product", {
            'name': 'borgor', 'real_price': 69, 'direct_labor': 23, 'direct_wages': 54, 'indirect_wages': 12,
            'indirect_labor': 23
        })

    def test_create_product(self):
        #Post request to create new product
        res = self.client.post("/api/create/product", {
            'name': 'HotDog', 'real_price': 69, 'direct_labor': 36, 'direct_wages': 50, 'indirect_wages': 12, 'indirect_labor': 23
        })
        self.assertEqual(res.status_code, 302)

    def test_get_product(self):
        #Get request for created product HotDog
        res = self.client.get('/product/borgor')
        self.assertEqual(res.status_code, 200)

    def test_get_analytics(self):
        #get request for HotDog analytics
        res = self.client.get('/product/borgor/analytics')
        self.assertEqual(res.status_code, 200)