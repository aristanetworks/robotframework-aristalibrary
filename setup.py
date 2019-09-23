#
# Copyright (c) 2015, Arista Networks, Inc.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
#   Redistributions of source code must retain the above copyright notice,
#   this list of conditions and the following disclaimer.
#
#   Redistributions in binary form must reproduce the above copyright
#   notice, this list of conditions and the following disclaimer in the
#   documentation and/or other materials provided with the distribution.
#
#   Neither the name of Arista Networks nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL ARISTA NETWORKS
# BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
# BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN
# IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
from os.path import abspath, dirname, join

CURDIR = dirname(abspath(__file__))

#from AristaLibrary import __version__, __author__
with open(join(CURDIR, 'AristaLibrary', 'version.py')) as version:
    exec(version.read())

with open(join(CURDIR, 'README.rst')) as readme:
    README = readme.read()

setup(
    name='robotframework-aristalibrary',
    version=VERSION,
    description='Python Robot Framework Library for EOS devices',
    long_description=README,
    author='Arista EOS+ Consulting Services',
    author_email='eosplus-dev@arista.com',
    url='https://aristanetworks.github.io/robotframework-aristalibrary/',
    download_url='https://github.com/aristanetworks/robotframework-aristalibrary/tarball/%s' % VERSION,
    license='BSD-3',
    platforms='any',
    keywords='robotframework testing testautomation arista eos eapi pyeapi',
    packages=['AristaLibrary'],
    install_requires=[
        'docutils>=0.9',
        'pyeapi>=0.8.2,<2',
        'robotframework>=3.0'
    ]
)

