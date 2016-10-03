#!/usr/bin/env python
from __future__ import absolute_import
from __future__ import print_function
import os
import sys
import stat
from subprocess import call
from os.path import join as pj
import argparse

try:
    #py3
    from urllib.request import urlretrieve
except:
    #py2 fallback
    from urllib import urlretrieve


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

        print(os.listdir(self.bin_dir))
        self.non_local_pip = False


    def call_bin(self, script_name, args):
        call([pj(self.bin_dir, script_name)] + list(args))

    def pip(self, *args):
        if self.non_local_pip:
            self.python(*['-m', 'pip'] + list(args))
        else:
            self.call_bin('pip', list(args))

    def python(self, *args):
        self.call_bin('python', args)

    def python_oneliner(self, snippet):
        self.python('-c', snippet)

    def has_pip(self):
        return (
            os.path.isfile(pj(self.bin_dir, 'pip'))
            or os.path.isfile(pj(self.bin_dir, 'pip.exe'))
        )

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
            help='Specifies the ape_root_dir that is to be created.'
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
            '--local-checkout',
            dest='local_checkout',
            action='store_true',
            help='Install local ape version (assumes you cloned the repo e.g. for hacking on ape itself)'
        )
        parser.add_argument(
            '--use-pyenv',
            dest='use_pyenv',
            action='store_true',
            help='EXPERIMENTAL: set this, to use pyenv instead of virtualenv (requires at least python3.5)'
        )

        self.arg_dict = parser.parse_args()
        # check for exclusive arguments.
        numversionargs = sum([int(x) for x in [
            bool(self.arg_dict.commit_id),
            bool(self.arg_dict.version),
            self.arg_dict.dev,
            self.arg_dict.local_checkout,
        ]])
        
        if numversionargs > 1:
            raise InstallationError('more than one of the following exclusive parameters specified: --dev --git --pypi --local-checkout')

        if self.arg_dict.use_pyenv and sys.version_info < (3, 4):
            raise InstallationError('--use-pyenv is unsupported for this python version. Use python3.5 or above.')

        if self.arg_dict.dev:
            self.arg_dict.commit_id = 'master'

    def get_venv_creation_args(self):
        """
        Returns a list of arguments to install virtualenv.
        :return: list
        """
        install_cmd = ['virtualenv', self.get_venv_dir(), '--no-site-packages']
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
    ape_root_dir = cmdargs.get_ape_root_dir()
    ape_dir = cmdargs.get_ape_dir()
    venv_dir = cmdargs.get_venv_dir()
    venv_creation_args = cmdargs.get_venv_creation_args()
    ape_install_args = cmdargs.get_ape_install_args()
    activape_dest = cmdargs.get_activape_dest()
    aperun_dest = cmdargs.get_aperun_dest()

    # create the ape root dir
    if os.path.exists(ape_root_dir):
        raise InstallationError('ape root dir already exists: ', ape_root_dir)

    if not os.path.isdir(os.path.dirname(ape_root_dir)):
        raise InstallationError('Parent directory not found: ', os.path.dirname(ape_root_dir))

    # create the required ape directories
    # -----------------------------------------
    os.mkdir(ape_root_dir)
    os.mkdir(ape_dir)

    if not cmdargs.arg_dict.use_pyenv:
        # default: install the venv on python2
        try:
            call(venv_creation_args)
        except OSError:
            raise InstallationError('You probably dont have virtualenv installed: pip install virtualenv')
        venv = VirtualEnv(venv_dir)
    else:
        #for py3.4 and up, use venv module from stdlib
        from venv import EnvBuilder
        builder = EnvBuilder(with_pip=True)
        builder.create(venv_dir)

        #check if pip is installed - for some reason, it is currently unavailable on travis ci
        venv = VirtualEnv(venv_dir)
        if not venv.has_pip():
            urlretrieve('https://bootstrap.pypa.io/get-pip.py', 'get-pip.py')
            venv.python('get-pip.py')
            os.remove('get-pip.py')

    #validate that pip is available in venv
    if not venv.has_pip():
        #after installation, if pip is still not here, assume that pip works
        #TODO venv.non_local_pip = True
        raise InstallationError('Unable to install pip in venv')

    print('installing ape: ' + repr(ape_install_args))
    venv.pip('install', *ape_install_args)

    print('*** creating _ape/activape and aperun scripts')

    # get the activape_template from inside the ape package installed in venv
    venv.python_oneliner(
        'import os, shutil, pkg_resources;'
        'shutil.copyfile(os.path.abspath('
        'pkg_resources.resource_filename('
        '"ape", "resources/activape_template"'
        ')), "%s")'
         % activape_dest.replace('\\', '/')
    )

    venv.python_oneliner(
        'import os, shutil, pkg_resources;'
        'shutil.copyfile(os.path.abspath('
        'pkg_resources.resource_filename('
        '"ape", "resources/aperun_template"'
        ')), "%s")'
         % aperun_dest.replace('\\', '/')
    )

    st = os.stat(aperun_dest)
    os.chmod(aperun_dest, st.st_mode | stat.S_IEXEC)

    if not os.path.isfile(activape_dest):
        raise InstallationError('Error creating activape script')

    if not os.path.isfile(aperun_dest):
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
