Contributing to AristaLibrary
=============================

AristaLibrary welcomes suggestions, comments, and contributions from anyone.
Please use GitHub Issues to file issues, whether bugs or requests for
enhancements.  

Contributing Keywords, etc.
---------------------------

Please keep keywords as small and reusable as possible and follow the general
style of other Robot Framework libraries.   Additionally, this library is
heavily based on `pyeapi<http://github.com/arista-eosplus/pyeapi>` and future
keywords should continue that trend.  There may be cases where enhancing pyeapi
is appropriate to enable better keywords in AristaLibrary.

Before submitting a pull request to AristaLibrary:

* Fork the repository
* Make code changes
* Include/update docstrings
  * ``make docs`` will update doc/AristaLibrary.html
* Run ``make pep8 && make pyflakes``
* Add tests to test/unittest.txt (Robot Framework)
  * ``pybot --pythonpath Aristalibrary --dryrun test/unittest.txt``
* Ensure all tests pass when running against EOS (or vEOS).
  * If you have a vEOS vagrant box and VirtualBox, then run ``cd test/; run_robot_tests_veos.sh``.  This will spin up 2 vEOS nodes, interconnected on Et1, then execute the tests with pybot.
* Rebase to latest develop branch
* Submit a Pull Reuest


Contact
-------

Please contact eosplus-dev@arista.com with any questions or comments on this library.
