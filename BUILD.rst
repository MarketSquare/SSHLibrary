SSHLibrary for Robot Framework
==============================

Releasing a new version
-----------------------

1. Update the release notes at https://code.google.com/p/robotframework-sshlibrary/wiki/ReleaseNotes

    Either by cloning the wiki as a Git repository or via the GoogleCode wiki editing UI.
    
    The script at
    https://code.google.com/p/robotframework/source/browse/tools/get_issues.py?repo=wiki
    can be used for generating the issue list.

2. Update the VERSION identifier

    Edit 'src/SSHLibrary/version.py' in the source repo, commit and push the changes.

3. Create an annotated Git tag in the source repo and push it

    VERSION=N.N git tag -a $VERSION -m "Release $VERSION" && git push --tags

4. Create a source .tar.gz distribution

    python setup.py sdist --formats=gztar

    Verify that the content is correct:

        tar -ztvf robotframework-sshlibrary-N.N.tar.gz)

5. Upload the source distribution to PyPi

    python setup.py sdist upload

6. Create the Windows installers (both win32 and win-amd64)

    python setup.py bdist_wininst

    Installers should be created and verified on Windows.

7. Upload the Windows installers PyPi

    python setup.py bdist_wininst upload

8. Update the 'News' section at https://code.google.com/p/robotframework-sshlibrary

    Done via https://code.google.com/p/robotframework-sshlibrary/admin.

9. Write and send the release announcement to the mailing lists

    Include the following lists: devel, users, announce.

10. Tweet about the new version

    Preferably tweet directly as @robotframework or at least retweet as it.
