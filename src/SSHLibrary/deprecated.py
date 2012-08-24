#  Copyright 2008-2012 Nokia Siemens Networks Oyj
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from robot import utils


class DeprecatedSSHLibraryKeywords(object):
    """Mixin class containing deprecated keywords"""

    def set_timeout(self, timeout):
        """*DEPRECATED* Use `Set Default Configuration` instead."""
        old = self._config.timeout
        self._config.update(timeout=timeout)
        return utils.secs_to_timestr(old)

    def set_newline(self, newline):
        """*DEPRECATED* Use `Set Default Configuration` instead."""
        old = self._config.newline
        self._config.update(newline=newline)
        return old

    def set_prompt(self, prompt):
        """*DEPRECATED* Use `Set Default Configuration` instead."""
        old = self._config.prompt or ''
        self._config.update(prompt=prompt)
        return old

    def set_default_log_level(self, level):
        """*DEPRECATED* Use `Set Default Configuration` instead."""
        old = self._config.loglevel
        self._config.update(loglevel=level)
        return old
