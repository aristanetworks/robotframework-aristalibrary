Contributing to AristaLibrary
=============================


Releasing a new version
-----------------------


1. Update the VERSION identifier

   Edit ``AristaLibrary/version.py`` then commit changes

2. Ensure docs are up to date

   * make docs
   * git checkout gh-pages
   * publish doc/AristaLibrary.html to gh-pages
   * push
   * git checkout release-branch

3. Tag the release branch

   ``git tag -a vX.Y -m "Release X.Y" && git push --tags

4. Create the sdist package

   ``python setup.py sdist --formats=gztar``

5. Upload to PyPI

   ``python setup.py sdist upload``

6. Generate a GitHub Release and include release notes

   `https://github.com/arista-eosplus/robotframework-aristalibrary/releases`

7. Publish news

   * EOS Central
   * Email
   * Publish news to other sites?

Contact
-------

Contact eosplus-dev@arista.com with any questions or comments on this library.
