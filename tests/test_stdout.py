import pytest


def test_report_header(testdir):
    testdir.makepyfile("""
        def test_empty():
            pass
        """)

    result = testdir.runpytest(
        '-v'
    )

    assert result.ret == 0

    result.stdout.fnmatch_lines(["*Timestamp:*"])
    result.stdout.fnmatch_lines(["*Logfest:*"])
    result.stdout.fnmatch_lines(["*Log level:*"])


def test_logging_stdout_test_passes(testdir):
    testdir.makepyfile("""
        import pytest

        def test_pass(logfest):
            logfest.debug("Debug log line")
            pass
    """)

    result = testdir.runpytest(
        '-v'
    )

    assert result.ret == 0

    assert not any(line for line in result.outlines if "Debug log line" in line)


def test_logging_stdout_test_fails(testdir):
    testdir.makepyfile("""
        import pytest

        def test_pass(logfest):
            logfest.debug("Debug log line")
            assert False
    """)

    result = testdir.runpytest(
        '-v'
    )

    assert result.ret == 1

    result.stdout.fnmatch_lines(["*Debug log line*"])
    result.stdout.fnmatch_lines(["*TEST ERROR / FAIL*"])


@pytest.mark.xfail(reason="SETUP ERROR / FAIL not in stdout; is present in log files")
def test_logging_stdout_setup_fails(testdir):
    testdir.makepyfile("""
        import pytest

        @pytest.fixture(scope='function')
        def setup():
            assert False

        def test_pass(logfest, setup):
            logfest.debug("Debug log line")
            pass
    """)

    result = testdir.runpytest(
        '-v'
    )

    assert result.ret == 1

    result.stdout.fnmatch_lines(["*SETUP ERROR / FAIL*"])
    assert not any(line for line in result.outlines if "Debug log line" in line)


@pytest.mark.xfail(reason='request.node.rep_teardown remains empty, so no TEARDOWN ERROR / FAIL is logged')
def test_logging_stdout_teardown_fails(testdir):
    testdir.makepyfile("""
        import pytest

        @pytest.fixture(scope='function')
        def teardown():
            yield

            assert False

        def test_pass(logfest, teardown):
            logfest.debug("Debug log line")
            pass
    """)

    result = testdir.runpytest(
        '-v'
    )

    assert result.ret == 1

    result.stdout.fnmatch_lines(["*Debug log line*"])
    result.stdout.fnmatch_lines(["*TEARDOWN ERROR / FAIL*"])
