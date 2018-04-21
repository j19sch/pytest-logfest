# -*- coding: utf-8 -*-

import datetime
import errno
import os
import logging
import pytest


try:
    from pathlib import Path
except (ImportError, AttributeError):
    from pathlib2 import Path


ROOT_LOG_NODE = 'lf'


def pytest_addoption(parser):
    # ToDo: re-add configurability of logging
    parser.addoption("--logfest", action="store", default="quiet", help="Default: quiet. Other options: basic, full")

    parser.addini("log_level", "log level", default="DEBUG")
    parser.addini("log_format", "log format", default='%(name)s - %(levelname)s - %(message)s')


def pytest_report_header(config):
    print("Logfest: %s; Timestamp: %s, Log level: %s" % (config.getoption("logfest"), config._timestamp,
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


@pytest.fixture(scope='session', autouse=True)
def session_fmh(request):
    filename_components = [pytest.config._timestamp, "session"]
    request.config.hook.pytest_logfest_log_file_name_basic(filename_components=filename_components)
    filename = "-".join(filename_components) + ".log"

    file_handler = logging.FileHandler('./artifacts/%s' % filename, mode='a')
    file_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s %(levelname)s - %(name)s - %(message)s', "%H:%M:%S")
    file_handler.setFormatter(formatter)

    file_memory_handler = MyMemoryHandler(capacity=None, flushLevel=logging.WARNING, target=file_handler)
    file_memory_handler.set_name("session_mem_file")
    return file_memory_handler


@pytest.fixture(scope='session', autouse=True)
def session_logger(session_fhm):
    logger = logging.getLogger(ROOT_LOG_NODE)
    logger.addHandler(session_fhm)

    yield logger

    session_fhm.flush_info_and_higer()


@pytest.fixture(scope='module', autouse=True)
def module_logger(request, session_logger, session_fhm):
    full_path = Path(request.node.name)
    file_basename = full_path.stem

    file_path = list(full_path.parents[0].parts)

    logger = session_logger.getChild(".".join(file_path + [file_basename]))

    log_dir = "./artifacts/" + os.path.sep.join(file_path)
    _create_directory_if_it_not_exists(log_dir)

    filename_components = [pytest.config._timestamp, file_basename]
    request.config.hook.pytest_logfest_log_file_name_full(filename_components=filename_components)
    filename = "-".join(filename_components) + ".log"

    fh = logging.FileHandler('%s/%s' % (log_dir, filename), mode='a')
    fh.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s %(name)s: %(message)s', "%H:%M:%S")
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    yield logger

    session_fhm.flush_info_and_higer()


@pytest.fixture(scope='function', autouse=True)
def function_logger(request, module_logger, session_fhm):
    logger = module_logger.getChild(request.node.name)

    logger.info("TEST START")

    yield logger

    try:
        if request.node.rep_setup.failed:
            logger.warning("TEST SETUP ERROR\n")
    except AttributeError:
        pass

    try:
        if request.node.rep_call.failed:
            logger.warning("TEST FAIL\n")
    except AttributeError:
        pass

    logger.info("TEST END\n")

    session_fhm.flush_info_and_higer()


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

    def flush_info_and_higer(self):
        self.target.addFilter(self.info_filter)
        self.flush()
        self.target.removeFilter(self.info_filter)


def _create_directory_if_it_not_exists(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise
