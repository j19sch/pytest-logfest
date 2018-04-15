# -*- coding: utf-8 -*-

import datetime
import pytest

from .logfest import LogfestLogger


def pytest_addoption(parser):
    parser.addoption("--logfest", action="store", default="quiet", help="Default: quiet. Other options: basic, full")

    parser.addini("log_level", "log level", default="DEBUG")
    parser.addini("log_format", "log format", default='%(name)s - %(levelname)s - %(message)s')


def pytest_report_header(config):
    print("Logfest: %s; Timestamp: %s, Log level: %s" % (config.getoption("logfest"), config._timestamp, config.getini("log_level")))


def pytest_addhooks(pluginmanager):
    from . import hooks
    pluginmanager.add_hookspecs(hooks)


@pytest.fixture(scope='function')
def logfest_logger(request):
    logfest = LogfestLogger(request)

    logfest.logger.info("TEST STARTED")

    yield logfest.logger

    logfest.tear_down(request)


@pytest.hookimpl(tryfirst=True)
def pytest_configure(config):
    config._timestamp = datetime.datetime.now().strftime('%Y%m%d-%H-%M-%S')


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """makes test result available to fixtures"""
    outcome = yield
    rep = outcome.get_result()

    setattr(item, "rep_" + rep.when, rep)
