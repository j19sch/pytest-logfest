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
        '--logfest=basic'
    )

    assert result.ret == 0

    artifacts_dir = str(testdir.tmpdir.join('artifacts'))

    assert os.path.isdir(artifacts_dir) is True

    log_files = helpers.get_logfiles_in_testdir(artifacts_dir)
    assert len(log_files) == 1

    timestamp = helpers.get_timestamp_from_logfile_name(log_files[0])
    basic_logfile = "session-%s-fizzbuzz.log" % timestamp

    helpers.assert_filename_in_list_of_files(basic_logfile, log_files)


def test_full_logging_filename_hook(testdir):
    testdir.makeconftest("""
        import pytest

        @pytest.mark.optionalhook
        def pytest_logfest_log_file_name_full(filename_components):
            filename_components.append("fizzbuzz")
    """)

    testdir.makepyfile("""
        import pytest

        def test_pass(function_logger):
            pass
    """)

    result = testdir.runpytest(
        '--logfest=full'
    )

    assert result.ret == 0

    artifacts_dir = str(testdir.tmpdir.join('artifacts'))

    assert os.path.isdir(str(artifacts_dir)) is True

    log_file = [file for file in os.listdir(str(artifacts_dir)) if ".log" in file]
    assert len(log_file) == 2

    log_files = helpers.get_logfiles_in_testdir(artifacts_dir)
    assert len(log_files) == 2

    timestamp = helpers.get_timestamp_from_logfile_name(log_files[0])
    basic_logfile = "session-%s.log" % timestamp
    full_logfile = "test_full_logging_filename_hook-%s-fizzbuzz.log" % timestamp

    helpers.assert_filename_in_list_of_files(basic_logfile, log_files)
    helpers.assert_filename_in_list_of_files(full_logfile, log_files)
