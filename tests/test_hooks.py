import os

from . import helpers


def test_basic_logging_filename_hook(testdir):
    testdir.makeconftest("""
        import pytest

        @pytest.mark.optionalhook
        def pytest_logfest_log_file_name_basic(filename_components):
            filename_components.append("fizzbuzz")
    """)

    testdir.makepyfile("""
        import pytest

        def test_pass(function_logger):
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
    basic_logfile = "session-%s-fizzbuzz.log" % timestamp

    helpers.assert_filename_in_list_of_files(basic_logfile, log_files)


def test_full_logging_filename_hook_module(testdir):
    testdir.makeconftest("""
        import pytest

        @pytest.mark.optionalhook
        def pytest_logfest_log_file_name_full_module(filename_components):
            filename_components.append("fizzbuzz")
    """)

    testdir.makepyfile("""
        import pytest

        def test_pass(function_logger):
            pass
    """)

    result = testdir.runpytest(
        '--logfest=full', '--log-level=debug'
    )

    assert result.ret == 0

    artifacts_dir = str(testdir.tmpdir.join('artifacts'))

    assert os.path.isdir(str(artifacts_dir)) is True

    log_files = helpers.get_logfiles_in_testdir(artifacts_dir)
    assert len(log_files) == 2

    timestamp = helpers.get_timestamp_from_logfile_name(log_files[0])
    full_logfile = "test_full_logging_filename_hook_module-%s-fizzbuzz.log" % timestamp
    helpers.assert_filename_in_list_of_files(full_logfile, log_files)


def test_full_logging_filename_hook_session(testdir):
    testdir.makeconftest("""
        import pytest

        @pytest.fixture(scope='session', autouse='true')
        def session_log(session_logger):
            session_logger.info("Session info log line")

        @pytest.mark.optionalhook
        def pytest_logfest_log_file_name_full_session(filename_components):
            filename_components.append("fizzbuzz")
    """)

    testdir.makepyfile("""
        import pytest

        def test_pass(function_logger):
            pass
    """)

    result = testdir.runpytest(
        '--logfest=full', '--log-level=debug'
    )

    assert result.ret == 0

    artifacts_dir = str(testdir.tmpdir.join('artifacts'))

    assert os.path.isdir(str(artifacts_dir)) is True

    log_files = helpers.get_logfiles_in_testdir(artifacts_dir)
    assert len(log_files) == 3

    timestamp = helpers.get_timestamp_from_logfile_name(log_files[0])
    full_logfile_session = "test_full_logging_filename_hook_session0-%s-fizzbuzz.log" % timestamp
    helpers.assert_filename_in_list_of_files(full_logfile_session, log_files)
