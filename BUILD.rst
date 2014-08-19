SSHLibrary for Robot Framework
==============================

Releasing a new version
-----------------------
1. Run the `tests <atest/README.rst>`__.


2. Update the VERSION identifier

    Edit 'src/SSHLibrary/version.py' in the source repo, commit and push the changes.

3. Create an annotated Git tag in the source repo and push it

    VERSION=N.N git tag -a $VERSION -m "Release $VERSION" && git push --tags

4. Close the milestone from issuetracker: https://github.com/robotframework/SSHLibrary/milestones

5. Create release on github. See example from previous releases: https://github.com/robotframework/SSHLibrary/releases

6. Create a source .tar.gz distribution

    python setup.py sdist --formats=gztar

    Verify that the content is correct:

        tar -ztvf robotframework-sshlibrary-N.N.tar.gz)

7. Upload the source distribution to PyPi

    python setup.py sdist upload


8. Tweet (or re-tweet) about the release as @robotframework to get it into
   News at http://robotframework.org.

9. Send release mails.
