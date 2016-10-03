from __future__ import absolute_import
from __future__ import print_function
import warnings
import unittest
from ..base import SilencedTest
import os
import sys
import uuid
import tempfile
import ape_install
import shutil
import stat
from os.path import join as pj

__all__ = ['InstallTest']

# try to use unittest.skip if available; use fallback otherwise
# python 2.6 compat
try:
    from unittest import skip
except:
    def skip(reason):
        def wrapper(func):
            return None
        return wrapper

def _rmtree_onerror(func, path, exc_info):
    """
    error handler for rmtree

    also delete readonly files if possible, ignore otherwise
    """
    success = False
    if not os.access(path, os.W_OK):
        os.chmod(path, stat.S_IWUSR)
        try:
            func(path)
            success = True
        except:
            pass

    if not success:
        print("!!! Unable to delete folder. Please clean up '%s' manually. Error was: %s" % (path, str(exc_info)))


def rmtree(path):
    """
    delete directory recursively like shutil.rmtree.
    This impl also deletes readonly files if possible.
    """
    shutil.rmtree(path, False, _rmtree_onerror)


class InstallTest(SilencedTest, unittest.TestCase):
    """
    Testcases for the ape_install installation script.
    """

    def tearDown(self):
        SilencedTest.tearDown(self)

        if os.path.isdir(self._webapps_dir):
            print('deleting testcontainer')
            rmtree(self._webapps_dir)

    def _get_webapps_dir(self):
        """
        Returns a path to a uuid-suffixed webapps dir in the system's tempfolder.
        :return:
        """
        tmpdir_root = tempfile.gettempdir()
        if 'TRAVIS' in os.environ:
            tmpdir_root = os.path.abspath('.')
        self._webapps_dir = os.path.join(tmpdir_root, 'webapps_%s' % uuid.uuid4())
        return self._webapps_dir

    def run_install(self, *args):
        webapps_dir = self._get_webapps_dir()
        old_argv = sys.argv
        try:
            sys.argv = ['ape_install', webapps_dir] + list(args)
            ape_install.main()
            return webapps_dir
        finally:
            sys.argv = old_argv

    def verify_install(self, install_dir):
        self.assertTrue(os.path.isdir(install_dir), 'ape container should exist')
        self.assertTrue(os.path.isdir(pj(install_dir, '_ape')), '_ape should exist')

        self.assertTrue(os.path.isfile(pj(install_dir, '_ape', 'activape')), 'activape script should exist')
        self.assertTrue(os.path.isfile(pj(install_dir, '_ape', 'aperun')), 'aperun script should exist')

        self.assertTrue(os.path.isdir(pj(install_dir, '_ape', 'venv')), '_ape/venv should exist')
        self.assertTrue(
            os.path.isfile(pj(install_dir, '_ape', 'venv/bin/activate'))
                or os.path.isfile(pj(install_dir, '_ape', 'venv/Scripts/activate.bat')),
            '_ape/venv/.../activate should exist'
        )
        self.assertTrue(
            os.path.isfile(pj(install_dir, '_ape', 'venv/bin/pip'))
                or os.path.isfile(pj(install_dir, '_ape', 'venv/Scripts/pip.exe')),
            '_ape/venv/.../pip should exist'
        )


    @skip('pypi version does not support py3 currently')
    def test_simple_installation(self):
        """
        Tests the simple installation without any further arguments.
        :return:
        """
        install_dir = self.run_install()
        self.verify_install(install_dir)

    @skip('pypi version does not support py3 currently')
    def skip_test_ape_version_installation(self):
        """
        Tests the installation with an explicitly passed ape version.
        :return:
        """
        install_dir = self.run_install('--pypi', '0.4')
        self.verify_install(install_dir)

    def test_ape_commit_id_installation(self):
        """
        Tests the installation with an explicitly passed commit id.
        :return:
        """
        install_dir = self.run_install('--git', 'travis-debug')
        self.verify_install(install_dir)
        self.assertTrue(os.path.isdir(pj(install_dir, '_ape', 'venv', 'src', 'ape')), 'ape should be installed in venv/src')

    @skip('master branch does not support py3 currently')
    def test_ape_development_installation(self):
        """
        Tests the installation with an explicitly passed commit id.
        :return:
        """
        install_dir = self.run_install('--dev')
        self.verify_install(install_dir)
