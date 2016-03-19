from subprocess import call
from os.path import join as pj
import glob
import os


class VirtualEnv(object):

    def __init__(self, venv_dir):
        self.venv_dir = venv_dir

        self.bin_dir = pj(venv_dir, 'bin')

        if not os.path.isdir(self.bin_dir):
            self.bin_dir = pj(venv_dir, 'Scripts')

    def call_bin(self, script_name, args):
        call([pj(self.bin_dir, script_name)] + list(args))

   
    def pip_install(self, repo_url):
        self.call_bin('pip', ['install', '-e', 'git+%s' % repo_url])
        
        
    def pip_install_requirements(self, file_path):
        file_path = pj(os.environ['CONTAINER_DIR'], file_path)
        self.call_bin('pip', ['install', '-r', file_path])

    
    def get_paths(self):
        '''
        get list of module paths
        '''
        
        #site package dir of virtualenv (os dependent)
        venv_site_packages = None

        #linux
        venv_site_packages_glob = glob.glob('%s/lib/*/site-packages' % self.venv_dir)

        if len(venv_site_packages_glob):
            venv_site_packages = venv_site_packages_glob[0]

        else:
            #windows
            win_venv_site_packages = '%s/lib/site-packages' % self.venv_dir
            if os.path.isdir(win_venv_site_packages):
                venv_site_packages = win_venv_site_packages

        return [
            self.venv_dir,
            venv_site_packages,
        ]

    def pip(self, *args):
        self.call_bin('pip', list(args))

    def python(self, *args):
        self.call_bin('python', args)

    def python_oneliner(self, snippet):
        self.python('-c', snippet)
