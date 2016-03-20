#!/usr/bin/env python
from __future__ import absolute_import
from __future__ import print_function
import os
import sys
import stat
from subprocess import call
from os.path import join as pj
import argparse



class VirtualEnv(object):
    """
    Provides an api for virtualenv.
    """

    def __init__(self, venv_dir):
        self.bin_dir = pj(venv_dir, 'bin')

    def call_bin(self, script_name, args):
        call([pj(self.bin_dir, script_name)] + list(args))

    def pip(self, *args):
        self.call_bin('pip', list(args))

    def python(self, *args):
        self.call_bin('python', args)

    def python_oneliner(self, snippet):
        self.python('-c', snippet)


class VersionCommitIdClash(Exception):
    """
    Raised in case both version and commit ID was passed which is illegal
    as both are exclusive.
    """
    pass


class CommandLineParser(object):
    """
    Wrapper arround argsparse.ArgumentParser. Encapsulates
    arg parsing and the construction of variables, such as the ape_install_args which
    may be the stable ape version from pypie or a specific commit.

    In fact this class encapsulates the variability originating from several script
    arguments to one common api. The installation routine thus only uses this
    api without bothering about python version for virtualenv or ape version/commit id.
    """

    def __init__(self):
        """
        Initializes the argparser.
        Pretty good overview about the commands the install script provides.
        """

        parser = argparse.ArgumentParser(description='install a productive environment')
        parser.add_argument(
            'ape_root_dir',
            type=str,
            help='Specifies the APE_ROOT_DIR that is to be created.'
        )
        parser.add_argument(
            '--git', type=str,
            dest='commit_id',
            help='Use this option to install a specific commit of ape.'
        )
        parser.add_argument(
            '--pypi', type=str,
            dest='version',
            help='Use this option to install a specific version of ape from PyPI'
        )
        parser.add_argument(
            '--python',
            type=str,
            dest='python_executable',
            help='Use this option to pass a custom python executable. E.g. to use python3.'
        )

        self.arg_dict = parser.parse_args()
        # check for exclusive arguments.
        if self.arg_dict.version and self.arg_dict.commit_id:
            raise VersionCommitIdClash()

    def get_venv_creation_args(self):
        """
        Returns a list of arguments to install virtualenv.
        :return: list
        """
        install_cmd = ['virtualenv', self.get_venv_dir(), '--no-site-packages']
        if self.arg_dict.python_executable:
            install_cmd += ['-p', self.arg_dict.python_executable]
        return install_cmd

    def get_ape_root_dir(self):
        """
        Returns the absolute path to the ape root dir.
        :return: string, path
        """
        return os.path.abspath(self.arg_dict.ape_root_dir)

    def get_ape_dir(self):
        """
        Returns the absolute path to the ape dir.
        :return: string
        """
        return os.path.join(self.get_ape_root_dir(), '_ape')

    def get_venv_dir(self):
        """
        Returns the absolute path to the virtualenv dir
        :return: string
        """
        return os.path.join(self.get_ape_dir(), 'venv')

    def get_ape_install_args(self):
        """
        Returns the installation arguments to install ape via pip taking the
        --v (version) and --c (commit id) command line arguments into account.
        :return: a list of aruments
        """
        install_args = []

        if self.arg_dict.version:
            install_args += ['ape==%s' % self.arg_dict.version]
        elif self.arg_dict.commit_id:
            install_args += ['-e', 'git+https://github.com/henzk/ape.git@%s#egg=ape' % self.arg_dict.commit_id]
        else:
            install_args += ['ape']

        return install_args

    def get_activape_dest(self):
        """
        Returns the absolute path to the activape command.
        """
        return os.path.join(self.get_ape_dir(), 'activape')

    def get_aperun_dest(self):
        """
        Returns the absolute path to the aperun
        :return:
        """
        return os.path.join(self.get_ape_dir(), 'aperun')



def main():
    """
    Main installation is executed here.
    :return:
    """

    # init the argparser
    try:
        cmdargs = CommandLineParser()
    except VersionCommitIdClash as e:
        print('ERROR: either specify version XOR commit_id, not both')
        sys.exit(1)

    # init all variables needed for furher installation
    APE_ROOT_DIR = cmdargs.get_ape_root_dir()
    APE_DIR = cmdargs.get_ape_dir()
    VENV_DIR = cmdargs.get_venv_dir()
    VENV_CREATION_ARGS = cmdargs.get_venv_creation_args()
    APE_INSTALL_ARGS = cmdargs.get_ape_install_args()
    ACTIVAPE_DEST = cmdargs.get_activape_dest()
    APERUN_DEST = cmdargs.get_aperun_dest()

    # create the ape root dir
    if os.path.exists(APE_ROOT_DIR):
        print('ape root dir already exists: ', APE_ROOT_DIR)
        print('aborted')
        sys.exit(1)

    if not os.path.isdir(os.path.dirname(APE_ROOT_DIR)):
        print('parent directory not found: ', os.path.dirname(APE_ROOT_DIR))
        print('aborted')
        sys.exit(1)

    # create the required ape directories
    # -----------------------------------------
    os.mkdir(APE_ROOT_DIR)
    os.mkdir(APE_DIR)

    # install the venv
    # -----------------------------------------
    try:
        call(VENV_CREATION_ARGS)
    except OSError:
        print('You probably dont have virtualenv installed: pip install virtualenv')
        sys.exit(1)

    venv = VirtualEnv(VENV_DIR)
    print(APE_INSTALL_ARGS)
    venv.pip('install', *APE_INSTALL_ARGS)

    print('*** creating _ape/activape and aperun scripts')

    # get the activape_template from inside the ape package installed in venv
    venv.python_oneliner(
        'import os, shutil, pkg_resources;'
        'shutil.copyfile(os.path.abspath('
        'pkg_resources.resource_filename('
        '"ape", "resources/activape_template"'
        ')), "%s")'
         % ACTIVAPE_DEST
    )

    venv.python_oneliner(
        'import os, shutil, pkg_resources;'
        'shutil.copyfile(os.path.abspath('
        'pkg_resources.resource_filename('
        '"ape", "resources/aperun_template"'
        ')), "%s")'
         % APERUN_DEST
    )

    st = os.stat(APERUN_DEST)
    os.chmod(APERUN_DEST, st.st_mode | stat.S_IEXEC)

    if not os.path.isfile(ACTIVAPE_DEST):
        print('!!Error creating activape script!!')
        print('aborted')
        sys.exit(1)

    if not os.path.isfile(APERUN_DEST):
        print('!!Error creating aperun script!!')
        print('aborted')
        sys.exit(1)

    print()
    print('*** ape container mode setup complete')

if __name__ == '__main__':
    main()
