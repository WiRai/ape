from __future__ import absolute_import
import unittest
from ..base import SilencedTest
import sys, os
import uuid
import tempfile
import ape_install

try:
    from unittest import skip
except:
    def skip(reason):
        def wrapper(func):
            return None
        return wrapper


__all__ = ['InstallTest']

class InstallTest(unittest.TestCase):
    """
    Testcases for the ape_install installation script.
    """

    def _get_webapps_dir(self):
        """
        Returns a path to a uuid-suffixed webapps dir in the system's tempfolder.
        :return:
        """
        tmpdir_root = tempfile.gettempdir()
        if 'TRAVIS' in os.environ:
            tmpdir_root = os.path.abspath('.')
        return os.path.join(tmpdir_root, 'webapps_%s' % uuid.uuid4())

    @skip('pypi version does not support py3 currently')
    def test_simple_installation(self):
        """
        Tests the simple installation without any further arguments.
        :return:
        """
        sys.argv = ['ape_install', self._get_webapps_dir()]
        ape_install.main()

    @skip('pypi version does not support py3 currently')
    def test_python_executable_installation(self):
        """
        Tests the installation with an explicitly passed python executable.
        :return:
        """
        sys.argv = ['ape_install', self._get_webapps_dir(), '--git', 'python3', '--python', 'python']
        ape_install.main()

    @skip('pypi version does not support py3 currently')
    def skip_test_ape_version_installation(self):
        """
        Tests the installation with an explicitly passed ape version.
        :return:
        """
        sys.argv = ['ape_install', self._get_webapps_dir(), '--pypi', '0.4']
        ape_install.main()

    def test_ape_commit_id_installation(self):
        """
        Tests the installation with an explicitly passed commit id.
        :return:
        """
        sys.argv = ['ape_install', self._get_webapps_dir(), '--git', 'python3']
        ape_install.main()

    @skip('master branch does not support py3 currently')
    def test_ape_development_installation(self):
        """
        Tests the installation with an explicitly passed commit id.
        :return:
        """
        sys.argv = ['ape_install', self._get_webapps_dir(), '--dev']
        ape_install.main()
