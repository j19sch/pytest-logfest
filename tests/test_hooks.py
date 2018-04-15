import os
import re


def test_basic_logging_filename_hook(testdir):
    testdir.makeconftest("""
        import pytest

        @pytest.mark.optionalhook
        def pytest_logfest_log_file_name_basic(filename_components):
            filename_components.append("fizzbuzz")
    """)

    testdir.makepyfile("""
        import pytest

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

    pattern = re.compile("^tests-(\d{8}-\d{2}-\d{2}-\d{2})-fizzbuzz.log$")
    assert pattern.match(log_file[0])


def test_full_logging_filename_hook(testdir):
    testdir.makeconftest("""
        import pytest

        @pytest.mark.optionalhook
        def pytest_logfest_log_file_name_full(filename_components):
            filename_components.append("fizzbuzz")
    """)

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
    pattern2 = re.compile("^test_full_logging_filename_hook-(\d{8}-\d{2}-\d{2}-\d{2})-fizzbuzz.log$")

    assert any(filename for filename in log_file if pattern1.match(filename))
    assert any(filename for filename in log_file if pattern2.match(filename))
