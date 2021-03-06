#! /usr/bin/env python
# -*- coding: utf-8 -*-

#
# Release process setup see:
# https://github.com/pypa/twine
#
# To setup password cache:
# sudo apt-get install python3-dbus
# pip3 install --user keyring
# python3 -m keyring set https://test.pypi.org/legacy/ your-username
#
# Run this to build the `dist/PACKAGE_NAME-xxx.tar.gz` file
#     rm -rf ./dist && python3 setup.py sdist
#
# Run this to build & upload it to `pypi`, type your account name when prompted.
#     twine upload dist/*
#
# All in one command:
#     rm -rf ./dist && python3 setup.py sdist && twine upload dist/*
#

import re
import os
import sys
import codecs

from setuptools import setup, Extension

# https://bugs.python.org/issue35893
from distutils.command.build_ext import build_ext
from distutils.sysconfig import get_config_vars

def get_export_symbols(self, ext):
    parts = ext.name.split(".")
    if parts[-1] == "__init__":
        initfunc_name = "PyInit_" + parts[-2]
    else:
        initfunc_name = "PyInit_" + parts[-1]

build_ext.get_export_symbols = get_export_symbols


try:
    # https://stackoverflow.com/questions/30700166/python-open-file-error
    with codecs.open( "README.md", 'r', errors='ignore' ) as file:
        readme_contents = file.read()

except Exception as error:
    readme_contents = ""
    sys.stderr.write( "Warning: Could not open README.md due %s\n" % error )

try:
    # https://stackoverflow.com/questions/2058802/how-can-i-get-the-version-defined-in-setup-py-setuptools-in-my-package
    filepath = 'source/version.h'

    with open( filepath, 'r' ) as file:
        __version__ ,= re.findall('__version__ = "(.*)"', file.read())

except Exception as error:
    __version__ = "0.0.1"
    sys.stderr.write( "Warning: Could not open '%s' due %s" % ( filepath, error ) )

cmdclass = {}
define_macros = []
extra_compile_args = []

# FASTFILE_DEBUG=1 pip3 install .
# set "FASTFILE_DEBUG=1" && pip3 install .
# https://stackoverflow.com/questions/677577/distutils-how-to-pass-a-user-defined-parameter-to-setup-py
debug_variable_name = 'FASTFILE_DEBUG'
regex_variable_name = 'FASTFILE_REGEX'
getline_variable_name = 'FASTFILE_GETLINE'
trimutf8_variable_name = 'FASTFILE_TRIMUFT8'

debug_variable_value = int( os.environ.get( debug_variable_name, 0 ) )
regex_variable_value = int( os.environ.get( regex_variable_name, 0 ) )
getline_variable_value = int( os.environ.get( getline_variable_name, 0 ) )
trimutf8_variable_value = int( os.environ.get( trimutf8_variable_name, 1 ) )

class build_ext_compiler_check(build_ext):
    def build_extensions(self):
        compiler = self.compiler.compiler_type

        # print('\n\ncompiler', compiler, 'debug_variable_value', debug_variable_value)
        for extension in self.extensions:

            if extension == myextension:

                if 'msvc' in compiler:

                    if debug_variable_value:
                        extension.extra_compile_args.append( '/Od' )
                        extension.extra_compile_args.append( '/Z7' )

                        extension.extra_link_args.append( '/Od' )
                        extension.extra_link_args.append( '/Z7' )

                else:

                    if debug_variable_value:
                        extension.extra_compile_args.append( '-O0' )
                        extension.extra_compile_args.append( '-g' )
                        extension.extra_compile_args.append( '-ggdb' )

                        extension.extra_link_args.append( '-O0' )
                        extension.extra_link_args.append( '-g' )
                        extension.extra_link_args.append( '-ggdb' )

                    extension.extra_compile_args.append( '-std=c++11' )
                    extension.extra_compile_args.append( '-fstack-protector-all' )

                    extension.extra_link_args.append( '-std=c++11' )
                    extension.extra_link_args.append( '-fstack-protector-all' )

                if regex_variable_value == 2:
                        extension.libraries.append( 'pcre2-8' )

                if regex_variable_value == 3:
                        extension.libraries.append( 're2' )

                if regex_variable_value == 4:
                        extension.libraries.append( 'hs' )
                        extension.include_dirs.append( '/usr/include/hs' )

        super().build_extensions()


cmdclass['build_ext'] = build_ext_compiler_check

def setcppoptmiztionflag(level):
    cfg_vars = get_config_vars()

    # https://stackoverflow.com/questions/17730788/search-and-replace-with-whole-word-only-option
    # https://stackoverflow.com/questions/8106258/cc1plus-warning-command-line-option-wstrict-prototypes-is-valid-for-ada-c-o
    for key, value in cfg_vars.items():

        if type(value) == str:
            # print('key %-20s' % key, 'value', value)
            # value = re.sub( r'\-g[^ ]*\b', r'', value )
            value = re.sub( r'\-O2\b', level, value )
            value = re.sub( r'\-O3\b', level, value )
            cfg_vars[key] = value

if debug_variable_value:
    setcppoptmiztionflag( r'-O0' )

    sys.stderr.write( "Using fastfilepackage '%s=%s' environment variable!\n" % ( debug_variable_name, debug_variable_value ) )
    define_macros.append( (debug_variable_name, debug_variable_value) )
else:
    setcppoptmiztionflag( r'-O2' )


if regex_variable_value:
    sys.stderr.write( "Using fastfilepackage '%s=%s' environment variable!\n" % ( regex_variable_name, regex_variable_value ) )
    define_macros.append( (regex_variable_name, regex_variable_value) )


if getline_variable_value:
    sys.stderr.write( "Using fastfilepackage '%s=%s' environment variable!\n" % ( getline_variable_name, getline_variable_value ) )
    define_macros.append( (getline_variable_name, getline_variable_value) )


if trimutf8_variable_value is not None:
    sys.stderr.write( "Using fastfilepackage '%s=%s' environment variable!\n" % ( trimutf8_variable_name, trimutf8_variable_value ) )
    define_macros.append( (trimutf8_variable_name, trimutf8_variable_value) )

    try:
        filepath = 'source/installation_options.h'
        result = "const int %s_CONSTANT = %s;\n" % ( trimutf8_variable_name, trimutf8_variable_value )

        with open( filepath, 'wb' ) as file:
            file.write( result.encode() )

    except Exception as error:
        sys.stderr.write( "Warning: Could not open '%s' due %s" % ( filepath, error ) )


# https://docs.python.org/3.7/distutils/apiref.html#distutils.core.Extension
# https://stackoverflow.com/questions/30985862/how-to-identify-compiler-before-defining-cython-extensions
# https://stackoverflow.com/questions/10924885/is-it-possible-to-include-subdirectories-using-dist-utils-setup-py-as-part-of
myextension = Extension(
    language = "c++",
    name = 'fastfilepackage',
    sources = [
        'source/debugger.cpp',
        'source/fastfile.cpp',
        'source/fastfilewrapper.cpp'
    ],
    include_dirs = [ 'source' ],
    define_macros = define_macros,
)

setup(
        name = 'fastfilepackage',
        version = __version__,
        description = 'An module written with pure Python C Extensions to open a file and cache the more recent accessed lines',
        author = 'Evandro Coan',
        license = "LGPLv2.1",
        url = 'https://github.com/evandrocoan/fastfilepackage',
        ext_modules= [ myextension ],

        # https://stackoverflow.com/questions/7522250/how-to-include-package-data-with-setuptools-distribute/
        package_data = { '': [ '**.txt', '**.md', '**.py', '**.h', '**.hpp', '**.c', '**.cpp' ], },
        cmdclass=cmdclass,
        long_description = readme_contents,
        long_description_content_type='text/markdown',
        classifiers=[
            'Development Status :: 5 - Production/Stable',
            'Environment :: Console',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: GNU Lesser General Public License v2 or later (LGPLv2+)',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.5',
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: 3.7',
            'Topic :: Software Development :: Libraries :: Python Modules',
        ],
    )

