import inspect
from typing import Set, List

import algotrader.pipeline
import algotrader.pipeline.processors
import algotrader.pipeline.sources
import algotrader.pipeline.strategies


def _get_all_of_class(base_class):
    results: Set[str] = set()

    def list_module_childs(m):
        for name, obj in inspect.getmembers(m):
            if inspect.ismodule(obj) and obj.__name__.startswith(m.__name__):
                list_module_childs(obj)
            elif inspect.isclass(obj) and issubclass(obj, base_class) and obj.__name__ != base_class.__name__:
                results.add(obj)

    list_module_childs(algotrader.pipeline)
    return results


def _get_all_of_class_names(base_class) -> List[str]:
    return [p.__name__ for p in _get_all_of_class(base_class)]


def _get_single_by_name(base_class, name: str):
    return next(filter(lambda p: p.__name__ == name, _get_all_of_class(base_class)))


def _describe_object(obj):
    if obj.__doc__:
        print(f'Description: {obj.__doc__}')
    if obj.__init__.__doc__:
        print(f'Parameters: {obj.__init__.__doc__}')
