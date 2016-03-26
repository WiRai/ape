
# path hack to place ape_install on the python path, so we can import it for testing
import sys
from os.path import abspath, dirname, join
APE_PTH = abspath(dirname(__file__))
sys.path.append(join(APE_PTH,  '../../../bin/'))

# import your tests here
from . install_tests import *
from . commandlineparser_tests import *
