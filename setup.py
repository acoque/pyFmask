# Copyright 2021 Arthur Coqué
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from setuptools import setup, find_packages


def readme():
    with open('README.md', 'r') as f:
        return f.read()


setup(
    name='pyFmask',
    version='0.2.0',
    description='A user-friendly python CLI for Fmask 4.3 software (GERS Lab, UCONN).',
    long_description=readme(),
    url='https://github.com/acoque/pyFmask',
    author='A. Coqué',
    author_email='arthur.coque@pm.me',
    license='Apache 2.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'click',
        'psutil',
        'PyYAML'
    ],
    python_requires='>=3.8',
    entry_points="""
        [console_scripts]
        pyFmask=pyfmask.cli:cli
    """,
    zip_safe=True
)
