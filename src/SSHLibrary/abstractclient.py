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

    def put_file(self, source, destination, mode):
        homedir = self._create_sftp_client() 
        mode = int(mode)
        sourcepaths = glob.glob(source)
        if len(sourcepaths) > 1 and not self._remote_destination_is_directory(destination):
            raise ValueError('It is not possible to copy multiple source files ' 
                             'to one destination file.')
        if destination.endswith('/'):
            dirpath = destination 
        elif '/' in destination:
            dirpath = '/'.join(destination.split('/')[:-1])
        else:
            dirpath = ''
        self._create_missing_dest_dirs(dirpath)
        if self._remote_destination_is_directory(destination):
            if not destination:
                prefix = homedir
            else:
                prefix = destination
            destpaths = [ prefix + os.path.split(path)[1] for path in sourcepaths ]
        elif destination.startswith('/'):
            destpaths = [ destination ]        
        else:
            destpaths = [ homedir + '/' + destination ]
        self._info("Putting %s to %s" % (sourcepaths, destpaths))
        self._put_files(sourcepaths, destpaths, mode)
        self.sftp_client.close()
    
    def _remote_destination_is_directory(self, destination):
        return destination.endswith('/') or destination == ''
    
    def get_file(self, source, destination):
        self._create_sftp_client()
        sourcefiles = self._get_source_files(source)
        destfiles = self._get_dest_files(sourcefiles, destination)
        self._info('Getting %s to %s' % (sourcefiles, destfiles))
        self._get_files(sourcefiles, destfiles)
        self.sftp_client.close()
        
    def _get_dest_files(self, sourcefiles, dest):
        is_dir = dest.endswith(os.path.sep) or dest == '.'
        if not is_dir and len(sourcefiles) > 1:
            raise ValueError('It is not possible to copy multiple source files ' 
                             'to one destination file.')
        dest = os.path.abspath(dest.replace('\\', '/').replace('/', os.sep)) 
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
