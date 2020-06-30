import sys
from unittest import TestSuite
from boot_django import boot_django
from django.test.runner import DiscoverRunner

boot_django()
runner = DiscoverRunner(verbosity=1)
failures = runner.run_tests(["backend.tests"])
if failures:
    sys.exit(failures)
