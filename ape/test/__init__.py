from __future__ import absolute_import
import unittest
from ape.test.argparser import ArgParserTest
from ape.test.invokation import TaskInvokationTest
from ape.test.installation import *
from ape.test.core_tasks import CoreTasksTest


def suite():
    cases = [
        unittest.TestLoader().loadTestsFromTestCase(ArgParserTest),
        unittest.TestLoader().loadTestsFromTestCase(TaskInvokationTest),
        unittest.TestLoader().loadTestsFromTestCase(InstallTest),
        unittest.TestLoader().loadTestsFromTestCase(CommandLineParserTest),
        unittest.TestLoader().loadTestsFromTestCase(CoreTasksTest),
    ]
    return unittest.TestSuite(cases)


def run_all():
    return unittest.TextTestRunner(verbosity=2).run(suite())
