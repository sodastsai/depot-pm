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
import six


class Package(object):

    def __init__(self, package_source):
        if isinstance(package_source, dict):
            self._name = package_source.get('package', None)
            self._test = package_source.get('test', None)
            self._skip_test = package_source.get('skip-test', False)
            self._single_install = package_source.get('single', False)
            self._post_install_script = package_source.get('post-install', None)
        else:
            self._name = package_source
            self._test = None
            self._skip_test = False
            self._single_install = False
            self._post_install_script = None

        assert self._name and isinstance(self._name, six.string_types),\
            'Package name is required field. (package_source={})'.format(package_source)

    @property
    def name(self):
        """
        :rtype: str
        """
        return self._name

    @property
    def test(self):
        """
        :rtype: str | None
        """
        return self._test

    @property
    def skip_test(self):
        """
        :rtype: bool
        """
        return self._skip_test

    @property
    def single_install(self):
        """
        :rtype: bool
        """
        return self._single_install

    @property
    def post_install_script(self):
        """
        :rtype: str | None
        """
        return self._post_install_script

    def __repr__(self):
        return '<{} {}>'.format(self.__class__.__name__, self.name)
