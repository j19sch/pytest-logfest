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

.. image:: https://img.shields.io/github/license/mashape/apistatus.svg
    :target: https://github.com/j19sch/pytest-logfest/blob/master/LICENSE
    :alt: MIT license

Pytest plugin providing three logger fixtures with basic or full writing to log files

----


Features
--------

Three logger fixtures, one of each scope: session, module and function.

Three options for writing log records to file: quiet, basic, full.



Requirements
------------

* Pytest
* Pathlib2 (if using Python 2.7)



Installation
------------

You can install "pytest-logfest" via `pip`_ from `PyPI`_::

    $ pip install pytest-logfest



Usage
-----

Fixtures
~~~~~~~~
The three logger fixtures exposed by this plugin are:

- ``session_logger``
- ``module_logger``
- ``function_logger``

They expose a Python ``Logger`` object, so you can use them as such, e.g. ``session_logger.INFO("This is a log record of level INFO.")``
The log nodes of these loggers match the path to the corresponding location or file.

Pytest's ``--log-cli-level=<level>`` will display these log records on stdout.


Log filenames
~~~~~~~~~~~~~
Writing the log records of the loggers to file can be controlled by the ``--logfest`` command-line option:

- ``--logfest=quiet`` or option omitted: no log files are written.
- ``--logfest=basic``: one log file containing INFO and higher for passed tests, DEBUG and higher for setup errors or failed tests.
- ``--logfest=full``: in addition to the basic log file, all log records are written to a session log file and one log file per module.

Log file names and locations are as follows (directories will be created if needed):

- basic log file in ``./artifacts``: ``session-<session timestmap>.log``
- session-level full log file in ``./artifacts``: ``<request.node.name | logfest-root-node>-<session timestmap>.log``
- module-level full log file in ``./artifacts/<path-to-module>``: ``<module_name>-<session timestmap>.log``

``logfest-root-node`` can be set in ``pytest.ini`` (see below). You can change the compostion of file names through hooks (see below).


pytest.ini
~~~~~~~~~~
The following values in ``pytest.ini`` are relevant to this plugin:

- ``logfest-root-node``: name used as root log node and in log filenames; if not set, defaults to the session's ``request.node.name``.
- ``log-level``: should be set to ``info`` or lower, so pytest captures all relevant log records.
- ``log-format``: the default format is not very convenient in combination with this plugin, suggestion: ``%(name)s - %(levelname)s - %(message)s``


Hooks
~~~~~
There are three hooks to change the components of the log filenames:

- ``pytest_logfest_log_file_name_basic``
- ``pytest_logfest_log_file_name_full_session``
- ``pytest_logfest_log_file_name_full_module``

The expose a list that will be joined with the separator character ``-`` and appended with ``.log``.



Contributing
------------
Contributions are very welcome. Tests can be run with `tox`_, please ensure
good test coverage before you submit a pull request.



License
-------

Distributed under the terms of the `MIT`_ license, "pytest-logfest" is free and open source software.



Issues
------

If you encounter any problems, please `file an issue`_ along with a detailed description.



Acknowledgements
----------------
This `pytest`_ plugin was generated with `Cookiecutter`_ along with `@hackebrot`_'s `cookiecutter-pytest-plugin`_ template.

Thanks to my employer `Mendix`_, for the crafting days in which I worked on this plugin, and for the permission to open-source it.


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
.. _`Mendix`: https://www.mendix.com
