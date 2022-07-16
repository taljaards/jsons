from collections.abc import Iterable
from multiprocessing import Process
from typing import Tuple, Optional

from typish import get_args, get_type

from jsons._dump_impl import dump
from jsons._multitasking import multi_task
from jsons.exceptions import SerializationError


def default_iterable_serializer(
        obj: Iterable,
        cls: type = None,
        *,
        strict: bool = False,
        tasks: int = 1,
        task_type: type = Process,
        **kwargs) -> list:
    """
    Serialize the given ``obj`` to a list of serialized objects.
    :param obj: the iterable that is to be serialized.
    :param cls: the (subscripted) type of the iterable.
    :param strict: a bool to determine if the serializer should be strict
    (i.e. only dumping stuff that is known to ``cls``).
    :param tasks: the allowed number of tasks (threads or processes).
    :param task_type: the type that is used for multitasking.
    :param kwargs: any keyword arguments that may be given to the serialization
    process.
    :return: a list of which all elements are serialized.
    """
    # The meta kwarg store_cls is filtered out, because an iterable should have
    # its own -meta attribute.
    kwargs_ = {**kwargs, 'strict': strict}
    kwargs_.pop('_store_cls', None)
    if strict:
        cls_ = determine_cls(obj, cls)
        # cls_ = cls or get_type(obj)  # Get the List[T] type from the instance.
        subclasses = _get_subclasses(obj, cls_)
    else:
        subclasses = _get_subclasses(obj, None)

    if tasks < 2:
        return [
            dump(elem, cls=subclasses[i], **kwargs_)
            for i, elem in enumerate(obj)
        ]

    zipped_objs = list(zip(obj, subclasses))
    return multi_task(do_dump, zipped_objs, tasks, task_type, **kwargs_)


def _get_subclasses(obj: Iterable, cls: type = None) -> Tuple[type, ...]:
    subclasses = (None,) * len(obj)
    if cls:
        args = get_args(cls)
        if len(args) == 1:
            # E.g. List[int]
            subclasses = args * len(obj)
        elif len(args) > 1:
            # E.g. Tuple[int, str, str]
            subclasses = args
    if len(subclasses) != len(obj):
        msg = f'Not enough generic types ({len(subclasses)}) in {cls}, expected {len(obj)} to match the iterable of length {len(obj)}'

        raise SerializationError(msg)
    return subclasses


def do_dump(obj_cls_tuple: Tuple[object, type], *args, **kwargs):
    kwargs_ = {**kwargs, 'tasks': 1}
    return dump(*obj_cls_tuple, *args, **kwargs_)


def determine_cls(obj: Iterable, cls: Optional[type]) -> Optional[type]:
    cls_ = cls
    if not cls_ and hasattr(obj, '__getitem__') and len(obj) > 0:
        obj_with_only_one_elem = obj.__getitem__(slice(0, 1))
        cls_ = get_type(obj_with_only_one_elem)
    return cls_
