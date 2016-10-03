from __future__ import absolute_import
from __future__ import print_function
import unittest
from ape.main import run
from .base import SilencedTest
import sys
import os

class CoreTasksTest(unittest.TestCase):

    def test_noparam(self):
        os.environ['PRODUCT_EQUATION'] = "json"
        run([])

    def test_help(self):
        os.environ['PRODUCT_EQUATION'] = "json"
        run(['help'])

    def test_explain_features(self):
        os.environ['PRODUCT_EQUATION'] = "json"
        run(['explain_features'])

    def test_explain_feature(self):
        os.environ['PRODUCT_EQUATION'] = "json"
        run(['explain_feature', 'ape'])
