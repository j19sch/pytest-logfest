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

    # ToDo: consider different solutions (and document why they're needed)
    parser.addini("log_level", "log level", default="DEBUG")
    parser.addini("log_format", "log format", default='%(name)s - %(levelname)s - %(message)s')


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
def session_fmh(request):
    if request.config.getoption("logfest") in ["basic", "full"]:
        filename_components = ["session", pytest.config._timestamp]
        request.config.hook.pytest_logfest_log_file_name_basic(filename_components=filename_components)
        filename = "-".join(filename_components) + ".log"

        _create_directory_if_it_not_exists('./artifacts')

        # ToDo: add try... except ...
        file_handler = logging.FileHandler('./artifacts/%s' % filename, mode='a')
        file_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s %(levelname)s - %(name)s - %(message)s', "%H:%M:%S")
        file_handler.setFormatter(formatter)

        fmh_target = file_handler
    else:
        fmh_target = None

    file_memory_handler = MyMemoryHandler(capacity=None, flushLevel=logging.WARNING, target=fmh_target)
    return file_memory_handler


@pytest.fixture(scope='session', name='session_logger')
def fxt_session_logger(session_fmh):
    logger = logging.getLogger(ROOT_LOG_NODE)
    logger.addHandler(session_fmh)

    yield logger

    # ToDo: if logfest=full, write all session nodes log records to session log file
    session_fmh.clear_handler()


@pytest.fixture(scope='module', name='module_logger')
def fxt_module_logger(request, session_logger, session_fmh):
    full_path = Path(request.node.name)
    file_basename = full_path.stem

    file_path = list(full_path.parents[0].parts)

    logger = session_logger.getChild(".".join(file_path + [file_basename]))

    if request.config.getoption("logfest") == "full":
        log_dir = "./artifacts/" + os.path.sep.join(file_path)
        _create_directory_if_it_not_exists(log_dir)

        # ToDo: add try... except ...
        filename_components = [file_basename, pytest.config._timestamp]
        request.config.hook.pytest_logfest_log_file_name_full(filename_components=filename_components)
        filename = "-".join(filename_components) + ".log"

        fh = logging.FileHandler('%s/%s' % (log_dir, filename), mode='a')
        fh.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s %(levelname)s - %(name)s - %(message)s', "%H:%M:%S")
        fh.setFormatter(formatter)
        logger.addHandler(fh)

    yield logger

    session_fmh.clear_handler()


@pytest.fixture(scope='function', name='function_logger')
def fxt_function_logger(request, module_logger, session_fmh):
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

    session_fmh.clear_handler()


class MyMemoryHandler(logging.handlers.MemoryHandler):
    def __init__(self, *args, **kwargs):
        class FilterInfoAndHigher(logging.Filter):
            def filter(self, record):
                return record.levelno >= logging.INFO

        self.info_filter = FilterInfoAndHigher()
        super(MyMemoryHandler, self).__init__(*args, **kwargs)

    def shouldFlush(self, record):
        if self.capacity is None:
            return record.levelno >= self.flushLevel
        else:
            return super(MyMemoryHandler, self).shouldFlush(record)

    def clear_handler(self):
        if self.target:
            self.target.addFilter(self.info_filter)
            self.flush()
            self.target.removeFilter(self.info_filter)
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
