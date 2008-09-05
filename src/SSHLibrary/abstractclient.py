#  Copyright 2008 Nokia Siemens Networks Oyj
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


import os
import re
import time
import glob
import posixpath

from robot import utils


class AbstractSSHClient:

    def close(self):
        self.client.close()

    def read_until_regexp(self, regexp, timeout):
        """Regexp can be a pattern or a compiled re-object."""
        data = ''
        if isinstance(regexp, basestring):
            regexp = re.compile(regexp)
        start_time = time.time()
        while time.time() < start_time + int(timeout):
            char = self._read()
            if char is not None:
                data += char
            if regexp.search(data): 
                return data
        raise AssertionError("No match found for '%s' in %s"
                             % (regexp.pattern, utils.secs_to_timestr(timeout)))
    
    def read_until(self, expected, timeout):
        data = ''
        start_time = time.time()
        while time.time() < float(timeout) + start_time :
            data += self._read()
            if expected in data:
                return data
        return data

    def put_file(self, source, destination, mode):
        self._create_sftp_client()
        sourcefiles = self._get_put_file_sources(source)
        destfiles, destpath = self._get_put_file_destinations(sourcefiles, destination)
        self._create_missing_dest_dirs(destpath)
        for source, destination in zip(sourcefiles, destfiles):
            self._info("Putting '%s' to '%s'" % (source, destination))
            self._put_file(source, destination, mode)
        self._close_sftp_client()
        
    def _get_put_file_sources(self, source):
        return glob.glob(source.replace('/', os.sep))
        
    def _get_put_file_destinations(self, sources, dest):
        dest = dest.replace('\\', '/')
        if dest == '.':
            dest = self.homedir + '/'
        if len(sources) > 1 and dest[-1] != '/':
            raise ValueError('It is not possible to copy multiple source files ' 
                             'to one destination file.')
        dirpath, filename = self._parse_path_elements(dest)
        if filename:
            return [ posixpath.join(dirpath, filename) ], dirpath
        return [ posixpath.join(dirpath, os.path.split(path)[1]) for path in sources ], dirpath
    
    def _parse_path_elements(self, dest):
        if not posixpath.isabs(dest):
            dest = posixpath.join(self.homedir, dest)
        return posixpath.split(dest)
        
    def get_file(self, source, destination):
        self._create_sftp_client()
        sourcefiles = self._get_get_file_sources(source)
        destfiles = self._get_get_file_destinations(sourcefiles, destination)
        for source, dest in zip(sourcefiles, destfiles):
            self._info('Getting %s to %s' % (source, dest))
            self._get_file(source, dest)
        self._close_sftp_client()
        
    def _get_get_file_sources(self, source):
        path, pattern = posixpath.split(source)
        if not path:
            path = '.'
        sourcefiles = []
        for filename in self._listdir(path):
            if utils.matches(filename, pattern):
                if path:
                    filename = posixpath.join(path, filename)
                sourcefiles.append(filename)
        return sourcefiles
        
    def _get_get_file_destinations(self, sourcefiles, dest):
        if dest == '.':
            dest = os.curdir + os.sep
        is_dir = dest.endswith(os.sep)
        if not is_dir and len(sourcefiles) > 1:
            raise ValueError('It is not possible to copy multiple source files ' 
                             'to one destination file.')
        dest = os.path.abspath(dest.replace('/', os.sep)) 
        self._create_missing_local_dirs(dest, is_dir)
        if is_dir:
            return [ os.path.join(dest, os.path.split(name)[1]) for name in sourcefiles ]
        else:
            return [ dest ]
        
    def _create_missing_local_dirs(self, dest, is_dir):
        if not is_dir:
            dest = os.path.dirname(dest)
        if not os.path.exists(dest):
            self._info("Creating missing local directories for path '%s'" % dest)
            os.makedirs(dest)
    
    def _info(self, msg):
        self._log(msg, 'INFO')
        
    def _log(self, msg, level):
        msg = msg.strip()
        print '*%s* %s' % (level.upper(), msg)
