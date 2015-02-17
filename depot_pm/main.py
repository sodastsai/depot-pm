#!/usr/bin/env python

#
# Copyright 2015 sodastsai
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
#

from __future__ import unicode_literals, division, absolute_import, print_function
import os
from depot_pm import __version__ as depot_pm_version
from taskr import task, console
import yaml
from depot_pm.configuration import Configuration


def resolve_package_content_path(source_path):
    """
    :type source_path: str
    :rtype: str
    """
    dir_path = None
    while not source_path:
        # Go to upper level
        new_dir_path = os.path.split(dir_path)[0] if dir_path else os.getcwd()
        if new_dir_path == dir_path:
            break
        else:
            dir_path = new_dir_path
        # Check file - yaml first
        source_path = os.path.join(dir_path, 'depot.yaml')
        if not os.path.exists(source_path):
            # Check file - json
            source_path = os.path.join(dir_path, 'depot.json')
            if not os.path.exists(source_path):
                source_path = None

    return source_path


default_installers = {
    'pip': {},
    'gem': {},
    'yum': {
        'os': True,
        'sudo': True,
        'syntax': '{} install -y {}',
    },
    'brew': {
        'os': True,
    },
}
"""
keys:
  sudo(bool, default=False),
  os(bool, default=False),
  multiple(bool, default=True),
  syntax(str, default='{} install {}'),
  command(str, default=<installer name>)
"""


@task
@task.set_argument('package_file', help='path of package file', nargs='?')
@task.set_argument('--verbose', '-v', dest='verbose', action='store_true')
@task.set_argument('--dry-run', '-d', dest='dry_run', action='store_true')
def install(package_file=None, verbose=False, dry_run=False):
    try:
        configuration = Configuration.auto_discover(package_file)
    except yaml.YAMLError as e:
        if verbose:
            console.error('Cannot parse package file: {}'.format(e))
        task.exit(2)
        return  # suppress pycharm warning

    if configuration:
        if verbose:
            console.info('resolved package file: {}'.format(configuration.config_file_path))
    else:
        if verbose:
            console.error('Cannot find package file.')
        task.exit(1)
        return  # suppress pycharm warning

    # Go
    if dry_run and verbose:
        console.info('dry run: depot-pm won\'t perfom following commands.')

    for command in configuration.commands:
        if verbose:
            console.info('Execute command: {}'.format(command))
        if not dry_run:
            os.system(command)
        else:
            console.show(command)

    if verbose:
        console.success('done')


@task
def version():
    print('depot-pm {}'.format(depot_pm_version))


if __name__ == '__main__':
    task.should_raise_exceptions = True
    task.dispatch()
