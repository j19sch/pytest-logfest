import os
import pytest

from . import helpers


def test_logging_full_session_fixture(testdir):
    testdir.makepyfile("""
        import pytest

        @pytest.fixture(scope='session', autouse=True)
        def session_fixture(session_logger):
            session_logger.debug("Session debug log line - start")
            yield
            session_logger.debug("Session debug log line - end")

        def test_pass(function_logger, session_fixture):
            pass
     """)

    result = testdir.runpytest(
        '--logfest=full', '--log-level=debug'
    )

    assert result.ret == 0

    artifacts_dir = str(testdir.tmpdir.join('artifacts'))

    assert os.path.isdir(artifacts_dir) is True

    log_files = helpers.get_logfiles_in_testdir(artifacts_dir)
    assert len(log_files) == 3

    timestamp = helpers.get_timestamp_from_logfile_name(log_files[0])
    basic_logfile = "session-%s.log" % timestamp
    helpers.assert_filename_in_list_of_files(basic_logfile, log_files)

    expected_log_lines = ["TEST STARTED",
                          "TEST ENDED"
                          ]
    non_expected_log_lines = ["Session debug log line - start",
                              "Session debug log line - end"
                              ]
    helpers.assert_lines_in_logfile(artifacts_dir + "/" + basic_logfile, expected_log_lines, non_expected_log_lines)

    session_logfile = "test_logging_full_session_fixture0-%s.log" % timestamp
    helpers.assert_filename_in_list_of_files(session_logfile, log_files)

    expected_log_lines = ["Session debug log line - start",
                          "Session debug log line - end"
                          ]
    non_expected_log_lines = ["TEST STARTED",
                              "TEST ENDED"
                              ]
    helpers.assert_lines_in_logfile(artifacts_dir + "/" + session_logfile, expected_log_lines, non_expected_log_lines)


def test_logging_full_test_passes(testdir):
    testdir.makepyfile("""
        import pytest

        def test_pass(function_logger):
            function_logger.debug("Debug log line")
            pass
     """)

    result = testdir.runpytest(
        '--logfest=full', '--log-level=debug'
    )

    assert result.ret == 0

    artifacts_dir = str(testdir.tmpdir.join('artifacts'))

    assert os.path.isdir(artifacts_dir) is True

    log_files = helpers.get_logfiles_in_testdir(artifacts_dir)
    assert len(log_files) == 2

    timestamp = helpers.get_timestamp_from_logfile_name(log_files[0])
    basic_logfile = "session-%s.log" % timestamp
    helpers.assert_filename_in_list_of_files(basic_logfile, log_files)

    full_logfile = "test_logging_full_test_passes-%s.log" % timestamp
    helpers.assert_filename_in_list_of_files(full_logfile, log_files)

    expected_log_lines = ["TEST STARTED",
                          "TEST ENDED"]
    helpers.assert_lines_in_logfile(artifacts_dir + "/" + basic_logfile, expected_log_lines, ["Debug log line"])
    helpers.assert_lines_in_logfile(artifacts_dir + "/" + full_logfile, expected_log_lines.append("Debug log line"))


def test_logging_basic_test_passes(testdir):
    testdir.makepyfile("""
        import pytest

        def test_pass(function_logger):
            function_logger.debug("Debug log line")
            pass
     """)

    result = testdir.runpytest(
        '--logfest=basic', '--log-level=debug'
    )

    assert result.ret == 0

    artifacts_dir = str(testdir.tmpdir.join('artifacts'))

    assert os.path.isdir(artifacts_dir) is True

    log_files = helpers.get_logfiles_in_testdir(artifacts_dir)
    assert len(log_files) == 1

    timestamp = helpers.get_timestamp_from_logfile_name(log_files[0])
    basic_logfile = "session-%s.log" % timestamp
    helpers.assert_filename_in_list_of_files(basic_logfile, log_files)

    expected_log_lines = ["TEST STARTED",
                          "TEST ENDED"]
    helpers.assert_lines_in_logfile(artifacts_dir + "/" + basic_logfile, expected_log_lines, ["Debug log line"])


def test_logging_basic_test_fails(testdir):
    testdir.makepyfile("""
        import pytest

        def test_pass(function_logger):
            function_logger.debug("Debug log line")
            assert False
     """)

    result = testdir.runpytest(
        '--logfest=basic', '--log-level=debug'
    )

    assert result.ret == 1

    artifacts_dir = str(testdir.tmpdir.join('artifacts'))

    assert os.path.isdir(artifacts_dir) is True

    log_files = helpers.get_logfiles_in_testdir(artifacts_dir)
    assert len(log_files) == 1

    timestamp = helpers.get_timestamp_from_logfile_name(log_files[0])
    basic_logfile = "session-%s.log" % timestamp
    helpers.assert_filename_in_list_of_files(basic_logfile, log_files)

    expected_log_lines = ["TEST STARTED",
                          "Debug log line",
                          "TEST FAIL",
                          "TEST ENDED",
                          ]
    helpers.assert_lines_in_logfile(artifacts_dir + "/" + basic_logfile, expected_log_lines)


def test_logging_basic_setup_fails(testdir):
    testdir.makepyfile("""
        import pytest

        @pytest.fixture(scope='function')
        def setup():
            assert False

        def test_pass(function_logger, setup):
            function_logger.debug("Debug log line")
     """)

    result = testdir.runpytest(
        '--logfest=basic', '--log-level=debug'
    )

    assert result.ret == 1

    artifacts_dir = str(testdir.tmpdir.join('artifacts'))

    assert os.path.isdir(artifacts_dir) is True

    log_files = helpers.get_logfiles_in_testdir(artifacts_dir)
    assert len(log_files) == 1

    timestamp = helpers.get_timestamp_from_logfile_name(log_files[0])
    basic_logfile = "session-%s.log" % timestamp
    helpers.assert_filename_in_list_of_files(basic_logfile, log_files)

    expected_log_lines = ["TEST STARTED",
                          "SETUP ERROR",
                          "TEST ENDED",
                          ]
    helpers.assert_lines_in_logfile(artifacts_dir + "/" + basic_logfile, expected_log_lines, ["Debug log line"])


@pytest.mark.xfail(reason='request.node.rep_teardown remains empty, so no TEARDOWN ERROR / FAIL is logged')
def test_logging_basic_teardown_fails(testdir):
    testdir.makepyfile("""
        import pytest

        @pytest.fixture(scope='function')
        def teardown():
            yield

            assert False

        def test_pass(function_logger, teardown):
            function_logger.debug("Debug log line")
     """)

    result = testdir.runpytest(
        '--logfest=basic', '--log-level=debug'
    )

    assert result.ret == 1

    artifacts_dir = str(testdir.tmpdir.join('artifacts'))

    assert os.path.isdir(artifacts_dir) is True

    log_files = helpers.get_logfiles_in_testdir(artifacts_dir)
    assert len(log_files) == 1

    timestamp = helpers.get_timestamp_from_logfile_name(log_files[0])
    basic_logfile = "session-%s.log" % timestamp
    helpers.assert_filename_in_list_of_files(basic_logfile, log_files)

    expected_log_lines = ["TEST STARTED",
                          "Debug log line",
                          "TEARDOWN ERROR / FAIL",
                          "TEST ENDED",
                          ]
    helpers.assert_lines_in_logfile(artifacts_dir + "/" + basic_logfile, expected_log_lines)
