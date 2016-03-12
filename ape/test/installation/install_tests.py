from __future__ import absolute_import
import unittest
from ..base import SilencedTest
import sys, os
import ape_install
import uuid
import tempfile

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
        return os.path.join(tempfile.gettempdir(), 'webapps_%s' % uuid.uuid4())


    def test_simple_installation(self):
        """
        Tests the simple installation without any further arguments.
        :return:
        """
        sys.argv = ['ape_install', self._get_webapps_dir()]
        ape_install.main()


    def test_python_executable_installation(self):
        """
        Tests the installation with an explicitly passed python executable.
        :return:
        """
        sys.argv = ['ape_install', self._get_webapps_dir(), '--p', 'python3']
        ape_install.main()


    def test_ape_version_installation(self):
        """
        Tests the installation with an explicitly passed ape version.
        :return:
        """
        sys.argv = ['ape_install', self._get_webapps_dir(), '--v', '0.3']
        ape_install.main()

    def test_ape_commit_id_installation(self):
        """
        Tests the installation with an explicitly passed commit id.
        :return:
        """
        sys.argv = ['ape_install', self._get_webapps_dir(), '--c', '1ad83e92788d89d55ce90c8101502d3a9f6cc5f8']
        ape_install.main()




