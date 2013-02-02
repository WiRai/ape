#! /usr/bin/env python

def read(fname):
    import os.path
    try:
        return open(os.path.join(os.path.dirname(__file__), fname)).read()
    except IOError:
        return ''


setup(
    name='ape',
    version='0.1',
    description='A Productive Environment - make/rake/ant/fab-like system with support for FOSD',
    long_description=read('README.rst'),
    url='http://github.com/henzk/ape',
    author='Hendrik Speidel',
    author_email='hendrik@schnapptack.de',
    license="MIT License",
    keywords='fosd, fop, features, build tool',
    packages=['ape'],
    package_dir={'ape': 'ape'},
    package_data={'ape': []},
    zip_safe=False,
    include_package_data=True,
    scripts=[],
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Operating System :: OS Independent',
        'Topic :: System :: Systems Administration',
        'Topic :: Software Development',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Environment :: Console',
    ],
)