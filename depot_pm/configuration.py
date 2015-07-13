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
from taskr.contrib.lang import lazy_property
import yaml
from .check import test_names
from .package import Package
from .installer import Installer, default_installers


class Configuration(object):

    @classmethod
    def auto_discover(cls, source_path=None):
        """
        :rtype: Configuration
        """

        # Find source
        accept_exts = ('yaml', 'yml', 'json')
        dir_path = None
        while not source_path:
            # Go to upper level
            new_dir_path = os.path.split(dir_path)[0] if dir_path else os.getcwd()
            if new_dir_path == dir_path:
                break
            else:
                dir_path = new_dir_path
            # Check file
            for accept_ext in accept_exts:
                source_path = os.path.join(dir_path, 'depot.{}'.format(accept_ext))
                if os.path.exists(source_path):
                    break
                else:
                    source_path = None

        return cls(source_path) if source_path else None

    def __init__(self, config_file_path):
        self._config_file_path = config_file_path
        with open(self._config_file_path, 'r') as f:
            self._config_content = yaml.load(f)
            """:type: dict[str, dict]"""

    @property
    def config_file_path(self):
        return self._config_file_path

    @lazy_property
    def packages(self):
        """
        :rtype: dict[str, list[Package]]
        """
        return {name: list(map(Package, packages))
                for name, packages in self._config_content.get('packages', {}).items()}

    @lazy_property
    def installers(self):
        """
        :rtype: list[Installer]
        """

        # Get installers by merging default and user defined ones
        installers = {installer.name: installer for installer in default_installers}
        installers.update({installer.name: installer for installer in
                           map(lambda x: Installer(x[0], **(x[1] or {})),
                               self._config_content.get('installers', {}).items())})

        # Feed installer packages
        for installer in installers.values():
            installer.packages = self.packages.get(installer.name, [])

        # filter out unavailable one and sort by os type
        return sorted(filter(lambda _installer: _installer.available, installers.values()),
                      key=lambda _installer: _installer.os,
                      reverse=True)

    @staticmethod
    def _finalize_test(raw_test, package):
        if raw_test.startswith(':'):
            check_test_name, _, args = raw_test[1:].partition(':')
            if check_test_name in test_names:
                test = 'depot-pm check {} {}'.format(check_test_name, args)
            else:
                raise ValueError('Invalid test name for *check* command: {}'.format(check_test_name))
        else:
            test = raw_test
        return test.format(package=package.name)

    @property
    def commands(self):
        # Traversal installers
        for installer in self.installers:
            commands = []
            multi_install_packages = []
            # Traversal packages
            for package in installer:
                if not package.skip_test and package.test:
                    test = self._finalize_test(package.test, package)
                elif not package.skip_test and installer.test:
                    test = self._finalize_test(installer.test, package)
                else:
                    test = None

                if installer.multiple and not test and not package.single_install and not package.post_install_script:
                    # Install multiple packages directly at once
                    multi_install_packages.append(package.name)
                else:
                    # Install one-by-one (including test)
                    command = installer.syntax.format(installer.name, package.name)
                    if test:
                        command = '{} 1>/dev/null 2>&1 || {}'.format(test, command)
                    if package.post_install_script:
                        command = '({}) && ({})'.format(command, '; '.join(package.post_install_script.splitlines()))
                    commands.append(command)
            # Collect multuple-installing pacakges
            if multi_install_packages:
                commands.append(installer.syntax.format(installer.name, ' '.join(multi_install_packages)))
            # Append sudo
            if installer.sudo:
                commands = map(lambda c: 'sudo {}'.format(c), commands)

            for command in commands:
                yield command
