# -*- coding: utf-8 -*-

import datetime
import errno
import os
import logging
import logging.handlers
import pytest

from pytest_logfest.logging_classes import FilterOnExactNodename, MyMemoryHandler

try:
    from pathlib import Path
except (ImportError, AttributeError):
    from pathlib2 import Path


def pytest_addoption(parser):
    parser.addoption("--logfest", action="store", default="", help="Default: <empty>. Options: quiet, basic, full")

    parser.addini("logfest-root-node", "root log node of logfest plugin", default=None)


def pytest_report_header(config):
    if config.getoption("logfest"):
        print("Logfest: %s; Timestamp: %s; Log level: %s" % (config.getoption("logfest"), config._timestamp,
                                                             config.getini("log_level")))


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Makes test result available to fixtures"""
    outcome = yield
    rep = outcome.get_result()

    setattr(item, "rep_" + rep.when, rep)


def pytest_addhooks(pluginmanager):
    from . import hooks
    pluginmanager.add_hookspecs(hooks)


@pytest.hookimpl(tryfirst=True)
def pytest_configure(config):
    config._timestamp = datetime.datetime.now().strftime('%Y%m%d-%H-%M-%S')


@pytest.fixture(scope='session', autouse=True)
def root_log_node(request):
    """Returns name of the root log node taken either from the .ini file or else from the session node name."""
    if request.config.getini("logfest-root-node"):
        return request.config.getini("logfest-root-node")
    else:
        return request.node.name


@pytest.fixture(scope='session')
def session_filememoryhandler(request):
    """Returns a FileMemoryHandler that flushes at level WARNING to the target_filehandler"""
    if request.config.getoption("logfest") in ["basic", "full"]:
        target_filehandler = _create_basic_session_filehandler(request)
    else:
        target_filehandler = logging.NullHandler()

    file_memory_handler = MyMemoryHandler(capacity=None, flushLevel=logging.WARNING, target=target_filehandler)
    return file_memory_handler


@pytest.fixture(scope='session', name='session_logger')
def fxt_session_logger(request, root_log_node, session_filememoryhandler):
    """
    Yields a logger named {root_log_node} with one or two handlers:
        - session_filememoryhandler: flushes at level WARNING and flushes with filter after fixture regains control
        - session_handler_full (optional): writes all log records to session-level file
    """
    logger = logging.getLogger(root_log_node)
    logger.addHandler(session_filememoryhandler)

    if request.config.getoption("logfest") == "full":
        session_handler_full = _create_full_session_filehandler(request, root_log_node)
        logger.addHandler(session_handler_full)

    yield logger

    session_filememoryhandler.flush_with_filter_on_info()


@pytest.fixture(scope='module', name='module_logger')
def fxt_module_logger(request, session_logger, session_filememoryhandler):
    """
    Yields a logger, child of the session logger and named the path to the module, with one optional handler:
        - module_logger_full (optional): writes all log records to module- and function-level file

    """
    full_path = Path(request.node.name)
    file_basename = full_path.stem
    file_path = list(full_path.parents[0].parts)

    logger = session_logger.getChild(".".join(file_path + [file_basename]))

    if request.config.getoption("logfest") == "full":
        module_logger_full = _create_full_module_filehandler(request, file_path, file_basename)
        logger.addHandler(module_logger_full)

    yield logger

    session_filememoryhandler.flush_with_filter_on_info()


@pytest.fixture(scope='function', name='function_logger')
def fxt_function_logger(request, module_logger, session_filememoryhandler):
    """
    Yields a logger, child of the module logger and named the name of the function.
    Adds records for test started, setup error, test fail, and test ended.

    """
    logger = module_logger.getChild(request.node.name)

    logger.info("TEST STARTED")

    yield logger

    try:
        if request.node.rep_setup.failed:
            logger.warning("SETUP ERROR")
    except AttributeError:
        pass

    try:
        if request.node.rep_call.failed:
            logger.warning("TEST FAIL")
    except AttributeError:
        pass

    logger.info("TEST ENDED\n")

    session_filememoryhandler.flush_with_filter_on_info()


def _create_logging_file_handler(path_to_file, delay=False):
    file_handler = logging.FileHandler(path_to_file, mode='a', delay=delay)
    file_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s %(levelname)s - %(name)s - %(message)s', "%H:%M:%S")
    file_handler.setFormatter(formatter)

    return file_handler


def _create_basic_session_filehandler(request):
    filename_components = ["session", request.config._timestamp]
    request.config.hook.pytest_logfest_log_file_name_basic(filename_components=filename_components)
    filename = "-".join(filename_components) + ".log"

    _create_directory_if_it_not_exists('./artifacts')

    file_handler = _create_logging_file_handler('./artifacts/%s' % filename)

    return file_handler


def _create_full_session_filehandler(request, root_log_node):
    filename_components = [root_log_node, request.config._timestamp]
    request.config.hook.pytest_logfest_log_file_name_full_session(filename_components=filename_components)
    filename = "-".join(filename_components) + ".log"

    file_handler = _create_logging_file_handler('./artifacts/%s' % filename, delay=True)

    filter = FilterOnExactNodename(root_log_node)  # only session-level records, all others go to module filehandler
    file_handler.addFilter(filter)

    return file_handler


def _create_full_module_filehandler(request, file_path, file_basename):
    log_dir = "./artifacts/" + os.path.sep.join(file_path)
    _create_directory_if_it_not_exists(log_dir)

    filename_components = [file_basename, request.config._timestamp]
    request.config.hook.pytest_logfest_log_file_name_full_module(filename_components=filename_components)
    filename = "-".join(filename_components) + ".log"

    file_handler = _create_logging_file_handler('%s/%s' % (log_dir, filename), delay=True)

    return file_handler


def _create_directory_if_it_not_exists(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise
