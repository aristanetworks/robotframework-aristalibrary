Contributing to AristaLibrary
=============================


Releasing a new version
-----------------------

1. Create a release branch

   ``git checkout -b release-X.Y develop``

2. Update the VERSION identifier

   Edit ``AristaLibrary/version.py`` then commit changes

3. Ensure docs are up to date

   * make docs
   * copy doc/AristaLibrary.html
   * git checkout gh-pages
   * replace AristaLibrary.html in gh-pages
   * git add AristaLibrary.html
   * git commit -m "Publish latest docs"
   * git push origin gh-pages
   * git checkout release-branch

4. Create the test sdist package

   ``python setup.py sdist --formats=gztar``

5. Finish the release branch

   * ``git checkout master``
   * ``git merge --no-ff release-X.Y``
   * ``git tag -a vX.Y -m "Release X.Y" && git push --tags``
   * ``git checkout develop``
   * ``git merge --no-ff release-X.Y``  # Then resolve conflicts and commit.
   * ``git branch -d release-X.Y``

6. Create the final sdist package

   ``python setup.py sdist --formats=gztar``

7. Upload to PyPI

   ``python setup.py sdist upload``

8. Generate a GitHub Release and include release notes

   `https://github.com/aristanetworks/robotframework-aristalibrary/releases`

9. Publish news

   * EOS Central
   * Email
   * Publish news to other sites?

Contact
-------

Contact eosplus-dev@arista.com with any questions or comments on this library.
