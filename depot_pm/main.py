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
import requests
from depot_pm import __version__ as depot_pm_version
from taskr import task, console
from taskr.contrib.system import os_info, has_command, run
import yaml
from .configuration import Configuration
from .check import test_names, check as check_core


@task
@task.set_argument('--verbose', '-v', dest='verbose', action='store_true')
@task.set_argument('--dry-run', '-d', dest='dry_run', action='store_true')
def setup(verbose=False, dry_run=False):
    version(warning_only=True)

    if os_info.is_osx:
        # Check for `brew`
        if not has_command('brew'):
            if verbose:
                console.info('Install homebrew as package manager')
            command = 'ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"'
            if dry_run or verbose:
                console.show(command)
            if not dry_run:
                os.system(command)
        # Check the source of python and ruby
        python_version, _ = run('brew ls --versions python', capture_output=True)
        if not python_version:
            console.warn('You should use brew-installed python. (brew install python)')
        ruby_version, _ = run('brew ls --versions ruby', capture_output=True)
        if not ruby_version:
            console.warn('You should use brew-installed ruby. (brew install ruby)')

    elif os_info.is_linux:
        # TODO: Add yum/apt-get check
        pass


@task
@task.set_argument('package_file', help='path of package file', nargs='?')
@task.set_argument('--verbose', '-v', dest='verbose', action='store_true')
@task.set_argument('--dry-run', '-d', dest='dry_run', action='store_true')
def install(package_file=None, verbose=False, dry_run=False):
    version(warning_only=True)

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
            run(command, should_raise_when_fail=True)
        else:
            console.show(command)

    if verbose:
        console.success('done')


@task
@task.set_argument('--warning-only', dest='warning_only', action='store_true')
def version(warning_only=False):
    version_cmp = lambda s: tuple(map(int, s.split('.')))
    newest_version = max(list(requests.get('https://pypi.python.org/pypi/depot-pm/json').json()['releases'].keys()),
                         key=version_cmp)
    if max(newest_version, depot_pm_version, key=version_cmp) != depot_pm_version:
        console.info('The newest version of depot-pm is {}'.format(newest_version))
        console.info('Update your depot-pm via `pip install -U depot-pm`.')

    if not warning_only:
        console.show('depot-pm {}'.format(depot_pm_version))


@task
@task.set_argument('script_path', nargs='?')
def init_script(script_path=None):
    script = """#!/bin/sh

# Install depot-pm if necessary
which depot-pm 1>/dev/null 2>&1 || {
    [ -z "${PIP}" ] && {
        which pip3 1>/dev/null 2>&1 && PIP=pip3
    } || {
        which pip 1>/dev/null 2>&1 && PIP=pip || {
            easy_install pip
            PIP=pip
        }
    }
    # Go
    ${PIP} install depot-pm
}
# Run install
depot-pm setup
depot-pm install
"""

    script_path = script_path or os.path.abspath(os.path.join(os.getcwd(), 'depot-pm-init'))
    with open(script_path, 'w') as f:
        f.write(script)
    os.system('chmod +x {}'.format(script_path))


@task
@task.set_argument('test_name', choices=test_names)
@task.set_argument('args', nargs='*')
@task.set_argument('-v', '--verbose', dest='verbose', action='store_true')
def check(test_name, args=(), verbose=False):
    try:
        check_core(test_name, *args)
    except ValueError as e:
        if verbose:
            console.error(str(e))
        task.exit(1)
    else:
        task.exit(0)


if __name__ == '__main__':
    task.should_raise_exceptions = True
    task.dispatch()
