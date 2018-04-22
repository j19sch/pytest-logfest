import os
import pytest

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

    assert os.path.isdir(str(testdir.tmpdir.join('artifacts'))) is False


def test_logging_quiet(testdir):
    testdir.makepyfile("""
        import pytest

        def test_pass(function_logger):
            pass
    """)

    result = testdir.runpytest(
        '-v', '--logfest=quiet'
    )

    assert result.ret == 0

    assert os.path.isdir(str(testdir.tmpdir.join('artifacts'))) is False


def test_logging_basic(testdir):
    testdir.makepyfile("""
        import pytest

        def test_pass(function_logger):
            function_logger.debug("Debug log line")
            pass
     """)

    result = testdir.runpytest(
        '-v', '--logfest=basic'
    )

    assert result.ret == 0

    artifacts_dir = testdir.tmpdir.join('artifacts')

    assert os.path.isdir(str(artifacts_dir)) is True

    log_files = [logfile for logfile in os.listdir(str(artifacts_dir)) if ".log" in logfile]
    assert len(log_files) == 1

    timestamp = helpers.get_timestamp_from_logfile_name(log_files[0])
    basic_logfile = "session-%s.log" % timestamp
    assert any(filename for filename in log_files if filename == basic_logfile)


def test_logging_full(testdir):
    testdir.makepyfile("""
        import pytest

        def test_pass(function_logger):
            function_logger.debug("Debug log line")
            pass
     """)

    result = testdir.runpytest(
        '-v', '--logfest=full'
    )

    assert result.ret == 0

    artifacts_dir = testdir.tmpdir.join('artifacts')

    assert os.path.isdir(str(artifacts_dir)) is True

    log_files = [logfile for logfile in os.listdir(str(artifacts_dir)) if ".log" in logfile]
    assert len(log_files) == 2

    timestamp = helpers.get_timestamp_from_logfile_name(log_files[0])

    basic_logfile = "session-%s.log" % timestamp
    assert any(filename for filename in log_files if filename == basic_logfile)

    full_logfile = "test_logging_full-%s.log" % timestamp
    assert any(filename for filename in log_files if filename == full_logfile)


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
        '-v', '--logfest=full'
    )

    assert result.ret == 0

    artifacts_dir = testdir.tmpdir.join('artifacts')

    assert os.path.isdir(str(artifacts_dir)) is True

    log_files = [logfile for logfile in os.listdir(str(artifacts_dir)) if ".log" in logfile]
    assert len(log_files) == 3

    timestamp = helpers.get_timestamp_from_logfile_name(log_files[0])

    basic_logfile = "session-%s.log" % timestamp
    assert any(filename for filename in log_files if filename == basic_logfile)

    full_logfile_1 = "test_file_one-%s.log" % timestamp
    assert any(filename for filename in log_files if filename == full_logfile_1)

    full_logfile_2 = "test_file_two-%s.log" % timestamp
    assert any(filename for filename in log_files if filename == full_logfile_2)


def test_logging_full_subdirs(testdir):
    test_file = testdir.mkdir("my-tests").join("test_logging_full_subdirs.py")
    test_file.write("""import pytest

def test_pass(function_logger):
    pass
""")

    result = testdir.runpytest(
        '-v', '--logfest=full'
    )

    assert result.ret == 0

    artifacts_dir = testdir.tmpdir.join('artifacts')
    assert os.path.isdir(str(artifacts_dir)) is True

    log_files = [logfile for logfile in os.listdir(str(artifacts_dir)) if ".log" in logfile]
    assert len(log_files) == 1
    timestamp = helpers.get_timestamp_from_logfile_name(log_files[0])
    basic_logfile = "session-%s.log" % timestamp
    assert any(filename for filename in log_files if filename == basic_logfile)

    artifacts_subdir = testdir.tmpdir.join('artifacts/my-tests')
    assert os.path.isdir(str(artifacts_subdir)) is True

    log_files = [logfile for logfile in os.listdir(str(artifacts_subdir)) if ".log" in logfile]
    assert len(log_files) == 1
    full_logfile = "test_logging_full_subdirs-%s.log" % timestamp
    assert any(filename for filename in log_files if filename == full_logfile)
