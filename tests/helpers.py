import os
import re


def get_timestamp_from_logfile_name(logfile):
    match = re.match(r".*(\d{8}-\d{2}-\d{2}-\d{2}).*.log", logfile)
    return match.group(1)


def get_logfiles_in_testdir(dir):
    return [logfile for logfile in os.listdir(dir) if ".log" in logfile]


def assert_filename_in_list_of_files(filename, list):
    assert any(_ for _ in list if _ == filename), "File %s was not present in: %s" % (filename, list)


def assert_lines_in_logfile(logfile, present=None, not_present=None):
    with open(logfile, "r") as log_file:
        log = log_file.read()

    if present:
        for line in present:
            assert line in log, "Not present in file but should be: %s" % line

    if not_present:
        for line in not_present:
            assert line not in log, "Present in file but should not be: %s" % line
