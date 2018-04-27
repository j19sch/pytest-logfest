import os

from . import helpers


def test_no_fixtures(testdir):
    testdir.makepyfile("""
        import pytest

        def test_pass():
            pass


    """.format("Info log line: session"))

    result = testdir.runpytest(
        '--logfest=basic'
    )

    assert result.ret == 0

    artifacts_dir = str(testdir.tmpdir.join('artifacts'))
    assert os.path.isdir(artifacts_dir) is False


def test_logging_quiet(testdir):
    testdir.makepyfile("""
        import pytest

        def test_pass(function_logger):
            pass
    """)

    result = testdir.runpytest(
        '--logfest=quiet'
    )

    assert result.ret == 0

    artifacts_dir = str(testdir.tmpdir.join('artifacts'))
    assert os.path.isdir(artifacts_dir) is False


def test_logging_basic(testdir):
    testdir.makepyfile("""
        import pytest

        def test_pass(function_logger):
            function_logger.debug("Debug log line")
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
    basic_logfile = "session-%s.log" % timestamp
    helpers.assert_filename_in_list_of_files(basic_logfile, log_files)


def test_logging_full(testdir):
    testdir.makepyfile("""
        import pytest

        def test_pass(function_logger):
            function_logger.debug("Debug log line")
            pass
     """)

    result = testdir.runpytest(
        '--logfest=full'
    )

    assert result.ret == 0

    artifacts_dir = str(testdir.tmpdir.join('artifacts'))

    assert os.path.isdir(artifacts_dir) is True

    log_files = helpers.get_logfiles_in_testdir(artifacts_dir)
    assert len(log_files) == 2

    timestamp = helpers.get_timestamp_from_logfile_name(log_files[0])

    basic_logfile = "session-%s.log" % timestamp
    helpers.assert_filename_in_list_of_files(basic_logfile, log_files)

    full_logfile = "test_logging_full-%s.log" % timestamp
    helpers.assert_filename_in_list_of_files(full_logfile, log_files)


def test_logging_full_two_testfiles(testdir):
    test_file1 = testdir.tmpdir.join("test_file_one.py")
    test_file1.write("""import pytest

def test_pass(function_logger):
    pass
""")

    test_file2 = testdir.tmpdir.join("test_file_two.py")
    test_file2.write("""import pytest

def test_pass(function_logger):
    pass
""")

    result = testdir.runpytest(
        '--logfest=full'
    )

    assert result.ret == 0

    artifacts_dir = str(testdir.tmpdir.join('artifacts'))

    assert os.path.isdir(artifacts_dir) is True

    log_files = helpers.get_logfiles_in_testdir(artifacts_dir)
    assert len(log_files) == 3

    timestamp = helpers.get_timestamp_from_logfile_name(log_files[0])

    basic_logfile = "session-%s.log" % timestamp
    helpers.assert_filename_in_list_of_files(basic_logfile, log_files)

    full_logfile_1 = "test_file_one-%s.log" % timestamp
    helpers.assert_filename_in_list_of_files(full_logfile_1, log_files)

    full_logfile_2 = "test_file_two-%s.log" % timestamp
    helpers.assert_filename_in_list_of_files(full_logfile_2, log_files)


def test_logging_full_subdirs(testdir):
    test_file = testdir.mkdir("my-tests").join("test_logging_full_subdirs.py")
    test_file.write("""import pytest

def test_pass(function_logger):
    pass
""")

    result = testdir.runpytest(
        '--logfest=full'
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
    full_logfile = "test_logging_full_subdirs-%s.log" % timestamp
    helpers.assert_filename_in_list_of_files(full_logfile, log_files)
