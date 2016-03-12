import sys
import os
# add the installation script dir to the path.
sys.path.append(
    os.path.abspath(
        os.path.join(
            os.path.abspath(
                os.path.dirname(__file__)
            ),
            '../../bin/'
        )
    )
)
from ape import test


#   This is the main test runner of ape.
#   Further test cases are placed within ape.test.
#   To add new test cases add them in their own module within
#   ape/test and register them in ape/test/__init__.py



if __name__ == '__main__':

    result = test.run_all()
    retval = 0 if result.wasSuccessful() else 1
    sys.exit(retval)
