SSHLibrary for Robot Framework
==============================

Releasing a new version
-----------------------
1. Run the `tests <atest/README.rst>`__.


2. Update the release notes at https://code.google.com/p/robotframework-sshlibrary/wiki/ReleaseNotes

    Either by cloning the wiki as a Git repository or via the GoogleCode wiki editing UI.

    The script at
    https://code.google.com/p/robotframework/source/browse/tools/get_issues.py?repo=wiki
    can be used for generating the issue list.

3. Update the VERSION identifier

    Edit 'src/SSHLibrary/version.py' in the source repo, commit and push the changes.

4. Create an annotated Git tag in the source repo and push it

    VERSION=N.N git tag -a $VERSION -m "Release $VERSION" && git push --tags

5. Create a source .tar.gz distribution

    python setup.py sdist --formats=gztar

    Verify that the content is correct:

        tar -ztvf robotframework-sshlibrary-N.N.tar.gz)

6. Upload the source distribution to PyPi

    python setup.py sdist upload

7. Update the 'News' section at https://code.google.com/p/robotframework-sshlibrary

    Done via https://code.google.com/p/robotframework-sshlibrary/admin.

8. Tweet (or re-tweet) about the release as @robotframework to get it into
   News at http://robotframework.org.

9. Send release mails.
