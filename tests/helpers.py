import re


def get_timestamp_from_logfile_name(logfile):
    match = re.match(r".*(\d{8}-\d{2}-\d{2}-\d{2}).*.log", logfile)
    return match.group(1)
