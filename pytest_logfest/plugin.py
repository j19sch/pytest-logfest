# -*- coding: utf-8 -*-

import datetime
import errno
import os
import logging
import logging.handlers
import pytest

from pytest_logfest.logging_classes import FilterOnLogLevel, FilterOnExactNodename, MyMemoryHandler

try:
    from pathlib import Path
except (ImportError, AttributeError):
    from pathlib2 import Path


ROOT_LOG_NODE = 'lf'


def pytest_addoption(parser):
    parser.addoption("--logfest", action="store", default="", help="Default: <empty>. Options: quiet, basic, full")

    parser.addini("logfest-root-node", "root log node of logfest plugin", default=None)


def pytest_report_header(config):
    if config.getoption("logfest"):
        print("Logfest: %s; Timestamp: %s; Log level: %s" % (config.getoption("logfest"), config._timestamp,
                                                             config.getini("log_level")))


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """makes test result available to fixtures"""
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
    if request.config.getini("logfest-root-node"):
        return request.config.getini("logfest-root-node")
    else:
        return request.node.name


@pytest.fixture(scope='session')
def session_filememoryhandler(request):
    target_filehandler = _session_filehandler(request)

    file_memory_handler = MyMemoryHandler(capacity=None, flushLevel=logging.WARNING, target=target_filehandler)
    return file_memory_handler


@pytest.fixture(scope='session', name='session_logger')
def fxt_session_logger(request, root_log_node, session_filememoryhandler):
    logger = logging.getLogger(root_log_node)
    logger.addHandler(session_filememoryhandler)
    logger.addHandler(_session_filtered_filehandler(request, root_log_node))

    yield logger

    filter = FilterOnLogLevel(logging.INFO)
    session_filememoryhandler.clear_handler_with_filter(filter)


@pytest.fixture(scope='module', name='module_logger')
def fxt_module_logger(request, session_logger, session_filememoryhandler):
    full_path = Path(request.node.name)
    file_basename = full_path.stem
    file_path = list(full_path.parents[0].parts)

    logger = session_logger.getChild(".".join(file_path + [file_basename]))

    logger.addHandler(_module_filehandler(request, file_path, file_basename))

    yield logger

    filter = FilterOnLogLevel(logging.INFO)
    session_filememoryhandler.clear_handler_with_filter(filter)


@pytest.fixture(scope='function', name='function_logger')
def fxt_function_logger(request, module_logger, session_filememoryhandler):
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

    filter = FilterOnLogLevel(logging.INFO)
    session_filememoryhandler.clear_handler_with_filter(filter)


def _session_filehandler(request):
    if request.config.getoption("logfest") in ["basic", "full"]:
        filename_components = ["session", pytest.config._timestamp]
        request.config.hook.pytest_logfest_log_file_name_basic(filename_components=filename_components)
        filename = "-".join(filename_components) + ".log"

        _create_directory_if_it_not_exists('./artifacts')

        file_handler = logging.FileHandler('./artifacts/%s' % filename, mode='a')
        file_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s %(levelname)s - %(name)s - %(message)s', "%H:%M:%S")
        file_handler.setFormatter(formatter)

        return file_handler
    else:
        return logging.NullHandler()


def _session_filtered_filehandler(request, root_log_node):
    if request.config.getoption("logfest") == "full":
        filename_components = [root_log_node, pytest.config._timestamp]
        request.config.hook.pytest_logfest_log_file_name_full_session(filename_components=filename_components)
        filename = "-".join(filename_components) + ".log"

        file_handler = logging.FileHandler('./artifacts/%s' % filename, mode='a', delay=True)
        file_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s %(levelname)s - %(name)s - %(message)s', "%H:%M:%S")
        file_handler.setFormatter(formatter)

        filter = FilterOnExactNodename(root_log_node)
        file_handler.addFilter(filter)

        return file_handler
    else:
        return logging.NullHandler()


def _module_filehandler(request, file_path, file_basename):
    if request.config.getoption("logfest") == "full":
        log_dir = "./artifacts/" + os.path.sep.join(file_path)
        _create_directory_if_it_not_exists(log_dir)

        filename_components = [file_basename, pytest.config._timestamp]
        request.config.hook.pytest_logfest_log_file_name_full_module(filename_components=filename_components)
        filename = "-".join(filename_components) + ".log"

        file_handler = logging.FileHandler('%s/%s' % (log_dir, filename), mode='a')
        file_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s %(levelname)s - %(name)s - %(message)s', "%H:%M:%S")
        file_handler.setFormatter(formatter)

        return file_handler
    else:
        return logging.NullHandler()


def _create_directory_if_it_not_exists(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise
