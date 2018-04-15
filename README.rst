==============
pytest-logfest
==============

.. image:: https://img.shields.io/pypi/v/pytest-logfest.svg
    :target: https://pypi.org/project/pytest-logfest
    :alt: PyPI version

.. image:: https://img.shields.io/pypi/pyversions/pytest-logfest.svg
    :target: https://pypi.org/project/pytest-logfest
    :alt: Python versions

.. image:: https://travis-ci.org/j19sch/pytest-logfest.svg?branch=master
    :target: https://travis-ci.org/j19sch/pytest-logfest
    :alt: See Build Status on Travis CI

.. image:: https://ci.appveyor.com/api/projects/status/github/j19sch/pytest-logfest?branch=master
    :target: https://ci.appveyor.com/project/j19sch/pytest-logfest/branch/master
    :alt: See Build Status on AppVeyor

Pytest plugin to write test logs to file(s)

----


Features
--------

Logger fixture with specific log node for each test:
  - ``--logfest=full`` writes one log file per test file in a dir tree matching the tests, containing:
    - log records for start and end of each test
    - all log records from the test
  - ``--logfest=basic`` writes one log file per root test dir, containing:
    - log records for start and end of each test
    - all log records of level ``info`` or higher from the test
    - in case of setup or test failing, all log records from the test


Requirements
------------

* Pytest
* Pathlib2 (if using Python 2)


Installation
------------

You can install "pytest-logfest" via `pip`_ from `PyPI`_::

    $ pip install pytest-logfest


Usage
-----

Run ``pytest`` with either ``--logfest=full`` or ``--logfest=basic``. If you use ``--logfest=quiet`` or don't provide the parameter, no log files will be generated.

Note that the plugin sets ``log_level`` and ``log_format``, so changing those will affect the behaviour of the plugin.


Contributing
------------
Contributions are very welcome. Tests can be run with `tox`_, please ensure
the coverage at least stays the same before you submit a pull request.


License
-------

Distributed under the terms of the `MIT`_ license, "pytest-logfest" is free and open source software.


Issues
------

If you encounter any problems, please `file an issue`_ along with a detailed description.


Acknowledgements
----------------
This `pytest`_ plugin was generated with `Cookiecutter`_ along with `@hackebrot`_'s `cookiecutter-pytest-plugin`_ template.


.. _`Cookiecutter`: https://github.com/audreyr/cookiecutter
.. _`@hackebrot`: https://github.com/hackebrot
.. _`MIT`: http://opensource.org/licenses/MIT
.. _`BSD-3`: http://opensource.org/licenses/BSD-3-Clause
.. _`GNU GPL v3.0`: http://www.gnu.org/licenses/gpl-3.0.txt
.. _`Apache Software License 2.0`: http://www.apache.org/licenses/LICENSE-2.0
.. _`cookiecutter-pytest-plugin`: https://github.com/pytest-dev/cookiecutter-pytest-plugin
.. _`file an issue`: https://github.com/j19sch/pytest-logfest/issues
.. _`pytest`: https://github.com/pytest-dev/pytest
.. _`tox`: https://tox.readthedocs.io/en/latest/
.. _`pip`: https://pypi.org/project/pip/
.. _`PyPI`: https://pypi.org/project
