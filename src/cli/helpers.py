import inspect
from typing import Set

import pipeline
import pipeline.strategies
import pipeline.processors


def _get_all_of_class(base_class):
    results: Set[str] = set()

    def list_module_childs(m):
        for name, obj in inspect.getmembers(m):
            if inspect.ismodule(obj) and obj.__name__.startswith(m.__name__):
                list_module_childs(obj)
            elif inspect.isclass(obj) and issubclass(obj, base_class) and obj.__name__ != base_class.__name__:
                results.add(obj)

    list_module_childs(pipeline)
    return results


def _describe_object(obj):
    if obj.__doc__:
        print(f'Description: {obj.__doc__}')
    if obj.__init__.__doc__:
        print(f'Parameters: {obj.__init__.__doc__}')
