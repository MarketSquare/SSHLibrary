#!/usr/bin/env python

from distutils.core import setup


def main():
    setup(name         = 'SSHLibrary',
          version      =  '0.7',
          description  = 'Test Library for Robot Framework enabling SSH',
          author       = 'Robot Framework Developers',
          author_email = 'robotframework-devel@groups.google.com',
          url          = 'http://code.google.com/p/robotframework-sshlibrary/',
          package_dir  = { '' : 'src'},
          packages     = ['SSHLibrary']
          )
        

if __name__ == "__main__":
    main()
