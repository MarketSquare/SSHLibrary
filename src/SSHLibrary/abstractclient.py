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
        start_time = time.time()
        data = ''
        regexp = re.compile(regexp)
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
        dirpath = ''
        if destination.endswith('/'):
            dirpath = destination 
        elif '/' in destination:
            dirpath = '/'.join(destination.split('/')[:-1])
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
        self._create_missing_local_dirs(destination)
        sourcefiles = self._get_source_files(source)
        if self._local_destination_is_directory(destination):
            if not destination:
                prefix = os.path.abspath(os.curdir) + '/'
            else:
                prefix = destination
            destfiles = [ prefix + os.path.split(name)[1] for name in sourcefiles ]
        elif len(sourcefiles) > 1:
            raise ValueError('It is not possible to copy multiple source files ' 
                             'to one destination file.')
        elif not os.path.isabs(destination):
            destfiles = [ os.path.join(os.path.abspath(os.path.curdir), 
                                       destination) ]
        self._info('Getting %s to %s' % (sourcefiles, destfiles))
        self._get_files(sourcefiles, destfiles)
        self.sftp_client.close()
    
    def _local_destination_is_directory(self, destination):
        return destination.endswith(os.path.sep) or destination == ''
    
    def _create_missing_local_dirs(self, destination):
        curdir = os.path.abspath(os.path.curdir)
        for dirname in os.path.split(destination)[0].split(os.path.sep):
            curdir = os.path.join(curdir, dirname)
            if dirname and not os.path.exists(curdir):
                os.mkdir(curdir)
    
    def _info(self, msg):
        self._log(msg, 'INFO')
        
    def _log(self, msg, level):
        msg = msg.strip()
        print '*%s* %s' % (level.upper(), msg)
