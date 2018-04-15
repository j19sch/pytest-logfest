import os
import pytest
import re


def test_logging_quiet(testdir):
    testdir.makepyfile("""
        import pytest

        def test_pass(logfest_logger):
            pass
    """)

    result = testdir.runpytest(
        '-v', '--logfest=quiet'
    )

    assert result.ret == 0

    assert os.path.isdir(str(testdir.tmpdir.join('artifacts'))) is False


def test_logging_basic_test_passes(testdir):
    testdir.makepyfile("""
        import pytest

        def test_pass(logfest_logger):
            logfest_logger.debug("Debug log line")
            pass
     """)

    result = testdir.runpytest(
        '-v', '--logfest=basic'
    )

    assert result.ret == 0

    artifacts_dir = testdir.tmpdir.join('artifacts')

    assert os.path.isdir(str(artifacts_dir)) is True

    log_file = [file for file in os.listdir(str(artifacts_dir)) if ".log" in file]
    assert len(log_file) == 1

    pattern = re.compile("^tests-(\d{8}-\d{2}-\d{2}-\d{2}).log$")
    assert pattern.match(log_file[0])

    with open(str(artifacts_dir) + "/" + log_file[0], "r") as file:
        log = file.read()
    assert "test_logging_basic_test_passes.test_pass" in log
    assert "TEST STARTED" in log
    assert "Debug log line" not in log
    assert "TEST COMPLETED" in log


def test_logging_basic_setup_fails(testdir):
    testdir.makepyfile("""
        import pytest

        @pytest.fixture(scope='function')
        def setup():
            assert False

        def test_pass(logfest_logger, setup):
            logfest_logger.debug("Debug log line")
     """)

    result = testdir.runpytest(
        '-v', '--logfest=basic'
    )

    assert result.ret == 1

    artifacts_dir = testdir.tmpdir.join('artifacts')

    assert os.path.isdir(str(artifacts_dir)) is True

    log_file = [file for file in os.listdir(str(artifacts_dir)) if ".log" in file]
    assert len(log_file) == 1

    pattern = re.compile("^tests-(\d{8}-\d{2}-\d{2}-\d{2}).log$")
    assert pattern.match(log_file[0])

    with open(str(artifacts_dir) + "/" + log_file[0], "r") as file:
        log = file.read()
    assert "test_logging_basic_setup_fails.test_pass" in log
    assert "TEST STARTED" in log
    assert "SETUP ERROR / FAIL" in log
    assert "Debug log line" not in log
    assert "TEST COMPLETED" in log


def test_logging_basic_test_fails(testdir):
    testdir.makepyfile("""
        import pytest

        def test_pass(logfest_logger):
            logfest_logger.debug("Debug log line")
            assert False
     """)

    result = testdir.runpytest(
        '-v', '--logfest=basic'
    )

    assert result.ret == 1

    artifacts_dir = testdir.tmpdir.join('artifacts')

    assert os.path.isdir(str(artifacts_dir)) is True

    log_file = [file for file in os.listdir(str(artifacts_dir)) if ".log" in file]
    assert len(log_file) == 1

    pattern = re.compile("^tests-(\d{8}-\d{2}-\d{2}-\d{2}).log$")
    assert pattern.match(log_file[0])

    with open(str(artifacts_dir) + "/" + log_file[0], "r") as file:
        log = file.read()
    assert "test_logging_basic_test_fails.test_pass" in log
    assert "TEST STARTED" in log
    assert "Debug log line" in log
    assert "TEST ERROR / FAIL" in log
    assert "TEST COMPLETED" in log


@pytest.mark.xfail(reason='request.node.rep_teardown remains empty, so no TEARDOWN ERROR / FAIL is logged')
def test_logging_basic_teardown_fails(testdir):
    testdir.makepyfile("""
        import pytest

        @pytest.fixture(scope='function')
        def teardown():
            yield

            assert False

        def test_pass(logfest_logger, teardown):
            logfest_logger.debug("Debug log line")
     """)

    result = testdir.runpytest(
        '-v', '--logfest=basic'
    )

    assert result.ret == 1

    artifacts_dir = testdir.tmpdir.join('artifacts')

    assert os.path.isdir(str(artifacts_dir)) is True

    log_file = [file for file in os.listdir(str(artifacts_dir)) if ".log" in file]
    assert len(log_file) == 1

    pattern = re.compile("^tests-(\d{8}-\d{2}-\d{2}-\d{2}).log$")
    assert pattern.match(log_file[0])

    with open(str(artifacts_dir) + "/" + log_file[0], "r") as file:
        log = file.read()
    assert "test_logging_basic_teardown_fails.test_pass" in log
    assert "TEST STARTED" in log
    assert "Debug log line" in log
    assert "TEARDOWN ERROR / FAIL" in log
    assert "TEST COMPLETED" in log


def test_logging_full_test_passes(testdir):
    testdir.makepyfile("""
        import pytest

        def test_pass(logfest_logger):
            pass
    """)

    result = testdir.runpytest(
        '-v', '--logfest=full'
    )

    assert result.ret == 0

    artifacts_dir = testdir.tmpdir.join('artifacts')

    assert os.path.isdir(str(artifacts_dir)) is True

    log_file = [file for file in os.listdir(str(artifacts_dir)) if ".log" in file]
    assert len(log_file) == 2

    pattern1 = re.compile("^tests-(\d{8}-\d{2}-\d{2}-\d{2}).log$")
    pattern2 = re.compile("^test_logging_full_test_passes-(\d{8}-\d{2}-\d{2}-\d{2}).log$")

    assert any(filename for filename in log_file if pattern1.match(filename))
    assert any(filename for filename in log_file if pattern2.match(filename))

    for logfile in log_file:
        with open(str(artifacts_dir) + "/" + logfile, "r") as file:
            log = file.read()
        assert "test_logging_full_test_passes.test_pass" in log
        assert "TEST STARTED" in log
        assert "TEST COMPLETED" in log


def test_logging_full_two_testfiles(testdir):
    test_file1 = testdir.tmpdir.join("test_file_one.py")
    test_file1.write("""import pytest

def test_pass(logfest_logger):
    pass
""")

    test_file2 = testdir.tmpdir.join("test_file_two.py")
    test_file2.write("""import pytest

def test_pass(logfest_logger):
    pass
""")

    result = testdir.runpytest(
        '-v', '--logfest=full'
    )

    assert result.ret == 0

    artifacts_dir = testdir.tmpdir.join('artifacts')

    assert os.path.isdir(str(artifacts_dir)) is True

    log_file = [file for file in os.listdir(str(artifacts_dir)) if ".log" in file]
    assert len(log_file) == 3

    match = re.match(r".*(\d{8}-\d{2}-\d{2}-\d{2}).log", log_file[0])
    timestamp = match.group(1)

    basic_logfile = "tests-%s.log" % timestamp
    full_logfile_1 = "test_file_one-%s.log" % timestamp
    full_logfile_2 = "test_file_two-%s.log" % timestamp

    assert any(filename for filename in log_file if filename == basic_logfile)
    with open(str(artifacts_dir) + "/" + basic_logfile, "r") as file:
        basic_log = file.read()
    assert "test_file_one.test_pass" in basic_log
    assert "test_file_two.test_pass" in basic_log
    assert basic_log.count("TEST STARTED") == 2
    assert basic_log.count("TEST COMPLETED") == 2

    assert any(filename for filename in log_file if filename == full_logfile_1)
    with open(str(artifacts_dir) + "/" + full_logfile_1, "r") as file:
        basic_log = file.read()
    assert "test_file_one.test_pass" in basic_log
    assert basic_log.count("TEST STARTED") == 1
    assert basic_log.count("TEST COMPLETED") == 1

    assert any(filename for filename in log_file if filename == full_logfile_2)
    with open(str(artifacts_dir) + "/" + full_logfile_2, "r") as file:
        basic_log = file.read()
    assert "test_file_two.test_pass" in basic_log
    assert basic_log.count("TEST STARTED") == 1
    assert basic_log.count("TEST COMPLETED") == 1


def test_logging_full_setup_fails(testdir):
    testdir.makepyfile("""
        import pytest

        @pytest.fixture(scope='function')
        def setup():
            assert False

        def test_pass(logfest_logger, setup):
            pass
    """)

    result = testdir.runpytest(
        '-v', '--logfest=full'
    )

    assert result.ret == 1

    artifacts_dir = testdir.tmpdir.join('artifacts')

    assert os.path.isdir(str(artifacts_dir)) is True

    log_file = [file for file in os.listdir(str(artifacts_dir)) if ".log" in file]
    assert len(log_file) == 2

    pattern1 = re.compile("^tests-(\d{8}-\d{2}-\d{2}-\d{2}).log$")
    pattern2 = re.compile("^test_logging_full_setup_fails-(\d{8}-\d{2}-\d{2}-\d{2}).log$")

    assert any(filename for filename in log_file if pattern1.match(filename))
    assert any(filename for filename in log_file if pattern2.match(filename))

    for logfile in log_file:
        with open(str(artifacts_dir) + "/" + logfile, "r") as file:
            log = file.read()
        assert "test_logging_full_setup_fails.test_pass" in log
        assert "TEST STARTED" in log
        assert "SETUP ERROR / FAIL" in log
        assert "TEST COMPLETED" in log


def test_logging_full_test_fails(testdir):
    testdir.makepyfile("""
        import pytest

        def test_pass(logfest_logger):
            assert False
    """)

    result = testdir.runpytest(
        '-v', '--logfest=full'
    )

    assert result.ret == 1

    artifacts_dir = testdir.tmpdir.join('artifacts')

    assert os.path.isdir(str(artifacts_dir)) is True

    log_file = [file for file in os.listdir(str(artifacts_dir)) if ".log" in file]
    assert len(log_file) == 2

    pattern1 = re.compile("^tests-(\d{8}-\d{2}-\d{2}-\d{2}).log$")
    pattern2 = re.compile("^test_logging_full_test_fails-(\d{8}-\d{2}-\d{2}-\d{2}).log$")

    assert any(filename for filename in log_file if pattern1.match(filename))
    assert any(filename for filename in log_file if pattern2.match(filename))

    for logfile in log_file:
        with open(str(artifacts_dir) + "/" + logfile, "r") as file:
            log = file.read()
        assert "test_logging_full_test_fails.test_pass" in log
        assert "TEST STARTED" in log
        assert "TEST ERROR / FAIL" in log
        assert "TEST COMPLETED" in log


@pytest.mark.xfail(reason='request.node.rep_teardown remains empty, so no TEARDOWN ERROR / FAIL is logged')
def test_logging_full_teardown_fails(testdir):
    testdir.makepyfile("""
        import pytest

        @pytest.fixture(scope='function')
        def teardown():
            yield

            assert False

        def test_pass(logfest_logger, teardown):
            pass
    """)

    result = testdir.runpytest(
        '-v', '--logfest=full'
    )

    assert result.ret == 1

    artifacts_dir = testdir.tmpdir.join('artifacts')

    assert os.path.isdir(str(artifacts_dir)) is True

    log_file = [file for file in os.listdir(str(artifacts_dir)) if ".log" in file]
    assert len(log_file) == 2

    pattern1 = re.compile("^tests-(\d{8}-\d{2}-\d{2}-\d{2}).log$")
    pattern2 = re.compile("^test_logging_full_teardown_fails-(\d{8}-\d{2}-\d{2}-\d{2}).log$")

    assert any(filename for filename in log_file if pattern1.match(filename))
    assert any(filename for filename in log_file if pattern2.match(filename))

    for logfile in log_file:
        with open(str(artifacts_dir) + "/" + logfile, "r") as file:
            log = file.read()
        assert "test_logging_full_teardown_fails.test_pass" in log
        assert "TEST STARTED" in log
        assert "TEARDOWN ERROR / FAIL" in log
        assert "TEST COMPLETED" in log


def test_logging_basic_subdirs(testdir):
    test_file = testdir.mkdir("my-tests").join("test_logging_basic_subdirs.py")
    test_file.write("""import pytest

def test_pass(logfest_logger):
    pass
""")

    result = testdir.runpytest(
        '-v', '--logfest=basic'
    )

    assert result.ret == 0

    artifacts_dir = testdir.tmpdir.join('artifacts')

    assert os.path.isdir(str(artifacts_dir)) is True

    log_file = [file for file in os.listdir(str(artifacts_dir)) if ".log" in file]
    assert len(log_file) == 1

    pattern = re.compile("^my-tests-(\d{8}-\d{2}-\d{2}-\d{2}).log$")
    assert pattern.match(log_file[0])

    with open(str(artifacts_dir) + "/" + log_file[0], "r") as file:
        log = file.read()
    assert "my-tests.test_logging_basic_subdirs.test_pass" in log
    assert "TEST STARTED" in log
    assert "TEST COMPLETED" in log


def test_logging_full_subdirs(testdir):
    test_file = testdir.mkdir("my-tests").join("test_logging_full_subdirs.py")
    test_file.write("""import pytest

def test_pass(logfest_logger):
    pass
""")

    result = testdir.runpytest(
        '-v', '--logfest=full'
    )

    assert result.ret == 0

    artifacts_dir = testdir.tmpdir.join('artifacts')
    assert os.path.isdir(str(artifacts_dir)) is True

    log_file = [file for file in os.listdir(str(artifacts_dir)) if ".log" in file]
    assert len(log_file) == 1
    pattern = re.compile("^my-tests-(\d{8}-\d{2}-\d{2}-\d{2}).log$")
    assert pattern.match(log_file[0])

    with open(str(artifacts_dir) + "/" + log_file[0], "r") as file1:
        log = file1.read()
    assert "my-tests.test_logging_full_subdirs.test_pass" in log
    assert "TEST STARTED" in log
    assert "TEST COMPLETED" in log

    artifacts_subdir = testdir.tmpdir.join('artifacts/my-tests')
    assert os.path.isdir(str(artifacts_subdir)) is True

    log_file = [file for file in os.listdir(str(artifacts_subdir)) if ".log" in file]
    assert len(log_file) == 1
    pattern = re.compile("^test_logging_full_subdirs-(\d{8}-\d{2}-\d{2}-\d{2}).log$")
    assert pattern.match(log_file[0])

    with open(str(artifacts_subdir) + "/" + log_file[0], "r") as file2:
        log = file2.read()
    assert "my-tests.test_logging_full_subdirs.test_pass" in log
    assert "TEST STARTED" in log
    assert "TEST COMPLETED" in log
