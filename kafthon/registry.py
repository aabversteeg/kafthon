import importlib

from .utils import get_cls_path
from .exceptions import UnknownRunnable


class Registry():
    def __init__(self):
        self.__runnables = {}

    def register_runnable(self, runnable_cls):
        runnable_path = get_cls_path(runnable_cls)
        self.__runnables[runnable_path] = runnable_cls

    def get_runnable(self, runnable_path):
        if runnable_path not in self.__runnables:
            module_name, _ = runnable_path.split('-')
            importlib.import_module(module_name)

        if runnable_path not in self.__runnables:
            raise UnknownRunnable(f'Runnable with path {runnable_path} was not registered.')

        return self.__runnables[runnable_path]


registry = Registry()


__all__ = ['registry']
