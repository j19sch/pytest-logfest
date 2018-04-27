# -*- coding: utf-8 -*-

import datetime
import errno
import os
import logging
import logging.handlers
import pytest


try:
    from pathlib import Path
except (ImportError, AttributeError):
    from pathlib2 import Path


ROOT_LOG_NODE = 'lf'


def pytest_addoption(parser):
    parser.addoption("--logfest", action="store", default="", help="Default: <empty>. Options: quiet, basic, full")


def pytest_report_header(config):
    if config.getoption("logfest"):
        print("Logfest: %s; Timestamp: %s; Log level: %s" % (config.getoption("logfest"), config._timestamp,
                                                             config.getini("log_level")))


def pytest_addhooks(pluginmanager):
    from . import hooks
    pluginmanager.add_hookspecs(hooks)


@pytest.hookimpl(tryfirst=True)
def pytest_configure(config):
    config._timestamp = datetime.datetime.now().strftime('%Y%m%d-%H-%M-%S')


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """makes test result available to fixtures"""
    outcome = yield
    rep = outcome.get_result()

    setattr(item, "rep_" + rep.when, rep)


@pytest.fixture(scope='session')
def session_filehandler(request):
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


@pytest.fixture(scope='session')
def session_filememoryhandler(session_filehandler):
    file_memory_handler = MyMemoryHandler(capacity=None, flushLevel=logging.WARNING, target=session_filehandler)
    return file_memory_handler


@pytest.fixture(scope='session', name='session_logger')
def fxt_session_logger(session_filememoryhandler):
    # ToDo: change root log node to request.node.name; implement hook to change it
    logger = logging.getLogger(ROOT_LOG_NODE)
    logger.addHandler(session_filememoryhandler)

    yield logger

    filter = FilterOnLogLevel(logging.INFO)
    session_filememoryhandler.clear_handler_with_filter(filter)


@pytest.fixture(scope='module', name='module_logger')
def fxt_module_logger(request, session_logger, session_filememoryhandler):
    full_path = Path(request.node.name)
    file_basename = full_path.stem

    file_path = list(full_path.parents[0].parts)

    logger = session_logger.getChild(".".join(file_path + [file_basename]))

    if request.config.getoption("logfest") == "full":
        log_dir = "./artifacts/" + os.path.sep.join(file_path)
        _create_directory_if_it_not_exists(log_dir)

        filename_components = [file_basename, pytest.config._timestamp]
        request.config.hook.pytest_logfest_log_file_name_full(filename_components=filename_components)
        filename = "-".join(filename_components) + ".log"

        fh = logging.FileHandler('%s/%s' % (log_dir, filename), mode='a')
        fh.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s %(levelname)s - %(name)s - %(message)s', "%H:%M:%S")
        fh.setFormatter(formatter)
        logger.addHandler(fh)

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


class FilterOnLogLevel(logging.Filter):
    def __init__(self, level):
        self.level = level
        super(FilterOnLogLevel, self).__init__()

    def filter(self, record):
        return record.levelno >= self.level


class FilterOnExactNodename(logging.Filter):
    def __init__(self, node_name):
        self.node_name = node_name
        super(FilterOnExactNodename, self).__init__()

    def filter(self, record):
        return record.name == self.node_name


class MyMemoryHandler(logging.handlers.MemoryHandler):
    def __init__(self, *args, **kwargs):
        super(MyMemoryHandler, self).__init__(*args, **kwargs)

    def shouldFlush(self, record):
        if self.capacity is None:
            return record.levelno >= self.flushLevel
        else:
            return super(MyMemoryHandler, self).shouldFlush(record)

    def clear_handler_with_filter(self, filter):
        if self.target:
            self.target.addFilter(filter)
            self.flush()
            self.target.removeFilter(filter)
        else:
            self.flush()


def _create_directory_if_it_not_exists(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise
