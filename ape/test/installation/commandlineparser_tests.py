from __future__ import absolute_import
import unittest
from ..base import SilencedTest
import sys, os
import ape_install

__all__ = ['CommandLineParserTest']

class CommandLineParserTest(SilencedTest, unittest.TestCase):
    """
    Testcases for the ape_install installation script.
    """

    def test_paths(self):
        """
        Tests the path construction.
        :return:
        """
        target_dir = 'webapps'
        sys.argv = ['ape_install.py', target_dir,]

        cmdargs = ape_install.CommandLineParser()
        APE_ROOT_DIR = cmdargs.get_ape_root_dir()
        APE_DIR = cmdargs.get_ape_dir()
        VENV_DIR = cmdargs.get_venv_dir()
        VENV_CREATION_ARGS = cmdargs.get_venv_creation_args()
        APE_INSTALL_ARGS = cmdargs.get_ape_install_args()
        ACTIVAPE_DEST = cmdargs.get_activape_dest()
        APERUN_DEST = cmdargs.get_aperun_dest()


        cwd = os.getcwd()

        self.assertEquals(APE_ROOT_DIR, os.path.join(cwd, target_dir))
        self.assertEquals(APE_DIR, os.path.join(cwd, target_dir, '_ape'))
        self.assertEquals(VENV_DIR, os.path.join(cwd, target_dir, '_ape/venv'))
        self.assertEquals(ACTIVAPE_DEST, os.path.join(cwd, target_dir, '_ape/activape'))
        self.assertEquals(APERUN_DEST, os.path.join(cwd, target_dir, '_ape/aperun'))

    def test_venv_creation_args(self):
        """
        Tests the construction of the venv creation args.
        :return:
        """
        target_dir = 'webapps'
        sys.argv = ['ape_install.py', target_dir, '--p', 'python3']

        cmdargs = ape_install.CommandLineParser()
        VENV_CREATION_ARGS = cmdargs.get_venv_creation_args()
        self.assertIn('-p', VENV_CREATION_ARGS)
        self.assertIn('python3', VENV_CREATION_ARGS)

    def test_ape_install_args_with_version(self):
        """
        Tests the construction of the venv creation args.
        :return:
        """
        target_dir = 'webapps'
        sys.argv = ['ape_install.py', target_dir, '--v', '0.3']

        cmdargs = ape_install.CommandLineParser()
        return_val = cmdargs.get_ape_install_args()[0]
        self.assertIn('ape==0.3', return_val)

    def test_ape_install_args_with_commit_id(self):
        """
        Tests the construction of the venv creation args.
        :return:
        """
        target_dir = 'webapps'
        sys.argv = ['ape_install.py', target_dir, '--c', 'aabbcc']

        cmdargs = ape_install.CommandLineParser()
        return_val = cmdargs.get_ape_install_args()[1] # [1] must be the URL containing the commit id
        self.assertIn('@aabbcc', return_val)



    def test_ape_install_version_xor_commit_id(self):
        """
        Ensures that either version or commit_id can be passed, not both.
        :return:
        """
        target_dir = 'webapps'
        sys.argv = ['ape_install.py', target_dir, '--c', 'aabbcc', '--v', '0.3']

        self.assertRaises(
            ape_install.VersionCommitIdClash,
            ape_install.CommandLineParser,
        )