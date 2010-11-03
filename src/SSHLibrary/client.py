#  Copyright 2008-2009 Nokia Siemens Networks Oyj
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

class SSHLibraryClient(object):

    def put_file(self, source, dest, mode, newline_char):
        remotefile = self._create_remote_file(dest, mode)
        localfile = open(source, 'rb')
        position = 0
        while True:
            data = localfile.read(4096)
            if not data:
                break
            if newline_char and '\n' in data:
                data = data.replace('\n', newline_char)
            self._write_to_remote_file(remotefile, data, position)
            position += len(data)
        self._close_remote_file(remotefile)
        localfile.close()
