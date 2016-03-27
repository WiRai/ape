#!/usr/bin/env python
from __future__ import absolute_import
from __future__ import print_function
import os
import sys
import stat
from subprocess import call
from os.path import join as pj
import argparse


class InstallationError(Exception):
    '''
    generic exception for installation failure
    '''
    pass


class VirtualEnv(object):
    """
    Provides an api for virtualenv.
    """

    def __init__(self, venv_dir):
        self.bin_dir = None
        bin_dirs = ['bin', 'Scripts']

        for basename in bin_dirs:
            absdir = pj(venv_dir, basename)
            if os.path.isdir(absdir):
                self.bin_dir = absdir
                break
        
        if not self.bin_dir:
            raise InstallationError('bin dir not found in virtualenv')

        print os.listdir(self.bin_dir)


    def call_bin(self, script_name, args):
        call([pj(self.bin_dir, script_name)] + list(args))

    def pip(self, *args):
        self.call_bin('pip', list(args))

    def python(self, *args):
        self.call_bin('python', args)

    def python_oneliner(self, snippet):
        self.python('-c', snippet)


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
            '--git',
            type=str,
            dest='commit_id',
            help='Use this option to install a specific commit of ape.'
        )
        parser.add_argument(
            '--pypi',
            type=str,
            dest='version',
            help='Use this option to install a specific version of ape from PyPI'
        )
        parser.add_argument(
            '--dev',
            dest='dev',
            action='store_true',
            help='Install development version (tip of master branch at github)'
        )
        parser.add_argument(
            '--python',
            type=str,
            dest='python_executable',
            help='Use this option to pass a custom python executable. E.g. to use python3.'
        )

        self.arg_dict = parser.parse_args()
        # check for exclusive arguments.
        numversionargs = sum([int(x) for x in [
            bool(self.arg_dict.commit_id),
            bool(self.arg_dict.version),
            self.arg_dict.dev,
        ]])
        
        if numversionargs > 1:
            raise InstallationError('more than one of the following exclusive parameters specified: --dev --git --pypi')

        if self.arg_dict.dev:
            self.arg_dict.commit_id = 'master'

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
    version_info = sys.version_info

    print()
    print('a productive environment installation started')
    print()
    print('...running on Python %s' % '.'.join([str(x) for x in version_info]))

    if version_info < (2, 6) or (version_info >= (3, 0) and version_info < (3, 4)):
        raise InstallationError('Unsupported python version. Please use Python 2.6., 2.7, or 3.4+.')

    # init the argparser
    cmdargs = CommandLineParser()

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
        raise InstallationError('ape root dir already exists: ', APE_ROOT_DIR)

    if not os.path.isdir(os.path.dirname(APE_ROOT_DIR)):
        raise InstallationError('Parent directory not found: ', os.path.dirname(APE_ROOT_DIR))

    # create the required ape directories
    # -----------------------------------------
    os.mkdir(APE_ROOT_DIR)
    os.mkdir(APE_DIR)

    if version_info < (3, 0):
        # install the venv on python2
        try:
            call(VENV_CREATION_ARGS)
        except OSError:
            raise InstallationError('You probably dont have virtualenv installed: pip install virtualenv')

    else:
        #for py3.4 and up, use venv module from stdlib
        from venv import EnvBuilder
        builder = EnvBuilder(with_pip=True)
        builder.create(VENV_DIR)

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
         % ACTIVAPE_DEST.replace('\\', '/')
    )

    venv.python_oneliner(
        'import os, shutil, pkg_resources;'
        'shutil.copyfile(os.path.abspath('
        'pkg_resources.resource_filename('
        '"ape", "resources/aperun_template"'
        ')), "%s")'
         % APERUN_DEST.replace('\\', '/')
    )

    st = os.stat(APERUN_DEST)
    os.chmod(APERUN_DEST, st.st_mode | stat.S_IEXEC)

    if not os.path.isfile(ACTIVAPE_DEST):
        raise InstallationError('Error creating activape script')

    if not os.path.isfile(APERUN_DEST):
        raise InstallationError('Error creating aperun script')

    print()
    print('*** ape container mode setup complete')

if __name__ == '__main__':
    try:
        main()
    except InstallationError as e:
        print(repr(e))
        print('aborted')
        sys.exit(1)
