import sys
try:
    #py2
    from cStringIO import StringIO
except:
    #py3
    from io import StringIO

class SilencedTest(object):
    '''mixin for unittest.TestCase
    silences the test by redirecting stdout and stderr
    '''

    def setUp(self):
        self.out = sys.stdout
        self.err = sys.stderr
        sys.stdout = StringIO()
        sys.stderr = StringIO()

    def tearDown(self):
        sys.stdout = self.out
        sys.stderr = self.err
