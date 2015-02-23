Contributing to AristaLibrary
=============================


Releasing a new version
-----------------------

1. Update the release notes at TBD

1.5 Ensure docs are up to date

   * make docs
   * git checkout gh-pages
   * publish doc/AristaLibrary.html to gh-pages
   * push
   * git checkout release-branch

2. Update the VERSION identifier

   Edit ``AristaLibrary/version.py`` then commit changes

3. Tag the release branch

   ``git tag -a x.y -m "Release x.y" && git push --tags

4. Create the sdist package

   ``python setup.py sdist --formats=gztar``

5. Upload to PyPI

   ``python setup.py sdist upload``

6. Publish news

   * EOS Central
   * Email
   * Publish news to other sites?

Contact
-------

Please contact eosplus-dev@arista.com with any questions or comments on this library.
