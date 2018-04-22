import os

from . import helpers


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
        '--logfest=full'
    )

    assert result.ret == 0

    artifacts_dir = testdir.tmpdir.join('artifacts')

    assert os.path.isdir(str(artifacts_dir)) is True

    log_files = [logfile for logfile in os.listdir(str(artifacts_dir)) if ".log" in logfile]
    assert len(log_files) == 1

    timestamp = helpers.get_timestamp_from_logfile_name(log_files[0])
    basic_logfile = "session-%s.log" % timestamp
    assert any(filename for filename in log_files if filename == basic_logfile)

    with open(str(artifacts_dir) + "/" + basic_logfile, "r") as logfile:
        log = logfile.read()
    assert "INFO - lf - Info log line: session" in log


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
        '--logfest=full'
    )

    assert result.ret == 0

    artifacts_dir = testdir.tmpdir.join('artifacts')

    assert os.path.isdir(str(artifacts_dir)) is True

    log_files = [logfile for logfile in os.listdir(str(artifacts_dir)) if ".log" in logfile]
    assert len(log_files) == 2

    timestamp = helpers.get_timestamp_from_logfile_name(log_files[0])
    basic_logfile = "session-%s.log" % timestamp
    full_logfile = "test_module_logger-%s.log" % timestamp

    assert any(filename for filename in log_files if filename == basic_logfile)
    assert any(filename for filename in log_files if filename == full_logfile)

    for log_file in [basic_logfile, full_logfile]:
        with open(str(artifacts_dir) + "/" + log_file, "r") as logfile:
            log = logfile.read()
        assert "INFO - lf.test_module_logger - Info log line: module" in log


def test_function_logger(testdir):
    testdir.makepyfile("""
        import pytest

        def test_pass(function_logger):
            function_logger.info("{0}")
            pass


    """.format("Info log line: function"))

    result = testdir.runpytest(
        '--logfest=full'
    )

    assert result.ret == 0

    artifacts_dir = testdir.tmpdir.join('artifacts')

    assert os.path.isdir(str(artifacts_dir)) is True

    log_files = [logfile for logfile in os.listdir(str(artifacts_dir)) if ".log" in logfile]
    assert len(log_files) == 2

    timestamp = helpers.get_timestamp_from_logfile_name(log_files[0])
    basic_logfile = "session-%s.log" % timestamp
    full_logfile = "test_function_logger-%s.log" % timestamp

    assert any(filename for filename in log_files if filename == basic_logfile)
    assert any(filename for filename in log_files if filename == full_logfile)

    for log_file in [basic_logfile, full_logfile]:
        with open(str(artifacts_dir) + "/" + log_file, "r") as logfile:
            log = logfile.read()
        assert "INFO - lf.test_function_logger.test_pass - TEST STARTED" in log
        assert "INFO - lf.test_function_logger.test_pass - Info log line: function" in log
        assert "INFO - lf.test_function_logger.test_pass - TEST ENDED" in log


def test_test_in_subdir(testdir):
    test_file = testdir.mkdir("my-tests").join("test_subdir.py")
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
    full_logfile = "test_subdir-%s.log" % timestamp
    assert any(filename for filename in log_files if filename == full_logfile)

    for log_file in [str(artifacts_dir) + "/" + basic_logfile, str(artifacts_subdir) + "/" + full_logfile]:
        with open(log_file, "r") as logfile:
            log = logfile.read()
        assert "INFO - lf.my-tests.test_subdir.test_pass - TEST STARTED" in log
        assert "INFO - lf.my-tests.test_subdir.test_pass - TEST ENDED" in log
