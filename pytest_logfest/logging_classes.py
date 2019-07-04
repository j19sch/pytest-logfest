import logging.handlers


class FilterOnLogLevel(logging.Filter):
    def __init__(self, level):
        self.level = level
        super(FilterOnLogLevel, self).__init__()

    def filter(self, record):
        return record.levelno >= self.level


class FilterOnExactNodename(logging.Filter):
    def __init__(self, node_name):
        self.node_name = node_name
        super(FilterOnExactNodename, self).__init__()

    def filter(self, record):
        return record.name == self.node_name


class MyMemoryHandler(logging.handlers.MemoryHandler):
    def __init__(self, *args, **kwargs):
        super(MyMemoryHandler, self).__init__(*args, **kwargs)

    def shouldFlush(self, record):
        if self.capacity is None:
            return record.levelno >= self.flushLevel
        else:
            return super(MyMemoryHandler, self).shouldFlush(record)

    def flush_with_filter_on_info(self):
        filter_on_info = FilterOnLogLevel(logging.INFO)

        if self.target:
            self.target.addFilter(filter_on_info)
            self.flush()
            self.target.removeFilter(filter_on_info)
        else:
            self.flush()
