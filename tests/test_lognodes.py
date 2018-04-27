import os

from . import helpers


def test_custom_root_log_node(testdir):
    testdir.makefile(".ini", pytest='[pytest]\nlogfest_root_node=logfest\n')

    testdir.makepyfile("""
        import pytest

        @pytest.fixture(scope='session')
        def session(session_logger):
            session_logger.info("{0}")

        def test_pass(session):
            pass
    """.format("Info log line: session"))

    result = testdir.runpytest(
        '--logfest=full',
        '--log-level=debug',
        '--log-format="%(name)s - %(levelname)s - %(message)s"'
    )

    assert result.ret == 0

    artifacts_dir = str(testdir.tmpdir.join('artifacts'))
    assert os.path.isdir(artifacts_dir) is True

    log_files = helpers.get_logfiles_in_testdir(artifacts_dir)
    assert len(log_files) == 1

    timestamp = helpers.get_timestamp_from_logfile_name(log_files[0])
    basic_logfile = "session-%s.log" % timestamp
    helpers.assert_filename_in_list_of_files(basic_logfile, log_files)

    expected_log_lines = ["INFO - logfest - Info log line: session"]
    helpers.assert_lines_in_logfile(artifacts_dir + "/" + basic_logfile, expected_log_lines)


def test_session_logger(testdir):
    testdir.makepyfile("""
        import pytest

        @pytest.fixture(scope='session')
        def session(session_logger):
            session_logger.info("{0}")

        def test_pass(session):
            pass
    """.format("Info log line: session"))

    result = testdir.runpytest(
        '--logfest=full',
        '--log-level=debug',
        '--log-format="%(name)s - %(levelname)s - %(message)s"'
    )

    assert result.ret == 0

    artifacts_dir = str(testdir.tmpdir.join('artifacts'))
    assert os.path.isdir(artifacts_dir) is True

    log_files = helpers.get_logfiles_in_testdir(artifacts_dir)
    assert len(log_files) == 1

    timestamp = helpers.get_timestamp_from_logfile_name(log_files[0])
    basic_logfile = "session-%s.log" % timestamp
    helpers.assert_filename_in_list_of_files(basic_logfile, log_files)

    expected_log_lines = ["INFO - test_session_logger0 - Info log line: session"]
    helpers.assert_lines_in_logfile(artifacts_dir + "/" + basic_logfile, expected_log_lines)


def test_module_logger(testdir):
    testdir.makepyfile("""
        import pytest

        @pytest.fixture(scope='module')
        def module(module_logger):
            module_logger.info("{0}")

        def test_pass(module):
            pass


    """.format("Info log line: module"))

    result = testdir.runpytest(
        '--logfest=full',
        '--log-level=debug',
        '--log-format="%(name)s - %(levelname)s - %(message)s"'
    )

    assert result.ret == 0

    artifacts_dir = str(testdir.tmpdir.join('artifacts'))
    assert os.path.isdir(artifacts_dir) is True

    log_files = helpers.get_logfiles_in_testdir(artifacts_dir)
    assert len(log_files) == 2

    timestamp = helpers.get_timestamp_from_logfile_name(log_files[0])
    basic_logfile = "session-%s.log" % timestamp
    full_logfile = "test_module_logger-%s.log" % timestamp

    helpers.assert_filename_in_list_of_files(basic_logfile, log_files)
    helpers.assert_filename_in_list_of_files(full_logfile, log_files)

    expected_log_lines = ["INFO - test_module_logger0.test_module_logger - Info log line: module"]
    helpers.assert_lines_in_logfile(artifacts_dir + "/" + basic_logfile, expected_log_lines)


def test_function_logger(testdir):
    testdir.makepyfile("""
        import pytest

        def test_pass(function_logger):
            function_logger.info("{0}")
            pass


    """.format("Info log line: function"))

    result = testdir.runpytest(
        '--logfest=full',
        '--log-level=debug',
        '--log-format="%(name)s - %(levelname)s - %(message)s"'
    )

    assert result.ret == 0

    artifacts_dir = str(testdir.tmpdir.join('artifacts'))
    assert os.path.isdir(artifacts_dir) is True

    log_files = helpers.get_logfiles_in_testdir(artifacts_dir)
    assert len(log_files) == 2

    timestamp = helpers.get_timestamp_from_logfile_name(log_files[0])
    basic_logfile = "session-%s.log" % timestamp
    full_logfile = "test_function_logger-%s.log" % timestamp

    helpers.assert_filename_in_list_of_files(basic_logfile, log_files)
    helpers.assert_filename_in_list_of_files(full_logfile, log_files)

    expected_log_lines = ["INFO - test_function_logger0.test_function_logger.test_pass - TEST STARTED",
                          "INFO - test_function_logger0.test_function_logger.test_pass - Info log line: function",
                          "INFO - test_function_logger0.test_function_logger.test_pass - TEST ENDED"
                          ]
    helpers.assert_lines_in_logfile(artifacts_dir + "/" + basic_logfile, expected_log_lines)
    helpers.assert_lines_in_logfile(artifacts_dir + "/" + full_logfile, expected_log_lines)


def test_test_in_subdir(testdir):
    test_file = testdir.mkdir("my-tests").join("test_subdir.py")
    test_file.write("""import pytest

def test_pass(function_logger):
    pass
""")

    result = testdir.runpytest(
        '--logfest=full',
        '--log-level=debug',
        '--log-format="%(name)s - %(levelname)s - %(message)s"'
    )

    assert result.ret == 0

    artifacts_dir = str(testdir.tmpdir.join('artifacts'))
    assert os.path.isdir(artifacts_dir) is True

    log_files = helpers.get_logfiles_in_testdir(artifacts_dir)
    assert len(log_files) == 1
    timestamp = helpers.get_timestamp_from_logfile_name(log_files[0])
    basic_logfile = "session-%s.log" % timestamp
    helpers.assert_filename_in_list_of_files(basic_logfile, log_files)

    artifacts_subdir = str(testdir.tmpdir.join('artifacts/my-tests'))
    assert os.path.isdir(artifacts_subdir) is True

    log_files = helpers.get_logfiles_in_testdir(artifacts_subdir)
    assert len(log_files) == 1
    full_logfile = "test_subdir-%s.log" % timestamp
    helpers.assert_filename_in_list_of_files(full_logfile, log_files)

    expected_log_lines = ["INFO - test_test_in_subdir0.my-tests.test_subdir.test_pass - TEST STARTED",
                          "INFO - test_test_in_subdir0.my-tests.test_subdir.test_pass - TEST ENDED"
                          ]

    helpers.assert_lines_in_logfile(artifacts_dir + "/" + basic_logfile, expected_log_lines)
    helpers.assert_lines_in_logfile(artifacts_subdir + "/" + full_logfile, expected_log_lines)
