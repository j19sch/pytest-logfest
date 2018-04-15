import errno
import logging
import logging.handlers
import os


try:
    from pathlib import Path
except (ImportError, AttributeError):
    from pathlib2 import Path


class LogfestLogger(object):
    def __init__(self, request):
        path_as_list, module_basename = self._get_path_and_module_basename_from_request_name(request.node.parent.name)
        # ToDo: ignore root directory of path if `testpaths` contains only one directory
        function_name = request.node.name
        log_node = ".".join(path_as_list + [module_basename, function_name])

        self.logger = logging.getLogger(log_node)

        formatter = logging.Formatter('%(asctime)s %(name)s: %(message)s', "%H:%M:%S")
        formatter_with_level = logging.Formatter('%(asctime)s %(levelname)s - %(name)s - %(message)s', "%H:%M:%S")

        if request.config.getoption("logfest") == "full":
            log_dir = os.path.sep.join(path_as_list)
            self._create_directory_if_it_not_exists('./artifacts/%s' % log_dir)
            filename_components = [module_basename, request.config._timestamp]
            request.config.hook.pytest_logfest_log_file_name_full(filename_components=filename_components)
            filename = "-".join(filename_components) + ".log"

            fh = logging.FileHandler('./artifacts/%s/%s' % (log_dir, filename), mode='a')
            fh.setLevel(logging.DEBUG)
            fh.setFormatter(formatter)
            self.logger.addHandler(fh)

        if request.config.getoption("logfest") != "quiet":
            self._create_directory_if_it_not_exists('./artifacts')
            filename_components = [request.config._timestamp]
            if path_as_list:
                filename_components.insert(0, path_as_list[0])
            else:
                filename_components.insert(0, "tests")
            request.config.hook.pytest_logfest_log_file_name_basic(filename_components=filename_components)
            filename = "-".join(filename_components) + ".log"

            file_handler = logging.FileHandler('./artifacts/%s' % filename, mode='a')
            self.logger.setLevel(logging.DEBUG)
            file_handler.setFormatter(formatter_with_level)

            file_memory_handler = MyMemoryHandler(capacity=None, flushLevel=logging.WARNING, target=file_handler)
            file_memory_handler.set_name("mem_file")
            self.logger.addHandler(file_memory_handler)

    def tear_down(self, request=None):
        try:
            if request.node.rep_setup.failed:
                self.logger.warning("SETUP ERROR / FAIL")
        except AttributeError:
            pass

        try:
            if request.node.rep_call.failed:
                self.logger.warning("TEST ERROR / FAIL")
        except AttributeError:
            pass

        # ToDo: find a different way, because no rep_teardown when this code is called
        # try:
        #     if request.node.rep_teardown.failed:
        #         self.logger.warning("TEARDOWN ERROR / FAIL")
        # except AttributeError:
        #     pass

        finally:
            self.logger.info("TEST COMPLETED\n")

        for handler in self.logger.handlers:
            if handler.get_name() == "mem_file":
                handler.target.addFilter(FilterInfoAndHigher())
                handler.flush()

            handler.buffer = []

    @staticmethod
    def _get_path_and_module_basename_from_request_name(name):
        full_path = Path(name)
        file_basename = full_path.stem

        file_path = list(full_path.parents[0].parts)

        return file_path, file_basename

    @staticmethod
    def _create_directory_if_it_not_exists(path):
        try:
            os.makedirs(path)
        except OSError as exc:
            if exc.errno == errno.EEXIST and os.path.isdir(path):
                pass
            else:
                raise


class MyMemoryHandler(logging.handlers.MemoryHandler):
    def __init__(self, *args, **kwargs):
        super(MyMemoryHandler, self).__init__(*args, **kwargs)

    def shouldFlush(self, record):
        if self.capacity is None:
            return record.levelno >= self.flushLevel
        else:
            return super(MyMemoryHandler, self).shouldFlush(record)


class FilterInfoAndHigher(logging.Filter):
    def filter(self, record):
        return record.levelno >= logging.INFO
