import os
import pytest

from . import helpers


@pytest.mark.xfail(reason='not implemented yet')
def test_logging_full_session_fixture(testdir):
    testdir.makepyfile("""
        import pytest

        @pytest.fixture(scope='session', autouse=True)
        def session_fixture(session_logger):
            session_logger.debug("Session debug log line - start")
            yield
            session_logger.debug("Session debug log line - end")

        def test_pass(function_logger, session_fixture):
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

    with open(str(artifacts_dir) + "/" + basic_logfile, "r") as file:
        log = file.read()
    assert "Session debug log line - start" in log
    assert "TEST STARTED" in log
    assert "Debug log line" not in log
    assert "TEST ENDED" in log
    assert "Session debug log line - end" in log


def test_logging_basic_test_passes(testdir):
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

    with open(str(artifacts_dir) + "/" + basic_logfile, "r") as file:
        log = file.read()
    assert "TEST STARTED" in log
    assert "Debug log line" not in log
    assert "TEST ENDED" in log


def test_logging_full_test_passes(testdir):
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
    with open(str(artifacts_dir) + "/" + basic_logfile, "r") as file:
        log = file.read()
    assert "TEST STARTED" in log
    assert "Debug log line" not in log
    assert "TEST ENDED" in log

    full_logfile = "test_logging_full_test_passes-%s.log" % timestamp
    assert any(filename for filename in log_files if filename == full_logfile)
    with open(str(artifacts_dir) + "/" + full_logfile, "r") as file:
        log = file.read()
    assert "TEST STARTED" in log
    assert "Debug log line" in log
    assert "TEST ENDED" in log


def test_logging_basic_test_fails(testdir):
    testdir.makepyfile("""
        import pytest

        def test_pass(function_logger):
            function_logger.debug("Debug log line")
            assert False
     """)

    result = testdir.runpytest(
        '-v', '--logfest=basic'
    )

    assert result.ret == 1

    artifacts_dir = testdir.tmpdir.join('artifacts')

    assert os.path.isdir(str(artifacts_dir)) is True

    log_files = [logfile for logfile in os.listdir(str(artifacts_dir)) if ".log" in logfile]
    assert len(log_files) == 1

    timestamp = helpers.get_timestamp_from_logfile_name(log_files[0])
    basic_logfile = "session-%s.log" % timestamp
    assert any(filename for filename in log_files if filename == basic_logfile)

    with open(str(artifacts_dir) + "/" + basic_logfile, "r") as file:
        log = file.read()
    assert "TEST STARTED" in log
    assert "Debug log line" in log
    assert "TEST FAIL" in log
    assert "TEST ENDED" in log


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
        '-v', '--logfest=basic'
    )

    assert result.ret == 1

    artifacts_dir = testdir.tmpdir.join('artifacts')

    assert os.path.isdir(str(artifacts_dir)) is True

    log_files = [logfile for logfile in os.listdir(str(artifacts_dir)) if ".log" in logfile]
    assert len(log_files) == 1

    timestamp = helpers.get_timestamp_from_logfile_name(log_files[0])
    basic_logfile = "session-%s.log" % timestamp
    assert any(filename for filename in log_files if filename == basic_logfile)

    with open(str(artifacts_dir) + "/" + basic_logfile, "r") as file:
        log = file.read()
    assert "test_logging_basic_setup_fails.test_pass" in log
    assert "TEST STARTED" in log
    assert "SETUP ERROR" in log
    assert "Debug log line" not in log
    assert "TEST ENDED" in log


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
        '-v', '--logfest=basic'
    )

    assert result.ret == 1

    artifacts_dir = testdir.tmpdir.join('artifacts')

    assert os.path.isdir(str(artifacts_dir)) is True

    log_files = [logfile for logfile in os.listdir(str(artifacts_dir)) if ".log" in logfile]
    assert len(log_files) == 1

    timestamp = helpers.get_timestamp_from_logfile_name(log_files[0])
    basic_logfile = "session-%s.log" % timestamp
    assert any(filename for filename in log_files if filename == basic_logfile)

    with open(str(artifacts_dir) + "/" + basic_logfile, "r") as file:
        log = file.read()
    assert "test_logging_basic_teardown_fails.test_pass" in log
    assert "TEST STARTED" in log
    assert "Debug log line" in log
    assert "TEARDOWN ERROR / FAIL" in log
    assert "TEST ENDED" in log
